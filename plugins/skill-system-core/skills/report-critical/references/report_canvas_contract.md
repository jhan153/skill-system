# Report Canvas Contract

Report Canvas is the Skill System's optional human-facing HTML projection. It turns one already
completed, evidence-calibrated Markdown report into a self-contained artifact when HTML or an
inspectable spatial view is actually requested. It is a presentation layer, not a report owner,
content source, router, evidence source, quality validator, or claim of user understanding.

## Selection Gate

Use owner and output intent, not document length, to select the projection:

1. Follow `references/report_delivery_contract.md`. Markdown is the default report output; select
   Canvas only for explicit `html`/`both` delivery or when inspectable spatial evidence is required.
2. Keep ordinary non-report answers, status updates, implementation closeouts, and one-step
   factual replies in concise chat. Never attach a report or HTML automatically after a task.
3. Honor an explicit `chat-only`, `no file`, exact non-HTML format, raw patch, or machine-only
   request. If the host has no safe writable artifact surface, return the same calibrated result
   in concise chat; never invent a file or link.
4. Preserve canonical lifecycle, machine, patch, schema, and repository-required formats. Canvas
   is an optional readability/navigation layer over those artifacts, not a replacement for them.
5. Keep Markdown as the content-primary report. Markdown, chat, and Canvas never outrank the
   underlying source, runtime, test, diff, or accepted decision.

The owning skill and its Markdown report determine the claims, verdict, evidence boundary, and
next action. Canvas only determines how that same content is navigated.

## Runtime Asset Resolution

Only after HTML is selected, set `REPORT_SKILL_DIR` to the directory containing the active report
skill's resolved `SKILL.md`, then resolve the renderer inside that same package:

```text
REPORT_PLUGIN_ROOT := parent(parent(REPORT_SKILL_DIR))
REPORT_CANVAS_DIR  := REPORT_PLUGIN_ROOT/shared/report-canvas
```

This relation is identical for canonical `source/skills/<skill>` and generated Core plugin skills.
The exposed `SKILL.md` path is the authority; the working directory, inferred install root, or
presumed latest plugin version is not.

Require `$REPORT_SKILL_DIR/references/report_canvas_contract.md` and
`$REPORT_CANVAS_DIR/render_report.py`. If either is absent, treat the active package as incomplete
for HTML only. Name the missing asset and deliver the completed Markdown result. Do not wander
through sibling plugins, another provider root/cache version, unrelated checkouts, or app-managed
system-skill directories looking for a substitute.

Repository authoring uses `source/shared/docs/report_canvas_contract.md`,
`source/shared/report-canvas/`, and `source/tools/generate_targets.py`. Those paths are only for
maintaining and projecting the bundle: `generate_targets.py` does not render reports and must not
be run during an ordinary report invocation.

## Shared Model

For selected HTML delivery, derive one JSON model from the completed Markdown report and conform it
to `$REPORT_CANVAS_DIR/report-model.schema.json`. The first viewport
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

Authoring follows `references/visual_decision_contract.md`. Canvas chrome and
model copy must be sourced decisions, not a factory costume. Do not fill the
first viewport with restating kickers, decorative emoji, invented stat rows,
highlighted-keyword prose, or “not just X — it's Y.” Title the outcome in a
few words; keep the sentence in `summary`. Set `eyebrow` only when it adds a
dimension the title and mode do not already say.

The four modes are:

| Mode | Use | Typical owners |
|---|---|---|
| `decision` | verdict, recommendation, option consequence, one next choice | `report-critical`, `report-qualitative` |
| `compare` | verified before/after, changed behavior or artifact comparison | `report-implementation-explainer` (`compare`), qualitative comparison |
| `trace` | causal path, lifecycle progression, state/ownership sequence | `report-implementation-explainer`, `report-lifecycle-artifacts` |
| `spatial` | inspectable 3D, mesh, math surface/field, or graphics geometry | any `report-*` skill when seeing the shape is the claim |

### Inspectable visual gate

If the user asked to see 3D, a mesh, a math surface/field, or a graphics
result, or the material claim cannot be checked without inspecting geometry,
the core visual **must** be `spatial`. A `decision` or `trace` card wall is a
failed delivery, not a fallback. Author the model; do not restyle Canvas CSS
or write a custom Three.js page.

Geometry may be a repo/user GLB/glTF **or** `buffer_geometry` sampled from a
stated function or dataset (`purpose: display`). That sample is display data,
not a browser reimplementation of a production topology algorithm. If no
asset and no sampleable source exist, mark the spatial projection `unverified`,
name the missing file, and preserve the Markdown result. Do not invent a decorative mesh.

Do not choose `spatial` merely for decoration or “interactivity.” An API
comparison or a QA verdict with no geometry stays non-spatial and must not
embed Three.js. When the gate fires, follow `references/report_visual_authoring.md`.

In `trace`, declare `trace_kind: causal` or `trace_kind: lifecycle` and keep evidence confidence in
node `status`. A lifecycle trace requires `lifecycle_status` on every node so its execution/result
state cannot fall back to prose. Never encode `planned`, `not_executed`, or another lifecycle
result in a label merely to bypass the typed model.

## Rendering

For selected HTML delivery, invoke the resolved skill's bundled renderer by absolute path; the
working directory need not be the skill directory:

```bash
REPORT_SKILL_DIR="/absolute/path/to/active/report-skill"
REPORT_PLUGIN_ROOT="$(cd "$REPORT_SKILL_DIR/../.." && pwd)"
REPORT_CANVAS_DIR="$REPORT_PLUGIN_ROOT/shared/report-canvas"
python3 "$REPORT_CANVAS_DIR/render_report.py" \
  --input /absolute/path/report-model.json \
  --output /absolute/path/report.html
```

The renderer, template, schema, examples, static files, and vendored dependencies are stored once
under the active Core package's `shared/report-canvas/`; no sibling plugin or runtime root is
required. The
output is a single offline HTML file. Pico CSS is vendored as a small semantic base. Three.js,
`OrbitControls`, and `GLTFLoader` are pinned and bundled locally, then embedded only when
`mode: spatial`; decision, compare, and trace reports do not pay the Three.js payload cost.
The renderer fails when the output already exists. Pass `--force` only for an intentional
replacement; the input and output paths must always differ.

Use `$REPORT_CANVAS_DIR/examples/` as structural examples, never as claim or domain templates. Populate
only sections already supported by the Markdown report. Render after content stabilizes; do not
generate variants or enter a visual-polish loop.

### Artifact delivery

1. Preserve the Markdown report as the primary content artifact. For the HTML projection, use a
   user-specified path first, then an existing repository report/artifact convention, then
   the host's writable task-artifact directory. Otherwise choose a descriptive, non-colliding
   `.html` path in the current writable workspace. The renderer rejects an existing output by
   default; use `--force` only after intentionally selecting that exact replacement target.
2. Treat the JSON model as renderer input, not as the document the user must read. Retain or remove
   it according to the repository's artifact policy.
3. Return a concise chat receipt containing the outcome and Markdown link first, then the HTML
   link, calibrated result/evidence label, and closing action state. Do not duplicate the report
   body in chat.
4. If the report owns canonical non-HTML artifacts, deliver those in their required formats and
   let Markdown remain the first human-facing index. Canvas is an optional readability view.

## Theme

Oblivion / Hagoromo is the chosen report identity. Apply it as paper and ink
plus one chrome accent, not as a rainbow dashboard.

- Dark mode is **Oblivion**: background `#303030`, text `#D3D7CF`, selection `#555753`, yellow
  `#EDD400`, blue `#729FCF`, green `#73D216`, orange `#FD971F`, red/error `#F92672`, and plum
  `#AD7FA8`.
- Light mode is **Oblivion Hagoromo**: warm light alpha surfaces with dark `#2E3436` text and
  Tango-derived dark accents such as blue `#3465A4`, green `#4E9A06`, orange `#CE5C00`, red
  `#A40000`, plum `#75507B`, and yellow `#C4A000`.
- Follow system preference initially, provide a manual three-state toggle, and print with the
  Hagoromo/light relationship.
- Spend yellow on selection, focus, and the single next action. Spend the other hues only on
  evidence/status labels and spatial overlays. Do not use them as page atmosphere.
- Chrome stays a system sans, flat surfaces, a small held radius, and hairline rules. The
  renderer must not introduce Inter, a decorative page grid, a restating default kicker,
  display-size crushed tracking, pill + fog-shadow chrome, or left-bar finding cards.

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
- Keep dependency versions and SHA-256 values in `$REPORT_CANVAS_DIR/vendor/versions.json`, with
  upstream MIT licenses beside the vendored files.

## Validation

For selected HTML delivery:

1. validate the model and render it with the deterministic renderer;
2. confirm no remote dependency or unresolved template marker exists;
3. confirm non-spatial reports exclude the Three.js payload;
4. perform one bounded readback of the first viewport and evidence navigation; do not run a broad
   browser/theme/viewport suite unless the user or report claim requires it;
5. for `spatial`, inspect one representative asset, selection, state change, overlay source IDs,
   and the no-reimplementation boundary;
6. keep actual user comprehension and field usefulness `unverified` until observed in use.
