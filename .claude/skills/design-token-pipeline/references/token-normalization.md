# Token Normalization Reference

Use this reference when a token source exists and the task needs a normalized token inventory or platform mapping.

## Source priority

1. Explicit design token file or design-system source.
2. Repository theme, CSS variables, Tailwind config, or native constants.
3. Figma-exported token table or style guide.
4. Design spec values tied to a named component or frame.
5. Screenshot-derived candidates, marked inferred.

## Categories

- `color`: semantic colors, raw palette, state colors, surface colors, border colors.
- `typography`: font family, size, weight, line-height, letter spacing, text style aliases.
- `spacing`: gaps, padding, margins, layout rhythm, grid gutters.
- `radius`: control, card, modal, avatar, pill, and surface radius.
- `shadow`: elevation, blur, spread, offset, opacity, ambient/key layers.
- `motion`: duration, easing, delay, transition purpose.
- `breakpoint`: viewport names, min/max widths, density modes.
- `z-index`: overlays, popovers, modals, sticky surfaces.

## Naming guidance

- Prefer role names when the source encodes purpose: `color.action.primary`, `space.card.padding`.
- Preserve existing repo naming conventions when mapping into an established system.
- Keep aliases explicit; do not hide raw values behind new names without a source.
- Use mode suffixes only when modes exist in source: `light`, `dark`, `compact`, `highContrast`.

## Platform mapping

- CSS variables: keep `--` names stable and map aliases to source tokens.
- Tailwind: map to `theme.extend` only when the project already uses Tailwind customization.
- JS/TS theme objects: preserve object shape and typing conventions.
- Native/mobile constants: preserve platform naming and density conventions.

## Report discipline

- Confirmed tokens cite a source pointer.
- Inferred tokens include the inference basis.
- Missing values stay missing.
- Conflicts list both values and their source pointers.
