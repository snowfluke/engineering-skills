#!/usr/bin/env python3
"""Check commits, branch names, and pull requests against the project's conventions.

The rules come from one fenced `pr-hygiene` block in the coding standard
(docs/coding-standard/10-comments-commits-and-docs.md, or an older single
CODING_STANDARD.md). The same file runs as a commit-msg hook, a pre-push
branch check, and a CI step, so one rule set applies everywhere.

  pr_hygiene.py commit-msg FILE            [--standard PATH]
  pr_hygiene.py branch NAME                [--standard PATH]
  pr_hygiene.py pr --title FILE --body FILE --branch NAME [--changed FILE] [--standard PATH]
  pr_hygiene.py --self-test

The block, with one key per line (repeat a key to add a value):

  ```pr-hygiene
  branch: ^(feat|fix|chore|docs|refactor|test)/(?P<kind>BE|FE|TL|DB)-S\\d+-\\d+-[a-z0-9-]+$
  commit-subject: ^(feat|fix|chore|docs|refactor|test|perf)(\\([a-z0-9-]+\\))?: \\S.{0,70}$
  forbidden: Co-Authored-By
  forbidden: Generated with
  pr-heading: ## Summary
  pr-heading: ## Tests
  test-files: (\\.test\\.|\\.spec\\.|/tests?/)
  e2e-files: ^e2e/
  tests-required: BE FE
  ```

The ASCII rule covers commit messages, the PR title, and the PR body outside
fenced code. It never covers source files: UI copy may be in any language.
A missing block or a missing key fails closed. Standard library only.
"""
import glob
import os
import re
import sys

BLOCK_RE = re.compile(r"^```pr-hygiene[ \t]*\n(.*?)^```", re.S | re.M)
REQUIRED_KEYS = ("branch", "commit-subject", "forbidden", "pr-heading", "test-files", "e2e-files", "tests-required")
STANDARD_PATHS = ("docs/coding-standard", "docs/CODING_STANDARD.md", "CODING_STANDARD.md",
                  "docs/CODING_STANDARDS.md", "CODING_STANDARDS.md")


class ConfigError(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_rules(standard=None):
    """Find the pr-hygiene block in the coding standard (a folder or a single file)."""
    paths = [standard] if standard else [p for p in STANDARD_PATHS if os.path.exists(p)]
    texts = []
    for p in paths:
        if os.path.isdir(p):
            texts += [read(f) for f in sorted(glob.glob(os.path.join(p, "*.md")))]
        elif os.path.isfile(p):
            texts.append(read(p))
    blocks = [m.group(1) for t in texts for m in BLOCK_RE.finditer(t)]
    if not blocks:
        raise ConfigError("no ```pr-hygiene block found in the coding standard "
                          f"(looked in: {', '.join(paths) or ', '.join(STANDARD_PATHS)})")
    if len(blocks) > 1:
        raise ConfigError("more than one ```pr-hygiene block in the coding standard; keep one")
    rules = {}
    for line in blocks[0].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        rules.setdefault(key.strip(), []).append(value.strip())
    missing = [k for k in REQUIRED_KEYS if k not in rules]
    if missing:
        raise ConfigError("the pr-hygiene block misses: " + ", ".join(missing))
    return rules


def non_ascii(text, label, skip_fences=False):
    errs, fence = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if skip_fences and line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        bad = sorted({c for c in line if ord(c) > 127})
        if bad:
            shown = " ".join(f"{c!r} (U+{ord(c):04X})" for c in bad)
            errs.append(f"{label} line {n}: non-ASCII {shown}. Use plain ASCII: '-' or ':' for dashes, '->' for arrows, no emoji.")
    return errs


def forbidden(text, rules, label):
    return [f"{label}: contains '{phrase}'. Remove it."
            for phrase in rules["forbidden"] if phrase.lower() in text.lower()]


def check_commit(text, rules):
    lines = [l for l in text.splitlines() if not l.startswith("#")]  # git comment lines
    body = "\n".join(lines).strip()
    errs = non_ascii(body, "commit message") + forbidden(body, rules, "commit message")
    subject = body.splitlines()[0] if body else ""
    if not any(re.match(p, subject) for p in rules["commit-subject"]):
        errs.append(f"commit subject {subject!r} does not match the pattern in the coding standard")
    return errs


def check_branch(name, rules):
    if name in ("main", "master", "dev", "test", "develop"):
        return []
    if not any(re.match(p, name) for p in rules["branch"]):
        return [f"branch {name!r} does not match the pattern in the coding standard: {rules['branch'][0]}"]
    return []


def card_kind(branch, rules):
    for p in rules["branch"]:
        m = re.match(p, branch)
        if m and "kind" in m.groupdict():
            return m.group("kind")
    return None


def sections(body):
    """Map each '## ' heading to the text under it."""
    out, cur = {}, None
    for line in body.splitlines():
        if line.startswith("## "):
            cur = line.strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def filled(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return bool(re.sub(r"[\s\-\[\]x*_>]+", "", text))


def check_pr(title, body, branch, changed, rules):
    errs = non_ascii(title, "PR title") + non_ascii(body, "PR body", skip_fences=True)
    errs += forbidden(title + "\n" + body, rules, "PR")
    errs += check_branch(branch, rules)
    found = sections(body)
    for heading in rules["pr-heading"]:
        if heading not in found:
            errs.append(f"PR body misses the template section {heading!r}")
        elif not filled(found[heading]):
            errs.append(f"PR body section {heading!r} is empty; fill it or write 'None' with a reason")
    if changed is not None:
        kind = card_kind(branch, rules)
        need_tests = set(" ".join(rules["tests-required"]).split())
        wiring = "wiring" in (title + " " + branch).lower()
        tests = [f for f in changed if any(re.search(p, f) for p in rules["test-files"])]
        e2e = [f for f in changed if any(re.search(p, f) for p in rules["e2e-files"])]
        if wiring and not e2e:
            errs.append("a wiring card must change an e2e test; none of the changed files matches e2e-files")
        elif kind in need_tests and not wiring and not tests:
            errs.append(f"a {kind} card must change a test file; none of the changed files matches test-files")
    return errs


def self_test():
    std = """# 10. Comments, commits, and docs

```pr-hygiene
branch: ^(feat|fix|chore|docs|refactor|test)/(?P<kind>BE|FE|TL|DB)-S\\d+-\\d+-[a-z0-9-]+$
commit-subject: ^(feat|fix|chore|docs|refactor|test|perf)(\\([a-z0-9-]+\\))?: \\S.{0,70}$
forbidden: Co-Authored-By
forbidden: Generated with
pr-heading: ## Summary
pr-heading: ## Tests
test-files: (\\.test\\.|\\.spec\\.|/tests?/)
e2e-files: ^e2e/
tests-required: BE FE
```
"""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "docs/coding-standard"))
        with open(os.path.join(d, "docs/coding-standard/10-comments-commits-and-docs.md"), "w") as f:
            f.write(std)
        rules = load_rules(os.path.join(d, "docs/coding-standard"))
        try:
            load_rules(d)
            raise AssertionError("a folder without the block must fail closed")
        except ConfigError:
            pass
    assert check_commit("feat(tasks): add CSV export\n\nAdds the endpoint.\n", rules) == []
    assert check_commit("feat: add export\n\nCo-Authored-By: Bot <b@x>\n", rules), "trailer not caught"
    assert check_commit("feat: add export — fast\n", rules), "em dash not caught"
    assert check_commit("feat: add export → csv\n", rules), "arrow not caught"
    assert check_commit("Added export\n", rules), "subject pattern not enforced"
    assert check_commit("feat: add export\n# Please enter the commit message\n", rules) == [], "git comments must be ignored"
    assert check_branch("feat/BE-S2-05-csv-export", rules) == []
    assert check_branch("main", rules) == []
    assert check_branch("feature/csv", rules), "bad branch not caught"
    body = "## Summary\nAdds CSV export.\n\n## Tests\n- tasks.test.ts covers AC-29.01\n\n```text\narrow → ok in code\n```\n"
    b = "feat/BE-S2-05-csv-export"
    assert check_pr("feat(tasks): CSV export", body, b, ["src/tasks.ts", "src/tasks.test.ts"], rules) == []
    assert check_pr("feat(tasks): CSV export", body, b, ["src/tasks.ts"], rules), "BE card without a test change not caught"
    assert check_pr("chore: bump deps", body, "chore/TL-S2-01-bump-deps", ["package.json"], rules) == [], "a TL chore needs no test"
    assert check_pr("feat: wiring CSV export", body, "feat/FE-S2-07-wiring-csv", ["src/view.tsx", "src/view.test.tsx"], rules), "wiring without e2e not caught"
    assert check_pr("feat: wiring CSV export", body, "feat/FE-S2-07-wiring-csv", ["e2e/csv.spec.ts"], rules) == []
    assert check_pr("feat: CSV export", "## Summary\nx\n", b, None, rules), "missing section not caught"
    assert check_pr("feat: CSV export", "## Summary\nx\n## Tests\n<!-- list tests -->\n", b, None, rules), "empty section not caught"
    assert check_pr("feat: CSV export \U0001F680", body, b, None, rules), "emoji in title not caught"
    assert check_pr("feat: CSV export", body + "\nGenerated with Claude Code\n", b, None, rules), "generated-by line not caught"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    import argparse
    ap = argparse.ArgumentParser(prog="pr_hygiene.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("commit-msg")
    c.add_argument("file")
    b = sub.add_parser("branch")
    b.add_argument("name")
    p = sub.add_parser("pr")
    p.add_argument("--title", required=True, help="file with the PR title")
    p.add_argument("--body", required=True, help="file with the PR body")
    p.add_argument("--branch", required=True)
    p.add_argument("--changed", help="file listing the changed paths, one per line")
    for s in (c, b, p):
        s.add_argument("--standard", help="the coding standard: a folder or a single file")
    a = ap.parse_args(argv)
    try:
        rules = load_rules(a.standard)
    except ConfigError as e:
        print(f"pr-hygiene: {e}", file=sys.stderr)
        sys.exit(2)
    if a.cmd == "commit-msg":
        errs = check_commit(read(a.file), rules)
    elif a.cmd == "branch":
        errs = check_branch(a.name, rules)
    else:
        changed = [l.strip() for l in read(a.changed).splitlines() if l.strip()] if a.changed else None
        errs = check_pr(read(a.title).strip(), read(a.body), a.branch, changed, rules)
    if errs:
        print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
