# controlled_transition

Apply the common Compilation Model, full Selection Gate, Test Authority, Typed Edge Vocabulary,
and Plan Authoring And Validation Boundary from `../graph-method-profiles.md` before this detail.

```mermaid
flowchart TD
    R0["Preflight"] --> G1["Approval and rollback ready"]
    G1 --> C1["Canary or bounded batch"]
    C1 --> V1["Readback"]
    V1 --> D1["Advance or rollback"]
    D1 --> H0["Close approval"]
```

No irreversible step runs before approval and rollback readiness. Each batch has direct
readback; a failed readback selects rollback or stop, never automatic continuation.

