---
name: address-review
description: Answer a code review on your own pull request. Reads the latest review round, fixes each OPEN finding until its "Done when" holds, answers each QUESTION, declines a NIT only with a reason, commits and pushes the fixes, replies once per finding ID, and asks for a re-review. Works with the lead-review skill's round format, and falls back to plain review comments. Use when the user says "address the review", "fix the review comments", "reply to the reviewer", or a PR has changes requested.
---

# Address Review

Answer the review. Do not redo it: never re-review the code, never re-argue a
severity, and never touch a finding that is already RESOLVED, DECLINED, or
ANSWERED.

`scripts/open_findings.py` sits next to this `SKILL.md`. Call it by absolute
path, because the shell runs in the project. It needs only `python3`.

## 1. Read the round

```bash
gh pr view <number> --json reviews --jq '[.reviews[] | select(.body | startswith("## Round"))] | last | .body // empty' > /tmp/pr<number>-round.md
python3 <this skill's dir>/scripts/open_findings.py /tmp/pr<number>-round.md
```

It lists the OPEN findings: BLOCKERs first, then QUESTIONs, then NITs, each
with its Where, Fix, and Done when.

A commit audit keeps its rounds in an issue titled `Review: <branch> ...`, not
in a PR. Read its last round from the issue comments:

```bash
gh issue view <n> --json comments --jq '[.comments[] | select(.body | startswith("## Round"))] | last | .body // empty' > /tmp/issue<n>-round.md
```

Fix the findings on a new branch and open a PR with `open-pr`. Its body says
`Refs #<n>`, never `Closes #<n>`: the reviewer closes the issue. Reply on the
issue in step 4 with `gh issue comment`. If the file is empty, the reviewer used
plain comments: read them with `gh pr view <number> --comments`, and treat
each requested change as one finding.

Read the project's coding standard and `CLAUDE.md` or `AGENTS.md` before you
change code. The project's rules apply to every fix.

## 2. Handle each finding

| Severity | Do |
| --- | --- |
| BLOCKER | Make the Done when hold. The Fix and its diff are the reviewer's suggestion; the Done when is the contract. Run the check the Done when names. If you think the finding is wrong, change nothing for it: reply with your evidence and stop for the human. A BLOCKER cannot be declined. |
| QUESTION | Answer with facts and a `file:line`. If the answer matches its "Bug if", say so plainly; the reviewer opens a new BLOCKER. |
| NIT | Apply it, or decline it with a one-line reason. |

Fix only what the findings ask. Do not refactor nearby code in the same
change.

## 3. Verify and commit

Run the project's full check command. Commit with `git-commit`, one commit per
finding or per closely related group, and put the finding ID in the subject,
for example `fix(tasks): allow the owning project (review F1)`. Push the
branch. If a hook blocks the push, hand the push command to the user.

## 4. Reply once per finding

Post one comment that covers every OPEN finding, in ID order. Write it to a
file and post it with `gh pr comment <number> --body-file <file>`:

```text
F1: fixed in 1a2b3c4. Done when checked: adapter-scope.routes.test.ts passes a Files adapter through.
F3: answered. The vendor caps retries at 5 (docs/integrations/vendor.md:12), so the Bug if does not hold.
F5: declined. The helper is used in three modules; inlining it would repeat it.
F6: not changed. I think the finding is wrong: <evidence>. Waiting for your call.
```

The comment is ASCII only, with no attribution line. Then ask for a re-review:
`gh pr edit <number> --add-reviewer <reviewer login>`. For a commit audit, post
the reply on the issue and assign it back: `gh issue edit <n> --add-assignee <reviewer login>`.

## 5. Stop

Stop after the reply. The reviewer sets each status in the next round. If a
BLOCKER is waiting for a human call, say so in your report to the user.
