# Component Contract Schema

Use this reference when producing a component-to-code mapping report.

## Contract fields

```yaml
component:
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

## Mapping rules

- A repo mapping needs a path, export, story, or usage evidence.
- A design component with no repo match stays `unmapped_design_components`.
- A repo component with missing design evidence stays `unverified`, not confirmed.
- Page-specific layout and copy are not automatically reusable component API.
- Proposed API changes must be separated from confirmed mappings.
