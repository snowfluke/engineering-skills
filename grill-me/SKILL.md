---
name: grill-me
description: Stress-test a plan, design, or decision by interviewing the user one question at a time, each with a recommended answer, until every open branch is decided or deferred. Reads the code and docs instead of asking when they hold the answer, checks terms against GLOSSARY.md and decisions against docs/adr/ when the repo has them, and ends with a decision log file. Use before building, or when the user says "grill me", wants a plan challenged, or wants to align on a design.
---

# Grill Me

Interview the user until the plan has no open branch. Every question carries
your recommended answer, so the user can reply "yes" and move on.

## 1. Map the open branches

Read the plan. Read the code and docs it touches. List the decisions the plan
still leaves open, and order them so that each one comes after the decisions it
depends on. Show the list in a few short lines, then start with the first item.

Add a branch when an answer opens one. Drop a branch when an answer closes it.

## 2. Ask one question at a time

Before each question, check whether the code or the docs already answer it. If
they do, state what you found with a `file:line`, and move to the next branch.
Do not ask the user what the repo can tell you.

Otherwise ask one question in this shape:

```text
Q4. <the question>
Recommend: <your answer>. <one sentence: why>
Unblocks: <the branches this decides>
```

Wait for the answer. A "yes" takes your recommendation.

## 3. Push back

- If an answer contradicts the code, a doc, the glossary, or an earlier answer, quote the conflict and ask which one is right.
- If an answer uses a vague or overloaded word, propose one precise term. Test it with a concrete scenario that sits on the edge of the definition.
- If you think an answer is wrong, say so and give your strongest reason once. Accept the user's call after that, and record it.

## 4. Update the project docs, if they exist

This step runs only for docs the repo already has. Do not create a glossary or
an ADR folder.

**`GLOSSARY.md`.** Check every term the user uses against it. When the session
settles a term, update the glossary at once, in its existing format: domain
group, canonical term, UI label if different, and a one-to-two-sentence
definition. Definitions only, no implementation detail.

**`docs/adr/`.** Offer an ADR only for a decision that meets all three tests:

1. It is hard to reverse.
2. A future reader will be surprised by it without the context.
3. It came from a real trade-off between genuine alternatives.

If the user accepts, write `docs/adr/NNNN-<slug>.md` with the next free number.
Follow the format of the existing ADRs. If they have none to copy, write a title
and one paragraph: the context, the decision, and why.

## 5. Stop, and write the decision log

Stop when every branch is decided or deferred. A deferred branch names a reason
and who decides it.

Write the log. Inside a git repo, save it as `docs/decisions/YYYY-MM-DD-<topic>.md`.
Outside one, save it as `YYYY-MM-DD-<topic>-decisions.md` in the current
directory. Tell the user the path.

```markdown
# <Topic>: decisions

Date: YYYY-MM-DD

| # | Question | Decision | Why |
|---|----------|----------|-----|
| Q1 | ... | ... | ... |

## Deferred

| Branch | Reason | Who decides |
|--------|--------|-------------|

## Docs changed

- GLOSSARY.md: <terms added or changed>
- docs/adr/NNNN-<slug>.md: <title>
```

Leave out an empty section. The log is the input for the next step, for
example `to-prd` or `technical-spec`.
