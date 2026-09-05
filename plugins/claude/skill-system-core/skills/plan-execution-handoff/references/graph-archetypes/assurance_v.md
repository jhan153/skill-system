# assurance_v

Apply the common Compilation Model, full Selection Gate, Test Authority, Typed Edge Vocabulary,
and Plan Authoring And Validation Boundary from `../graph-method-profiles.md` before this detail.

```mermaid
flowchart TD
    R0["Accepted requirement"] --> D1["Architecture contract"]
    D1 --> C1["Implementation"]
    C1 --> V1["Unit verification"]
    V1 --> V2["Integration verification"]
    V2 --> H0["Acceptance authority gate"]
```

Use Typed Edges to record which contract is `verified_by` which node. Maker self-report cannot
replace the evidence path required by the accepted assurance contract.

