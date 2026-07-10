# Independent qualitative review B

- Reviewer: `/root/review_forward_b`
- Checked at: `2026-07-10T18:53:06Z`
- Scope: 9.1.1 ledger-mode and Kanboard forward artifacts plus their case contracts
- 9.1.0 observed artifacts: not read

## solar-911-ledger-modes-001 — PASS

- Primary output SHA-256: `c9dc2f792fae25ab7dd9419585f18c16fd1e9af4088b1f47720f5f45aa63359e`
- Final owner is `workflow-validation`; `gpt-5.6-sol` outer exit is 0.
- Distinct run IDs produced distinct SHA-256 directories and one-event ledgers; both chains verified independently.
- The family analyzer reported `ledger_count: 2` and `distinct_run_ids: 2`.
- Output gate remained `observe` while Recovery Guard independently changed between `audit` and `off`.
- No global temp fallback, run mixing, mode collapse, or live `~/.codex` mutation was observed.

Supporting SHA-256:

- `alpha-hook-events.jsonl`: `cb114e2f6d1342547f647f19cd50ab141bb01260ac9426d77715eddb29626cc9`
- `beta-hook-events.jsonl`: `65cb368791cce31a3fc53cbfeb81839c5695bb8e9c4e42f09cd14bb82c090700`
- `measurement.json`: `2701aa8f0a3e16ae9c7e32499d346714ad83b01f04faf304da50af15720c3e16`
- `status-audit.json`: `89414b8bd1eebcc7b0ad9948d79e6251a74897a239c303b3c4465cab519f31fc`
- `status-off.json`: `e3629b0bcfdabc23f7e26c01f7341e83cb468a562252a91bcac0e5113e584885`

## solar-911-kanboard-unittest-fallback-001 — PASS

- Primary output SHA-256: `2dc8d108e3b0e7aa81ba4575c63f838aad2aa8e2c0fe30f3e02b9e865b2f1db5`
- Final owner is `workflow-validation`; `gpt-5.6-sol` outer and verifier exits are 0.
- The pytest probe failed with `ModuleNotFoundError` and exit 1, selecting required stdlib unittest discovery.
- The actual fallback ran 97 tests, returned `OK`, and produced profile/check `PASS` with zero skips.
- No stale reviewed state or execution-free PASS claim was used.

Supporting SHA-256:

- `integration-profile.json`: `9c47a90a1fb426671f222a4e01ee5baea2d9336f7a5b2e45762524c806fe517c`
- `invocation-receipt.json`: `728454e847d3832db8c3b3c9585005838814360fdd313247a622512f8dce6c37`
- `pytest-probe.txt`: `c719d37b0cb3556c225c89dd014a15d79a30a0e3e8b312e33d794b6dbbcac0e6`
