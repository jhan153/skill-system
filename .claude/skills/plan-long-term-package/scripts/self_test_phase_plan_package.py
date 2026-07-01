#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import re
from pathlib import Path

from phase_plan_schema import ARCHETYPES, MODIFIERS, UNIVERSAL_REQUIRED_SPECS, required_specs_for


SCRIPT_DIR = Path(__file__).resolve().parent
INIT = SCRIPT_DIR / "init_phase_plan_package.py"
VALIDATE = SCRIPT_DIR / "validate_phase_plan_package.py"
CATALOG = SCRIPT_DIR.parent / "references" / "archetype-catalog.md"


def run(args: list[str], expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True)
    if expect_ok and result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    if not expect_ok and result.returncode == 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write("expected command to fail:\n")
        sys.stderr.write(" ".join(args) + "\n")
        raise SystemExit(1)
    return result


def common_args(root: str, package: str, slug: str, archetype: str, modifiers: str = "") -> list[str]:
    args = [
        "--root",
        root,
        "--package",
        package,
        "--slug",
        slug,
        "--dated-plan",
        f"docs/plan/2026-04-24-{slug}.md",
        "--archetype",
        archetype,
    ]
    if modifiers:
        args.extend(["--modifiers", modifiers])
    return args


def init_and_validate(tmp: str, package: str, slug: str, archetype: str, modifiers: str = "") -> list[str]:
    args = common_args(tmp, package, slug, archetype, modifiers)
    run(["python3", str(INIT), *args])
    run(["python3", str(VALIDATE), *args])
    return args


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        sys.stderr.write(text)
        raise SystemExit(f"missing expected validation message for {label}: {needle}")


def insert_table_row(path: Path, heading: str, row: str) -> None:
    text = path.read_text(encoding="utf-8")
    before, marker, after = text.partition(heading)
    if not marker:
        raise SystemExit(f"missing heading {heading} in {path}")
    lines = after.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| ---"):
            lines.insert(index + 1, row)
            path.write_text(before + marker + "\n".join(lines) + "\n", encoding="utf-8")
            return
    raise SystemExit(f"missing table separator under {heading} in {path}")


def normalize_contract_doc_name(name: str) -> str:
    normalized = name.strip().strip("`").lower()
    aliases = {
        "canonical dated plan": "",
        "handoff index": "agent-handoff-index",
    }
    if normalized in aliases:
        return aliases[normalized]
    return normalized.replace(" ", "-")


def parse_catalog_required_docs() -> dict[str, set[str]]:
    text = CATALOG.read_text(encoding="utf-8")
    _, marker, after = text.partition("## Core Archetypes")
    if not marker:
        raise SystemExit("missing catalog section ## Core Archetypes")
    body = after.split("\n## ", 1)[0]
    parsed: dict[str, set[str]] = {}
    for line in body.splitlines():
        if not line.startswith("| `"):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if len(cols) < 3:
            continue
        archetype = cols[0].strip("`")
        docs = set()
        for raw_doc in cols[2].split(","):
            doc = normalize_contract_doc_name(raw_doc)
            if doc:
                docs.add(doc)
        parsed[archetype] = docs
    return parsed


def seed_release_gate_for_strict(path: Path) -> None:
    insert_table_row(path, "## Datasets", "| fixture-dataset | v1 | local | all | true | self-test | 1 | docs |")
    insert_table_row(
        path,
        "## Numeric Thresholds",
        "| required-docs | 1 | count | >= | self-test | generated | P0 | generated docs exist |",
    )
    insert_table_row(
        path,
        "## Regression Matrix",
        "| scaffold | package validates | validator exits 0 | docs | automated |",
    )
    insert_table_row(path, "## Rollback Triggers", "| validator failure | P0 | stop release |")
    insert_table_row(path, "## Evidence Artifacts", "| validation-log | /tmp/phase-subplan-selftest.log | self-test |")


def seed_generic_contract_for_strict(path: Path) -> None:
    insert_table_row(path, "## Contract Matrix", "| C-001 | required behavior | must hold | validator | draft | /tmp/evidence.log |")
    insert_table_row(path, "## Evidence", "| E-001 | /tmp/evidence.log | self-test | 2026-04-24 |")


def seed_contract_for_strict(spec_dir: Path, slug: str, suffix: str) -> None:
    path = spec_dir / f"{slug}-{suffix}.md"
    if suffix in {"agent-handoff-index", "integration-contract"}:
        return
    if suffix == "release-gate":
        seed_release_gate_for_strict(path)
    elif suffix == "capability-map":
        insert_table_row(
            path,
            "## Capability Matrix",
            f"| CAP-001 | Core capability | docs | required behavior | current | target | P0 | docs/spec/{slug}-release-gate.md | source | planned | decision-001 | 2026-04-24 |",
        )
    elif suffix == "algorithm-inventory":
        text = path.read_text(encoding="utf-8").replace("### <Algorithm Name>", "### Fixture Algorithm")
        path.write_text(text, encoding="utf-8")
        insert_table_row(path, "## Validation Matrix", "| Fixture Algorithm | fixture-dataset | rmse | 0.01 | /tmp/algorithm.json |")
    elif suffix == "api-contract":
        insert_table_row(path, "## Endpoint Matrix", "| EP-001 | GET | /health | api | draft |")
        insert_table_row(path, "## Request Response Contracts", "| EP-001 | none | health schema | backward-compatible |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/api.log | self-test | 2026-04-24 |")
    elif suffix == "app-runtime-contract":
        insert_table_row(path, "## Runtime Scope", "| RT-001 | macOS | single process | app |")
        insert_table_row(path, "## Lifecycle Matrix", "| launch | restore workspace | ready | restart |")
        insert_table_row(path, "## Resource Ownership", "| mesh cache | runtime | session | close document |")
    elif suffix == "architecture-contract":
        insert_table_row(path, "## Architecture Goals", "| ARCH-001 | isolate domain | no UI rewrite | arch | draft |")
        insert_table_row(path, "## Layer Model", "| Domain | business rules | Core | UI | stable |")
        insert_table_row(path, "## State Ownership", "| session | domain | UI | domain | session |")
        insert_table_row(path, "## Dependency Direction", "| UI | Domain | true | DEP-001 | linter |")
    elif suffix == "benchmark-contract":
        insert_table_row(path, "## Benchmark Cases", "| BENCH-001 | fixture | dataset-v1 | python bench.py | 5 | perf | draft |")
        insert_table_row(path, "## Metrics", "| M-001 | latency | <= | 10 | ms | P0 |")
        insert_table_row(path, "## Baseline", "| BASE-001 | fixture-build | local | /tmp/baseline.json | true |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/benchmark.json | self-test | 2026-04-24 |")
    elif suffix == "behavior-parity-contract":
        insert_table_row(path, "## Behavior Matrix", "| BEH-001 | input | old | new | exact | 0 |")
        insert_table_row(path, "## Characterization Tests", "| T-001 | BEH-001 | python test.py | fixture | /tmp/golden.json |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/parity.log | self-test | 2026-04-24 |")
    elif suffix == "compatibility-matrix":
        insert_table_row(path, "## Compatibility Matrix", "| v1 | v2 | true | additive | compat |")
        insert_table_row(path, "## Supported Combinations", "| COMBO-001 | macOS 14 | true | smoke-test |")
        insert_table_row(path, "## Validation", "| compatible | python compat.py | pass | /tmp/compat.json |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/compat.log | self-test | 2026-04-24 |")
    elif suffix == "build-contract":
        insert_table_row(path, "## Build Targets", "| BUILD-001 | app | macOS | release | build |")
        insert_table_row(path, "## Build Commands", "| CMD-001 | BUILD-001 | xcodebuild build | /tmp/app.zip |")
        insert_table_row(path, "## Artifacts", "| ART-001 | /tmp/app.zip | xcodebuild | release |")
        insert_table_row(path, "## Environment Inputs", "| SDK | Xcode | true | xcodebuild -version |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/build.log | self-test | 2026-04-24 |")
    elif suffix == "characterization-test-plan":
        insert_table_row(path, "## Characterization Inventory", "| BEH-001 | current behavior | fixture | source | P0 |")
        insert_table_row(path, "## Test Matrix", "| T-001 | BEH-001 | python test.py | /tmp/golden.json | automated |")
        insert_table_row(path, "## Golden Artifacts", "| G-001 | /tmp/golden.json | fixture | true |")
    elif suffix == "data-contract":
        insert_table_row(path, "## Entity Matrix", "| User | data | sqlite | session |")
        insert_table_row(path, "## Schema Rules", "| users.v1 | table | true | additive |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/data.log | self-test | 2026-04-24 |")
    elif suffix == "dataset-contract":
        insert_table_row(path, "## Dataset Matrix", "| fixture | v1 | local | all | true |")
        insert_table_row(path, "## Data Quality Rules", "| DQ-001 | completeness | >= | 1 | count |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/dataset.json | self-test | 2026-04-24 |")
    elif suffix == "dependency-graph":
        insert_table_row(path, "## Graph Scope", "| GRAPH-001 | Sources | Tests | focus |")
        insert_table_row(path, "## Dependency Matrix", "| A | B | import | true | /tmp/graph.dot |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/graph.dot | self-test | 2026-04-24 |")
    elif suffix == "dependency-rule-contract":
        insert_table_row(path, "## Rule Matrix", "| DEP-001 | UI depends inward | app | linter | no waiver |")
        insert_table_row(path, "## Allowed Dependencies", "| UI | Domain | inward | DEP-001 |")
        insert_table_row(path, "## Forbidden Dependencies", "| Domain | UI | outward | linter |")
        insert_table_row(path, "## Enforcement", "| dependency check | python check_deps.py | pass | arch |")
    elif suffix == "deployment-contract":
        insert_table_row(path, "## Deployment Matrix", "| DEPLOY-001 | prod | /tmp/app.zip | release | draft |")
        insert_table_row(path, "## Release Environments", "| prod | staging | release-owner | smoke-test |")
        insert_table_row(path, "## Rollout Rules", "| ROLL-001 | 10% users | staged | error-rate > 1 |")
        insert_table_row(path, "## Rollback Link", "| DEPLOY-001 | docs/spec/rollback-plan.md | gate fail | release |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/deploy.log | self-test | 2026-04-24 |")
    elif suffix == "environment-contract":
        insert_table_row(path, "## Environment Matrix", "| ENV-001 | ci | macOS | infra | draft |")
        insert_table_row(path, "## Toolchain Versions", "| Xcode | 15.0 | pinned | xcodebuild -version |")
        insert_table_row(path, "## Reproducibility", "| REP-001 | make build | pass | /tmp/repro.log |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/env.log | self-test | 2026-04-24 |")
    elif suffix == "evaluation-gate":
        insert_table_row(path, "## Evaluation Matrix", "| EVAL-001 | fixture | accuracy | evaluator | P0 |")
        insert_table_row(path, "## Numeric Thresholds", "| accuracy | 0.95 | ratio | >= | P0 |")
        insert_table_row(path, "## Required Artifacts", "| report | /tmp/eval.json | evaluator |")
    elif suffix == "experiment-contract":
        insert_table_row(path, "## Experiment Matrix", "| EXP-001 | improve quality | fixture | ml | draft |")
        insert_table_row(path, "## Reproducibility Rules", "| REP-001 | deterministic seed | python run.py | /tmp/exp.json |")
        insert_table_row(path, "## Metrics", "| accuracy | 0.95 | ratio | >= |")
        insert_table_row(path, "## Artifacts", "| ART-001 | /tmp/exp.json | trainer | retain |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/exp.log | self-test | 2026-04-24 |")
    elif suffix == "failure-matrix":
        insert_table_row(path, "## Failure Matrix", "| FAIL-001 | timeout | external api | P0 | adapter |")
        insert_table_row(path, "## Detection Matrix", "| FAIL-001 | timeout metric | 1 | ops |")
        insert_table_row(path, "## Fallback Matrix", "| FAIL-001 | retry | loading state | no loss |")
        insert_table_row(path, "## Escalation Rules", "| FAIL-001 | owner | true | block release |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/failure-matrix.log | self-test | 2026-04-24 |")
    elif suffix == "failure-mode-contract":
        insert_table_row(path, "## Failure Mode Matrix", "| FAIL-001 | invalid input | validation | P0 | owner |")
        insert_table_row(path, "## Detection Rules", "| DET-001 | FAIL-001 | exception | 1 |")
        insert_table_row(path, "## Recovery Rules", "| FAIL-001 | reject input | false | validation message |")
        insert_table_row(path, "## Escalation Rules", "| FAIL-001 | owner | true | block release |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/failure.log | self-test | 2026-04-24 |")
    elif suffix == "firmware-behavior-contract":
        insert_table_row(path, "## Firmware Scope", "| FW-001 | MCU | pointing | firmware |")
        insert_table_row(path, "## Behavior Matrix", "| BEH-001 | movement | report | 1 ms | P0 |")
        insert_table_row(path, "## Timing Requirements", "| TIME-001 | 1 | ms | logic analyzer |")
    elif suffix == "hardware-interface-contract":
        insert_table_row(path, "## Hardware Revisions", "| revA | board | true | /tmp/hw.pdf | baseline |")
        insert_table_row(path, "## Interface Matrix", "| IF-001 | I2C | bidirectional | 3.3V | 1 ms | hardware |")
        insert_table_row(path, "## Electrical Constraints", "| EC-001 | voltage | 3.3 | V | multimeter |")
        insert_table_row(path, "## Validation Fixtures", "| FIX-001 | board | fw | probe.sh | /tmp/hw.log |")
    elif suffix == "input-output-contract":
        insert_table_row(path, "## Input Matrix", "| IN-001 | mesh | true | schema validate | algo |")
        insert_table_row(path, "## Output Matrix", "| OUT-001 | mesh | algorithm | stable | algo |")
        insert_table_row(path, "## Transformation Rules", "| TR-001 | IN-001 | OUT-001 | deterministic | reject |")
        insert_table_row(path, "## Validation Fixtures", "| FIX-001 | /tmp/in.mesh | /tmp/out.mesh | python validate.py |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/io.log | self-test | 2026-04-24 |")
    elif suffix == "local-storage-contract":
        insert_table_row(path, "## Storage Matrix", "| STORE-001 | settings | app support | app | until uninstall |")
        insert_table_row(path, "## Schema And Versioning", "| settings | v1 | additive | migration-v1 |")
        insert_table_row(path, "## Persistence Rules", "| close | flush | restore | last-write-wins |")
        insert_table_row(path, "## Data Safety", "| corruption | checksum | backup | restore-test |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/storage.log | self-test | 2026-04-24 |")
    elif suffix == "migration-map":
        insert_table_row(path, "## Migration Scope", "| MIG-001 | old | new | owner |")
        insert_table_row(path, "## Old To New Mapping", "| old | new | automated |")
        insert_table_row(path, "## Sequence", "| 1 | migrate | none | validate |")
        insert_table_row(path, "## Rollback Hook", "| fail | restore | python rollback.py |")
    elif suffix == "module-boundary-map":
        insert_table_row(path, "## Module Matrix", "| Domain | business rules | API | internals | domain |")
        insert_table_row(path, "## Public Boundaries", "| B-001 | Domain | UI | API | v1 |")
        insert_table_row(path, "## Cross Module Rules", "| R-001 | no outward deps | linter | block |")
    elif suffix == "old-new-mapping":
        insert_table_row(path, "## Mapping Matrix", "| OldA | NewA | one-to-one | migration |")
        insert_table_row(path, "## Behavior Equivalence", "| BEH-001 | old | new | exact |")
        insert_table_row(path, "## Validation", "| mapping | python mapping.py | pass | /tmp/mapping.json |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/mapping.log | self-test | 2026-04-24 |")
    elif suffix == "observability-contract":
        insert_table_row(path, "## Signal Matrix", "| SIG-001 | metric | service | health | ops |")
        insert_table_row(path, "## Logging Rules", "| request | info | request_id | no secrets |")
        insert_table_row(path, "## Metrics", "| latency | ms | p95 | alert-001 |")
    elif suffix == "observability-gate":
        seed_generic_contract_for_strict(path)
    elif suffix == "performance-budget":
        insert_table_row(path, "## Budget Matrix", "| BUD-001 | render | frame time | 16 | ms | <= | python perf.py | perf | draft |")
        insert_table_row(path, "## Measurement Method", "| M-001 | profiler | local | 3 | 10 | /tmp/perf.json |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/perf.json | self-test | 2026-04-24 |")
    elif suffix == "pin-map":
        insert_table_row(path, "## Pin Matrix", "| P1 | SDA | inout | pullup | high | hw | I2C |")
        insert_table_row(path, "## Revision Mapping", "| revA | none | compatible | /tmp/pins.csv |")
        insert_table_row(path, "## Electrical Notes", "| I2C | voltage | 3.3 | V |")
    elif suffix == "parity-contract":
        insert_table_row(path, "## Parity Matrix", "| PAR-001 | old | new | exact | 0 |")
        insert_table_row(path, "## Comparison Method", "| CMP-001 | python compare.py | fixture | /tmp/parity.json |")
        insert_table_row(path, "## Validation Fixtures", "| FIX-001 | input | old.json | new.json |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/parity-contract.log | self-test | 2026-04-24 |")
    elif suffix == "platform-lifecycle-contract":
        insert_table_row(path, "## Platform Matrix", "| macOS | 14+ | true | notarized |")
        insert_table_row(path, "## Lifecycle Events", "| suspend | app background | save state | ui-test |")
        insert_table_row(path, "## Validation", "| launch | run app | ready | /tmp/lifecycle.log |")
    elif suffix == "protocol-contract":
        insert_table_row(path, "## Protocol Scope", "| HID | v1 | USB | firmware |")
        insert_table_row(path, "## Message Matrix", "| MSG-001 | out | report | ack |")
        insert_table_row(path, "## Timing Rules", "| T-001 | ack | 1 | ms |")
    elif suffix == "public-api-contract":
        insert_table_row(path, "## Public Surface", "| API-001 | module | stable | owner |")
        insert_table_row(path, "## Compatibility Policy", "| API-001 | semver | no breaking | v1 |")
        insert_table_row(path, "## Versioning Rules", "| v1 | additive | release |")
    elif suffix == "refactor-target-inventory":
        insert_table_row(path, "## Target Inventory", "| TAR-001 | ViewModel | coupled | split | P0 | refactor |")
        insert_table_row(path, "## Refactor Drivers", "| DRV-001 | coupling | /tmp/static.txt | high |")
        insert_table_row(path, "## Blast Radius", "| TAR-001 | UI, domain | medium | BEH-001 |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/refactor.log | self-test | 2026-04-24 |")
    elif suffix == "rendering-pipeline-contract":
        insert_table_row(path, "## Pipeline Stages", "| ST-001 | draw | scene | frame | render | device loss |")
        insert_table_row(path, "## Resource Flow", "| texture | loader | renderer | cleanup | frame |")
        insert_table_row(path, "## Frame Budget", "| orbit | frame-time | 16 | ms | profiler | /tmp/frame.json |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/render.log | self-test | 2026-04-24 |")
    elif suffix == "resource-lifecycle-contract":
        insert_table_row(path, "## Resource Matrix", "| RES-001 | texture | loader | renderer | disposer |")
        insert_table_row(path, "## Ownership Transfer", "| TR-001 | loader | renderer | upload | smoke-test |")
        insert_table_row(path, "## Lifecycle Rules", "| RES-001 | allocated, released | leaked | dispose |")
        insert_table_row(path, "## Leak Prevention", "| texture leak | profiler | 0 | dispose |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/resource.log | self-test | 2026-04-24 |")
    elif suffix == "regression-matrix":
        insert_table_row(path, "## Regression Matrix", "| REG-001 | smoke | pass | qa | automated |")
        insert_table_row(path, "## Baseline", "| BASE-001 | build-1 | /tmp/baseline.json | true |")
        insert_table_row(path, "## Execution", "| CMD-001 | pytest | local | /tmp/regression.log |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/regression.log | self-test | 2026-04-24 |")
    elif suffix == "rollback-plan":
        insert_table_row(path, "## Rollback Scope", "| RB-001 | release | P0 | owner |")
        insert_table_row(path, "## Triggers", "| gate fail | P0 | immediate |")
        insert_table_row(path, "## Procedure", "| 1 | restore | python rollback.py |")
        insert_table_row(path, "## Verification", "| verify | python smoke.py | pass | /tmp/rollback.log |")
    elif suffix == "rollback-trigger":
        insert_table_row(path, "## Trigger Matrix", "| TRIG-001 | error rate | 1 | P0 |")
        insert_table_row(path, "## Severity Rules", "| P0 | release blocker | rollback | release |")
        insert_table_row(path, "## Actions", "| TRIG-001 | rollback | python rollback.py | smoke-test |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/rollback-trigger.log | self-test | 2026-04-24 |")
    elif suffix == "route-contract":
        insert_table_row(path, "## Route Matrix", "| ROUTE-001 | /home | empty | web | draft |")
        insert_table_row(path, "## State Binding", "| ROUTE-001 | session | true | restore |")
        insert_table_row(path, "## Guard Rules", "| GUARD-001 | ROUTE-001 | authenticated | /login |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/route.log | self-test | 2026-04-24 |")
    elif suffix == "runtime-loop-contract":
        insert_table_row(path, "## Loop Matrix", "| LOOP-001 | render | 60hz | runtime |")
        insert_table_row(path, "## Timing Budget", "| LOOP-001 | frame | 16 | ms |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/runtime.log | self-test | 2026-04-24 |")
    elif suffix == "scene-graph-contract":
        insert_table_row(path, "## Node Matrix", "| mesh | renderable | scene root | renderer |")
        insert_table_row(path, "## Transform Rules", "| TR-001 | mesh | world | matrix test |")
        insert_table_row(path, "## Resource Binding", "| material | mesh | scene | dispose |")
        insert_table_row(path, "## Mutation Rules", "| transform | frame | main | mark dirty |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/scene.log | self-test | 2026-04-24 |")
    elif suffix == "security-contract":
        insert_table_row(path, "## Security Scope", "| SEC-001 | auth | P0 | owner |")
        insert_table_row(path, "## Threat Matrix", "| TH-001 | spoofing | auth bypass | control |")
        insert_table_row(path, "## Control Matrix", "| CTRL-001 | auth | test | owner |")
        insert_table_row(path, "## Verification", "| verify auth | python security.py | pass |")
    elif suffix == "source-of-truth-policy":
        return
    elif suffix == "theme-token-contract":
        insert_table_row(path, "## Semantic Components", "| PrimaryButton | ColorTokens, RadiusTokens | product surface |")
    elif suffix == "tolerance-contract":
        insert_table_row(path, "## Tolerance Matrix", "| CAP-001 | algorithm | mesh | 0.01 | mm | <= | fixture | P0 |")
        insert_table_row(path, "## Measurement Method", "| M-001 | validator | python tolerance.py | all | /tmp/tolerance.json |")
        insert_table_row(path, "## Dataset Binding", "| fixture | v1 | true | CAP-001 |")
    elif suffix == "threading-contract":
        insert_table_row(path, "## Thread Matrix", "| main | UI | app |")
        insert_table_row(path, "## Ownership Rules", "| resource | main | worker-readonly |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/threading.log | self-test | 2026-04-24 |")
    elif suffix == "training-pipeline-contract":
        insert_table_row(path, "## Pipeline Matrix", "| STAGE-001 | train | dataset | model | ml |")
        insert_table_row(path, "## Data Inputs", "| train | v1 | true | /tmp/dataset |")
        insert_table_row(path, "## Training Commands", "| TRAIN-001 | python train.py | local | /tmp/model.bin |")
        insert_table_row(path, "## Output Artifacts", "| MODEL-001 | /tmp/model.bin | trainer | retain |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/train.log | self-test | 2026-04-24 |")
    elif suffix == "test-inventory":
        insert_table_row(path, "## Test Inventory", "| TEST-001 | api | integration | qa | draft |")
        insert_table_row(path, "## Coverage Matrix", "| CAP-001 | TEST-001 | true | none |")
        insert_table_row(path, "## Execution Commands", "| CMD-001 | pytest | pass | /tmp/test.log |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/test.log | self-test | 2026-04-24 |")
    elif suffix == "ui-state-contract":
        insert_table_row(path, "## Canonical State IDs", "| empty | Empty | no material | app start | material loaded | none | false |")
        text = path.read_text(encoding="utf-8").replace(
            "## Transitions\n",
            "## Transitions\n```mermaid\nflowchart LR\n  empty --> material_loaded\n```\n",
            1,
        )
        path.write_text(text, encoding="utf-8")
        insert_table_row(path, "## Error States", "| error_loading | load failure | show error | retry load | retry preserves input |")
        insert_table_row(path, "## CTA Visibility / Enabled Rules", "| Export | material_loaded | material_loaded | missing material |")
    elif suffix == "validation-dataset":
        insert_table_row(path, "## Dataset Matrix", "| DATA-001 | v1 | local | all | true |")
        insert_table_row(path, "## Coverage", "| DATA-001 | CAP-001 | full | none |")
        insert_table_row(path, "## Access Rules", "| DATA-001 | /tmp/dataset | read | retain |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/dataset.log | self-test | 2026-04-24 |")
    elif suffix == "versioning-policy":
        insert_table_row(path, "## Versioning Rules", "| VER-001 | public api | semver | sdk |")
        insert_table_row(path, "## Compatibility Promises", "| API | backward compatible | v1 | compat-test |")
        insert_table_row(path, "## Breaking Change Policy", "| schema | false | migration notice | adapter |")
        insert_table_row(path, "## Release Tags", "| v* | release | CI | tag-check |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/version.log | self-test | 2026-04-24 |")
    elif suffix == "visual-regression-gate":
        insert_table_row(path, "## Baseline Artifacts", "| BASE-001 | main scene | /tmp/baseline.png | build-1 | true |")
        insert_table_row(path, "## Scenario Matrix", "| SCN-001 | main view | fixture | image | design | automated |")
        insert_table_row(path, "## Thresholds", "| pixel-diff | 0.01 | ratio | <= | P0 |")
        insert_table_row(path, "## Evidence", "| E-001 | /tmp/visual.json | self-test | 2026-04-24 |")
    else:
        seed_generic_contract_for_strict(path)


def parse_catalog_names(section_heading: str) -> set[str]:
    text = CATALOG.read_text(encoding="utf-8")
    _, marker, after = text.partition(section_heading)
    if not marker:
        raise SystemExit(f"missing catalog section {section_heading}")
    body = after.split("\n## ", 1)[0]
    names = set()
    for line in body.splitlines():
        match = re.match(r"\| `([^`]+)` \|", line)
        if match:
            names.add(match.group(1))
    return names


def test_catalog_schema_consistency() -> None:
    catalog_archetypes = parse_catalog_names("## Core Archetypes")
    catalog_modifiers = parse_catalog_names("## Modifiers")
    catalog_required_docs = parse_catalog_required_docs()
    if catalog_archetypes != set(ARCHETYPES):
        raise SystemExit(
            "archetype catalog drift: "
            f"missing={sorted(set(ARCHETYPES) - catalog_archetypes)} "
            f"extra={sorted(catalog_archetypes - set(ARCHETYPES))}"
        )
    if catalog_modifiers != set(MODIFIERS):
        raise SystemExit(
            "modifier catalog drift: "
            f"missing={sorted(set(MODIFIERS) - catalog_modifiers)} "
            f"extra={sorted(catalog_modifiers - set(MODIFIERS))}"
        )
    for archetype in ARCHETYPES:
        catalog_specs = set(catalog_required_docs.get(archetype, set())) | set(UNIVERSAL_REQUIRED_SPECS)
        schema_specs = set(required_specs_for(archetype))
        if catalog_specs != schema_specs:
            raise SystemExit(
                f"required docs catalog drift for {archetype}: "
                f"missing={sorted(schema_specs - catalog_specs)} "
                f"extra={sorted(catalog_specs - schema_specs)}"
            )


def test_every_archetype() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-archetypes-") as tmp:
        for archetype in sorted(ARCHETYPES):
            slug = archetype.replace("-", "")
            package = f"Plan-{slug}"
            init_and_validate(tmp, package, slug, archetype)
            for suffix in required_specs_for(archetype):
                path = Path(tmp) / "docs" / "spec" / f"{slug}-{suffix}.md"
                if not path.exists():
                    raise SystemExit(f"{archetype} did not generate {suffix}")


def test_every_modifier() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-modifiers-") as tmp:
        for modifier in sorted(MODIFIERS):
            slug = modifier.replace("-", "")
            package = f"Plan-{slug}"
            init_and_validate(tmp, package, slug, "backend-service", modifier)
            for suffix in required_specs_for("backend-service", [modifier]):
                path = Path(tmp) / "docs" / "spec" / f"{slug}-{suffix}.md"
                if not path.exists():
                    raise SystemExit(f"{modifier} did not generate {suffix}")


def test_aliases() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-aliases-") as tmp:
        for alias in ["ui-product", "algorithm-rewrite", "migration-only"]:
            slug = alias.replace("-", "")
            init_and_validate(tmp, f"Plan-{slug}", slug, alias)


def test_missing_template_error_message() -> None:
    result = run(
        [
            "python3",
            "-c",
            (
                "import sys; "
                f"sys.path.insert(0, {str(SCRIPT_DIR)!r}); "
                "import init_phase_plan_package as init; "
                "init.load_template('missing-template.md', 'demo-spec')"
            ),
        ],
        expect_ok=False,
    )
    assert_contains(
        result.stderr + result.stdout,
        "missing template missing-template.md for spec demo-spec",
        "missing template error",
    )


def test_release_blocking_gate_inputs() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-release-blocking-") as tmp:
        init_and_validate(tmp, "Plan-ArchBlocking", "archblocking", "architecture-refactor")
        arch_release = Path(tmp) / "docs" / "spec" / "archblocking-release-gate.md"
        arch_text = arch_release.read_text(encoding="utf-8")
        if "behavior-parity-contract | true |" not in arch_text:
            raise SystemExit("architecture-refactor should mark behavior-parity-contract release-blocking")

        init_and_validate(tmp, "Plan-FirmwareBlocking", "firmwareblocking", "firmware-hardware")
        fw_text = (Path(tmp) / "docs" / "spec" / "firmwareblocking-release-gate.md").read_text(encoding="utf-8")
        for suffix in ["hardware-interface-contract", "pin-map", "protocol-contract"]:
            if f"{suffix} | true |" not in fw_text:
                raise SystemExit(f"firmware-hardware should mark {suffix} release-blocking")

        init_and_validate(tmp, "Plan-RollbackBlocking", "rollbackblocking", "backend-service", "rollback-required")
        rollback_text = (Path(tmp) / "docs" / "spec" / "rollbackblocking-release-gate.md").read_text(encoding="utf-8")
        for suffix in ["rollback-plan", "rollback-trigger"]:
            if f"{suffix} | true |" not in rollback_text:
                raise SystemExit(f"rollback-required should mark {suffix} release-blocking")


def test_mesh_processing_modifier_and_group_density() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-mesh-modifier-") as tmp:
        args = init_and_validate(
            tmp,
            "Plan-Mesh",
            "mesh",
            "application-product",
            "mesh-processing-heavy,cross-session-handoff",
        )
        spec_dir = Path(tmp) / "docs" / "spec"
        for suffix in ["mesh-ops-contract", "tolerance-contract", "gap-registry"]:
            if not (spec_dir / f"mesh-{suffix}.md").exists():
                raise SystemExit(f"mesh-processing-heavy did not generate {suffix}")
        release = spec_dir / "mesh-release-gate.md"
        release_text = release.read_text(encoding="utf-8")
        for suffix in ["mesh-ops-contract", "tolerance-contract", "gap-registry"]:
            if f"{suffix} | true |" not in release_text:
                raise SystemExit(f"mesh-processing-heavy should mark {suffix} release-blocking")
        group3 = Path(tmp) / "docs" / "plan" / "Plan-Mesh" / "Phase1" / "Group3-Integration-Boundary-Map.md"
        group3_text = group3.read_text(encoding="utf-8")
        if "depends_on:\n  - group-1" not in group3_text:
            raise SystemExit("group dependency metadata was not rendered")
        if "mesh-ops-contract" not in group3_text or "Full required spec list lives in the package README" not in group3_text:
            raise SystemExit("group relevant specs were not rendered compactly")
        readme = Path(tmp) / "docs" / "plan" / "Plan-Mesh" / "README.md"
        readme_text = readme.read_text(encoding="utf-8")
        if "## Human Quickstart" not in readme_text or "## Dependency Graph" not in readme_text:
            raise SystemExit("README missing quickstart or dependency graph")
        run(["python3", str(VALIDATE), *args, "--quality-lint"])


def test_validation_command_consistency() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-command-consistency-") as tmp:
        args = init_and_validate(tmp, "Plan-Commands", "commands", "backend-service", "rollback-required")
        readme = Path(tmp) / "docs" / "plan" / "Plan-Commands" / "README.md"
        dated = Path(tmp) / "docs" / "plan" / "2026-04-24-commands.md"
        if "--strict --strict-handoff" not in readme.read_text(encoding="utf-8"):
            raise SystemExit("README strict command should include --strict-handoff")
        if readme.read_text(encoding="utf-8").count("validate_phase_plan_package.py") != dated.read_text(encoding="utf-8").count("validate_phase_plan_package.py"):
            raise SystemExit("README and canonical plan should render the same number of validation commands")
        readme.write_text(readme.read_text(encoding="utf-8").replace(" --strict --strict-handoff", " --strict", 1), encoding="utf-8")
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "validation commands differ", "validation command consistency")


def test_strict_fails_on_empty_contracts() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-strict-") as tmp:
        args = init_and_validate(
            tmp,
            "Plan-App",
            "app",
            "application-product",
            "local-device-runtime,rendering-heavy,performance-critical",
        )
        failed = run(["python3", str(VALIDATE), *args, "--strict"], expect_ok=False)
        assert_contains(failed.stdout, "strict mode requires", "strict empty contract rejection")


def test_strict_passes_on_populated_package() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-strict-pass-") as tmp:
        archetypes = [
            "architecture-refactor",
            "large-scale-refactor",
            "algorithm-engine",
            "rendering-engine",
            "firmware-hardware",
            "application-product",
            "backend-service",
        ]
        for archetype in archetypes:
            slug = archetype.replace("-", "")
            package = f"Plan-{slug}-Strict"
            args = init_and_validate(tmp, package, slug, archetype)
            spec_dir = Path(tmp) / "docs" / "spec"
            for suffix in required_specs_for(archetype):
                seed_contract_for_strict(spec_dir, slug, suffix)
            run(["python3", str(VALIDATE), *args, "--strict"])


def test_write_validation_stamp() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-stamp-") as tmp:
        args = init_and_validate(tmp, "Plan-Stamp", "stamp", "backend-service")
        readme = Path(tmp) / "docs" / "plan" / "Plan-Stamp" / "README.md"
        before = readme.read_text(encoding="utf-8")
        if "last_validated: Unverified" not in before:
            raise SystemExit("stamp fixture expected Unverified before validation")
        run(["python3", str(VALIDATE), *args, "--write-validation-stamp"])
        after = readme.read_text(encoding="utf-8")
        if "last_validated: Unverified" in after:
            raise SystemExit("write-validation-stamp did not update README")


def test_readme_checklist_rejection() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-readme-") as tmp:
        args = init_and_validate(tmp, "Plan-Readme", "readme", "web-product")
        readme = Path(tmp) / "docs" / "plan" / "Plan-Readme" / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n- [ ] stale checklist\n", encoding="utf-8")
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "README: contains checklist items", "README checklist rejection")


def test_ui_state_redefinition_rejection() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-state-") as tmp:
        args = init_and_validate(tmp, "Plan-State", "state", "web-product")
        group = next((Path(tmp) / "docs" / "plan" / "Plan-State").rglob("Group*.md"))
        group.write_text(group.read_text(encoding="utf-8") + "\n## Canonical State IDs\n", encoding="utf-8")
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "redefines canonical state ids", "UI state singularity")


def test_p0_placeholder_contract_rejection() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-p0-") as tmp:
        args = init_and_validate(tmp, "Plan-P0", "p0", "application-product")
        capability = Path(tmp) / "docs" / "spec" / "p0-capability-map.md"
        insert_table_row(
            capability,
            "## Capability Matrix",
            "| CAP-001 | Export | owner | desc | current | target | P0 | TBD | source | planned | - | 2026-04-24 |",
        )
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "P0 row missing contract link", "P0 placeholder contract")


def test_implementation_status_parsing() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-impl-") as tmp:
        args = init_and_validate(tmp, "Plan-Impl", "impl", "backend-service")
        integration = Path(tmp) / "docs" / "spec" / "impl-integration-contract.md"
        insert_table_row(
            integration,
            "## Unresolved Interfaces",
            "| IF-001 | unresolved | blocking | - | decide owner |",
        )
        run(["python3", str(VALIDATE), *args])

        dated = Path(tmp) / "docs" / "plan" / "2026-04-24-impl.md"
        dated.write_text(
            dated.read_text(encoding="utf-8").replace(
                "implementation_status: planning-only",
                "implementation_status: implementation-open",
            ),
            encoding="utf-8",
        )
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "blocking unresolved interface", "implementation status parsing")


def test_custom_phase_names_and_hard_predecessor_order() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-phases-") as tmp:
        args = common_args(tmp, "Plan-Phases", "phases", "architecture-refactor")
        run(
            [
                "python3",
                str(INIT),
                *args,
                "--phase-names",
                "Foundation,Extraction,Validation,Release",
            ]
        )
        run(["python3", str(VALIDATE), *args])

        release_group = next((Path(tmp) / "docs" / "plan" / "Plan-Phases" / "Release").rglob("Group*.md"))
        release_group.write_text(
            release_group.read_text(encoding="utf-8").replace("status: draft", "status: in-progress", 1),
            encoding="utf-8",
        )
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "hard predecessor", "phase_order hard predecessor gating")


def test_phase_count_mismatch_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-phasecount-") as tmp:
        args = common_args(tmp, "Plan-PhaseCount", "phasecount", "architecture-refactor")
        failed = run(["python3", str(INIT), *args, "--phases", "2"], expect_ok=False)
        assert_contains(failed.stderr + failed.stdout, "Placeholder groups are not generated", "phase count mismatch")


def test_non_numeric_threshold_rejection() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-threshold-") as tmp:
        args = init_and_validate(tmp, "Plan-Threshold", "threshold", "backend-service")
        release = Path(tmp) / "docs" / "spec" / "threshold-release-gate.md"
        insert_table_row(
            release,
            "## Numeric Thresholds",
            "| latency | fast | ms | <= | bench | base | P0 | invalid |",
        )
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "non-numeric threshold", "non-numeric threshold rejection")


def test_strict_checks_every_release_critical_row() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-strict-row-") as tmp:
        args = init_and_validate(tmp, "Plan-StrictRows", "strictrows", "backend-service")
        spec_dir = Path(tmp) / "docs" / "spec"
        for suffix in required_specs_for("backend-service"):
            seed_contract_for_strict(spec_dir, "strictrows", suffix)
        release = spec_dir / "strictrows-release-gate.md"
        insert_table_row(
            release,
            "## Numeric Thresholds",
            "| bad-threshold | TBD | ms | <= | self-test | generated | P0 | must fail even after a good row |",
        )
        failed = run(["python3", str(VALIDATE), *args, "--strict"], expect_ok=False)
        assert_contains(failed.stdout, "non-numeric value `TBD`", "strict checks every threshold row")


def test_strict_ui_state_contract_rules() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-ui-strict-") as tmp:
        args = init_and_validate(tmp, "Plan-UIStrict", "uistrict", "application-product")
        spec_dir = Path(tmp) / "docs" / "spec"
        for suffix in required_specs_for("application-product"):
            seed_contract_for_strict(spec_dir, "uistrict", suffix)
        ui = spec_dir / "uistrict-ui-state-contract.md"
        ui.write_text(ui.read_text(encoding="utf-8").replace("  empty --> material_loaded\n", ""), encoding="utf-8")
        failed = run(["python3", str(VALIDATE), *args, "--strict"], expect_ok=False)
        assert_contains(failed.stdout, "non-empty transition graph", "strict UI state transition graph")


def test_strict_theme_token_contract_rules() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-theme-strict-") as tmp:
        args = init_and_validate(tmp, "Plan-ThemeStrict", "themestrict", "web-product")
        spec_dir = Path(tmp) / "docs" / "spec"
        for suffix in required_specs_for("web-product"):
            if suffix != "theme-token-contract":
                seed_contract_for_strict(spec_dir, "themestrict", suffix)
        failed = run(["python3", str(VALIDATE), *args, "--strict"], expect_ok=False)
        assert_contains(failed.stdout, "## Semantic Components", "strict theme semantic components")


def test_strict_handoff_rejects_unverified_blockers() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-handoff-strict-") as tmp:
        args = init_and_validate(tmp, "Plan-HandoffStrict", "handoffstrict", "backend-service")
        failed = run(["python3", str(VALIDATE), *args, "--strict-handoff"], expect_ok=False)
        assert_contains(failed.stdout, "Active Blockers to be verified", "strict handoff blockers")


def test_canonical_front_matter_exact_value() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-canonical-") as tmp:
        args = init_and_validate(tmp, "Plan-Canonical", "canonical", "backend-service")
        readme = Path(tmp) / "docs" / "plan" / "Plan-Canonical" / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("canonical: false", "canonical: False", 1), encoding="utf-8")
        failed = run(["python3", str(VALIDATE), *args], expect_ok=False)
        assert_contains(failed.stdout, "canonical must be exactly true or false", "canonical exact value")


def test_auto_ingest_existing_reports() -> None:
    with tempfile.TemporaryDirectory(prefix="phase-subplan-selftest-ingest-") as tmp:
        report_dir = Path(tmp) / "docs" / "codebase-intel" / "sample"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "domain-report.md").write_text(
            "\n".join(
                [
                    "# Domain Report",
                    "LibrarySelection and ExportSelected are P0 capabilities.",
                    "ThreePointFrame, Kabsch, and ICP define the alignment algorithm path.",
                    "Cylinder cut, hole fill patch, and scanbody replacement are missing mesh ops.",
                    "UI state must gate align_ready, convert_ready, output_ready, and error states.",
                ]
            ),
            encoding="utf-8",
        )
        args = common_args(tmp, "Plan-Ingest", "ingest", "application-product")
        run(["python3", str(INIT), *args, "--auto-ingest"])
        run(["python3", str(VALIDATE), *args, "--quality-lint"])
        summary = Path(tmp) / "docs" / "plan" / "Plan-Ingest" / "domain-ingest-summary.md"
        if not summary.exists():
            raise SystemExit("missing domain-ingest-summary.md")
        text = summary.read_text(encoding="utf-8")
        assert_contains(text, "LibrarySelection", "ingested capability signal")
        assert_contains(text, "Cylinder cut", "ingested mesh ops signal")
        group = Path(tmp) / "docs" / "plan" / "Plan-Ingest" / "Phase1" / "Group1-Functional-Parity-Baseline.md"
        assert_contains(group.read_text(encoding="utf-8"), "Existing analysis inputs", "group domain current state")


def main() -> None:
    test_catalog_schema_consistency()
    test_every_archetype()
    test_every_modifier()
    test_aliases()
    test_missing_template_error_message()
    test_release_blocking_gate_inputs()
    test_mesh_processing_modifier_and_group_density()
    test_validation_command_consistency()
    test_strict_fails_on_empty_contracts()
    test_strict_passes_on_populated_package()
    test_write_validation_stamp()
    test_readme_checklist_rejection()
    test_ui_state_redefinition_rejection()
    test_p0_placeholder_contract_rejection()
    test_implementation_status_parsing()
    test_custom_phase_names_and_hard_predecessor_order()
    test_phase_count_mismatch_rejected()
    test_non_numeric_threshold_rejection()
    test_strict_checks_every_release_critical_row()
    test_strict_ui_state_contract_rules()
    test_strict_theme_token_contract_rules()
    test_strict_handoff_rejects_unverified_blockers()
    test_canonical_front_matter_exact_value()
    test_auto_ingest_existing_reports()
    print("SELF_TEST_OK")


if __name__ == "__main__":
    main()
