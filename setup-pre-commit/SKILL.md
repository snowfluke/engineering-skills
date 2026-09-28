---
name: setup-pre-commit
description: Set up git hooks that run the project's own formatter, linter, and type-checker on staged files before each commit, with Husky and lint-staged. Uses oxfmt and oxlint by default for JS/TS, or the formatter and linter the project already has. Optionally adds a pre-push hook that runs the full check command. Use when the user wants pre-commit hooks, Husky, lint-staged, or commit-time formatting, linting, or type checking.
---

# Set Up Pre-Commit Hooks

Pre-commit stays fast: format and lint the staged files, then type-check.
The full test suite belongs in the aggregate check command, which runs before
hand-off, in the optional pre-push hook, and in CI.

## 1. Detect the project

- **Package manager.** `bun.lock` or `bun.lockb` (bun), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), otherwise npm. Use it for every command below.
- **Formatter and linter.** Read the manifest and config files. Use what the project already has. If it has neither, use the defaults:

  | Found | Formatter | Linter |
  | --- | --- | --- |
  | Nothing yet (default) | `oxfmt` | `oxlint`, with the anti-slop plugin if the coding standard names it |
  | Prettier config | `prettier` | keep the existing linter |
  | ESLint config | keep the existing formatter | `eslint` |

- **Scripts.** Find the type-check script (`type-check`, `typecheck`) and the aggregate check script (`complete-check`, `check`, `ci`). If one is missing, tell the user. Do not invent it.
- **Other ecosystems.** For Go, Python, or Rust, stop and propose the ecosystem's own hook tool (for example `pre-commit` or `lefthook`) with the same three steps. This skill's mechanics are for JS/TS.

## 2. Install

Install as dev dependencies: `husky`, `lint-staged`, and the formatter and linter from step 1 if they are not installed yet. Then run `<pm> exec husky init` (for npm: `npx husky init`). It creates `.husky/` and adds `"prepare": "husky"` to the manifest.

## 3. Write the hooks

`.husky/pre-commit` (Husky v9+ needs no shebang):

```sh
<pm> exec lint-staged
<pm> run type-check
```

`.lintstagedrc.json`, with the default tools:

```json
{
  "*.{js,jsx,ts,tsx,mjs,cjs}": ["oxfmt", "oxlint --fix"],
  "*.{json,md,css,yml,yaml}": ["oxfmt"]
}
```

With Prettier or ESLint, use `prettier --write` or `eslint --fix` in the same places.

If the user wants it, `.husky/pre-push`:

```sh
<pm> run complete-check
```

## 4. Verify

- `.husky/pre-commit` exists and is executable.
- `<pm> exec lint-staged` runs clean on a staged change.
- A commit with a deliberate lint error is blocked.
- `package.json` has `"prepare": "husky"`.

Hand the new files to `git-commit`. The commit itself runs the new hook, which is the last check.
