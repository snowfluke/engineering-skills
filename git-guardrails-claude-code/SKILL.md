---
name: git-guardrails-claude-code
description: Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
---

# Setup Git Guardrails

Sets up a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them.

## What Gets Blocked

- `git push`, in every form
- `git reset --hard`
- `git clean` with `-f` or `--force`, in any flag cluster (`-fd`, `-xfd`)
- `git branch -D`, and `--delete` with `--force`
- `git checkout .` and `git restore .`, including `checkout -- .` and `restore --staged --worktree .`

The script splits the command into shell tokens and checks each git subcommand and its flags. It also checks commands after `&&`, `;`, and `|`, inside `$(...)`, and inside `bash -c "..."`. A dangerous phrase inside a commit message or a heredoc body does not block. A command it cannot parse is blocked.

When blocked, Claude sees a message that the user has prevented the command.

Requirements: `python3` on the machine. Known limit: it checks the command text, so a script file that runs git internally is not inspected.

## Steps

### 1. Ask scope

Ask the user: install for **this project only** (`.claude/settings.json`) or **all projects** (`~/.claude/settings.json`)?

### 2. Copy the hook script

The hook is two files in [scripts/](scripts/): `block-dangerous-git.sh`, a small wrapper, and `block_dangerous_git.py`, the logic. Copy both to the same folder:

- **Project**: `.claude/hooks/`
- **Global**: `~/.claude/hooks/`

Make both executable with `chmod +x`.

### 3. Add hook to settings

Add to the appropriate settings file:

**Project** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**Global** (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

If the settings file already exists, merge the hook into existing `hooks.PreToolUse` array — don't overwrite other settings.

### 4. Ask about customization

Ask if user wants to add or remove any blocked command. Edit `git_reason()` in the copied `block_dangerous_git.py`, add a case to its self-test, and run the self-test.

### 5. Verify

Run the self-test. It checks every blocked form and a set of commands that must pass:

```bash
python3 <hooks folder>/block_dangerous_git.py --self-test
```

It prints `self-test OK`. Do not test by typing a blocked command: the installed hook blocks the test itself.
