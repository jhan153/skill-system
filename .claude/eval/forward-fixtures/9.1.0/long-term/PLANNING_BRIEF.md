# Payment engine replacement package

Create a multi-document, cross-session phase package for replacing `legacy-pay` with `new-pay` over three releases.

Constraints:

- R1 shadows authorization decisions without changing customer-visible behavior.
- R2 sends 10% of refundable test-tenant traffic to the new engine and must support immediate rollback.
- R3 retires the legacy engine only after 30 days with no unexplained parity failures.
- PCI-scoped card data must never enter new logs or planning artifacts.
- Authorization result, idempotency, ledger postings, refund state, timeout behavior, and webhook order are compatibility surfaces.
- The current repository has `gateway/`, `ledger/`, `webhooks/`, and `ops/` components.
- Existing evidence includes a static endpoint inventory and one week of sampled authorization traces. Refund and timeout traces are not yet available.

The package must be resumable by another agent in a later session. Planning documents do not constitute runtime validation or implementation completion.
