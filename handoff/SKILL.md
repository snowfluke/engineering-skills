---
name: handoff
description: Compact the current conversation into a handoff document that a fresh agent can pick up. Optionally takes what the next session will focus on and tailors the document to it. Use when the user wants a handoff, a session summary for another agent, or to continue the work in a new session.
---

# Handoff

Write a handoff document so a fresh agent can continue the work without this
conversation.

## Where

Save it in the operating system's temp directory, not in the workspace, as
`handoff-YYYY-MM-DD-HHMM-<topic>.md`. Tell the user the path.

## What

If the user said what the next session will do, shape the document around it.

```markdown
# Handoff: <topic>

## Goal
<what the work is for, in one or two sentences>

## State
- Done: <what is finished, with commit hashes or paths>
- In progress: <what is half done, and where it stopped>
- Next: <the first concrete step for the next session>

## Artifacts
- <path or URL>: <what it is>

## Decisions
- <decision>: <why>

## Open questions
- <question>: <who can answer it>

## Suggested skills
- `<skill>`: <when to use it in the next session>
```

## Rules

- Reference an artifact that already exists (a PRD, plan, ADR, issue, commit, or diff) by path or URL. Do not copy its content.
- Leave out an empty section.
- Redact secrets: API keys, passwords, tokens, and personal data.
