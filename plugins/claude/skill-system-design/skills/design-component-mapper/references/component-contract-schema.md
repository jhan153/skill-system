# Component Contract Schema

Use this reference when producing a component-to-code mapping report.

## Contract fields

```yaml
catalog:
  source:
  version:
  sha256:
  scope:
  fallback_policy: approved_match_required | native_when_unmapped | explicit_exception_only
component:
  semantic_role:
  design_name:
  design_source:
  repo_name:
  repo_path:
  export_name:
  current_usage:
  variants:
    - name:
      design_value:
      repo_prop:
      status: mapped | missing | conflict | inferred
  states:
    - name:
      design_evidence:
      repo_evidence:
      status: implemented | missing | conflict | unverified
  slots:
    - name:
      required:
      repo_mechanism:
  events:
    - name:
      trigger:
      repo_handler:
  responsive_behavior:
    - breakpoint:
      expected:
      repo_evidence:
  accessibility:
    role:
    label_source:
    keyboard_expectation:
    focus_expectation:
  gaps: []
```

## Reuse report

Use this shape after implementation when a catalog or family policy makes reuse material:

```yaml
component_reuse:
  target_surface:
  semantic_role:
  required_behavior:
  catalog_component_id:
  repo_path:
  export_name:
  variant:
  app_surface_evidence:
    file:
    import_or_use_site:
    evidence_method: source | ast | project_lint
  status: planned | reused | approved_exception | unmapped | conflict | unverified
  nearest_rejected_candidate:
  exception:
    waived_rule:
    scope:
    reason:
    authorizing_source:
  verification_receipt:
  gaps: []
```

## Mapping rules

- A repo mapping needs a path, export, story, or usage evidence.
- `reused` needs actual app-surface import/use evidence; catalog membership or an export listing proves availability only.
- `planned` records an intended mapping only and cannot close a post-implementation reuse gate.
- A matching approved component makes a raw/default/custom app-surface implementation a `conflict` unless a scoped authorized exception applies.
- Semantic primitives inside the approved component's implementation remain outside the app-surface violation boundary.
- A design component with no repo match stays `unmapped_design_components`.
- An unmapped role follows the declared fallback policy; do not invent a match or exception.
- A repo component with missing design evidence stays `unverified`, not confirmed.
- Page-specific layout and copy are not automatically reusable component API.
- Proposed API changes must be separated from confirmed mappings.
- Project-specific AST/lint/import rules may prove only the exact boundary they inspect. Generic regex or export scans do not establish semantic reuse.

## Fallback outcomes

- `approved_match_required`: a no-match role stays `unmapped` and blocks that required control until the catalog is authoritatively extended; no native/custom substitute is allowed.
- `native_when_unmapped`: after inspected-scope no-match evidence, allow a platform-semantic native control with call-site/accessibility evidence; custom controls still require an authorized exception.
- `explicit_exception_only`: native or custom fallback requires the recorded waived rule, scope, reason, and authorizing source before implementation; otherwise remain blocked.

An approved match always remains mandatory unless the active policy explicitly permits and evidences a scoped deviation.
