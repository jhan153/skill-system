# Identifier Readability Principle

This principle governs judgment about identifier readability in repository-owned code. It does
not define a mandatory prefix, suffix, abbreviation catalog, or linter grammar.

## Governing Question

> When related identifiers are scanned together at their actual use sites, are their differences
> immediately visible?

## Decision Rule

Evaluate an identifier both for its standalone meaning and for its distinguishability within the
related identifier set. Put distinguishing information early when the higher-priority constraints
below allow it.

When a long common prefix or suffix hides the meaningful difference, first express the shared
category through a type, object, namespace, module, or other existing structural owner. Use an
abbreviation only when structural ownership is inappropriate and the team has already established
the abbreviation's meaning. Do not invent a non-standard abbreviation or mechanically spell every
term out merely to satisfy a naming slogan.

## Precedence

Apply these authorities in order; a lower item never overrides a higher one:

1. language, framework, and public-API conventions;
2. consistent domain vocabulary;
3. type or structural ownership of the shared category;
4. distinguishability within the related identifier set; and
5. an abbreviation already established by the team.

`ERR`, `num`, and similar spellings are examples only. This principle never admits them into a
shared abbreviation list or makes them mandatory.

## Activation And Scope

Apply this principle whenever related identifiers are introduced, renamed, or evaluated together.
Its semantic scope includes repository-owned production, test, tooling, and UI code. Generated or
externally owned names remain governed by their source authority.

Assess the declarations together with at least one representative use site. A name that reads well
alone can still fail when its meaningful difference is hidden among neighboring names.

## Review Contract

- Prefer code review over a linter for the judgment itself. A linter may enforce only an already
  accepted mechanical spelling or abbreviation catalog; it cannot decide contextual
  distinguishability.
- A finding names the exact identifier set and use site whose difference is hard to see. Personal
  taste, length alone, or deviation from an example prefix is not a finding.
- Preserve public API compatibility and established domain meaning. If either conflicts with local
  visual discrimination, keep the higher authority and report the tradeoff.
- Prefer structure over encoded name prefixes when a type, object, namespace, or module already
  owns the shared category.

## Task Cases

- **Positive:** several related identifiers repeat a long category token and differ only near the
  end. Move the shared category into an existing structural owner or otherwise expose the
  discriminating tokens without changing meaning.
- **Negative:** one isolated local identifier is already clear in its use site. Do not rename it or
  introduce a new abbreviation merely to demonstrate compliance.
- **Edge:** a language convention, public API, or established domain term fixes the spelling. Keep
  that spelling even when a locally different ordering would scan faster.
