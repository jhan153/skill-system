#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import replace
from pathlib import Path

from ingest_analysis_reports import discover_reports, expand_inputs, ingest, render_markdown
from phase_plan_schema import (
    ARCHETYPES,
    DEFAULT_ARTIFACT_CAP,
    DERIVED_VIEW_SPECS,
    MODIFIERS,
    SPEC_DOC_TYPES,
    GroupSpec,
    canonical_archetype,
    modifier_deltas_for,
    release_blocking_specs_for,
    required_specs_for,
    slugify_title,
)


SCRIPT_DIR = Path(__file__).resolve().parent
REF_DIR = SCRIPT_DIR.parent / "references"

def load_template(name: str, spec_suffix: str | None = None) -> str:
    path = REF_DIR / name
    if not path.exists():
        if spec_suffix:
            raise SystemExit(f"missing template {name} for spec {spec_suffix}")
        raise SystemExit(f"missing template {name}")
    return path.read_text(encoding="utf-8")


def render(template: str, replacements: dict[str, str]) -> str:
    out = template
    for key, value in replacements.items():
        out = out.replace(f"{{{{{key}}}}}", value)
    out = out.replace("<Slug>", replacements.get("SLUG", "slug"))
    return ensure_validation_metadata(out)


def ensure_validation_metadata(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    lines = text.splitlines()
    if "---" not in lines[1:]:
        return text
    existing = {line.split(":", 1)[0].strip() for line in lines if ":" in line}
    insert_after = next((i for i, line in enumerate(lines) if line.startswith("last_validated:")), None)
    if insert_after is None:
        return text
    additions = []
    defaults = {
        "last_validated_mode": "none",
        "strict_validated_at": "Unverified",
        "strict_handoff_validated_at": "Unverified",
        "release_ready": "false",
    }
    for key, value in defaults.items():
        if key not in existing:
            additions.append(f"{key}: {value}")
    if additions:
        lines[insert_after + 1 : insert_after + 1] = additions
    return "\n".join(lines) + "\n"


def unique_phase_names(groups: list[GroupSpec]) -> list[str]:
    seen = OrderedDict()
    for g in groups:
        seen[g.phase] = True
    return list(seen.keys())


def build_group_specs(archetype: str, phase_names: list[str] | None, phase_count: int | None) -> list[GroupSpec]:
    base = ARCHETYPES[canonical_archetype(archetype)].groups
    default_phases = unique_phase_names(base)

    if phase_names:
        custom = [x.strip() for x in phase_names if x.strip()]
        if len(custom) == len(default_phases):
            remap = {old: new for old, new in zip(default_phases, custom)}
            return [replace(g, phase=remap[g.phase]) for g in base]
        raise SystemExit(
            "--phase-names must provide the same number of phases as the selected archetype. "
            "Use an explicit group manifest in a future workflow instead of placeholder groups."
        )

    if phase_count is not None and phase_count > 0:
        if phase_count == len(default_phases):
            remap = {old: f"Phase{i+1}" for i, old in enumerate(default_phases)}
            return [replace(g, phase=remap[g.phase]) for g in base]
        raise SystemExit(
            "--phases must match the selected archetype phase count. "
            "Placeholder groups are not generated because they pass structure checks while losing planning meaning."
        )

    return base


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def yaml_list(items: list[str]) -> str:
    if not items:
        return "  []"
    return "\n".join(f"  - {item}" for item in items)


def inline_list(items: list[str]) -> str:
    return ", ".join(items) if items else "none"


def doc_title_from_suffix(suffix: str) -> str:
    return suffix.replace("-", " ").title()


def spec_path(slug: str, suffix: str) -> str:
    return f"docs/spec/{slug}-{suffix}.md"


def render_read_order(slug: str, required_specs: list[str], start_index: int = 2) -> str:
    lines = []
    for offset, suffix in enumerate(required_specs, start=start_index):
        lines.append(f"{offset}. `{spec_path(slug, suffix)}`")
    lines.append(f"{start_index + len(required_specs)}. active phase/group doc")
    lines.append(f"{start_index + len(required_specs) + 1}. package README")
    return "\n".join(lines)


def render_validation_commands(
    package_name: str,
    slug: str,
    dated_plan: Path,
    archetype: str,
    modifiers: list[str],
) -> str:
    modifiers_arg = f' --modifiers "{",".join(modifiers)}"' if modifiers else ""
    base = (
        "python3 scripts/validate_phase_plan_package.py "
        f"--root <repo-root> --package {package_name} --slug {slug} "
        f"--dated-plan {dated_plan.name} --archetype {archetype}{modifiers_arg}"
    )
    return "\n".join(
        [
            base,
            f"{base} --strict --strict-handoff",
            f"{base} --strict --strict-handoff --quality-lint",
            f"{base} --strict --strict-handoff --write-validation-stamp",
        ]
    )


def render_domain_context(
    root: Path,
    package: Path,
    package_name: str,
    paths: list[Path],
) -> tuple[str, str, object | None]:
    if not paths:
        return "", "", None
    result = ingest(paths)
    out = package / "domain-ingest-summary.md"
    out.write_text(render_markdown(result, root), encoding="utf-8")
    rel = f"docs/plan/{package_name}/domain-ingest-summary.md"
    derived_line = f'  - "{rel}"'
    return rel, derived_line, result


def resolve_domain_inputs(root: Path, reports: list[str], auto_ingest: bool, max_files: int) -> list[Path]:
    paths = expand_inputs(reports, root, max_files)
    if auto_ingest:
        paths.extend(discover_reports(root, max_files))
    return sorted(set(paths), key=lambda p: str(p))[:max_files]


def bound_domain_inputs(root: Path, summary: Path) -> list[Path]:
    """Restore the exact source files recorded by a canonical-stage ingest summary."""
    lines = summary.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("derived_from:") + 1
    except ValueError as exc:
        raise SystemExit(f"existing ingest summary has no derived_from binding: {summary}") from exc
    raw_sources: list[str] = []
    for line in lines[start:]:
        if line == "---":
            break
        if not line.startswith("  "):
            break
        item = line.strip()
        if item == "[]":
            continue
        if item.startswith("- "):
            raw_sources.append(item[2:].strip().strip('"').strip("'"))
    if not raw_sources:
        raise SystemExit(f"existing ingest summary has no bound source files: {summary}")
    sources: list[Path] = []
    missing: list[Path] = []
    for raw in raw_sources:
        source = Path(raw).expanduser()
        if not source.is_absolute():
            source = root / source
        source = source.resolve()
        if not source.is_file():
            missing.append(source)
        else:
            sources.append(source)
    if missing:
        raise SystemExit(
            "existing ingest summary references missing source files: "
            + ", ".join(str(path) for path in missing)
        )
    return sorted(set(sources), key=lambda path: str(path))


def pick_domain_buckets(title: str) -> list[str]:
    lower = title.lower()
    if "functional" in lower or "parity" in lower:
        return ["capabilities", "domain", "evidence"]
    if "runtime" in lower or "lifecycle" in lower or "stability" in lower:
        return ["integration", "algorithms", "ui_state"]
    if "integration" in lower or "boundary" in lower:
        return ["integration", "algorithms", "mesh_ops"]
    if "surface" in lower or "workspace" in lower or "state" in lower:
        return ["ui_state", "domain", "capabilities"]
    if "storage" in lower or "persistence" in lower or "export" in lower:
        return ["capabilities", "evidence", "integration"]
    if "validation" in lower or "release" in lower:
        return ["capabilities", "algorithms", "mesh_ops", "evidence"]
    return ["domain", "capabilities", "integration"]


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def render_domain_snippets(domain_result: object | None, spec: GroupSpec, root: Path, limit: int = 6) -> list[str]:
    if domain_result is None:
        return []
    buckets = getattr(domain_result, "buckets", {})
    snippets: list[str] = []
    for bucket in pick_domain_buckets(spec.title):
        for hit in buckets.get(bucket, []):
            source = relative_to_root(hit.source, root)
            snippets.append(f"`{source}:{hit.line_no}` {hit.text}")
            if len(snippets) >= limit:
                return snippets
    return snippets


def render_group_purpose(spec: GroupSpec, relevant_specs: list[str]) -> str:
    docs = ", ".join(relevant_specs[:4]) if relevant_specs else "canonical contracts"
    return (
        f"Use existing domain evidence to close `{spec.title}` against {docs}. "
        "This group must turn prior reports into implementation-ready contracts instead of leaving scaffold text."
    )


def render_group_current_state(spec: GroupSpec, snippets: list[str], domain_context_path: str | None) -> str:
    if snippets:
        return "\n".join(["Existing analysis inputs already contain these signals:"] + [f"- {item}" for item in snippets])
    if not domain_context_path:
        return (
            "No prior analysis report was admitted for this package. "
            "Inspect the source and evidence named by the canonical plan before implementation."
        )
    return (
        f"Domain ingest source: `{domain_context_path}`. "
        "No strong matching signal was extracted for this group; inspect the source reports before implementation."
    )


def render_group_target_state(spec: GroupSpec, relevant_specs: list[str]) -> str:
    docs = ", ".join(f"`{suffix}`" for suffix in relevant_specs)
    return (
        f"The group leaves {docs} with evidence-backed rows, concrete acceptance criteria, and no generic TODOs. "
        "If evidence is missing, record the gap in the gap registry or canonical dated plan before implementation-open."
    )


def render_before_structure(snippets: list[str], domain_context_path: str | None) -> str:
    if snippets:
        return "\n".join(snippets[:3])
    if not domain_context_path:
        return "No admitted prior report; inspect current source evidence before defining the target structure."
    return f"Existing reports are summarized in {domain_context_path}; inspect them before coding."


def filter_relevant_specs(spec: GroupSpec, required_specs: list[str]) -> list[str]:
    if not spec.relevant_specs:
        return required_specs[: min(len(required_specs), 6)]
    relevant = [suffix for suffix in spec.relevant_specs if suffix in required_specs]
    if "release-gate" in required_specs and "release-gate" not in relevant:
        relevant.append("release-gate")
    return relevant or required_specs[: min(len(required_specs), 6)]


def render_dependency_graph(group_specs: list[GroupSpec]) -> str:
    lines = ["flowchart LR"]
    group_ids = {idx: f"group-{idx}" for idx, _ in enumerate(group_specs, start=1)}
    labels = {f"group-{idx}": spec.title for idx, spec in enumerate(group_specs, start=1)}
    for group_id, label in labels.items():
        lines.append(f'  {group_id}["{group_id}: {label}"]')
    for idx, spec in enumerate(group_specs, start=1):
        this_id = group_ids[idx]
        for dep in spec.depends_on:
            lines.append(f"  {dep} --> {this_id}")
    if len(lines) == 1:
        lines.append('  group-1["group-1"]')
    return "\n".join(lines)


def render_target_module_structure(archetype: str) -> str:
    if archetype == "application-product":
        return "\n".join(
            [
                "flowchart LR",
                '  App["Target App / Module"] --> Surface["Window or Main Surface"]',
                '  Surface --> State["State Owner"]',
                '  State --> Domain["Domain Services"]',
                '  Domain --> Runtime["Runtime / IO / Rendering Adapters"]',
                '  Runtime --> Core["Reusable Core / Platform Subsystems"]',
            ]
        )
    if archetype in {"architecture-refactor", "modularization", "migration-modernization"}:
        return "\n".join(
            [
                "flowchart LR",
                '  Legacy["Current Structure"] --> Boundary["Target Boundaries"]',
                '  Boundary --> Modules["Modules / Layers"]',
                '  Modules --> Validation["Parity and Release Gates"]',
            ]
        )
    return "\n".join(["flowchart LR", '  Plan["Plan Package"] --> Contracts["Canonical Contracts"]'])


def render_checklist(slug: str, required_specs: list[str]) -> str:
    return "\n".join(f"- [ ] `{spec_path(slug, suffix)}` read" for suffix in required_specs)


def render_derived_from_specs(slug: str, required_specs: list[str]) -> str:
    return "\n".join(f'  - "{spec_path(slug, suffix)}"' for suffix in required_specs)


def render_canonical_docs_table(slug: str, required_specs: list[str], canonical_plan_path: str) -> str:
    rows = ["| Concern | Canonical Document |", "| --- | --- |"]
    for suffix in required_specs:
        rows.append(f"| {doc_title_from_suffix(suffix)} | `{spec_path(slug, suffix)}` |")
    rows.append(f"| Current execution status / approval / TODO | `{canonical_plan_path}` |")
    return "\n".join(rows)


def render_gate_input_rows(required_specs: list[str], release_blocking_specs: list[str]) -> str:
    release_blocking = set(release_blocking_specs)
    rows = []
    for index, suffix in enumerate((s for s in required_specs if s != "release-gate"), start=1):
        required = "true" if suffix in release_blocking else "false"
        rule = "must-pass release-blocking contract" if suffix in release_blocking else "contract validation input"
        rows.append(f"| GI-{index:03d} | {suffix} | {required} | {rule} | owner |")
    return "\n".join(rows)


def render_upstream_gate_rows(slug: str, required_specs: list[str], release_blocking_specs: list[str]) -> str:
    required = set(required_specs)
    upstream = [suffix for suffix in release_blocking_specs if suffix in required and suffix != "release-gate"]
    if not upstream:
        upstream = [next((suffix for suffix in required_specs if suffix != "release-gate"), "agent-handoff-index")]
    rows = []
    for suffix in upstream:
        condition = "release-blocking contract passes" if suffix in release_blocking_specs else "required contract validates"
        rows.append(f"| {suffix} | {spec_path(slug, suffix)} | {condition} | true |")
    return "\n".join(rows)


def group_relative_path(index: int, spec: GroupSpec) -> str:
    filename = f"Group{index}-{slugify_title(spec.title).replace('-', ' ').title().replace(' ', '-')}.md"
    return f"{spec.phase}/{filename}"


def projected_artifact_paths(
    root: Path,
    package_name: str,
    slug: str,
    dated_plan: Path,
    required_specs: list[str],
    group_specs: list[GroupSpec],
    include_ingest: bool,
) -> list[str]:
    paths = [relative_to_root(dated_plan, root)]
    paths.extend(spec_path(slug, suffix) for suffix in required_specs)
    if include_ingest:
        paths.append(f"docs/plan/{package_name}/domain-ingest-summary.md")
    paths.extend(
        f"docs/plan/{package_name}/{group_relative_path(index, spec)}"
        for index, spec in enumerate(group_specs, start=1)
    )
    paths.append(f"docs/plan/{package_name}/README.md")
    return paths


def normalize_cap_reason(raw: str) -> str:
    return " ".join(raw.split()).replace("`", "'")


def validate_artifact_budget(cap: int, reason: str, paths: list[str]) -> None:
    if cap < 1:
        raise SystemExit("artifact cap must be a positive integer")
    if cap > DEFAULT_ARTIFACT_CAP and not reason:
        raise SystemExit(
            f"artifact cap override above default {DEFAULT_ARTIFACT_CAP} requires a nonempty --artifact-cap-reason"
        )
    if len(paths) > cap:
        rendered = "\n".join(f"- {path}" for path in paths)
        raise SystemExit(
            f"projected artifact count {len(paths)} exceeds cap {cap}; "
            "select a narrower archetype/modifier set or provide an explicit higher cap with a nonempty reason\n"
            f"projected artifacts:\n{rendered}"
        )


def render_projected_artifacts(paths: list[str]) -> str:
    return "\n".join(f"  - `{path}`" for path in paths)


def render_modifier_admission_rows(archetype: str, modifiers: list[str]) -> tuple[str, list[str]]:
    if not modifiers:
        return "| none | not-selected | none | none |", []
    rows: list[str] = []
    absorbed: list[str] = []
    for modifier in modifiers:
        artifact_delta, release_delta = modifier_deltas_for(archetype, modifier)
        status = "admitted"
        if not artifact_delta and not release_delta:
            status = "absorbed-by-archetype"
            absorbed.append(modifier)
        artifact_text = ", ".join(artifact_delta) if artifact_delta else "none"
        release_text = ", ".join(release_delta) if release_delta else "none"
        rows.append(f"| `{modifier}` | `{status}` | {artifact_text} | {release_text} |")
    return "\n".join(rows), absorbed


def validate_existing_budget_record(
    dated_plan: Path,
    cap: int,
    reason: str,
    archetype: str,
    modifiers: list[str],
    projected_paths: list[str],
) -> None:
    if not dated_plan.exists():
        raise SystemExit(f"--derived-only requires existing canonical plan: {dated_plan}")
    text = dated_plan.read_text(encoding="utf-8")
    reason_record = reason or "none"
    expected = [
        f"default_artifact_cap: `{DEFAULT_ARTIFACT_CAP}`",
        f"effective_artifact_cap: `{cap}`",
        f"projected_artifact_count: `{len(projected_paths)}`",
        f"artifact_cap_override_reason: `{reason_record}`",
        f"- archetype: `{archetype}`",
        f"- modifiers: `{', '.join(modifiers) if modifiers else 'none'}`",
    ]
    missing = [line for line in expected if line not in text]
    if missing:
        raise SystemExit(
            "--derived-only budget arguments do not match the canonical plan record: " + "; ".join(missing)
        )
    _, budget_marker, budget_tail = text.partition("### Artifact Budget")
    budget_body, modifier_marker, _ = budget_tail.partition("### Modifier Admission")
    if not budget_marker or not modifier_marker:
        raise SystemExit("--derived-only requires canonical Artifact Budget and Modifier Admission sections")
    recorded_paths: list[str] = []
    in_projected_paths = False
    for line in budget_body.splitlines():
        if line == "- projected_artifacts:":
            in_projected_paths = True
            continue
        if in_projected_paths and line.startswith("  - `") and line.endswith("`"):
            recorded_paths.append(line[len("  - `") : -1])
    if recorded_paths != projected_paths:
        raise SystemExit(
            "--derived-only projected artifact manifest does not match the canonical plan record: "
            f"recorded={recorded_paths!r}; requested={projected_paths!r}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a phase subplan package")
    parser.add_argument("--root", required=True, help="Repo root")
    parser.add_argument("--package", required=True, help="Plan package directory name")
    parser.add_argument("--slug", required=True, help="Spec doc slug prefix")
    parser.add_argument("--dated-plan", required=True, help="Relative canonical dated plan path, e.g. docs/plan/2026-04-24-foo.md")
    parser.add_argument("--archetype", default="application-product", choices=sorted(set(ARCHETYPES.keys()) | {"ui-product", "algorithm-rewrite", "migration-only"}))
    parser.add_argument("--modifiers", default="", help="Optional comma-separated modifiers")
    parser.add_argument("--phases", type=int, default=None, help="Optional number of phases")
    parser.add_argument("--phase-names", default="", help="Optional comma-separated custom phase names")
    parser.add_argument("--auto-ingest", action="store_true", help="Auto-discover existing analysis reports under docs/ and create a domain ingest summary")
    parser.add_argument("--ingest-report", action="append", default=[], help="Report file or directory to ingest; may be repeated")
    parser.add_argument("--ingest-max-files", type=int, default=40, help="Maximum report files to ingest")
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument("--canonical-only", action="store_true", help="Materialize only the canonical plan, canonical specs, and admitted ingest evidence")
    stage.add_argument("--derived-only", action="store_true", help="Materialize derived README, phase/group docs, and handoff view from existing canonical artifacts")
    parser.add_argument("--artifact-cap", type=int, default=DEFAULT_ARTIFACT_CAP, help=f"Maximum final manifest artifacts (default: {DEFAULT_ARTIFACT_CAP})")
    parser.add_argument("--artifact-cap-reason", default="", help="Required nonempty reason when overriding the default artifact cap upward")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    package = root / "docs" / "plan" / args.package
    spec_dir = root / "docs" / "spec"
    dated_plan = root / args.dated_plan

    modifiers = [x.strip() for x in args.modifiers.split(",") if x.strip()]
    unknown_modifiers = [m for m in modifiers if m not in MODIFIERS]
    if unknown_modifiers:
        raise SystemExit(f"unknown modifiers: {', '.join(unknown_modifiers)}")

    canonical = canonical_archetype(args.archetype)
    required_specs = required_specs_for(canonical, modifiers)
    release_blocking_specs = release_blocking_specs_for(canonical, modifiers)
    group_specs = build_group_specs(
        args.archetype,
        [x.strip() for x in args.phase_names.split(",") if x.strip()] if args.phase_names else None,
        args.phases,
    )

    write_canonical = not args.derived_only
    write_derived = not args.canonical_only
    ingest_path = package / "domain-ingest-summary.md"
    domain_result = None
    if args.derived_only:
        if not ingest_path.exists():
            domain_inputs = []
        else:
            domain_inputs = bound_domain_inputs(root, ingest_path)
            explicitly_requested = [
                path.resolve()
                for path in resolve_domain_inputs(root, args.ingest_report, False, args.ingest_max_files)
            ]
            unbound = sorted(set(explicitly_requested) - set(domain_inputs), key=lambda path: str(path))
            if unbound:
                raise SystemExit(
                    "--derived-only ingest inputs are not bound by the canonical-stage summary: "
                    + ", ".join(str(path) for path in unbound)
                )
            domain_result = ingest(domain_inputs)
        if (args.auto_ingest or args.ingest_report) and not domain_inputs:
            raise SystemExit(
                "--derived-only cannot introduce a new ingest summary; run --canonical-only with the ingest inputs first"
            )
    else:
        domain_inputs = resolve_domain_inputs(root, args.ingest_report, args.auto_ingest, args.ingest_max_files)
    include_ingest = bool(domain_inputs)
    projected_paths = projected_artifact_paths(
        root,
        args.package,
        args.slug,
        dated_plan,
        required_specs,
        group_specs,
        include_ingest,
    )
    cap_reason = normalize_cap_reason(args.artifact_cap_reason)
    validate_artifact_budget(args.artifact_cap, cap_reason, projected_paths)

    modifier_admission_rows, absorbed_modifiers = render_modifier_admission_rows(canonical, modifiers)
    print(f"ARTIFACT_BUDGET_OK projected={len(projected_paths)} cap={args.artifact_cap}")
    for modifier in absorbed_modifiers:
        print(f"MODIFIER_ABSORBED_BY_ARCHETYPE {modifier}")

    if args.derived_only:
        validate_existing_budget_record(
            dated_plan,
            args.artifact_cap,
            cap_reason,
            canonical,
            modifiers,
            projected_paths,
        )
        missing_canonical = [
            spec_dir / f"{args.slug}-{suffix}.md"
            for suffix in required_specs
            if suffix not in DERIVED_VIEW_SPECS and not (spec_dir / f"{args.slug}-{suffix}.md").exists()
        ]
        if missing_canonical:
            raise SystemExit(
                "--derived-only requires existing canonical specs: "
                + ", ".join(str(path) for path in missing_canonical)
            )

    derived_from_specs = render_derived_from_specs(args.slug, required_specs)
    read_order = render_read_order(args.slug, required_specs)
    checklist = render_checklist(args.slug, required_specs)
    canonical_docs_table = render_canonical_docs_table(args.slug, required_specs, args.dated_plan)
    validation_commands = render_validation_commands(args.package, args.slug, dated_plan, canonical, modifiers)
    domain_context_path = f"docs/plan/{args.package}/domain-ingest-summary.md" if include_ingest else ""
    domain_context_derived = f'  - "{domain_context_path}"' if include_ingest else ""

    # The budget check above is deliberately the last gate before any mkdir/write.
    if write_canonical:
        spec_dir.mkdir(parents=True, exist_ok=True)
        dated_plan.parent.mkdir(parents=True, exist_ok=True)
        if domain_inputs:
            package.mkdir(parents=True, exist_ok=True)
            domain_context_path, domain_context_derived, domain_result = render_domain_context(
                root,
                package,
                args.package,
                domain_inputs,
            )
    if write_derived:
        package.mkdir(parents=True, exist_ok=True)

    # Create phase directories only when materializing derived views.
    rendered_group_specs = group_specs if write_derived else []
    phase_order = unique_phase_names(rendered_group_specs)
    phase_orders = {phase: idx for idx, phase in enumerate(phase_order, start=1)}
    for phase in phase_order:
        (package / phase).mkdir(exist_ok=True)

    # Group docs
    group_paths: list[Path] = []
    group_entries: list[str] = []
    phase_index_lines: list[str] = []
    grouped_for_index: OrderedDict[str, list[str]] = OrderedDict((phase, []) for phase in phase_order)
    for idx, spec in enumerate(rendered_group_specs, start=1):
        rel = group_relative_path(idx, spec)
        path = package / rel
        group_paths.append(path)
        grouped_for_index[spec.phase].append(rel)
        relevant_specs = filter_relevant_specs(spec, required_specs)
        primary_contract = f"docs/spec/{args.slug}-{relevant_specs[0]}.md" if relevant_specs else "docs/spec/<contract>.md"
        domain_snippets = render_domain_snippets(domain_result, spec, root)

        group_text = render(
            load_template("group-template.md"),
            {
                "PHASE_NAME": spec.phase,
                "GROUP_ID": f"group-{idx}",
                "GROUP_TITLE": f"Group {idx}: {spec.title}",
                "PACKAGE_DIR_NAME": args.package,
                "HARD_PREDECESSOR": "true" if spec.hard_predecessor else "false",
                "PHASE_ORDER": str(spec.phase_order or phase_orders[spec.phase]),
                "CANONICAL_PLAN_PATH": args.dated_plan,
                "DEPENDS_ON": yaml_list(spec.depends_on),
                "SOFT_DEPENDS_ON": yaml_list(spec.soft_depends_on),
                "BLOCKING_INTERFACES": yaml_list(spec.blocking_interfaces),
                "RELEVANT_SPECS_FM": yaml_list(relevant_specs),
                "DEPENDS_ON_INLINE": inline_list(spec.depends_on),
                "SOFT_DEPENDS_ON_INLINE": inline_list(spec.soft_depends_on),
                "BLOCKING_INTERFACES_INLINE": inline_list(spec.blocking_interfaces),
                "REFERENCED_CANONICAL_DOCS": markdown_list(
                    [f"`docs/spec/{args.slug}-{suffix}.md`" for suffix in relevant_specs]
                ),
                "GROUP_PURPOSE": render_group_purpose(spec, relevant_specs),
                "GROUP_CURRENT_STATE": render_group_current_state(spec, domain_snippets, domain_context_path),
                "GROUP_TARGET_STATE": render_group_target_state(spec, relevant_specs),
                "TARGET_COMPONENTS": markdown_list(spec.target_components or ["Target component list to be confirmed"]),
                "RESPONSIBILITIES": markdown_list(spec.responsibilities or ["Group responsibilities to be confirmed"]),
                "BEFORE_STRUCTURE": render_before_structure(domain_snippets, domain_context_path),
                "AFTER_STRUCTURE": " -> ".join(spec.target_components) if spec.target_components else "Target structure to be defined",
                "CRITICAL_GAP": spec.critical_gap or "Critical gap to be identified.",
                "FIRST_STEP": spec.first_step or "Inspect the relevant canonical contracts and current code assets.",
                "PRIMARY_CONTRACT": primary_contract,
                "GROUP_EVIDENCE_PATH": domain_context_path or args.dated_plan,
                "GROUP_VALIDATION_COMMAND": validation_commands.splitlines()[2],
                "PROHIBITED_SHORTCUTS": markdown_list(spec.prohibited_shortcuts or ["Do not bypass canonical contracts to make the group appear complete."]),
            },
        )
        path.write_text(group_text, encoding="utf-8")
        group_entries.append(f"`{rel}`")

    for phase, rels in grouped_for_index.items():
        bullets = "\n".join(f"  - `{rel}`" for rel in rels)
        phase_index_lines.append(f"- `{phase}`\n{bullets}")

    # Spec docs
    spec_entries = [f"`{spec_path(args.slug, suffix)}`" for suffix in required_specs]
    for suffix in required_specs:
        is_derived_view = suffix in DERIVED_VIEW_SPECS
        if is_derived_view and not write_derived:
            continue
        if not is_derived_view and not write_canonical:
            continue
        template_name = {
            "capability-map": "capability-map-template.md",
            "algorithm-inventory": "algorithm-inventory-template.md",
            "ui-state-contract": "ui-state-contract-template.md",
            "integration-contract": "integration-contract-template.md",
            "theme-token-contract": "theme-token-template.md",
            "release-gate": "release-gate-template.md",
            "agent-handoff-index": "handoff-index-template.md",
            "api-contract": "api-contract-template.md",
            "app-runtime-contract": "app-runtime-contract-template.md",
            "architecture-contract": "architecture-contract-template.md",
            "benchmark-contract": "benchmark-contract-template.md",
            "behavior-parity-contract": "behavior-parity-contract-template.md",
            "characterization-test-plan": "characterization-test-plan-template.md",
            "compatibility-matrix": "compatibility-matrix-template.md",
            "data-contract": "data-contract-template.md",
            "dataset-contract": "dataset-contract-template.md",
            "dependency-graph": "dependency-graph-template.md",
            "dependency-rule-contract": "dependency-rule-contract-template.md",
            "deployment-contract": "deployment-contract-template.md",
            "build-contract": "build-contract-template.md",
            "environment-contract": "environment-contract-template.md",
            "evaluation-gate": "evaluation-gate-template.md",
            "experiment-contract": "experiment-contract-template.md",
            "failure-matrix": "failure-matrix-template.md",
            "failure-mode-contract": "failure-mode-contract-template.md",
            "firmware-behavior-contract": "firmware-behavior-contract-template.md",
            "hardware-interface-contract": "hardware-interface-contract-template.md",
            "input-output-contract": "input-output-contract-template.md",
            "mesh-ops-contract": "mesh-ops-contract-template.md",
            "gap-registry": "gap-registry-template.md",
            "local-storage-contract": "local-storage-contract-template.md",
            "migration-map": "migration-map-template.md",
            "module-boundary-map": "module-boundary-map-template.md",
            "observability-contract": "observability-contract-template.md",
            "old-new-mapping": "old-new-mapping-template.md",
            "parity-contract": "parity-contract-template.md",
            "performance-budget": "performance-budget-template.md",
            "pin-map": "pin-map-template.md",
            "platform-lifecycle-contract": "platform-lifecycle-contract-template.md",
            "protocol-contract": "protocol-contract-template.md",
            "public-api-contract": "public-api-contract-template.md",
            "regression-matrix": "regression-matrix-template.md",
            "refactor-target-inventory": "refactor-target-inventory-template.md",
            "rendering-pipeline-contract": "rendering-pipeline-contract-template.md",
            "resource-lifecycle-contract": "resource-lifecycle-contract-template.md",
            "rollback-plan": "rollback-plan-template.md",
            "rollback-trigger": "rollback-trigger-template.md",
            "route-contract": "route-contract-template.md",
            "runtime-loop-contract": "runtime-loop-contract-template.md",
            "scene-graph-contract": "scene-graph-contract-template.md",
            "security-contract": "security-contract-template.md",
            "source-of-truth-policy": "source-of-truth-policy-template.md",
            "test-inventory": "test-inventory-template.md",
            "threading-contract": "threading-contract-template.md",
            "tolerance-contract": "tolerance-contract-template.md",
            "training-pipeline-contract": "training-pipeline-contract-template.md",
            "validation-dataset": "validation-dataset-template.md",
            "versioning-policy": "versioning-policy-template.md",
            "visual-regression-gate": "visual-regression-gate-template.md",
        }.get(suffix, "generic-contract-template.md")
        path = spec_dir / f"{args.slug}-{suffix}.md"
        text = render(
            load_template(template_name, suffix),
            {
                "SLUG": args.slug,
                "CANONICAL_PLAN_PATH": args.dated_plan,
                "DOC_TYPE": SPEC_DOC_TYPES[suffix],
                "DOC_KIND": suffix,
                "DOC_TITLE": doc_title_from_suffix(suffix),
                "DERIVED_FROM_SPECS": derived_from_specs,
                "READ_ORDER": read_order,
                "CHECKLIST": checklist,
                "GATE_INPUT_ROWS": render_gate_input_rows(required_specs, release_blocking_specs),
                "UPSTREAM_GATE_ROWS": render_upstream_gate_rows(args.slug, required_specs, release_blocking_specs),
            },
        )
        path.write_text(text, encoding="utf-8")

    # README
    if write_derived:
        active_group = "group-1"
        active_spec = group_specs[0] if group_specs else GroupSpec("Phase1", "Active Group")
        active_relevant = filter_relevant_specs(active_spec, required_specs)
        if domain_context_path:
            domain_context_purpose = f"- Domain ingest summary: `{domain_context_path}`"
            domain_context_quickstart = (
                f"5. If domain details look thin, open `{domain_context_path}` before editing contracts."
            )
            domain_context_section = "\n".join(
                [
                    f"- Derived ingest summary: `{domain_context_path}`",
                    "- This file is derived evidence, not canonical truth.",
                    "- Use it to fill Purpose, Current State, Target State, Acceptance Criteria, and TODOs with domain-specific content.",
                ]
            )
        else:
            domain_context_purpose = "- No domain ingest summary was generated because no report input was admitted."
            domain_context_quickstart = (
                "5. If domain details look thin, inspect the source/evidence named by the canonical plan."
            )
            domain_context_section = (
                "- No derived ingest summary is part of this manifest; add one only when an actual report input is admitted."
            )
        readme_text = render(
            load_template("package-readme-template.md"),
            {
                "PACKAGE_TITLE": args.package,
                "PACKAGE_DIR_NAME": args.package,
                "CANONICAL_PLAN_PATH": args.dated_plan,
                "ARCHETYPE": canonical,
                "MODIFIERS": ", ".join(modifiers) if modifiers else "none",
                "VALIDATION_MODIFIERS_ARG": f' --modifiers "{",".join(modifiers)}"' if modifiers else "",
                "SLUG": args.slug,
                "PHASE_INDEX": "\n".join(phase_index_lines),
                "GROUP_INDEX": markdown_list(group_entries),
                "DEPENDENCY_GRAPH": render_dependency_graph(group_specs),
                "SPEC_INDEX": markdown_list(spec_entries),
                "DATED_PLAN_BASENAME": dated_plan.name,
                "DERIVED_FROM_SPECS": derived_from_specs,
                "DOMAIN_INGEST_DERIVED_FROM": domain_context_derived,
                "CANONICAL_DOCS_TABLE": canonical_docs_table,
                "READ_ORDER": read_order,
                "VALIDATION_COMMANDS": validation_commands,
                "DOMAIN_CONTEXT_PURPOSE": domain_context_purpose,
                "DOMAIN_CONTEXT_QUICKSTART": domain_context_quickstart,
                "DOMAIN_CONTEXT_SECTION": domain_context_section,
                "ACTIVE_GROUP": active_group,
                "ACTIVE_GOAL": active_spec.title,
                "ACTIVE_MUST_READ": ", ".join(spec_path(args.slug, suffix) for suffix in active_relevant),
                "ACTIVE_BLOCKING_CONTRACTS": ", ".join(spec_path(args.slug, suffix) for suffix in active_relevant if suffix in release_blocking_specs),
                "ACTIVE_FIRST_FILE": "inspect current code assets referenced by the active group",
                "ACTIVE_FIRST_ARTIFACT": "group-specific evidence artifact named in Acceptance Criteria",
                "ACTIVE_STOP_CONDITION": "stop if a required contract, dependency, or blocking interface is unresolved",
                "TARGET_MODULE_STRUCTURE": render_target_module_structure(canonical),
            },
        )
        (package / "README.md").write_text(readme_text, encoding="utf-8")

    # Canonical dated plan
    if write_canonical:
        dated_plan_text = render(
            load_template("canonical-dated-plan-template.md"),
            {
                "PLAN_TITLE": args.package,
                "PACKAGE_PATH": f"docs/plan/{args.package}",
                "ARCHETYPE": canonical,
                "MODIFIERS": ", ".join(modifiers) if modifiers else "none",
                "VALIDATION_COMMANDS": validation_commands,
                "DOMAIN_CONTEXT_PATH": domain_context_path or "none (no admitted ingest input)",
                "DEFAULT_ARTIFACT_CAP": str(DEFAULT_ARTIFACT_CAP),
                "ARTIFACT_CAP": str(args.artifact_cap),
                "PROJECTED_ARTIFACT_COUNT": str(len(projected_paths)),
                "ARTIFACT_CAP_REASON": cap_reason or "none",
                "PROJECTED_ARTIFACTS": render_projected_artifacts(projected_paths),
                "MODIFIER_ADMISSION_ROWS": modifier_admission_rows,
            },
        )
        dated_plan.write_text(dated_plan_text, encoding="utf-8")

    print(package)
    print(dated_plan)


if __name__ == "__main__":
    main()
