---
name: tdd
description: Build a feature or fix a bug test-first, one behaviour at a time. Derives the behaviour list from the task, issue, or acceptance criteria, follows the project's own test rules, proves every new test can fail by breaking the code once after green, and hands off to git-commit when the list is done. Use when the user wants TDD, test-first development, red-green-refactor, or a bug fix covered by a behaviour test.
---

# Test-Driven Development

Build one behaviour at a time: a failing test, the least code that passes it,
then proof that the test can fail. Never write the tests in bulk. A batch of
tests describes behaviour you imagine, not behaviour you have seen.

## 1. Read the project's test rules

Read the coding standard and the review checklist (`docs/coding-standard/` and
`docs/code-review-checklist/`, or single files such as `CODING_STANDARD.md`,
`CODING_STANDARDS.md`, and `CODE_REVIEW_CHECKLIST.md` in an older project), and `CLAUDE.md` or `AGENTS.md`,
if they exist. Read two or three existing tests to learn the runner, the file
layout, and the naming. The project's rules win. The defaults in step 4 apply
only where the project says nothing.

## 2. List the behaviours

Take the behaviours from the task: the issue, the task card, or each THEN clause
of the acceptance criteria. For a bug, first check whether an existing
behaviour test should have caught it. If one should have, make it fail on the
bug, then fix the code. Add a new test only when no behaviour test covers the
case.

Write each behaviour as one observable outcome at the public interface, for
example "refuses an adapter the project does not own". Order the list so the
first item is the thinnest path through the whole feature. Show the list. Ask
the user only about what the task leaves open.

## 3. Run one cycle per behaviour

1. **Red.** Write one test for the next behaviour. Run it. It must fail on its assertion. A failure from a missing import or a syntax error does not count.
2. **Green.** Write the least code that makes it pass. Add nothing for later behaviours.
3. **Prove.** Break the implementation once: invert the condition, delete the branch, or return a wrong value. Run the test. It must go red. Restore the code. If the test stays green, it tests nothing; rewrite it.
4. Run the tests for the area you touch. Go to the next behaviour.

Do not refactor while a test is red.

## 4. Default test rules

Use these only where the project has no rule of its own.

- Test through the public interface, and assert on outcomes a caller can see. Do not test private functions or internal calls.
- Write expected values by hand. Never compute them with the code under test.
- Mock only at the system edge: the network, the clock, a third-party service. Never mock the unit under test or your own modules. Prefer an in-memory stand-in you own.
- One behaviour per test, named after the behaviour.
- No conditionals in a test.
- A test that breaks when you rename an internal function tests the implementation. Rewrite it.
- No change-detector tests: no re-recorded snapshots, no assertions on internal calls or private structure.
- For a complex feature, the e2e test covers a realistic scenario of medium or high complexity, with a failure or permission path, not only the simplest success case.
- Run e2e tests light: only the affected specs, the project's worker cap, one headless browser. Stop every server and browser you start.

## 5. Refactor on green

When every behaviour on the list passes, clean up the code you touched: remove
duplication, and pull complexity behind a smaller interface. Run the tests after
each step. Add no behaviour here. New behaviour needs a new cycle.

## 6. Finish

Run the project's full gate: type-check, lint, format, and tests. Report the
behaviours covered, confirm each one was proved to fail, and list anything
skipped with the reason. Then hand off to `git-commit`. This skill does not
commit.
