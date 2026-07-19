# Decomposition Rules

## Goal
Decompose planning packages by concern, not by arbitrary document count.

## Rules
- Put canonical contracts in `docs/spec/`
- Put execution decomposition in phase/group docs
- Use the canonical dated plan for status and approval only
- Default to 4 phases, but allow dynamic phase counts
- Use archetypes to suppress unnecessary docs
- Use modifiers to add validation docs without changing the primary archetype
- Keep `application-product` separate from `web-product`
- Keep `architecture-refactor` separate from `large-scale-refactor`

## Smells
- A phase exists only to hold one tiny note
- A group doc redefines canonical scope
- UI/theme docs are generated for a backend-only archetype
- Modifier risks are described in prose but missing from generated spec docs
