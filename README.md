# Engineering Skills

Agent skills for every engineer on the team. They take a card or an issue to a
reviewed pull request: test-first, one commit per intent, a filled PR
template, and no half-done work. The tech lead's skills, including the review
these skills answer, live in
[tech-lead-skills](https://github.com/snowfluke/tech-lead-skills).

## Install

Install with the [`skills` CLI](https://github.com/vercel-labs/skills). It works
with Claude Code, opencode, Codex, and other agents. Every installed skill adds
its description to each agent session, so install only what you use.

| Goal | Command |
| --- | --- |
| See the skills first | `npx skills add snowfluke/engineering-skills -l` |
| The everyday set, for you in every project | `npx skills add snowfluke/engineering-skills -g -s work-card -s tdd -s git-commit -s open-pr -s address-review -s grill-me -s diagnose` |
| Every skill | `npx skills add snowfluke/engineering-skills -g --all` |
| Some skills only | `npx skills add snowfluke/engineering-skills -g -s tdd -s git-commit` |
| Choose interactively | `npx skills add snowfluke/engineering-skills` |

### Some skills only: keep the pairs together

A few skills hand off to another skill. Install them together, or the first
one stops halfway:

| If you install | Also install |
| --- | --- |
| `work-card` | `tdd`, `git-commit`, `open-pr` |
| `address-review` | `git-commit`, `open-pr` |

### One project only

Run the command in the project root without `-g`. The skills go into the
project, and the CLI writes `skills-lock.json`. Commit both, so the team gets
the same skills.

```bash
cd my-project
npx skills add snowfluke/engineering-skills -s tdd -s git-commit -a claude-code
```

| Agent flag | Skills go to |
| --- | --- |
| `-a claude-code` | `.claude/skills/` |
| `-a opencode`, `-a codex` | `.agents/skills/` |

A teammate restores the project's skills from the lock file with
`npx skills experimental_install`. That command writes to `.agents/skills/`.
On Claude Code, run the `add` command above with `-a claude-code` instead.

### Edit and publish

Clone this repository and run `./link.sh`. It links every skill into
`~/.claude/skills` (or the directory you pass), so edits land in the clone.
Commit from inside a linked skill folder: git finds the clone through the
link. Every script supports `--self-test`:

```bash
for f in */scripts/*.py; do python3 "$f" --self-test; done
```

## Where to start

| Situation | Start with |
| --- | --- |
| A card on the board | `work-card` |
| A bug issue from SIT or UAT | `work-card` with the issue number |
| A plan you are unsure of | `grill-me` |
| A bug you cannot explain | `diagnose` |
| Work done, not yet committed | `git-commit`, then `open-pr` |
| The reviewer asked for changes, on a PR or an audit issue | `address-review` |
| A project without commit hooks | `setup-pre-commit` |

## The flow

```text
card or issue -> work-card -> tdd -> git-commit -> open-pr -> lead-review -> address-review -> merge
                                                             (tech lead)     (back to lead-review
                                                                               until approved)
```

A card ends DONE or BLOCKED. DONE means every AC it owns has a test named with
the AC ID, the full check passes, and the PR is open. BLOCKED means no PR and
one question to the user. There is no third ending.

## Skills

| Area | Skill | Use it to |
| --- | --- | --- |
| Build | `work-card` | Take a card or an issue to a pull request, with the tests its kind requires |
| Build | `tdd` | Build a feature or fix a bug test-first, proving each test can fail |
| Build | `diagnose` | Debug a hard bug: reproduce, minimise, hypothesise, instrument, fix, regression-test |
| Plan | `grill-me` | Stress-test a plan one question at a time, and keep a decision log |
| Ship | `git-commit` | Verify, split into logical commits, and write the commit message |
| Ship | `open-pr` | Check the branch and commits, self-review, fill the PR template, and open the PR |
| Ship | `address-review` | Answer a review one finding at a time, and ask for a re-review |
| Ship | `release-notes` | Write the body of a GitHub release |
| Session | `handoff` | Compact a conversation into a handoff document for another agent |
| Session | `bro` | Re-explain the last answer in plain words |
| Session | `caveman` | Answer in terse caveman style |
| Writing | `stop-slop` | Remove AI writing patterns from prose |
| Setup | `setup-pre-commit` | Add hooks that format, lint, and type-check staged files, and check commit messages and branch names |
| Setup | `git-guardrails-claude-code` | Add Claude Code hooks that block dangerous git commands |
| Media | `anthropic-art` | Draw editorial illustrations in Anthropic's hand-drawn style |

## Rules the hooks and CI enforce

`setup-pre-commit` installs `pr_hygiene.py`. It reads the `pr-hygiene` block in
the project's coding standard, and checks every commit, branch, and PR:

- ASCII only in commit messages, PR titles, and PR bodies. Source files may hold any language.
- No attribution lines: no `Co-Authored-By`, no "Generated with".
- The branch and commit-subject patterns from the coding standard.
- Every section of the PR template filled.
- A backend, frontend, or fix PR changes a test. A wiring PR changes an e2e test.
- Every AC ID in the PR body is named by a changed test.
- No to-do tags, skipped tests, or focused tests on added lines.
- No "gap", "follow-up", or "still open" in the PR body without the card or issue that holds the work.
