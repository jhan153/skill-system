# Report Delivery Contract

This contract defines the shared delivery boundary for `report-*` skills. Report meaning belongs
to the selected report owner. Delivery format never adds evidence, findings, verdicts, actions, or
workflow authority.

## Delivery Modes

| Mode | Activation | Required output |
| --- | --- | --- |
| `markdown` | default, or explicit Markdown/마크다운 request | one content-first Markdown report |
| `html` | explicit HTML request | one HTML projection plus a concise Markdown receipt or summary |
| `both` | explicit both/둘 다 request | one Markdown report and one HTML projection of the same content |
| `spatial` | the material claim requires inspectable 3D/mesh/math/graphics evidence | Markdown report plus spatial HTML when authoritative geometry exists |

An explicit `chat-only`, `no-file`, machine schema, raw patch, or other exact format overrides this
table. Do not create HTML merely because a report skill ran, a task finished, or an artifact is
large.

## Markdown Primary

- Complete the report's reasoning and evidence calibration in Markdown before considering HTML.
- Use only sections material to the selected report owner. Prefer direct prose, compact tables, and
  source links over dashboard cards, slogans, restating headings, or decorative summaries.
- Markdown is the content source for any secondary projection. If it is written to a file, use the
  user path, repository convention, or a descriptive non-colliding `.md` path in the writable task
  workspace, in that order.
- A simple report may stay in chat when the user requested chat-only or no durable artifact is
  useful. Do not manufacture a file solely to satisfy a template.

## HTML Projection

- Read `references/report_canvas_contract.md` only for `html`, `both`, or `spatial` delivery.
- Copy the Markdown report's supported title, summary, findings, evidence links, limitations, and
  closing action into the Canvas model. HTML may reorder or progressively disclose content for
  readability, but it must not add or strengthen a claim.
- Do not invent a visual relationship to satisfy the renderer. If no material relationship merits
  an HTML visual and HTML was not explicitly requested, stop with Markdown.
- Render once after the Markdown content is stable. Fix only a concrete structural/render failure;
  do not enter a visual-polish loop, generate variants, or repeatedly inspect themes/viewports.
- A missing or failed renderer affects only HTML. Deliver the completed Markdown with the exact
  HTML limitation instead of blocking or relabeling the report's substantive result.
- A later request for HTML may project the existing Markdown without repeating source analysis;
  reread evidence only when the report is stale or the requested content changed.

## Plan And Workflow Boundary

- A Report skill runs only on explicit report intent or an already accepted Plan node. It is never
  an automatic post-implementation, review, release, or closeout step.
- A report result never edits the reviewed artifact, changes Plan/Handoff, selects a successor,
  starts repair or validation, or becomes evidence merely because it was rendered.
- When a Plan names a Report node or QA condition, return only the assigned report artifact and
  condition-local result. The Coordinator applies the existing edge.
- Closing actions are user-facing recommendations, not dispatch commands.

## Delivery Receipt

Return the outcome and the Markdown link first. Add the HTML link only when produced. Name the
substantive status separately from projection status, and do not duplicate the report body in chat.
