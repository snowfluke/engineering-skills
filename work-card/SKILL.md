---
name: work-card
description: Take one card from the task breakdown, or one GitHub issue, and carry it to a pull request. Reads the card, its acceptance criteria, the specs it cites, and the project's rules; checks that the cards it depends on are done; creates the branch with the project's naming pattern; builds the work by card kind (backend, frontend, wiring, e2e, or chore) with the tests each kind requires; runs the full check; then hands off to git-commit and open-pr. Use when an engineer says "take card BE-S2-05", "work on this task", "implement this card", or picks up an issue from the board.
---

# Work a Card

One card, one branch, one pull request.

## Two endings

A card ends in one of two ways. There is no third.

| Ending | What is true |
| --- | --- |
| DONE | Every AC the card owns has a test that names its AC ID and passes. The full check passes. The PR is open. |
| BLOCKED | No PR. You ask the user one question that names the blocker. |

Never end with a list of what is left. "One gap remains", "mostly done", and
"still open" are not endings. If part of the work belongs to another card, file
that card or issue first. Then name it in the PR. The pr-hygiene gate refuses a
PR that says work is left over without a card ID or an issue number.

## 1. Read the card

Find the card on the board: `docs/task-breakdown/sprint-N.md`, an older
`docs/TASK_BREAKDOWN.md`, or its issue. Note its ID, title, AC IDs, spec
links, and the cards it depends on, when the board records them. If a card it
depends on is not merged, end BLOCKED.

A card can be a GitHub issue with no board row, for example a SIT or UAT bug.
Read it with `gh issue view <number>`. The issue number is its ID, and its
labels give its kind: `type:bug` is a fix with a regression test, because the
existing tests missed it.

## 2. Read the rules

Read each AC's GIVEN, WHEN, and THEN; the spec sections the card cites; the
coding standard and its `pr-hygiene` block; the review checklist; `CLAUDE.md`
or `AGENTS.md`; and the glossary. If an AC is unclear or conflicts with a
spec, end BLOCKED with that question. Do not guess the requirement.

If no spec defines the contract the card needs (the route, its inputs, its
errors), end BLOCKED. Ask one question, with the contract you propose as the
recommended answer. Build after the user confirms it.

A card can cite an AC whose THEN clause belongs to another layer, for example
a backend card that cites a frontend error message. Test the part your layer
produces. In the PR body, put that AC on a line that names the card that owns
the rest, for example `AC-29.05: the toast is FE-S2-06`.

## 3. Branch

Create the branch from the base branch with the pattern in the `pr-hygiene`
block, for example `feat/BE-S2-05-csv-export`, or `fix/123-login-timeout` for
issue 123. Check it:

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

Put the AC ID in the title of each test that proves it, for example
`test("AC-29.02 exports only the visible rows", ...)`. The gate matches AC IDs
in the PR body against the changed test files.

Do not leave a to-do tag, a skipped test, a focused test, or a stub that throws
in the diff. The gate refuses each one on an added line.

Follow the coding standard in every file. Clean up every server, browser, or
watcher you start.

## 5. Check

Run the project's full check command. It must pass. If the project has no
single command, run each gate it has: type-check, lint, format, and the tests.
If a gate needs a service that is not running, such as a database, start it
the way the development guide says and stop it after. If you cannot start it,
end BLOCKED. Run e2e specs light
locally: only the affected specs, the project's worker cap, one headless
browser. Confirm the "Done when" of the card's kind holds. If it does not
hold, keep working. If you cannot make it hold, end BLOCKED.

For a frontend or wiring card, also check the page in a real browser. Tests
pass on markup; a person sees the page.

1. Reuse the running dev server. If none runs, start it and note its PID and port.
2. Open the page headless with the project's Playwright, or with the browser tool your harness has.
3. Wait for the network to go idle before you read the page.
4. Walk each AC outcome the card owns: the text, and the loading, empty, and error states. Take one screenshot per state into `tmp/`, and look at each one.
5. Close the browser. Stop the server if you started it.

Do not commit the screenshots or the check script. A state that looks wrong is
a failed check, even when the tests pass.

## 6. Hand off

Commit with `git-commit`, with the card ID in each commit. Then open the pull
request with `open-pr`. When the review comes back, answer it with
`address-review`.
