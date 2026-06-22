# Wiki Bank Projection

Generated from accepted knowledge claims. This projection is not a Source of Truth.

## Claims

### KC-20260621-101

- Type: `decision`
- Authority: `normative`
- Context density: `low`
- Freshness: `current`
- Statement: 8.0.0 is the current Context Compounding target.
- Source spans: docs/plan/2026-06-21-context-assurance-llm-wiki-kanboard.md#section-4.5

### KC-20260621-102

- Type: `compatibility_contract`
- Authority: `normative`
- Context density: `mixed`
- Freshness: `current`
- Statement: 7.4.x labels are legacy transition traces, not the implementation target.
- Source spans: docs/plan/2026-06-21-context-assurance-llm-wiki-kanboard.md#section-7

### KC-20260621-103

- Type: `plan_state`
- Authority: `operational`
- Context density: `low`
- Freshness: `current`
- Statement: Active Kanboard card KB-20260621-001 anchors the current 8.0 implementation context.
- Source spans: kanboard://card/KB-20260621-001#status

## Relations

- `KE-20260621-101`: `KC-20260621-102` supports `KC-20260621-101`
- `KE-20260621-102`: `KC-20260621-103` depends_on `KC-20260621-101`
