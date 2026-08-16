# Report Visual Authoring

How a `report-*` skill fills the core visual. Chrome is already decided by
Report Canvas. Do not restyle the renderer.

## Order of work

1. Name the one claim the first viewport must make inspectable.
2. Choose the mode from that claim, not from a desire to look interactive.
3. Author the JSON model. Run the bundled renderer. Stop.

Never edit `scripts/report-canvas/static/*.css`, the template, Pico, or
Three.js. Never hand-author a custom Three.js scene, CDN, or second HTML
shell. A prettier card wall is not a report.

## Inspectable visual gate

Use `mode: spatial` when the user asked to **see** 3D, a mesh, a math
surface/field, or a graphics result, or when the material claim cannot be
checked without inspecting geometry.

Then the first viewport's `visual` must be `spatial` with real geometry:

1. A repo or user GLB/glTF, path relative to the model file.
2. Else `buffer_geometry` from a production dump or an explicit sample of a
   stated function/dataset.
3. If neither exists, do not invent a cube, statue, or indigo scene. Render
   is `blocked` or `unverified` and name the missing asset. Chat-only cards
   are not a substitute.

Sampling a stated `z = f(x, y)` (or loading a small mesh) is **authoring
display data**. It is not reimplementing a production topology algorithm in
the browser. Issue overlays still come only from supplied indices.

Use `purpose: display` for a sampled/explained shape. Use `purpose: topology`
only when overlays or identity arrays are authoritative issue evidence.

Do **not** choose spatial for an API comparison, a QA verdict with no
geometry, or “make it interactive.” That stays `decision`, `compare`, or
`trace`, and the HTML must not embed Three.js.

## Display sample

Prefer the bundled sampler over hand-typed coordinates:

```bash
python3 "$REPORT_SKILL_DIR/scripts/report-canvas/sample_display_surface.py" \
  --expr "sin(x)*sin(y)" \
  --xmin -3 --xmax 3 --ymin -3 --ymax 3 --nx 24 --ny 24 \
  --out /absolute/path/surface.geometry.json
```

Wrap the emitted `buffer_geometry` as `visual.asset`. Caption the sample
bounds, resolution, and formula. Label the geometry `observed` or
`inferred`; only a source file or measured dump is `verified`.

Allowed expression names are `x`, `y`, and the sampler's math allowlist.
Do not evaluate arbitrary Python.

## Validation

- Spatial HTML contains the bundled Three.js payload and at least one
  inspectable asset.
- Non-spatial HTML does not.
- The receipt links the HTML. Do not paste the model or restyle notes in
  chat.
