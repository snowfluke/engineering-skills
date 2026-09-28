---
name: setup-pre-commit
description: Set up git hooks that run the project's own formatter, linter, and type-checker on staged files before each commit, check every commit message and branch name against the conventions in the coding standard (ASCII only, no attribution trailers, the commit and branch patterns), and optionally run the full check before each push. Uses Husky and lint-staged, with oxfmt and oxlint as the JS/TS default. Use when the user wants pre-commit or commit-msg hooks, Husky, lint-staged, commit message rules, or branch naming rules.
---

# Set Up Git Hooks

Three hooks, each fast:

| Hook | Checks |
| --- | --- |
| `pre-commit` | Format and lint the staged files, then type-check |
| `commit-msg` | The commit message: ASCII only, no attribution trailers, the subject pattern |
| `pre-push` | The branch name, then the aggregate check command (optional) |

The message and branch rules come from the `pr-hygiene` block in the coding
standard. [scripts/pr_hygiene.py](scripts/pr_hygiene.py) reads that block, and
CI runs the same script on every pull request.

## 1. Detect the project

- **Package manager.** `bun.lock` or `bun.lockb` (bun), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), otherwise npm. Use it for every command below.
- **Formatter and linter.** Read the manifest and config files. Use what the project already has. If it has neither, use the defaults:

  | Found | Formatter | Linter |
  | --- | --- | --- |
  | Nothing yet (default) | `oxfmt` | `oxlint`, with the anti-slop plugin if the project has it (`tech-lead-setups` installs it) |
  | Prettier config | `prettier` | keep the existing linter |
  | ESLint config | keep the existing formatter | `eslint` |

- **Scripts.** Find the type-check script (`type-check`, `typecheck`) and the aggregate check script (`complete-check`, `check`, `ci`). If one is missing, tell the user. Do not invent it.
- **The `pr-hygiene` block.** Look for a fenced `pr-hygiene` block in `docs/coding-standard/10-comments-commits-and-docs.md` or in an older `CODING_STANDARD.md`. If it is missing, set up only the `pre-commit` hook, and tell the user to add the block with the `coding-standard` skill.
- **Other ecosystems.** For Go, Python, or Rust, stop and propose the ecosystem's own hook tool (for example `pre-commit` or `lefthook`) with the same checks. This skill's mechanics are for JS/TS. `pr_hygiene.py` works with any hook tool.

## 2. Install

Install as dev dependencies: `husky`, `lint-staged`, and the formatter and linter from step 1 if they are not installed yet. Then run `<x> husky init`, where `<x>` is the package runner: `bunx` on bun, `npx` on npm, `pnpm exec` on pnpm, `yarn exec` on yarn. Do not use `bun exec`: it runs a shell script, not a package binary. It creates `.husky/` and adds `"prepare": "husky"` to the manifest.

Copy [scripts/pr_hygiene.py](scripts/pr_hygiene.py) to `.github/scripts/pr_hygiene.py` in the project. The hooks and CI both call that copy. It needs only `python3`.

## 3. Write the hooks

`.husky/pre-commit` (Husky v9+ needs no shebang):

```sh
<x> lint-staged
<pm> run type-check
```

`.lintstagedrc.json`, with the default tools:

```json
{
  "*.{js,jsx,ts,tsx,mjs,cjs}": ["oxlint --fix", "oxfmt"],
  "*.{json,md,css,yml,yaml}": ["oxfmt"]
}
```

With Prettier or ESLint, use `prettier --write` or `eslint --fix` in the same places.

`.husky/commit-msg`:

```sh
python3 .github/scripts/pr_hygiene.py commit-msg "$1"
```

`.husky/pre-push`, where the full check is optional:

```sh
python3 .github/scripts/pr_hygiene.py branch "$(git rev-parse --abbrev-ref HEAD)"
<pm> run complete-check
```

## 4. Verify

- `python3 .github/scripts/pr_hygiene.py --self-test` prints `self-test OK`.
- `<x> lint-staged` runs clean on a staged change.
- A commit with a deliberate lint error is blocked.
- A commit message with an em dash or an attribution trailer is blocked.
- `package.json` has `"prepare": "husky"`.

Hand the new files to `git-commit`. The commit itself runs the new hooks, which is the last check.
