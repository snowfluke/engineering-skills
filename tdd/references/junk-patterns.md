# Junk patterns

Use this list only when the project's coding standard has none. A copy lives in
tech-lead-skills `coding-standard/references/baseline-rules.md`. Each skill
installs on its own; change both.

A test that matches one of these does not land:

1. It has no assertion.
2. It compares a value with itself or with a copy of itself.
3. It asserts a copied fixture, inventory, manifest, or export list against its source.
4. It greps for exact source text, an import, or a string. The exception: the cheapest guard of a user-facing key, byte, or path.
5. It tests a private predicate or a call shape that a boundary test already covers.
6. It repeats another test of the same contract.
7. It replays a shared helper's tests in a local copy.
8. It exists only to keep a test-only export, global, or wrapper alive.
9. It covers production code that only tests call. Delete the code and the test.
10. Its expected value comes from the helper or renderer under test.
11. Its mock implements the behaviour the test asserts, or one mock stands in for several different APIs.
12. Its fixture supplies what the code under test must produce, such as a receipt, an ordering, or a callback. Or it checks a store the code path never writes.
13. It restates a declared capability flag instead of exercising what the flag promises.
14. It is a negative test that passes for an unrelated reason, such as a refusal from a different guard.
15. Its name or fixture promises more than the test exercises.

A match stays only when it is the only guard of a public API, protocol, config,
migration, storage, security, default, or release contract.

Adapted from OpenClaw's test-audit skill. See [LICENSE-openclaw.md](LICENSE-openclaw.md).
