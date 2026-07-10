# Payment engine replacement package

Create a cross-session phase package for replacing `legacy-pay` with `new-pay` over three releases.

Constraints:

- R1 shadows authorization decisions without changing customer-visible behavior.
- R2 sends 10% of refundable test-tenant traffic to the new engine and must support immediate rollback.
- R3 retires the legacy engine only after 30 days with no unexplained parity failures.
- PCI-scoped card data must never enter logs or planning artifacts.
- Authorization result, idempotency, ledger postings, refund state, timeout behavior, and webhook order are compatibility surfaces.
- The repository has `gateway/`, `ledger/`, `webhooks/`, and `ops/` components.
- Strict behavior parity, rollback, cross-session handoff, data, and security risks are explicit. `legacy-parity` may be absorbed when the selected archetype already owns its artifacts and release gates.
- No prior report or plan is supplied, so do not generate an empty ingest summary.

Use the default 20-artifact final-manifest budget. Materialize canonical owners first, then derived navigation/group views. Planning documents do not constitute runtime validation or implementation completion.
