from __future__ import annotations

from dataclasses import dataclass, field


README_HEADINGS = [
    "## Purpose",
    "## Derived Status Notice",
    "## Human Quickstart",
    "## Canonical Documents",
    "## Archetype",
    "## Active Implementation Card",
    "## Target Module Structure",
    "## Phase Index",
    "## Group Index",
    "## Dependency Graph",
    "## Spec Docs",
    "## Canonical Read Order",
    "## Validation Commands",
    "## Notes",
]

REQUIRED_FRONT_MATTER = [
    "doc_type",
    "canonical",
    "status",
    "last_validated",
    "last_validated_mode",
    "strict_validated_at",
    "strict_handoff_validated_at",
    "release_ready",
    "source_of_truth_for",
    "derived_from",
]

UNIVERSAL_REQUIRED_SPECS = [
    "release-gate",
    "agent-handoff-index",
]

DATED_PLAN_HEADINGS = [
    "## 1) Task Overview",
    "## 2) Changed File List",
    "## 3) Change Summary",
    "## 4) Risks",
    "## 5) Validation Procedure",
    "## 6) Questions and Answers",
    "## 7) TODO",
    "## 8) Implementation Transition Status",
    "## 9) Approval Gate",
    "## 10) Progress Log",
    "## Active Implementation Card",
]

GROUP_HEADINGS = [
    "## Purpose",
    "## Current State",
    "## Target State",
    "## Derived Document Notice",
    "## Referenced Canonical Docs",
    "## Referenced Canonical IDs",
    "## Dependencies",
    "## Implementation Digest",
    "## Proposed Changes to Canonical Contracts",
    "## Acceptance Criteria",
    "## Prohibited Shortcuts",
    "## TODO",
]

SPEC_HEADINGS = {
    "capability-map": [
        "## Capability Matrix",
        "## P0 Scope Lock",
        "## Decision Log",
    ],
    "algorithm-inventory": [
        "## Inventory",
        "## Recommended Stack",
        "## Validation Matrix",
    ],
    "ui-state-contract": [
        "## State ID Naming Rule",
        "## Canonical State IDs",
        "## Transitions",
        "## Error States",
        "## CTA Visibility / Enabled Rules",
    ],
    "integration-contract": [
        "## Reused Subsystems",
        "## Extracted Capabilities",
        "## Boundaries",
        "## Interface Contracts",
        "## Unresolved Interfaces",
    ],
    "theme-token-contract": [
        "## Token Sets",
        "## Semantic Components",
        "## Hard Rules",
    ],
    "release-gate": [
        "## Gate Inputs",
        "## Upstream Gates",
        "## Datasets",
        "## Numeric Thresholds",
        "## Regression Matrix",
        "## Rollback Triggers",
        "## Waivers",
        "## Evidence Artifacts",
        "## Verdict Rule",
    ],
    "mesh-ops-contract": [
        "## Mesh Operation Matrix",
        "## Geometry Risk Matrix",
        "## PoC Plan",
        "## Output Validity",
    ],
    "gap-registry": [
        "## Gap Matrix",
        "## Gap Closure Rules",
    ],
    "agent-handoff-index": [
        "## Current Canonical Plan Path",
        "## Active Blockers",
        "## Human Quickstart",
        "## Read Order",
        "## Implementation Start Checklist",
        "## Update Rules",
        "## Prohibited Shortcuts",
        "## Last Validated At",
    ],
}

GENERIC_CONTRACT_HEADINGS = [
    "## Purpose",
    "## Contract Scope",
    "## Contract Matrix",
    "## Validation Rules",
    "## Open Decisions",
    "## Evidence",
]

GENERIC_CONTRACTS = {
    "api-contract",
    "app-runtime-contract",
    "architecture-contract",
    "benchmark-contract",
    "behavior-parity-contract",
    "build-contract",
    "characterization-test-plan",
    "compatibility-matrix",
    "compatibility-policy",
    "data-contract",
    "data-mapping-contract",
    "dataset-contract",
    "dependency-graph",
    "dependency-rule-contract",
    "deployment-contract",
    "deprecation-policy",
    "environment-contract",
    "evaluation-gate",
    "experiment-contract",
    "failure-matrix",
    "failure-mode-contract",
    "failure-mode-matrix",
    "failure-recovery-contract",
    "fallback-contract",
    "firmware-behavior-contract",
    "hardware-interface-contract",
    "input-output-contract",
    "local-storage-contract",
    "migration-map",
    "module-boundary-map",
    "module-map",
    "numeric-threshold",
    "observability-contract",
    "observability-gate",
    "old-new-mapping",
    "optimization-target-inventory",
    "parity-contract",
    "performance-baseline",
    "performance-budget",
    "pin-map",
    "platform-lifecycle-contract",
    "profiling-report",
    "protocol-contract",
    "public-api-contract",
    "public-boundary-contract",
    "refactor-target-inventory",
    "regression-matrix",
    "regression-plan",
    "rendering-pipeline-contract",
    "resource-lifecycle-contract",
    "resource-ownership-contract",
    "risk-map",
    "rollback-plan",
    "rollback-trigger",
    "route-contract",
    "runtime-loop-contract",
    "scene-graph-contract",
    "security-contract",
    "source-of-truth-policy",
    "stability-issue-inventory",
    "test-inventory",
    "threading-contract",
    "tolerance-contract",
    "training-pipeline-contract",
    "validation-dataset",
    "versioning-policy",
    "visual-regression-gate",
}

for _generic_contract in GENERIC_CONTRACTS:
    SPEC_HEADINGS[_generic_contract] = GENERIC_CONTRACT_HEADINGS

SPEC_HEADINGS.update(
    {
        "api-contract": [
            "## Endpoint Matrix",
            "## Request Response Contracts",
            "## Error Semantics",
            "## Compatibility",
            "## Evidence",
        ],
        "app-runtime-contract": [
            "## Runtime Scope",
            "## Lifecycle Matrix",
            "## Permission Matrix",
            "## Resource Ownership",
            "## Failure Recovery",
        ],
        "architecture-contract": [
            "## Architecture Goals",
            "## Layer Model",
            "## State Ownership",
            "## Dependency Direction",
            "## Behavior Parity Boundary",
            "## Open Decisions",
        ],
        "benchmark-contract": [
            "## Benchmark Cases",
            "## Metrics",
            "## Baseline",
            "## Execution Command",
            "## Evidence",
        ],
        "behavior-parity-contract": [
            "## Parity Scope",
            "## Behavior Matrix",
            "## Characterization Tests",
            "## Allowed Differences",
            "## Evidence",
        ],
        "characterization-test-plan": [
            "## Characterization Inventory",
            "## Test Matrix",
            "## Golden Artifacts",
            "## Coverage Gaps",
            "## Execution Command",
        ],
        "data-contract": [
            "## Entity Matrix",
            "## Schema Rules",
            "## Migration Rules",
            "## Data Safety",
            "## Evidence",
        ],
        "compatibility-matrix": [
            "## Compatibility Matrix",
            "## Supported Combinations",
            "## Breaking Change Risks",
            "## Validation",
            "## Evidence",
        ],
        "deployment-contract": [
            "## Deployment Matrix",
            "## Release Environments",
            "## Rollout Rules",
            "## Rollback Link",
            "## Evidence",
        ],
        "build-contract": [
            "## Build Targets",
            "## Build Commands",
            "## Artifacts",
            "## Environment Inputs",
            "## Evidence",
        ],
        "dataset-contract": [
            "## Dataset Matrix",
            "## Split Policy",
            "## Freeze Policy",
            "## Data Quality Rules",
            "## Evidence",
        ],
        "dependency-graph": [
            "## Graph Scope",
            "## Dependency Matrix",
            "## Cycle Policy",
            "## Risk Hotspots",
            "## Evidence",
        ],
        "dependency-rule-contract": [
            "## Rule Matrix",
            "## Allowed Dependencies",
            "## Forbidden Dependencies",
            "## Enforcement",
            "## Waivers",
        ],
        "environment-contract": [
            "## Environment Matrix",
            "## Toolchain Versions",
            "## Secret And Permission Rules",
            "## Reproducibility",
            "## Evidence",
        ],
        "failure-mode-contract": [
            "## Failure Mode Matrix",
            "## Detection Rules",
            "## Recovery Rules",
            "## Escalation Rules",
            "## Evidence",
        ],
        "firmware-behavior-contract": [
            "## Firmware Scope",
            "## Behavior Matrix",
            "## Timing Requirements",
            "## Error Handling",
            "## Verification",
        ],
        "evaluation-gate": [
            "## Evaluation Matrix",
            "## Numeric Thresholds",
            "## Required Artifacts",
            "## Failure Handling",
            "## Verdict Rule",
        ],
        "experiment-contract": [
            "## Experiment Matrix",
            "## Reproducibility Rules",
            "## Metrics",
            "## Artifacts",
            "## Evidence",
        ],
        "failure-matrix": [
            "## Failure Matrix",
            "## Detection Matrix",
            "## Fallback Matrix",
            "## Escalation Rules",
            "## Evidence",
        ],
        "hardware-interface-contract": [
            "## Hardware Revisions",
            "## Interface Matrix",
            "## Electrical Constraints",
            "## Validation Fixtures",
            "## Failure Modes",
        ],
        "input-output-contract": [
            "## Input Matrix",
            "## Output Matrix",
            "## Transformation Rules",
            "## Validation Fixtures",
            "## Evidence",
        ],
        "local-storage-contract": [
            "## Storage Matrix",
            "## Schema And Versioning",
            "## Persistence Rules",
            "## Data Safety",
            "## Evidence",
        ],
        "migration-map": [
            "## Migration Scope",
            "## Old To New Mapping",
            "## Sequence",
            "## Compatibility Risks",
            "## Rollback Hook",
        ],
        "module-boundary-map": [
            "## Module Matrix",
            "## Public Boundaries",
            "## Ownership",
            "## Cross Module Rules",
            "## Open Boundaries",
        ],
        "observability-contract": [
            "## Signal Matrix",
            "## Logging Rules",
            "## Metrics",
            "## Alerting",
            "## Evidence",
        ],
        "old-new-mapping": [
            "## Mapping Matrix",
            "## Behavior Equivalence",
            "## Data Migration Notes",
            "## Validation",
            "## Evidence",
        ],
        "parity-contract": [
            "## Parity Matrix",
            "## Allowed Differences",
            "## Comparison Method",
            "## Validation Fixtures",
            "## Evidence",
        ],
        "performance-budget": [
            "## Budget Matrix",
            "## Measurement Method",
            "## Enforcement Rule",
            "## Evidence",
        ],
        "pin-map": [
            "## Pin Matrix",
            "## Revision Mapping",
            "## Electrical Notes",
            "## Validation",
        ],
        "platform-lifecycle-contract": [
            "## Platform Matrix",
            "## Lifecycle Events",
            "## Backgrounding Rules",
            "## Packaging Rules",
            "## Validation",
        ],
        "protocol-contract": [
            "## Protocol Scope",
            "## Message Matrix",
            "## Timing Rules",
            "## Compatibility",
            "## Verification",
        ],
        "public-api-contract": [
            "## Public Surface",
            "## Compatibility Policy",
            "## Versioning Rules",
            "## Breaking Change Rules",
            "## Evidence",
        ],
        "refactor-target-inventory": [
            "## Target Inventory",
            "## Refactor Drivers",
            "## Blast Radius",
            "## Sequencing",
            "## Evidence",
        ],
        "regression-matrix": [
            "## Regression Matrix",
            "## Baseline",
            "## Execution",
            "## Failure Handling",
            "## Evidence",
        ],
        "resource-lifecycle-contract": [
            "## Resource Matrix",
            "## Ownership Transfer",
            "## Lifecycle Rules",
            "## Leak Prevention",
            "## Evidence",
        ],
        "rendering-pipeline-contract": [
            "## Pipeline Stages",
            "## Resource Flow",
            "## Frame Budget",
            "## Failure Modes",
            "## Evidence",
        ],
        "route-contract": [
            "## Route Matrix",
            "## State Binding",
            "## Guard Rules",
            "## Navigation Failure Handling",
            "## Evidence",
        ],
        "scene-graph-contract": [
            "## Node Matrix",
            "## Transform Rules",
            "## Resource Binding",
            "## Mutation Rules",
            "## Evidence",
        ],
        "security-contract": [
            "## Security Scope",
            "## Threat Matrix",
            "## Control Matrix",
            "## Secret Handling",
            "## Verification",
        ],
        "rollback-plan": [
            "## Rollback Scope",
            "## Triggers",
            "## Procedure",
            "## Data Safety",
            "## Verification",
        ],
        "rollback-trigger": [
            "## Trigger Matrix",
            "## Severity Rules",
            "## Actions",
            "## Owners",
            "## Evidence",
        ],
        "source-of-truth-policy": [
            "## Authority Map",
            "## Derived Documents",
            "## Drift Smells",
            "## Correction Rule",
            "## Validation Rule",
        ],
        "runtime-loop-contract": [
            "## Loop Matrix",
            "## Timing Budget",
            "## Backpressure",
            "## Failure Recovery",
            "## Evidence",
        ],
        "tolerance-contract": [
            "## Tolerance Matrix",
            "## Measurement Method",
            "## Dataset Binding",
            "## Failure Conditions",
        ],
        "threading-contract": [
            "## Thread Matrix",
            "## Ownership Rules",
            "## Synchronization",
            "## Race Prevention",
            "## Evidence",
        ],
        "training-pipeline-contract": [
            "## Pipeline Matrix",
            "## Data Inputs",
            "## Training Commands",
            "## Output Artifacts",
            "## Evidence",
        ],
        "test-inventory": [
            "## Test Inventory",
            "## Coverage Matrix",
            "## Execution Commands",
            "## Gaps",
            "## Evidence",
        ],
        "validation-dataset": [
            "## Dataset Matrix",
            "## Freeze Policy",
            "## Coverage",
            "## Access Rules",
            "## Evidence",
        ],
        "versioning-policy": [
            "## Versioning Rules",
            "## Compatibility Promises",
            "## Breaking Change Policy",
            "## Release Tags",
            "## Evidence",
        ],
        "visual-regression-gate": [
            "## Baseline Artifacts",
            "## Scenario Matrix",
            "## Thresholds",
            "## Review Rule",
            "## Evidence",
        ],
    }
)

SPEC_DOC_TYPES = {
    "capability-map": "capability_map",
    "algorithm-inventory": "algorithm_inventory",
    "ui-state-contract": "ui_state_contract",
    "integration-contract": "integration_contract",
    "theme-token-contract": "theme_token_contract",
    "release-gate": "release_gate",
    "agent-handoff-index": "handoff_index",
    "mesh-ops-contract": "mesh_ops_contract",
    "gap-registry": "gap_registry",
}

for _generic_contract in GENERIC_CONTRACTS:
    SPEC_DOC_TYPES[_generic_contract] = _generic_contract.replace("-", "_")


@dataclass(frozen=True)
class GroupSpec:
    phase: str
    title: str
    hard_predecessor: bool = False
    phase_order: int | None = None
    relevant_specs: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    soft_depends_on: list[str] = field(default_factory=list)
    blocking_interfaces: list[str] = field(default_factory=list)
    target_components: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    critical_gap: str = ""
    first_step: str = ""
    prohibited_shortcuts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArchetypeSpec:
    required_specs: list[str]
    groups: list[GroupSpec]


ARCHETYPES: dict[str, ArchetypeSpec] = {
    "application-product": ArchetypeSpec(
        required_specs=[
            "capability-map",
            "app-runtime-contract",
            "platform-lifecycle-contract",
            "ui-state-contract",
            "local-storage-contract",
            "integration-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec(
                "Phase1",
                "Functional Parity Baseline",
                relevant_specs=["capability-map", "behavior-parity-contract", "parity-contract", "old-new-mapping", "release-gate", "gap-registry"],
                target_components=["Capability map", "Legacy behavior matrix", "Golden fixture manifest"],
                responsibilities=["Lock P0 domain behavior", "Separate feature parity from UI appearance parity"],
                critical_gap="Golden fixture and legacy output artifacts are not frozen yet.",
                first_step="Enumerate P0 capabilities and bind each to evidence plus comparator.",
                prohibited_shortcuts=["Do not declare parity from UI screenshots only.", "Do not downgrade P0 without a decision record."],
            ),
            GroupSpec(
                "Phase1",
                "Runtime and Lifecycle Contracts",
                depends_on=["group-1"],
                relevant_specs=["app-runtime-contract", "platform-lifecycle-contract", "resource-lifecycle-contract", "performance-budget", "release-gate"],
                target_components=["Target app/module entry point", "Runtime owner", "Resource owner"],
                responsibilities=["Define app lifecycle", "Define resource ownership and cancellation boundaries"],
                critical_gap="Target app shell or runtime owner may not exist yet.",
                first_step="Inspect or create the target app/module boundary before UI work.",
                prohibited_shortcuts=["Do not run mesh jobs on UI-owned state.", "Do not leave resource release as an implementation detail."],
            ),
            GroupSpec(
                "Phase1",
                "Integration Boundary Map",
                depends_on=["group-1"],
                relevant_specs=["integration-contract", "mesh-ops-contract", "algorithm-inventory", "tolerance-contract", "gap-registry", "release-gate"],
                blocking_interfaces=["integration-boundary", "mesh-ops-strategy"],
                target_components=["Adapter boundary", "Reusable core subsystem list", "Mesh operation strategy"],
                responsibilities=["Separate direct reuse from reference-only code", "Resolve missing mesh/algorithm capabilities"],
                critical_gap="Mesh operation reuse/port/wrap strategy is usually the highest implementation risk.",
                first_step="Inspect target core APIs and classify each P0 mesh operation as reuse, port, wrap, or new.",
                prohibited_shortcuts=["Do not hide missing mesh ops behind UI workarounds.", "Do not reuse another product shell as the new product boundary."],
            ),
            GroupSpec(
                "Phase2",
                "Product Surface",
                depends_on=["group-1", "group-2"],
                relevant_specs=["capability-map", "ui-state-contract", "theme-token-contract", "visual-regression-gate", "release-gate"],
                target_components=["Main window/surface", "Library panel", "Workspace cards", "Toolbar"],
                responsibilities=["Map product workflow to target UI components", "Keep theme/design replaceable"],
                critical_gap="Visual surface can drift if design tokens and behavior state are coupled.",
                first_step="Create a surface responsibility map before coding components.",
                prohibited_shortcuts=["Do not copy platform-specific UI code directly.", "Do not make pixel parity release-blocking unless explicitly approved."],
            ),
            GroupSpec(
                "Phase2",
                "Workspace Interaction and State",
                depends_on=["group-2", "group-4"],
                relevant_specs=["ui-state-contract", "behavior-parity-contract", "rendering-pipeline-contract", "failure-mode-contract", "release-gate"],
                blocking_interfaces=["state-owner", "point-picking-event"],
                target_components=["State machine", "Interaction controller", "Point picking bridge"],
                responsibilities=["Drive CTA visibility from canonical states", "Convert renderer events into domain inputs"],
                critical_gap="Ad-hoc widget state will drift from algorithm readiness.",
                first_step="Implement state-machine tests before binding UI controls.",
                prohibited_shortcuts=["Do not redefine state ids in group docs or components.", "Do not enable convert/export outside canonical states."],
            ),
            GroupSpec(
                "Phase2",
                "Local Storage and Persistence",
                depends_on=["group-1", "group-2"],
                relevant_specs=["local-storage-contract", "input-output-contract", "compatibility-matrix", "release-gate"],
                target_components=["Library catalog store", "Export service", "Metadata writer"],
                responsibilities=["Define catalog versioning", "Define atomic export and metadata rules"],
                critical_gap="Export variants and metadata are easy to under-specify.",
                first_step="Write the output manifest schema before export code.",
                prohibited_shortcuts=["Do not write partial export files directly to user paths.", "Do not treat metadata as optional if downstream tools require it."],
            ),
            GroupSpec(
                "Phase3",
                "Stability Refactor",
                hard_predecessor=True,
                depends_on=["group-2", "group-3", "group-5"],
                relevant_specs=["failure-mode-contract", "resource-lifecycle-contract", "performance-budget", "rollback-trigger", "release-gate"],
                blocking_interfaces=["job-lifecycle", "resource-owner"],
                target_components=["Job runner", "Cancellation boundary", "Resource diagnostics"],
                responsibilities=["Prevent stale async work", "Prevent mesh/GPU/temp-file leaks"],
                critical_gap="Long-running algorithm jobs can mutate stale session state if lifecycle is not explicit.",
                first_step="Add cancellation/resource lifecycle tests before enabling implementation-open.",
                prohibited_shortcuts=["Do not rely on manual QA for race conditions.", "Do not mark conversion complete when partial output exists."],
            ),
            GroupSpec(
                "Phase4",
                "Validation and Release",
                depends_on=["group-1", "group-3", "group-5", "group-7"],
                relevant_specs=["release-gate", "benchmark-contract", "performance-budget", "visual-regression-gate", "rollback-plan", "agent-handoff-index"],
                target_components=["Release gate runner", "Parity report", "Rollback verification"],
                responsibilities=["Aggregate pass/fail evidence", "Prepare cross-session handoff"],
                critical_gap="Strict document validation is not the same as product readiness.",
                first_step="Freeze validation datasets and wire report artifact paths.",
                prohibited_shortcuts=["Do not pass release with planned-only artifacts.", "Do not ignore rollback trigger failures."],
            ),
        ],
    ),
    "web-product": ArchetypeSpec(
        required_specs=[
            "capability-map",
            "route-contract",
            "ui-state-contract",
            "api-contract",
            "theme-token-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Functional Baseline"),
            GroupSpec("Phase1", "Route and API Contracts"),
            GroupSpec("Phase2", "Web Product Surface"),
            GroupSpec("Phase2", "UI State and Theme"),
            GroupSpec("Phase3", "Integration and Rollout"),
            GroupSpec("Phase4", "Validation and Release"),
        ],
    ),
    "backend-service": ArchetypeSpec(
        required_specs=[
            "capability-map",
            "api-contract",
            "data-contract",
            "integration-contract",
            "observability-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Service Baseline"),
            GroupSpec("Phase1", "API and Data Contracts"),
            GroupSpec("Phase1", "Dependency and Boundary Map"),
            GroupSpec("Phase2", "Execution Surface"),
            GroupSpec("Phase2", "Observability and Failure Contract"),
            GroupSpec("Phase3", "Stability Refactor", hard_predecessor=True),
            GroupSpec("Phase4", "Validation and Release"),
        ],
    ),
    "architecture-refactor": ArchetypeSpec(
        required_specs=[
            "architecture-contract",
            "dependency-rule-contract",
            "module-boundary-map",
            "behavior-parity-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Current Architecture Baseline"),
            GroupSpec("Phase1", "Target Architecture Contract"),
            GroupSpec("Phase2", "Dependency Direction Plan"),
            GroupSpec("Phase3", "Behavior Parity Validation", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "large-scale-refactor": ArchetypeSpec(
        required_specs=[
            "refactor-target-inventory",
            "dependency-graph",
            "behavior-parity-contract",
            "risk-map",
            "characterization-test-plan",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Refactor Target Inventory"),
            GroupSpec("Phase1", "Dependency Graph"),
            GroupSpec("Phase2", "Refactor Sequence"),
            GroupSpec("Phase3", "Characterization Tests", hard_predecessor=True),
            GroupSpec("Phase4", "Validation and Release"),
        ],
    ),
    "modularization": ArchetypeSpec(
        required_specs=[
            "module-map",
            "dependency-rule-contract",
            "public-boundary-contract",
            "integration-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Module Inventory"),
            GroupSpec("Phase1", "Dependency Rules"),
            GroupSpec("Phase2", "Boundary Extraction"),
            GroupSpec("Phase3", "Integration Validation", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "migration-modernization": ArchetypeSpec(
        required_specs=[
            "migration-map",
            "old-new-mapping",
            "compatibility-matrix",
            "rollback-plan",
            "parity-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Migration Baseline"),
            GroupSpec("Phase1", "Old New Mapping"),
            GroupSpec("Phase2", "Compatibility Matrix"),
            GroupSpec("Phase3", "Rollback and Cutover Plan", hard_predecessor=True),
            GroupSpec("Phase4", "Validation and Release"),
        ],
    ),
    "algorithm-engine": ArchetypeSpec(
        required_specs=[
            "algorithm-inventory",
            "input-output-contract",
            "benchmark-contract",
            "tolerance-contract",
            "failure-mode-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Problem and Dataset Baseline"),
            GroupSpec("Phase1", "Algorithm Inventory"),
            GroupSpec("Phase1", "Tolerance Contract"),
            GroupSpec("Phase2", "Implementation Plan"),
            GroupSpec("Phase3", "Benchmark and Failure Modes", hard_predecessor=True),
            GroupSpec("Phase4", "Validation and Release"),
        ],
    ),
    "rendering-engine": ArchetypeSpec(
        required_specs=[
            "rendering-pipeline-contract",
            "scene-graph-contract",
            "resource-lifecycle-contract",
            "performance-budget",
            "visual-regression-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Rendering Pipeline Baseline"),
            GroupSpec("Phase1", "Scene Graph Contract"),
            GroupSpec("Phase2", "Resource Lifecycle"),
            GroupSpec("Phase3", "Performance Budget", hard_predecessor=True),
            GroupSpec("Phase4", "Visual Regression Gate"),
        ],
    ),
    "realtime-runtime-pipeline": ArchetypeSpec(
        required_specs=[
            "runtime-loop-contract",
            "threading-contract",
            "resource-ownership-contract",
            "failure-recovery-contract",
            "performance-budget",
        ],
        groups=[
            GroupSpec("Phase1", "Runtime Loop Baseline"),
            GroupSpec("Phase1", "Threading and Ownership"),
            GroupSpec("Phase2", "Failure Recovery"),
            GroupSpec("Phase3", "Performance Budget", hard_predecessor=True),
            GroupSpec("Phase4", "Validation"),
        ],
    ),
    "integration-adapter": ArchetypeSpec(
        required_specs=[
            "integration-contract",
            "data-mapping-contract",
            "failure-matrix",
            "fallback-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Adapter Boundary"),
            GroupSpec("Phase1", "Data Mapping"),
            GroupSpec("Phase2", "Failure and Fallback"),
            GroupSpec("Phase3", "Integration Validation", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "library-sdk": ArchetypeSpec(
        required_specs=[
            "public-api-contract",
            "compatibility-policy",
            "versioning-policy",
            "deprecation-policy",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Public API Baseline"),
            GroupSpec("Phase1", "Compatibility Policy"),
            GroupSpec("Phase2", "Versioning and Deprecation"),
            GroupSpec("Phase3", "Consumer Validation", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "infra-build-release": ArchetypeSpec(
        required_specs=[
            "environment-contract",
            "build-contract",
            "deployment-contract",
            "rollback-trigger",
            "observability-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Environment Baseline"),
            GroupSpec("Phase1", "Build Contract"),
            GroupSpec("Phase2", "Deployment Contract"),
            GroupSpec("Phase3", "Rollback and Observability", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "test-validation-system": ArchetypeSpec(
        required_specs=[
            "test-inventory",
            "regression-matrix",
            "validation-dataset",
            "numeric-threshold",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Test Inventory"),
            GroupSpec("Phase1", "Validation Dataset"),
            GroupSpec("Phase2", "Regression Matrix"),
            GroupSpec("Phase3", "Numeric Thresholds", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "stabilization-hardening": ArchetypeSpec(
        required_specs=[
            "stability-issue-inventory",
            "failure-mode-matrix",
            "observability-contract",
            "regression-plan",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Stability Issue Inventory"),
            GroupSpec("Phase1", "Failure Mode Matrix"),
            GroupSpec("Phase2", "Observability"),
            GroupSpec("Phase3", "Regression Plan", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "performance-optimization": ArchetypeSpec(
        required_specs=[
            "performance-baseline",
            "profiling-report",
            "optimization-target-inventory",
            "benchmark-contract",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Performance Baseline"),
            GroupSpec("Phase1", "Profiling Report"),
            GroupSpec("Phase2", "Optimization Targets"),
            GroupSpec("Phase3", "Benchmark Contract", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "firmware-hardware": ArchetypeSpec(
        required_specs=[
            "hardware-interface-contract",
            "firmware-behavior-contract",
            "pin-map",
            "protocol-contract",
            "failure-mode-matrix",
        ],
        groups=[
            GroupSpec("Phase1", "Hardware Interface"),
            GroupSpec("Phase1", "Pin Map and Protocol"),
            GroupSpec("Phase2", "Firmware Behavior"),
            GroupSpec("Phase3", "Failure Modes", hard_predecessor=True),
            GroupSpec("Phase4", "Validation"),
        ],
    ),
    "ml-data-training-pipeline": ArchetypeSpec(
        required_specs=[
            "dataset-contract",
            "training-pipeline-contract",
            "experiment-contract",
            "evaluation-gate",
            "release-gate",
        ],
        groups=[
            GroupSpec("Phase1", "Dataset Contract"),
            GroupSpec("Phase1", "Training Pipeline"),
            GroupSpec("Phase2", "Experiment Contract"),
            GroupSpec("Phase3", "Evaluation Gate", hard_predecessor=True),
            GroupSpec("Phase4", "Release Gate"),
        ],
    ),
    "documentation-handoff-package": ArchetypeSpec(
        required_specs=[
            "source-of-truth-policy",
            "capability-map",
            "release-gate",
            "agent-handoff-index",
        ],
        groups=[
            GroupSpec("Phase1", "Source Of Truth Policy"),
            GroupSpec("Phase1", "Canonical Plan Contract"),
            GroupSpec("Phase2", "Handoff Index"),
            GroupSpec("Phase3", "Validation and Drift Review", hard_predecessor=True),
        ],
    ),
}

ARCHETYPE_ALIASES = {
    "ui-product": "application-product",
    "algorithm-rewrite": "algorithm-engine",
    "migration-only": "migration-modernization",
}

MODIFIERS: dict[str, list[str]] = {
    "no-behavior-change": ["behavior-parity-contract"],
    "strict-behavior-parity": ["behavior-parity-contract", "parity-contract"],
    "legacy-parity": ["old-new-mapping", "parity-contract", "compatibility-matrix"],
    "performance-critical": ["performance-budget", "benchmark-contract"],
    "realtime-critical": ["runtime-loop-contract", "performance-budget"],
    "rendering-heavy": ["rendering-pipeline-contract", "resource-lifecycle-contract", "visual-regression-gate"],
    "local-device-runtime": ["app-runtime-contract", "platform-lifecycle-contract", "local-storage-contract"],
    "hardware-integration": ["hardware-interface-contract", "pin-map", "protocol-contract"],
    "mesh-processing-heavy": ["algorithm-inventory", "mesh-ops-contract", "tolerance-contract", "visual-regression-gate", "gap-registry"],
    "gap-tracking": ["gap-registry"],
    "external-api": ["integration-contract", "failure-matrix", "fallback-contract"],
    "rollback-required": ["rollback-plan", "rollback-trigger"],
    "cross-session-handoff": ["source-of-truth-policy", "agent-handoff-index"],
    "public-api-sensitive": ["public-api-contract", "compatibility-policy", "versioning-policy", "deprecation-policy"],
    "data-sensitive": ["data-contract", "migration-map", "compatibility-matrix"],
    "security-sensitive": ["security-contract"],
}

release_blocking_specs_by_archetype: dict[str, list[str]] = {
    "application-product": ["capability-map", "app-runtime-contract", "platform-lifecycle-contract", "ui-state-contract"],
    "web-product": ["capability-map", "route-contract", "ui-state-contract", "api-contract"],
    "backend-service": ["api-contract", "data-contract", "observability-contract"],
    "architecture-refactor": ["architecture-contract", "dependency-rule-contract", "behavior-parity-contract"],
    "large-scale-refactor": ["refactor-target-inventory", "behavior-parity-contract", "characterization-test-plan"],
    "modularization": ["module-map", "dependency-rule-contract", "public-boundary-contract"],
    "migration-modernization": ["migration-map", "old-new-mapping", "compatibility-matrix", "rollback-plan", "parity-contract"],
    "algorithm-engine": ["algorithm-inventory", "input-output-contract", "benchmark-contract", "tolerance-contract"],
    "rendering-engine": ["rendering-pipeline-contract", "resource-lifecycle-contract", "performance-budget", "visual-regression-gate"],
    "realtime-runtime-pipeline": ["runtime-loop-contract", "threading-contract", "performance-budget"],
    "integration-adapter": ["integration-contract", "data-mapping-contract", "failure-matrix", "fallback-contract"],
    "library-sdk": ["public-api-contract", "compatibility-policy", "versioning-policy"],
    "infra-build-release": ["environment-contract", "build-contract", "deployment-contract", "rollback-trigger", "observability-gate"],
    "test-validation-system": ["test-inventory", "regression-matrix", "validation-dataset", "numeric-threshold"],
    "stabilization-hardening": ["stability-issue-inventory", "failure-mode-matrix", "observability-contract", "regression-plan"],
    "performance-optimization": ["performance-baseline", "profiling-report", "optimization-target-inventory", "benchmark-contract"],
    "firmware-hardware": ["hardware-interface-contract", "pin-map", "protocol-contract", "firmware-behavior-contract"],
    "ml-data-training-pipeline": ["dataset-contract", "training-pipeline-contract", "experiment-contract", "evaluation-gate"],
    "documentation-handoff-package": ["source-of-truth-policy", "capability-map", "agent-handoff-index"],
}

release_blocking_specs_by_modifier: dict[str, list[str]] = {
    "no-behavior-change": ["behavior-parity-contract"],
    "strict-behavior-parity": ["behavior-parity-contract", "parity-contract"],
    "legacy-parity": ["old-new-mapping", "parity-contract", "compatibility-matrix"],
    "performance-critical": ["performance-budget", "benchmark-contract"],
    "realtime-critical": ["runtime-loop-contract", "performance-budget"],
    "rendering-heavy": ["rendering-pipeline-contract", "resource-lifecycle-contract", "visual-regression-gate"],
    "local-device-runtime": ["app-runtime-contract", "platform-lifecycle-contract", "local-storage-contract"],
    "hardware-integration": ["hardware-interface-contract", "pin-map", "protocol-contract"],
    "mesh-processing-heavy": ["algorithm-inventory", "mesh-ops-contract", "tolerance-contract", "visual-regression-gate", "gap-registry"],
    "gap-tracking": ["gap-registry"],
    "external-api": ["integration-contract", "failure-matrix", "fallback-contract"],
    "rollback-required": ["rollback-plan", "rollback-trigger"],
    "cross-session-handoff": ["source-of-truth-policy", "agent-handoff-index"],
    "public-api-sensitive": ["public-api-contract", "compatibility-policy", "versioning-policy", "deprecation-policy"],
    "data-sensitive": ["data-contract", "migration-map", "compatibility-matrix"],
    "security-sensitive": ["security-contract"],
}


def canonical_archetype(name: str) -> str:
    return ARCHETYPE_ALIASES.get(name, name)


def required_specs_for(archetype: str, modifiers: list[str] | None = None) -> list[str]:
    canonical = canonical_archetype(archetype)
    specs: list[str] = []
    for suffix in ARCHETYPES[canonical].required_specs:
        if suffix not in specs:
            specs.append(suffix)
    for modifier in modifiers or []:
        for suffix in MODIFIERS.get(modifier, []):
            if suffix not in specs:
                specs.append(suffix)
    for suffix in UNIVERSAL_REQUIRED_SPECS:
        if suffix not in specs:
            specs.append(suffix)
    return specs


def release_blocking_specs_for(archetype: str, modifiers: list[str] | None = None) -> list[str]:
    canonical = canonical_archetype(archetype)
    required_specs = set(required_specs_for(canonical, modifiers))
    specs: list[str] = []
    for suffix in release_blocking_specs_by_archetype.get(canonical, []):
        if suffix in required_specs and suffix not in specs:
            specs.append(suffix)
    for modifier in modifiers or []:
        for suffix in release_blocking_specs_by_modifier.get(modifier, []):
            if suffix in required_specs and suffix not in specs:
                specs.append(suffix)
    for suffix in ["release-gate"]:
        if suffix in required_specs and suffix not in specs:
            specs.append(suffix)
    return specs


def slugify_title(title: str) -> str:
    out = []
    for ch in title.lower():
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "group"
