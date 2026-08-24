# Product-Family Design Contract

Use this reference only when the repository or user supplies an authoritative shared-theme policy, approved component catalog, or family visual baselines. The profile is a project-owned input; this generic skill must not manufacture product values, thresholds, or exceptions.

## Profile shape

```yaml
product_family_profile:
  family_id:
  version:
  source:
  sha256:
  applies_to:
    platforms: []
    surfaces: []
  theme:
    modes: []
    density:
  hard_rules:
    required_theme_mechanism:
    forbidden_raw_values: []
    forbidden_imports: []
  governance_sources:
    - kind: tokens | typography | icons | assets | component_styles | surface_styles
      source:
      version:
      sha256:
      write_policy: consume_only | explicit_change_only
  component_catalog:
    source:
    version:
    sha256:
    fallback_policy: approved_match_required | native_when_unmapped | explicit_exception_only
  ux_policy:
    source:
    version:
  visual_baselines:
    - id:
      kind: component_state | surface_archetype
      source:
      viewport:
      state:
      theme_mode:
      version:
      sha256:
  verification_commands:
    - id:
      command:
      proves:
      applies_when:
  exceptions:
    - id:
      rule:
      scope:
      reason:
      authorizing_source:
      expires:
```

Use an equivalent existing repo schema instead of copying this shape when the project already has one. Record its field mapping and keep the repository authoritative.

## Resolution rules

1. Confirm that `applies_to` covers the target platform and surface.
2. Pin the profile, governance sources, catalog, UX policy, and baseline versions or digests used for the run. A mutable path alone is not a stable claim.
3. Treat only explicitly declared `hard_rules` as deterministic invariants. Treat undocumented patterns as supporting evidence, not hidden law.
4. Let the family profile own tokens, component sources, icons/assets, density, and theme mechanics. Let the selected artifact own content, hierarchy, geometry, and target state.
5. Resolve a cross-owner conflict only through an applicable profile exception or an explicit authorized user/project decision. Record the conflicting sources and affected rule.
6. Do not broaden an exception beyond its recorded rule and scope. An expired, ambiguous, or missing authorizing source does not waive a hard rule.
7. Treat governance sources as `consume_only` unless the profile explicitly says otherwise. `explicit_change_only` still requires user-scoped design-system work and authoritative replacement values or behavior.

## Fallback policy semantics

Use these meanings exactly; do not infer a more permissive fallback from the policy name.

| policy | when an approved match exists | when no approved match exists | minimum evidence and completion state |
| --- | --- | --- | --- |
| `approved_match_required` | reuse the approved component | record `unmapped`; do not implement a native/custom substitute until the catalog is authoritatively extended | catalog mapping plus app-surface import/use evidence; keep the required role unresolved |
| `native_when_unmapped` | reuse the approved component | a platform-semantic native control may be used; a custom control still needs an authorized exception | exhaustive inspected-scope no-match evidence, `unmapped` status, native call-site and accessibility evidence; may complete when other gates pass |
| `explicit_exception_only` | reuse the approved component unless a scoped exception authorizes deviation | native or custom fallback requires a scoped exception before implementation | waived rule, scope, reason, authorizing source, and call-site evidence; keep the required role unresolved without the exception |

A near visual match, generated control, or unversioned local component does not satisfy an approved match. Apply the policy per semantic role and required variant/state, not once for the whole screen.

## Enforcement boundary

- Project-specific lint, type, import-boundary, token, snapshot, or build commands can deterministically enforce only the rules they inspect. Run every applicable declared command and retain its exit status.
- A token path identifies the registry to consume; it does not authorize adding plausible colors, spacing, typography, or page/component CSS. Missing entries remain gaps for `design-tokens` unless an authoritative system change is in scope.
- Component implementations, icon sets, and baseline assets follow the same write-policy boundary. Do not patch an approved control merely to make one screen pass.
- A component export inventory proves availability, not that the target reused it. Require import/use evidence from `design-component-mapper`.
- A build proves integration, not theme fidelity or family coherence.
- A target screenshot proves rendered appearance for that state and viewport, not component provenance.
- Family coherence needs pinned component-state or surface-archetype baselines and a separate visual verdict.
- UX appropriateness is a reasoned decision plus critical-path evidence; it is not reducible to a token or screenshot check.

If an applicable profile is missing, stale, or internally inconsistent, follow established repo conventions where safe but mark family conformance `unverified`. Never claim “100% compliant” or invent a universal threshold.

## Minimum handoff

```yaml
product_family_conformance:
  profile: {source: null, version: null, sha256: null, status: pinned | missing | stale | conflict}
  applicable_hard_rules: []
  governance_sources: []
  component_catalog: {source: null, version: null, sha256: null}
  verification_receipts: []
  component_reuse_report:
  target_fidelity_verdict:
  family_coherence_verdict:
  exceptions: []
  conflicts: []
  unverified: []
```
