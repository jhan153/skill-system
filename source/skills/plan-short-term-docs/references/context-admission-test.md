# Context Admission Test

Before loading long instructions, old plans, raw archives, field feedback, or tool output, ask:

1. Is it directly connected to the current goal or explicit request?
2. Is raw content necessary for the current task?
3. Is lifecycle state active, or was this exact item explicitly requested?
4. Is it neither abandoned, superseded, nor archived?
5. Can an accepted compact summary replace it safely?

Return `admit_raw`, `admit_summary`, `explicit_request_only`, `reject_load`, or `unverified`. Prefer summaries, keep old plans explicit-only, and never load full Memory/chat/plan inventories to answer admission.
