# Engineering Skills

Agent skills for every engineer on the team. Tech-lead pipeline skills live in
[my-tech-lead-flow](https://github.com/snowfluke/my-tech-lead-flow).

## Skills

| Area | Skill | Use it to |
| --- | --- | --- |
| Build | `tdd` | Build a feature or fix a bug test-first (rework pending) |
| Build | `diagnose` | Debug a hard bug: reproduce, minimise, hypothesise, instrument, fix, regression-test |
| Plan | `grill-me` | Stress-test a plan or design before you build it (rework pending) |
| Ship | `git-commit` | Verify, split into logical commits, and write the commit message |
| Ship | `release-notes` | Write the body of a GitHub release |
| Session | `handoff` | Compact a conversation into a handoff document for another agent |
| Session | `bro` | Re-explain the last answer in plain words |
| Session | `caveman` | Answer in terse caveman style |
| Writing | `stop-slop` | Remove AI writing patterns from prose |
| Setup | `setup-pre-commit` | Add Husky pre-commit hooks with lint-staged, type checks, and tests |
| Setup | `git-guardrails-claude-code` | Add Claude Code hooks that block dangerous git commands |
| Media | `anthropic-art` | Draw editorial illustrations in Anthropic's hand-drawn style |
| Media | `app-launch-video` | Build a 90 s to 3 min launch video for an app you have the source of |
| Media | `motion-reel` | Build a 15 to 45 s looping motion-graphics reel |

`app-launch-video` needs the HyperFrames skills: `npx skills add heygen-com/hyperframes -g`.

## Install

Pick the skills you need. Every installed skill adds its description to each
agent session, so install only what you use.

```bash
npx skills add snowfluke/engineering-skills -l      # list the skills
npx skills add snowfluke/engineering-skills -g      # choose skills interactively
```

## Edit and publish (maintainer)

Clone the repo, then link its skills into your skills directory:

```bash
git clone git@github.com:snowfluke/engineering-skills.git
./engineering-skills/link.sh                  # links into ~/.claude/skills
./engineering-skills/link.sh ~/.agents/skills # or another skills directory
```

Each link points into the clone. Edit a skill in place, then commit and push
from the clone.
