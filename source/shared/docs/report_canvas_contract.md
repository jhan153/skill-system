# Report Canvas Contract

Report Canvas is the Skill System's shared human-facing report presentation. It turns one
evidence-calibrated report model into a self-contained HTML artifact that is faster to inspect
than a long linear document. It is a presentation layer, not a report owner, router, evidence
source, validator, or claim of user understanding.

## Selection Gate

Use owner and output intent, not document length, to select the projection:

1. Once a `report-*` skill admits a task, render its primary human-facing result as Report Canvas
   HTML by default. The user does not need to repeat “HTML,” “persistent,” or “interactive.”
2. Keep ordinary non-report answers, status updates, implementation closeouts, and one-step
   factual replies in concise chat. Do not attach a report automatically after implementation;
   the active report skill's admission gate still applies.
3. Honor an explicit `chat-only`, `no file`, exact non-HTML format, raw patch, or machine-only
   request. If the host has no safe writable artifact surface, return the same calibrated result
   in concise chat and state that HTML delivery was unavailable; never invent a file or link.
4. Preserve canonical lifecycle, machine, patch, schema, and repository-required formats. Canvas
   is the default human navigation layer over those artifacts, not a replacement for them.
5. Keep archival Markdown only when the user or repository contract requires it. Markdown, chat,
   and Canvas are projections of the same report model; none outranks the underlying source,
   runtime, test, diff, or accepted decision.

The owning skill determines the claims, verdict, evidence boundary, and next action. Canvas only
determines how those already-supported claims are navigated.

## Shared Model

Author a JSON model conforming to `scripts/report-canvas/report-model.schema.json`. The first viewport
must contain:

- one outcome title and concise summary;
- an explicit document `language` tag matching the report prose;
- calibrated `status` and `evidence_status`;
- one core visual;
- no more than three material findings;
- exactly one closing action state: `kind: next` with one atomic action, or `kind: none` when the
  report owner must not invent a follow-up.

The dependency-free renderer enforces the bundled schema recursively before writing output,
including nested types, required fields, `additionalProperties`, mode-specific visuals, and
format-specific spatial asset data. Its semantic pass also rejects duplicate or dangling IDs,
invalid GLB/glTF containers, missing initial states, and overlays outside their declared geometry
or state domain. It fails closed if a future schema revision introduces a validation keyword the
renderer cannot enforce.

Put source excerpts, traces, tests, raw diffs, and long rationale in progressive evidence drawers.
Every material finding should reference the corresponding evidence IDs. Missing or conflicting
evidence stays visible; the renderer must not turn `unverified`, `mixed`, `blocked`, `abstain`, or
`user-verification-needed` into a visual pass.

The four modes are:

| Mode | Use | Typical owners |
|---|---|---|
| `decision` | verdict, recommendation, option consequence, one next choice | `report-critical`, `report-qualitative` |
| `compare` | verified before/after, changed behavior or artifact comparison | `report-diff`, qualitative comparison |
| `trace` | causal path, lifecycle progression, state/ownership sequence | `report-implementation-explainer`, `report-lifecycle-artifacts` |
| `spatial` | authoritative 3D geometry, topology, overlay, and mutation-state inspection | implementation explainer or another explicit 3D report owner |

Do not choose `spatial` merely for decoration. Use it only when 3D interaction changes what the
reader can inspect.

In `trace`, declare `trace_kind: causal` or `trace_kind: lifecycle` and keep evidence confidence in
node `status`. A lifecycle trace requires `lifecycle_status` on every node so its execution/result
state cannot fall back to prose. Never encode `planned`, `not_executed`, or another lifecycle
result in a label merely to bypass the typed model.

## Rendering

Run from the active generated `report-*` skill directory:

```bash
python3 scripts/report-canvas/render_report.py \
  --input /absolute/path/report-model.json \
  --output /absolute/path/report.html
```

The renderer, template, schema, examples, static files, and vendored dependencies are all local to
that skill under `scripts/report-canvas/`; no sibling plugin or runtime root is required. The
output is a single offline HTML file. Pico CSS is vendored as a small semantic base. Three.js,
`OrbitControls`, and `GLTFLoader` are pinned and bundled locally, then embedded only when
`mode: spatial`; decision, compare, and trace reports do not pay the Three.js payload cost.
The renderer fails when the output already exists. Pass `--force` only for an intentional
replacement; the input and output paths must always differ.

Use `scripts/report-canvas/examples/` as structural examples, never as claim or domain templates. Populate
only sections supported by the owning report.

### Artifact delivery

1. Use a user-specified path first, then an existing repository report/artifact convention, then
   the host's writable task-artifact directory. Otherwise choose a descriptive, non-colliding
   `.html` path in the current writable workspace. The renderer rejects an existing output by
   default; use `--force` only after intentionally selecting that exact replacement target.
2. Treat the JSON model as renderer input, not as the document the user must read. Retain or remove
   it according to the repository's artifact policy.
3. Return a concise chat receipt containing the outcome, a clickable HTML artifact link, the
   calibrated result/evidence label, and the single closing action state. Do not duplicate the
   report body in chat.
4. If the report owns canonical non-HTML artifacts, deliver those in their required formats and
   make Canvas the first human-facing index over them.

## Theme

- Dark mode is **Oblivion**: background `#303030`, text `#D3D7CF`, selection `#555753`, yellow
  `#EDD400`, blue `#729FCF`, green `#73D216`, orange `#FD971F`, red/error `#F92672`, and plum
  `#AD7FA8`.
- Light mode is **Oblivion Hagoromo**: warm light alpha surfaces with dark `#2E3436` text and
  Tango-derived dark accents such as blue `#3465A4`, green `#4E9A06`, orange `#CE5C00`, red
  `#A40000`, plum `#75507B`, and yellow `#C4A000`.
- Follow system preference initially, provide a manual three-state toggle, and print with the
  Hagoromo/light relationship.

The digital palette derives from
[`jbrooksuk/Oblivion`](https://github.com/jbrooksuk/Oblivion). The GMK Oblivion/Hagoromo keycap
sets inform the alpha/modifier/accent relationships, not exact web HEX conversion from plastic
codes. Keep semantic overlay colors stable across themes: selection yellow, error/non-manifold
red, added/Y green, changed/Z blue, boundary orange, and unresolved/unknown plum.

## Spatial Evidence Boundary

Prefer GLB/glTF for portable production assets. Use `buffer_geometry` with explicit `positions`,
`indices`, optional normals, and source identity arrays when raw topology is the evidence. A
spatial report may provide:

- orbit, pan, zoom, fit, and reset;
- shaded, wireframe, vertex, and normal inspection;
- source object/face selection and isolate/hide controls;
- an X clipping plane;
- before/after mutation states and a previous-state ghost;
- supplied overlays for selection, non-manifold edges, boundaries, degenerates, added, removed,
  changed, or unknown elements.

An overlay applies to every declared state unless `state_refs` names the exact states where its
authoritative indices exist. The renderer validates each overlay against every applicable state;
do not rely on the browser silently dropping out-of-range indices.

Canvas must not independently implement or infer the production topology algorithm. Issue
classes, stable source IDs, mutation states, and trace ordering must come from authoritative
source/runtime data and be labeled with evidence anchors. The viewer may perform ordinary display
operations such as raycasting, camera fitting, clipping, and rendering supplied indices. If an
overlay is unavailable, show the gap or request the smallest production readback seam; do not
compute a persuasive substitute in browser JavaScript.

For small assets, embed them in the one-file report. The renderer accepts an asset `path` relative
to the model file for GLB/glTF and replaces it with embedded data. Reject paths that escape the
model directory. Large multi-file report bundles are a future field-driven extension, not the
default.

## Interaction And Comprehension

Interaction records only observable participation. An artifact can support
`explainer_generated`, `scenario_exercised`, `behavior_compared`, `decision_confirmed`, or
`assumption_delegated`; it must never emit `understood: true` or infer comprehension from opening,
scrolling, or time-on-page.

Use a real scenario, a state toggle, a comparison, or a decision consequence to reduce passive
reading. Keep checks open-book and tied to an actual next decision. Source code, another chat, and
the evidence drawers are legitimate navigation aids, not cheating.

## Security And Portability

- Use only local vendored CSS/JavaScript. Do not add CDNs, remote scripts, analytics, fonts,
  trackers, or automatic network requests.
- Treat model content as untrusted data. Build DOM with `textContent`; never insert model content
  through `innerHTML` or evaluate it as code.
- Keep the self-contained Content Security Policy. Only explicit user clicks may navigate to
  sanitized `http`, `https`, or same-document anchors.
- Redact credentials and audience-sensitive runtime data before model creation. Rendering is not a
  redaction boundary.
- Keep dependency versions and SHA-256 values in `scripts/report-canvas/vendor/versions.json`, with
  upstream MIT licenses beside the vendored files.

## Validation

Before delivery:

1. validate the model and render it with the deterministic renderer;
2. confirm no remote dependency or unresolved template marker exists;
3. confirm non-spatial reports exclude the Three.js payload;
4. inspect the first viewport, keyboard focus, both themes, narrow layout, and evidence drawers;
5. for `spatial`, inspect one representative asset, selection, state change, overlay source IDs,
   and the no-reimplementation boundary;
6. keep actual user comprehension and field usefulness `unverified` until observed in use.
