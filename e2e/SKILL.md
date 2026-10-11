---
name: e2e
description: Build or speed up a Playwright end-to-end suite that is fast, sharded and trustworthy. Measures time per project first, serves the build users get, seeds and signs in once, orders projects only where they share state, picks the worker count from the machine, splits CI into shards that skip themselves when their inputs did not change, and holds a zero-retry flake policy. Use when the user wants e2e tests set up, faster e2e, CI sharding, flaky Playwright tests fixed, or a slow browser stage cut down.
---

# Efficient end-to-end tests

A browser suite is slow for a few reasons, and each one has a fix you can
measure. Measure first, change one thing, measure again. Every number below
comes from one real suite (Testate: 13 Playwright projects, five CI shards)
unless it says otherwise.

| Change | Before | After |
| --- | --- | --- |
| Serve the built SPA, not the Vite dev server | `routes` 52.8 s; a blank "Loading..." in 1 load of 25 on the dev server | 20.3 s; 0 blank loads in 36 runs on each of the two builds |
| One CI job split into shards | a flaky test re-ran the whole 6-minute stage | it re-runs one shard; an unchanged shard skips |
| Move two projects out from behind the crawl | slowest shard 4 min 0 s: 110 s of crawl, then 45 s that waited for it | the 45 s run in the 1 min 41 s shard, beside the crawl's |

## 1. Read the project first

Read `CLAUDE.md` or `AGENTS.md`, the e2e guide if there is one (`docs/E2E.md`
or similar), `playwright.config.*`, and the CI workflow that runs the suite.
Run nothing heavy yet. On a developer's machine run one project or one spec
with one or two workers (`--workers=2`); the full chain is for CI. A laptop
running databases, an API and eight browser tabs freezes.

## 2. Measure

Add a reporter that prints, per project, the test count, the wall time from
first start to last end, and the summed test time. Wall time is what the run
waits for. Busy time over wall time is how well the workers were used. On
GitHub Actions, append the same table to `$GITHUB_STEP_SUMMARY`, so every run
shows where its minutes went. The reporter is `references/timing.ts`.

Keep the first table as the baseline. Every later step names the number it
moved.

## 3. Serve what users get

Do not point the suite at a dev server that compiles modules on request. Under
load it competes with the browsers for the same cores and produces failures
users never see. Build the frontend once when the test server starts, and
serve the built files from the backend. Keep the framework's development
build if its runtime diagnostics matter. Keep one small project on the
production build, because a bug can live in one build and not the other.

Build before the backend boots. A backend that rewrites asset paths at start
will not see a build that lands after it.

## 4. Seed once, sign in once

- `globalSetup` seeds the data through the API, once per run.
- Sign each role in once and save a `storageState` file per role. Tests load
  the file. They do not sign in through the form, unless sign-in is what they
  test.
- Never reset or wipe data in `playwright.config.*`. Every worker process
  evaluates that file.
- A slow password hash (argon2, bcrypt) makes concurrent sign-ins slow. Give
  the first assertion after a sign-in its own timeout.

## 5. Order projects only where they share state

Projects that only read the seed run first and in parallel. Projects that
change shared state (restores, deletes, a crawler that clicks every button)
run later, in a chain of `dependencies`.

Playwright runs projects in phases. A project starts only when every project
of the previous phase has finished, not only the ones it depends on. A short
project placed beside a long one waits for the long one. Put each project in
the phase where it costs the least wall clock, not the earliest phase its data
allows. Check the timing table after each move.

A crawler that clicks every control should walk one example of each kind of
screen, not every record. Clicking the same table screen once per database
engine cost a third of one crawl's time.

## 6. Pick the worker count from the machine

Read the machine at start and print the choice on the first line:

- On CI the runner does nothing else: one worker per core, four at most.
- On a developer's machine: half the cores, one fewer when the one-minute load
  average is above 70% of the cores, two at most under 12 GiB of memory, never
  fewer than one.
- An environment variable (`E2E_WORKERS`) overrides the rule.

The code is `references/capacity.ts`. Keep it a pure function with a unit
test, separate from the code that reads `os`.

## 7. Split CI into shards

One CI job per shard, each on its own runner with its own services and a fresh
instance. A shard is a list of projects.

- Keep the project list and the shard table in one data module with no
  runtime imports (`references/shards.ts`). The shard-key script reads it
  before anything is installed.
- `projectsFor(shard)` keeps the chain order inside the shard. A dependency on
  a project in another shard becomes that project's nearest predecessors in
  this shard. Dropping the dependency loses the order.
- Add a unit test that fails when a project, or a spec file, belongs to no
  shard.
- `fail-fast: false`, so one red shard does not cancel the others.
- Branch rules can require one check name. Add a small job that `needs` the
  matrix and fails when any shard failed.
- Balance by wall time from the timing table, not by test count.

## 8. Skip a shard whose inputs did not change

A shard's result depends on the app and its own specs, not on other shards'
specs or the docs. Hash the git blob of every tracked file the shard depends
on (`git ls-files -s` gives the blob hashes, so nothing is read twice).
Exclude the spec files only other shards run, and what no shard reads, such as
documentation. If the app is served from a folder you excluded (a site in
`docs/`, say), put that folder back. Use the hash as a cache key:

1. Restore the key with `lookup-only: true`.
2. On a hit, print a notice and skip every later step.
3. On success, save a small marker file under the key.

A spec-only change then runs one shard; an app change runs them all. A failed
shard is re-run alone with "Re-run failed jobs". The script is
`references/shard-key.ts`, and the workflow is `references/ci-e2e.yml`.

## 9. Make the CI setup cheap

- Start the slowest step first. Service image pulls were the slowest step, so
  they start in the background while packages install.
- Cache the package manager's download cache, keyed on the lockfile.
- Use the browser the runner already has (`channel: "chrome"` on GitHub's
  Ubuntu runners), and skip `playwright install`.
- Retry a service's health wait a few times, and print its logs on the last
  failure, rather than a bare exit code.
- Publish service ports below 32768 on Linux runners. The kernel hands out
  outgoing ports from 32768 up, so a higher host port can be taken at the
  moment Docker binds it.
- Upload the HTML report, traces and screenshots as an artifact for every
  shard, on failure and success alike.

## 10. Coverage that means something

Tag each test with the requirement it proves (`@story-42` in the title). A
small spec reads the requirement list, writes a coverage report, and pins the
total. A requirement added later fails the run until a test or an explicit
exception covers it. Tag the test that proves the requirement, not one that
passes through its screen.

## 11. Flake policy

- `retries: 0`. A retry hides the bug that a user meets once in 25 loads.
- A red test that names an app bug gets an app fix. Change the test only when
  the suite itself is wrong.
- Reproduce cheaply before you rerun anything: delay one route with
  `page.route`, throttle the CPU through CDP, or run the one spec with
  `--repeat-each`.
- Iterate on one project with `--project <name> --no-deps`.
- Stop every server, browser and container you start. A backend left on a port
  makes the next run serve old code or wipe live data.

## Before you finish

- [ ] A timing table from before and after, with the change named
- [ ] The frontend is built once and served; no dev server in the suite
- [ ] One sign-in per role, saved to `storageState`
- [ ] The worker count is printed at start, with an override
- [ ] Every project and spec belongs to a shard, and a test says so
- [ ] Each shard skips itself on unchanged inputs, and one job reports the result
- [ ] `retries: 0`
