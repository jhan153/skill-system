# Review Checklist

## Package-Level
- [ ] canonical dated plan exists
- [ ] README is derived and link-only
- [ ] all required spec docs exist for the archetype
- [ ] all modifier-required spec docs exist
- [ ] phase/group docs exist
- [ ] package metadata archetype matches validator archetype
- [ ] skill-internal changes pass `scripts/self_test_phase_plan_package.py`
- [ ] every planning doc has required front matter
- [ ] every generated group doc has numeric `phase_order`
- [ ] final-manifest count is at or below 20, or the canonical plan records the explicit higher cap, nonempty reason, projected count, and complete path list
- [ ] every modifier records artifact/release-blocking deltas; `0/0` modifiers are marked `absorbed-by-archetype`
- [ ] no empty ingest summary exists when no report/prior-plan input was admitted
- [ ] derived views were materialized after canonical owners and full validation ran only after both stages

## Anti-Drift
- [ ] UI states are defined only once
- [ ] README status does not conflict with dated plan
- [ ] release thresholds are numeric
- [ ] P0 scope has contract links or explicit downgrade decisions
- [ ] blocking interfaces do not coexist with open implementation
- [ ] hard predecessors do not trail progressed dependent phases
- [ ] modifier risks have contract docs, not only prose notes
- [ ] `--strict` validation has been run before implementation handoff or handoff readiness
- [ ] release-critical docs have numeric thresholds, evidence artifacts, and non-placeholder rows
- [ ] release gate lists gate inputs and upstream gates
- [ ] `--write-validation-stamp` was used only after a passing validation run
- [ ] archetype catalog and schema are consistent
