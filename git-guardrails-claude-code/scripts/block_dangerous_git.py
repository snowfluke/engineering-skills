#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block destructive git commands.

Reads the hook JSON on stdin and checks tool_input.command. Exit 2 blocks the
command and shows stderr to the agent. Exit 0 lets it run.

The command is split into shell tokens, so a dangerous phrase inside a commit
message or a heredoc body does not block, and long flag forms do not slip
through. A command that cannot be parsed is blocked: the hook fails closed.

  block_dangerous_git.py --self-test
"""
import json
import re
import shlex
import sys

OPERATORS = {"&&", "||", ";", "|", "&", "(", ")", "\n"}
SHELLS = {"bash", "sh", "zsh", "eval"}
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def strip_heredocs(command):
    """Drop heredoc bodies; their text is data, not commands."""
    out, end = [], None
    for line in command.split("\n"):
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = re.search(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", line)
        if m:
            end = m.group(1)
    return "\n".join(out)


def segments(command):
    lexer = shlex.shlex(strip_heredocs(command), posix=True, punctuation_chars=True)
    lexer.whitespace = " \t\r"  # keep newlines as command separators
    lexer.whitespace_split = True
    seg = []
    for tok in lexer:
        if tok in OPERATORS or set(tok) <= set("&|;()"):
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok)
    if seg:
        yield seg


def short_flags(args):
    """Letters of clustered short flags: -fdx gives {'f', 'd', 'x'}."""
    return {c for a in args if a.startswith("-") and not a.startswith("--") for c in a[1:]}


def git_reason(args):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_GLOBAL_WITH_VALUE else 1
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    flags = short_flags(rest)
    if sub == "push":
        return "git push"
    if sub == "reset" and "--hard" in rest:
        return "git reset --hard"
    if sub == "clean" and ("f" in flags or "--force" in rest):
        return "git clean -f"
    if sub == "branch" and ("D" in flags or (("d" in flags or "--delete" in rest) and ("f" in flags or "--force" in rest))):
        return "git branch -D"
    if sub in ("checkout", "restore") and "." in rest:
        return f"git {sub} ."
    return None


def reason(command, depth=0):
    for seg in segments(command):
        i = 0
        while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
            i += 1  # skip VAR=value prefixes
        if i >= len(seg):
            continue
        cmd, args = seg[i].rsplit("/", 1)[-1], seg[i + 1:]
        if cmd == "git":
            found = git_reason(args)
            if found:
                return found
        elif cmd in SHELLS and depth < 3:
            inner = args[args.index("-c") + 1] if "-c" in args and args.index("-c") + 1 < len(args) else " ".join(args)
            found = reason(inner, depth + 1)
            if found:
                return found
    return None


def check(command):
    """Return the blocking reason, or None to allow."""
    try:
        return reason(command)
    except ValueError as e:
        return f"a command the guardrail cannot parse ({e})"


def self_test():
    blocked = [
        "git push", "git push --force origin main", "git reset --hard", "git reset --hard HEAD~1",
        "git clean -f", "git clean -fd", "git clean -xfd", "git clean --force",
        "git branch -D topic", "git branch --delete --force topic", "git branch -d -f topic",
        "git checkout .", "git checkout -- .", "git restore .", "git restore --staged --worktree .",
        "cd repo && git reset --hard", "git -C repo reset --hard", "/usr/bin/git push",
        'bash -c "git reset --hard"', "FOO=1 git push", "echo $(git reset --hard)",
        'git commit -m "unclosed',
    ]
    allowed = [
        "git status", "git log -- .", "git diff .", "git add .", "git checkout -b feature",
        "git branch -d merged", "git restore --staged file.ts", "git fetch origin",
        'git commit -m "document why reset --hard is blocked"',
        "git commit -F - <<'EOF'\nwe don't run git reset --hard or git push here\nEOF",
        'echo "git push"', "grep -rn 'git push' docs",
    ]
    for c in blocked:
        assert check(c), f"should block: {c!r}"
    for c in allowed:
        assert not check(c), f"should allow: {c!r} (got {check(c)!r})"
    print("self-test OK")


def main():
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (ValueError, AttributeError):
        print("BLOCKED: the guardrail could not read the hook input.", file=sys.stderr)
        sys.exit(2)
    found = check(command or "")
    if found:
        print(f"BLOCKED: this command runs `{found}`. The user has prevented you from doing this.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
