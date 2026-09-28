# Engineering Skills

Agent skills for every engineer on the team. Tech-lead pipeline skills live in
[tech-lead-skills](https://github.com/snowfluke/tech-lead-skills).

## Skills

| Area | Skill | Use it to |
| --- | --- | --- |
| Build | `tdd` | Build a feature or fix a bug test-first, proving each test can fail |
| Build | `diagnose` | Debug a hard bug: reproduce, minimise, hypothesise, instrument, fix, regression-test |
| Plan | `grill-me` | Stress-test a plan one question at a time, and keep a decision log |
| Ship | `git-commit` | Verify, split into logical commits, and write the commit message |
| Ship | `release-notes` | Write the body of a GitHub release |
| Session | `handoff` | Compact a conversation into a handoff document for another agent |
| Session | `bro` | Re-explain the last answer in plain words |
| Session | `caveman` | Answer in terse caveman style |
| Writing | `stop-slop` | Remove AI writing patterns from prose |
| Setup | `setup-pre-commit` | Add pre-commit hooks that format, lint, and type-check staged files (oxfmt and oxlint by default) |
| Setup | `git-guardrails-claude-code` | Add Claude Code hooks that block dangerous git commands |
| Media | `anthropic-art` | Draw editorial illustrations in Anthropic's hand-drawn style |

## Install

Install with the [`skills` CLI](https://github.com/vercel-labs/skills). It works
with Claude Code, opencode, Codex, and other agents. Every installed skill adds
its description to each agent session, so install only what you use.

| Goal | Command |
| --- | --- |
| See the skills first | `npx skills add snowfluke/engineering-skills -l` |
| The everyday set, for you in every project | `npx skills add snowfluke/engineering-skills -g -s grill-me -s tdd -s diagnose -s git-commit -s stop-slop` |
| Choose interactively | `npx skills add snowfluke/engineering-skills -g` |

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

## Edit and publish (maintainer)

Clone the repo, then link its skills into your skills directory:

```bash
git clone git@github.com:snowfluke/engineering-skills.git
./engineering-skills/link.sh                  # links into ~/.claude/skills
./engineering-skills/link.sh ~/.agents/skills # or another skills directory
```

Each link points into the clone. Edit a skill in place, then commit and push
from the clone.
