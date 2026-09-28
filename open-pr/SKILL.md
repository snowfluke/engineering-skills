---
name: open-pr
description: Open a pull request for a finished card. Checks the branch name and every commit message, walks the project's review checklist against your own diff, fills every section of the PR template, runs the pr-hygiene gate on the title, body, and changed files, then opens the PR, links the card, and moves the board card to review. Use when the user says "open a PR", "create the pull request", "raise a PR for this card", or a card's work is committed and ready for review.
---

# Open a Pull Request

A reviewer should find nothing the project's own checks could have caught.
Run those checks first, then open the PR.

## 1. Check the branch and the commits

Read the base branch from the repo (`gh repo view --json defaultBranchRef`) or
the project's branch model. Then:

```bash
python3 .github/scripts/pr_hygiene.py branch "$(git rev-parse --abbrev-ref HEAD)"
for c in $(git rev-list origin/<base>..HEAD); do git log -1 --format=%B $c > /tmp/msg.txt; python3 .github/scripts/pr_hygiene.py commit-msg /tmp/msg.txt || echo "commit $c"; done
```

Reword a bad commit message before the branch is shared: `git commit --amend`
for the last commit. For an older commit, ask the user to reword it. If the project has no
`.github/scripts/pr_hygiene.py`, apply its rules by hand: ASCII only, no
attribution lines, the branch and commit patterns in the coding standard.

## 2. Run the gate and walk the checklist

Run the project's full check command. It must pass.

Then walk the review checklist against your own diff, item by item. Read the
checklist from the base branch, not from your branch, for example
`git show origin/<base>:docs/code-review-checklist/06-tests.md`. Fix every item your
diff breaks before you open the PR. If the `lead-review` skill is installed,
its `review_body.py walk` prints the checklist lines for you.

## 3. Write the title and the body

- **Title:** the commit-subject pattern from the coding standard, with the card ID.
- **Body:** read `.github/PULL_REQUEST_TEMPLATE.md` and fill every section. Card: the card ID, and the US and AC IDs it covers. Tests: each test and the AC or behaviour it proves, and how to run it. A wiring card names its e2e flow. Tick a checklist box only for a check you ran.
- No attribution line anywhere, and ASCII only.

Write the title to `/tmp/pr-title.txt` and the body to `/tmp/pr-body.md`.

## 4. Run the pr-hygiene gate

```bash
git diff --name-only origin/<base>...HEAD > /tmp/pr-changed.txt
git diff origin/<base>...HEAD > /tmp/pr-diff.txt
python3 .github/scripts/pr_hygiene.py pr --title /tmp/pr-title.txt --body /tmp/pr-body.md \
  --branch "$(git rev-parse --abbrev-ref HEAD)" --changed /tmp/pr-changed.txt --diff /tmp/pr-diff.txt
```

Fix every error and run it again. Do not argue with the gate. It refuses:

- a BE or FE card that changes no test;
- an AC ID in the body that no changed test names;
- a to-do tag, a skipped or focused test, or a throwing stub on an added line;
- a body line that says work is left over and names no card or issue.

For left-over work, file the card or issue first, then name it on that line.
If the work is not done and you cannot finish it, do not open the PR.

## 5. Open and link

```bash
gh pr create --base <base> --title "$(cat /tmp/pr-title.txt)" --body-file /tmp/pr-body.md
```

If the project files an issue per card, put `Closes #<issue>` in the Card
section, and move the issue's board card to the review column. If it does not,
reference the card ID only. Report the PR URL.
