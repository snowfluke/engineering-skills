# Card kinds

Find the card's kind first. The Card ID prefix gives it (`BE-`, `FE-`, `TL-`,
`DB-`); a card with "wiring" in its title is a wiring card; a card whose work
is an e2e spec is an e2e card. An older board may name the role in a column.

| Kind | Build | Tests that must change | Done when |
| --- | --- | --- | --- |
| Backend (`BE`) | The service and the handler in the module pattern of the coding standard. The contract and the error codes follow `docs/api-specs/`. | A behaviour test for each AC the card owns. A refusal test for each error the service returns, asserting the code and the details. | Each owned AC passes as a test. The operation's row in the api-spec status tracker says `OK`. |
| Frontend (`FE`) | The feature in the frontend pattern of the coding standard, against the stub or the real contract. The loading, empty, and error states. UI text copied verbatim from the AC. | A behaviour test for each visible outcome the card owns. | Each owned AC outcome has a test. Every UI string matches the AC text exactly. |
| Wiring | Replace the mock with the real client. Map the live errors, empty results, and permission refusals. | An e2e flow that proves the AC end to end: a realistic scenario with a failure or permission path, not only the happy path. | The e2e flow passes against the running dev server. |
| E2E | A realistic scenario of medium or high complexity. Set up its own data and remove it after. Tag it heavy if it is slow. | The e2e spec itself. Break the feature once and watch the spec fail. | The spec passes in CI and runs light locally. |
| Chore (`TL`, `DB`) | Configuration, dependencies, scaffold, or schema. No change in behaviour. | None required. A schema change runs the project's migration checks. | The full check passes. The PR says there is no behaviour change. |

A card that fits two kinds, for example a backend card with a schema change,
follows both rows.
