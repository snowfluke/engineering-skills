---
name: work-card
description: Take one card from the task breakdown and carry it to a pull request. Reads the card, its acceptance criteria, the specs it cites, and the project's rules; checks that the cards it depends on are done; creates the branch with the project's naming pattern; builds the work by card kind (backend, frontend, wiring, e2e, or chore) with the tests each kind requires; runs the full check; then hands off to git-commit and open-pr. Use when an engineer says "take card BE-S2-05", "work on this task", "implement this card", or picks up an issue from the board.
---

# Work a Card

One card, one branch, one pull request.

## 1. Read the card

Find the card on the board: `docs/task-breakdown/sprint-N.md`, an older
`docs/TASK_BREAKDOWN.md`, or its issue. Note its ID, title, AC IDs, spec
links, and the cards it depends on. If a card it depends on is not merged,
stop and tell the user.

## 2. Read the rules

Read each AC's GIVEN, WHEN, and THEN; the spec sections the card cites; the
coding standard and its `pr-hygiene` block; the review checklist; `CLAUDE.md`
or `AGENTS.md`; and the glossary. If an AC is unclear or conflicts with a
spec, stop and ask. Do not guess the requirement.

## 3. Branch

Create the branch from the base branch with the pattern in the `pr-hygiene`
block, for example `feat/BE-S2-05-csv-export`. Check it:

```bash
git switch -c <branch> origin/<base>
python3 .github/scripts/pr_hygiene.py branch <branch>
```

## 4. Build by card kind

Find the card's kind in [references/card-kinds.md](references/card-kinds.md).
Its row says what to build, which tests must change, and when the card is
done. For a behaviour card (backend, frontend, wiring, e2e), build it with the
`tdd` skill, one behaviour at a time. For a chore, make the change and keep
behaviour the same.

Follow the coding standard in every file. Clean up every server, browser, or
watcher you start.

## 5. Check

Run the project's full check command. It must pass. Run e2e specs light
locally: only the affected specs, the project's worker cap, one headless
browser. Confirm the "Done when" of the card's kind holds.

## 6. Hand off

Commit with `git-commit`, with the card ID in each commit. Then open the pull
request with `open-pr`. When the review comes back, answer it with
`address-review`.
