# Visual Decision Contract

Shared presentation rule for design implementation and Report Canvas authoring.
It is not a taste catalog, a linter, or a license to restyle a chosen brand.

Slop is the **absence of a decision**. A gradient, serif, emoji, badge, or
monospace chrome is allowed when a source chose it. The same mark is slop when
it is a factory default used to look finished.

## Rule

Every visual or copy mark must be sourced, explicitly proposed by the delegated visual-design
owner, or removed:

- **Sourced:** user instruction, product-family profile, approved catalog, repo
  token/theme, measured evidence, or a named brand asset.
- **Proposed:** only when the user explicitly delegated new UI visual design to
  `workflow-ui-design`; tie the choice to accepted content hierarchy, product behavior, platform,
  brand context, and required states, and label it as a proposed design decision rather than
  existing product truth.
- **Removed:** unspecified chrome filled with a generative default so the
  surface looks designed.

Outside delegated visual creation, keep the existing sourced look or ask when the choice changes
the deliverable. During delegated creation, make one intentional proposed decision and state its
rationale; do not fall back to a prettier factory default.

## Principles

1. Decide before decorating. If the choice cannot be explained, do not make it.
2. One chrome accent and one voice. Extra hues and extra typefaces need a job.
3. Hierarchy comes from scale, weight, and space — not colored words, font
   swaps, or a hat on every heading.
4. Subtract first. The first move toward a decided surface is deletion.
5. Specific beats punchy. Real nouns, numbers, and consequences beat triad
   copy.
6. Decoration is a signal. Icons, badges, callouts, and stat rows stay only
   when they carry information.

## Keep

- Declared brand or family tokens, including a purple identity or glass that
  the source actually uses.
- One justified accent, including a chosen report palette.
- Semantic color that marks a real state, overlay, or evidence label.
- A kicker, badge, emoji, or number that adds a dimension the heading does not
  already say.
- System or repo type chosen on purpose, including landing back on Inter after
  comparison.

## Refuse when no source chose them

These are the current factory costume, not a complete inventory:

- indigo→violet or rainbow fills used as “premium”
- gradient-clipped headlines
- restating kickers (`FEATURES` over features, mode name over the title)
- decorative emoji, badge pills, and left-border callouts on ordinary lists
- invented `10k+` / `99.9%` / `24/7` rows
- Inter / Space Grotesk / Geist as the uncompared default pairing
- glass + max-radius + fog shadow as atmosphere
- equal-weight ALL-CAPS card grids and cards nested in cards
- “not just X — it's Y”, triad slogans, and highlight-every-keyword copy

A sourced instance of any item above is not this failure.

## Design

Owners: `workflow-ui-design` for delegated visual creation and `design-frontend` for production
implementation, with `design-tokens`, `design-ui-decomposer`, and
`design-visual-regression` as evidence/support owners.

- Extract the source/family/repo look before adding chrome.
- When visual creation is explicitly delegated, turn accepted requirements and content hierarchy
  into one coherent proposed direction; record why its typography, color, composition, density,
  imagery, and component language fit the target.
- If no look is decided, reuse the repo theme or a neutral system stack. Do
  not mint a landing-page kit.
- Token gaps stay gaps. Do not fill missing color/type/radius with framework
  ramps.
- Decomposition must not promote a common template into observed intent.
- Visual extras that are not in the source are fidelity misses, not polish.

Dashboard and section-web profiles still follow their surface rules: do not
invent metrics, and do not turn an app into a marketing page.

## Report Canvas

Owners: every `report-*` skill only when HTML is selected through
`report_delivery_contract.md` and `report_canvas_contract.md`.

- Oblivion / Hagoromo is the chosen report identity. Keep that palette.
- Spend color on status, evidence, selection, and spatial overlays — not on
  wallpaper, glowing cards, or a second accent in chrome.
- Title the outcome in a few words; put the sentence in the summary.
- Set `eyebrow` only when it adds a dimension (named target, snapshot, date).
  Never default it to the product name or the mode.
- Findings carry severity in words. Do not invent a stat row or icon tile to
  fill the first viewport.
- Keep copy specific. Do not write release-note theater.
- Do not spend the report turn restyling Canvas. Author the JSON model. If
  the claim must be seen in 3D or as a math/graphics surface, use `spatial`
  and supply geometry; cards are not a substitute.

The renderer must not reintroduce factory chrome: no Inter webfont, no
decorative page grid, no restating default kicker, no display-size crushed
tracking, no pill + fog-shadow chrome, no left-bar finding costume.

## Validation

Positive: a page or report with no visual source stays repo-neutral or
paper/ink, and every remaining accent can be pointed at a source.

Negative: a declared purple brand, glass card, or Inter-after-comparison is
left in place.

A passing scan, a green build, or a styled first viewport is not proof of a
decision.
