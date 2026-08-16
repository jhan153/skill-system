from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


def find_bundle_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "source" / "skills").is_dir():
            return parent
        if (parent / ".codex" / "skills").is_dir():
            return parent
    raise RuntimeError("could not locate Skill System bundle root")


ROOT = find_bundle_root()
SOURCE = ROOT / "source"
HOST_PRODUCT_PATTERN = re.compile(r"\b(?:Codex|Claude|ChatGPT)\b", re.IGNORECASE)


def canonical(relative: str) -> Path:
    source_path = SOURCE / relative
    if source_path.is_file():
        return source_path
    runtime_path = ROOT / ".codex" / relative.removeprefix("platform/codex/")
    if runtime_path.is_file():
        return runtime_path
    raise FileNotFoundError(relative)


class SkillInstructionQualityTests(unittest.TestCase):
    def test_current_skill_inventory_and_metadata_surface_are_bounded(self) -> None:
        skills = sorted((SOURCE / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills)
        registry = canonical("shared/docs/skill_registry.md").read_text(encoding="utf-8")
        for skill in skills:
            self.assertIn(f"`{skill.parent.name}`", registry)
            agent = skill.parent / "agents" / "openai.yaml"
            self.assertTrue(agent.is_file(), skill.parent.name)
            for line in agent.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("short_description:"):
                    value = line.split(":", 1)[1].strip().strip('"')
                    self.assertLessEqual(len(value), 64, skill.parent.name)

    def test_redefined_skill_ids_use_established_primary_families(self) -> None:
        expected_families = {
            "management-project-context-checkpoint": "management",
            "management-project-context": "management",
            "analysis-llm-wiki-context": "analysis",
            "analysis-loop-readiness": "analysis",
            "plan-task-handoff": "planning",
            "plan-decision-map": "planning",
            "plan-stakeholder-questionnaire": "planning",
            "workflow-loop-runner": "workflow",
            "management-knowledge-base-record": "management",
        }
        retired_ids = {
            "skill-system-repo-adapter",
            "project-context-checkpoint",
            "project-context-init",
            "project-context-update",
            "llm-wiki-context",
            "loop-readiness-router",
            "loop-verifier-registry",
            "coordination-handoff",
            "wayfinder",
            "wait-what",
            "to-questionnaire",
            "workflow-skill-system-integration",
            "workflow-evaluation-maintenance",
            "workflow-explanation-repair",
            "search-router",
            "plan-loop-verification",
            "knowledge-algorithm-record",
            "knowledge-architecture-record",
            "knowledge-code-review-record",
            "knowledge-design-record",
            "knowledge-domain-record",
            "analysis-router",
            "research-router",
            "report-diff",
            "workflow-comment-maintenance",
            "plan-spec-curator",
            "memory-bank-correction-capture",
            "knowledge-plan-sync",
            "workflow-project-context-init",
            "workflow-project-context-update",
            "workflow-project-context",
            "workflow-project-context-checkpoint",
            "knowledge-base-record",
            "knowledge-base-init",
            "knowledge-base-read",
            "knowledge-base-update",
            "knowledge-base-maintenance",
            "memory-bank-harness",
            "memory-bank-init",
            "memory-bank-update",
            "memory-bank-maintenance",
            "analysis-codebase",
            "analysis-codebase-design",
            "kanboard-plan-rollout",
            "kanboard-plan-ops",
        }
        registry = canonical("shared/docs/skill_registry.md").read_text(encoding="utf-8")
        registry_rows = registry.split("## Registry", 1)[1].split("## Group Alias Map", 1)[0]
        alias_map = registry.split("## Group Alias Map", 1)[1].split(
            "## Legacy Skill Alias Migration", 1
        )[0]

        for skill_id, family in expected_families.items():
            self.assertTrue((SOURCE / "skills" / skill_id / "SKILL.md").is_file(), skill_id)
            row = next(
                line for line in registry_rows.splitlines() if line.startswith(f"| `{skill_id}` |")
            )
            self.assertEqual(row.rsplit("|", 2)[1].strip(), f"`{family}`", skill_id)

        for skill_id in retired_ids:
            self.assertFalse((SOURCE / "skills" / skill_id).exists(), skill_id)
        for retired_family in ("coordination", "loop", "skill_system", "knowledge", "memory"):
            self.assertNotIn(f"| `{retired_family}` |", alias_map)
        self.assertIn("| `evaluation` |", alias_map)

    def test_skill_frontmatter_metadata_is_complete_and_host_neutral(self) -> None:
        for skill in sorted((SOURCE / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill.parent.name):
                text = skill.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), skill.parent.name)
                parts = text.split("---", 2)
                self.assertEqual(len(parts), 3, skill.parent.name)
                metadata = yaml.safe_load(parts[1])
                self.assertIsInstance(metadata, dict, skill.parent.name)
                if not isinstance(metadata, dict):
                    continue
                self.assertEqual(metadata.get("name"), skill.parent.name)
                description = metadata.get("description")
                self.assertIsInstance(description, str, skill.parent.name)
                if not isinstance(description, str):
                    continue
                self.assertTrue(description.strip(), skill.parent.name)
                self.assertIsNone(
                    HOST_PRODUCT_PATTERN.search(description),
                    f"{skill.parent.name}: frontmatter description must be host-neutral",
                )

    def test_global_agents_stays_thin_and_delegates_routing(self) -> None:
        text = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 850)
        self.assertNotIn("## Skill Alias Interpretation", text)
        self.assertNotIn("### Loop Readiness Gate", text)
        self.assertIn("$CODEX_HOME/context-routing.md", text)
        self.assertNotIn("Read `.codex/context-routing.md`", text)
        self.assertIn("ambiguous non-trivial routing", text)
        self.assertNotIn("When routing is relevant", text)
        self.assertIn("Route explicit `/goal`", text)
        self.assertIn("unknown or stale explicit skill alias", text)

    def test_global_agents_result_labels_are_consistent(self) -> None:
        text = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        status_line = next(
            line for line in text.splitlines() if line.startswith("- Use only these task-result")
        )
        self.assertEqual(
            set(re.findall(r"`([^`]+)`", status_line)),
            {"agent-verified", "user-verification-needed", "unverified", "blocked"},
        )
        self.assertNotIn("`analysis-only`", text)
        self.assertIn("Analysis-only describes work scope, not a result label", text)
        self.assertIn("task-level result label", text)
        self.assertIn("a label never replaces condition evidence", text)
        self.assertIn("a user-only check", status_line)
        self.assertIn("unavailable evidence without blocked work", status_line)

    def test_global_agents_requires_pre_answer_depth_gate(self) -> None:
        text = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("intended outcome before drafting", text)
        self.assertIn("## Pre-Answer Depth Gate", text)
        self.assertIn("constrain presentation, not investigation depth", text)
        self.assertIn("Speed, brevity, or immediately usable output", text)
        self.assertIn("applies without a router or specialist", text)
        self.assertIn("Minimal change shapes solutions only after the behavior boundary", text)
        self.assertIn("smallest complete behavior", text)
        self.assertIn("inspect source/runtime", text)
        self.assertIn("one disconfirming case", text)
        self.assertIn("invalidates the working frame", text)
        self.assertIn("reconstruct the positive objective", text)
        self.assertIn("partition topology", text)
        self.assertIn("Do not finalize until", text)
        self.assertIn("evidence passes add none", text)
        self.assertIn("up to three passes", text)
        self.assertIn("distinct material hypotheses", text)
        self.assertIn("owner retains scope, synthesis, and final judgment", text.lower())

    def test_direct_analysis_selection_treats_brevity_as_output_shape(self) -> None:
        routing = canonical("platform/codex/context-routing.md").read_text(encoding="utf-8")
        self.assertIn("current owner selects one specialist directly", routing)
        self.assertIn("### Technical analysis", routing)
        self.assertIn("Requested brevity", routing)
        self.assertIn("does not change the task owner", routing)

    def test_routing_docs_do_not_own_eval_payloads(self) -> None:
        routing = canonical("platform/codex/context-routing.md").read_text(encoding="utf-8")
        research = canonical("platform/codex/research-routing.md").read_text(encoding="utf-8")
        self.assertNotIn(".codex/eval/", routing)
        self.assertNotIn("routing_smoke_tests:", routing)
        self.assertIn(".codex/eval/research_regression_cases.yaml", research)
        self.assertNotIn("research_route_smoke_tests:", research)

    def test_family_entry_routing_has_one_shared_registry_owner(self) -> None:
        registry = canonical("shared/docs/skill_registry.md").read_text(encoding="utf-8")
        claude_routing = canonical("platform/claude/context-routing.md").read_text(encoding="utf-8")
        alias_map = registry.split("## Group Alias Map", 1)[1].split(
            "## Legacy Skill Alias Migration", 1
        )[0]
        self.assertIn("| family | display name | entry skill (Phase A) | aliases |", alias_map)
        self.assertIn("one shared family-selection owner", alias_map)
        for required_entry in (
            "report-lifecycle-artifacts",
            "analysis-bug",
            "analysis-algorithm",
            "plan-requirements-discovery",
            "plan-requirements-brief",
        ):
            self.assertIn(f"`{required_entry}`", alias_map)
        search_lane = next(
            line
            for line in registry.splitlines()
            if line.startswith("- `search` secondary-tag (evidence lane) candidates:")
        )
        self.assertIn("`management-knowledge-base-read`", search_lane)
        self.assertIn("`analysis-llm-wiki-context`", search_lane)
        self.assertIn("Do not maintain a second family-entry table here", claude_routing)
        self.assertNotIn("Family entry routing (Phase A):", claude_routing)

    def test_legacy_skill_aliases_map_to_current_owners_without_stub_packages(self) -> None:
        expected = {
            "coordination-brief": ("plan-task-handoff", "brief"),
            "coordination-multi-agent": ("plan-task-handoff", "multi_agent"),
            "report-artifact-inventory": ("plan-task-handoff", "artifact_inventory"),
            "design-mobile-screen": ("design-frontend", "mobile"),
            "design-dashboard": ("design-frontend", "dashboard"),
            "design-section-web": ("design-frontend", "section-web"),
            "create-skill-pack": ("task implementation owner", "direct_repository_skill_change"),
        }
        registry = canonical("shared/docs/skill_registry.md").read_text(encoding="utf-8")
        routing = canonical("platform/codex/context-routing.md").read_text(encoding="utf-8")
        case_data = yaml.safe_load(
            canonical("shared/eval/routing_cases.yaml").read_text(encoding="utf-8")
        )
        cases = case_data["cases"]

        for legacy, (owner, mode) in expected.items():
            row = next(
                line for line in registry.splitlines() if line.startswith(f"| `{legacy}` |")
            )
            if owner == "task implementation owner":
                self.assertIn(owner, row)
            else:
                self.assertIn(f"`{owner}`", row)
            self.assertIn(f"`{mode}`", row)
            self.assertFalse((SOURCE / "skills" / legacy).exists(), legacy)
            alias_case = next(
                case
                for case in cases
                if case.get("legacy_alias") == legacy and not case.get("direct_invocation")
            )
            self.assertEqual(alias_case.get("expected_mode"), mode)
            if owner == "task implementation owner":
                self.assertEqual(alias_case.get("expected_route_class"), "direct_task_owner")
                self.assertFalse(alias_case.get("expected_supporting_skills", []))
            else:
                self.assertEqual(alias_case.get("expected_primary_skill"), owner)

        direct_case = next(case for case in cases if case.get("direct_invocation"))
        self.assertEqual(
            direct_case.get("expected_route_class"), "legacy_direct_invocation_unavailable"
        )
        self.assertIn("model-level compatibility", registry)
        self.assertIn("Direct slash/plugin invocation", registry)
        self.assertIn("exact path supplied by the user", routing)
        self.assertIn("Do not scan unrelated home directories", routing)
        self.assertNotIn("`coordination-*`", routing)

    def test_handoff_propagates_selected_skills_without_guessing(self) -> None:
        handoff = canonical("skills/plan-task-handoff/SKILL.md").read_text(
            encoding="utf-8"
        )
        schema = canonical(
            "skills/plan-task-handoff/references/handoff-schemas.md"
        ).read_text(encoding="utf-8")
        team_patterns = canonical("shared/docs/team_patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("`selected_skills`", handoff)
        self.assertIn("instead of asking the worker to rediscover", handoff)
        self.assertIn("never invent an adjacent skill ID", handoff)
        self.assertIn("selected_skills: []", schema)
        self.assertIn("normal implicit routing", schema)
        self.assertIn("selected_skills: []", team_patterns)
        self.assertIn("repeated in the worker instruction", team_patterns)

    def test_research_routing_disambiguates_search_and_development(self) -> None:
        text = canonical("platform/codex/research-routing.md").read_text(encoding="utf-8")
        self.assertIn("latest papers/evidence/citations", text)
        self.assertIn("one claim needs independent evidence lanes", text)
        self.assertIn("current task owner asks for the missing deliverable", text)
        self.assertIn("Concrete implementation of an already selected method remains development work", text)
        self.assertIn("## Route Matrix", text)

    def test_long_term_plan_uses_claims_and_behavior_oracles(self) -> None:
        skill = canonical("skills/plan-long-term-package/SKILL.md").read_text(encoding="utf-8")
        core = canonical(
            "skills/plan-long-term-package/references/package-core-invariants.md"
        ).read_text(encoding="utf-8")
        self.assertIn("claim ledger", skill.lower())
        self.assertIn("behavior oracle", skill.lower())
        self.assertIn("cannot pass logic", core)

    def test_plan_runner_separates_batch_phase_and_plan_completion(self) -> None:
        text = canonical("skills/workflow-plan-runner/SKILL.md").read_text(encoding="utf-8")
        for state in ("batch_complete", "phase_complete", "plan_complete"):
            self.assertIn(state, text)
        self.assertIn("Never infer `phase_complete` or `plan_complete`", text)
        self.assertIn("do not stop after the first passing batch", text)

    def test_qualitative_default_is_compact_and_detailed_refs_are_conditional(self) -> None:
        text = canonical("skills/report-qualitative/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("zero to three items", text)
        self.assertIn("only in `FullOrScored` mode", text)
        self.assertIn("do not reward static presence", text)

    def test_recovery_protocol_keeps_owner_one_hypothesis_and_original_signal(self) -> None:
        text = canonical("shared/docs/recovery_protocol.md").read_text(encoding="utf-8")
        self.assertIn("exactly one falsifiable hypothesis", text.lower())
        self.assertIn("original success check", text)
        self.assertIn("After two `unchanged` recovery actions", text)
        self.assertIn("does not create another workflow owner", text)

    def test_global_review_and_implementation_preserve_evidence_and_minimality(self) -> None:
        agents = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        rigor = canonical("skills/workflow-rigor/SKILL.md").read_text(encoding="utf-8")
        implementation = canonical("skills/workflow-implementation/SKILL.md").read_text(
            encoding="utf-8"
        )
        minimal = canonical("skills/workflow-minimal-implementation/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("separate read-only review", agents)
        self.assertIn("Contract/Spec", agents)
        self.assertIn("Repository/Constraints", agents)
        self.assertIn("lite", rigor)
        self.assertIn("standard", rigor)
        self.assertIn("strict", rigor)
        self.assertIn("do not re-plan or reimplement", rigor)
        self.assertIn("workflow-minimal-implementation", implementation)
        self.assertIn("complete required behavior boundary", implementation)
        self.assertIn("Classify the change as local only", implementation)
        self.assertIn("smallest complete behavior", implementation)
        self.assertIn("actual dependencies, overlapping writes, and unresolved decisions", implementation)
        self.assertIn("Stop at the first rung", minimal)
        self.assertIn("Future reuse is not justification", minimal)
        self.assertIn("role: execution_modifier", minimal)
        self.assertIn("never use the minimum ladder to narrow evidence gathering", minimal)
        self.assertIn("primary owner reconstructs it", minimal)

    def test_loop_quality_conditions_do_not_pass_from_report_presence(self) -> None:
        design = canonical(
            "skills/plan-loop-term/references/design-loop-contract.md"
        ).read_text(encoding="utf-8")
        catalog = canonical(
            "skills/plan-loop-term/references/verifier-catalog.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Use `artifact_exists` only when the condition itself", design)
        self.assertIn("cannot prove framing, fidelity", design)
        self.assertIn("Artifact existence proves only", catalog)
        self.assertIn("semantic `command_exit`/`manual_check`/`diff_scope` pass is fail-closed", catalog)

    def test_algorithm_and_bug_depth_are_proportional(self) -> None:
        algorithm = canonical("skills/analysis-algorithm/SKILL.md").read_text(encoding="utf-8")
        bug = canonical("skills/analysis-bug/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("use one direct recommendation", algorithm)
        self.assertIn("do not manufacture extra candidates", algorithm)
        self.assertNotIn("## Effectiveness Metrics", algorithm)
        self.assertIn("do not fabricate three hypotheses", bug)
        self.assertIn("Static inspection can establish possible paths", bug)
        self.assertNotIn("## Output Templates", bug)

    def test_research_skills_keep_distinct_quality_oracles(self) -> None:
        checks = {
            "research-literature-synthesis": ["do not use paper count as consensus", "field gap from a coverage gap"],
            "research-literature-ideation": ["observed gap", "selection is omitted"],
            "research-hypothesis-planning": ["cheapest Stage-0 discriminator", "two rival explanations"],
            "research-experiment-blueprint": ["experimental unit", "smallest core experiment"],
            "research-experiment-scaffold": ["thinnest end-to-end synthetic path", "Do not create empty directories"],
            "research-statistical-analysis": ["analysis units", "pseudoreplication"],
            "research-manuscript-writing": ["only actual execution/result artifacts support Results", "separate list"],
            "research-peer-review": ["exact section/claim/table/figure anchor", "ordered by scientific consequence"],
        }
        for skill_id, required in checks.items():
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            for phrase in required:
                self.assertIn(phrase.lower(), text.lower(), skill_id)

    def test_evidence_search_does_not_reward_majority_or_confirmation(self) -> None:
        deep = canonical("skills/search-deep-evidence/SKILL.md").read_text(encoding="utf-8")
        paper = canonical("skills/search-paper-evidence/SKILL.md").read_text(encoding="utf-8")
        method = canonical("skills/search-deep-evidence/references/deep-evidence-method.md").read_text(encoding="utf-8")
        self.assertIn("no majority vote decides truth", deep)
        self.assertIn("Source existence does not verify a claim", deep)
        self.assertIn("Source identity is not claim verification", method)
        self.assertIn("acquisition_status", paper)
        self.assertIn("claim_relation", paper)
        self.assertNotIn("Kill the claim when a majority", method)

    def test_memory_writers_share_transaction_and_no_destructive_reinit(self) -> None:
        contract = canonical("shared/docs/memory_mutation_contract.md").read_text(encoding="utf-8")
        self.assertIn("Never report success from a partial", contract)
        self.assertIn("retries reuse it", contract)
        for skill_id in (
            "management-memory-bank-init",
            "management-memory-bank-update",
            "management-memory-bank-maintenance",
        ):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("memory_mutation_contract.md", text, skill_id)
        init = canonical("skills/management-memory-bank-init/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never overwrite active history", init)

    def test_memory_context_uses_declared_narrow_current_slice(self) -> None:
        memory = canonical("skills/management-memory-bank-harness/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("project-context.yaml", memory)
        self.assertIn("active", memory)
        self.assertIn("candidate", memory)
        self.assertIn("deprecated", memory)
        self.assertIn("full `current.md`", memory)

    def test_knowledge_records_keep_temporal_relational_provenance_without_scores(self) -> None:
        contract = canonical("shared/docs/knowledge_record_contract.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "relations: []",
            "observations: []",
            "provenance_root",
            "revisions: []",
            "adopted_snapshot",
            "Overlap Classification",
            "distinct verified provenance roots",
            "one typed edge at a time",
            "Source identity, source existence, or an explicit report alone does not verify",
            "Terms found only in an unverified observation do not silently become current search anchors",
        ):
            self.assertIn(phrase, contract)
        self.assertIn("never persist one scalar score", contract)
        self.assertIn("Similarity is a candidate-discovery signal, not merge authority", contract)
        self.assertFalse((SOURCE / "shared/schemas/knowledge/context-pack.schema.json").exists())

        writers = (
            "management-knowledge-base-record",
            "management-knowledge-base-init",
            "management-knowledge-base-maintenance",
            "management-knowledge-base-update",
            "management-project-context-checkpoint",
        )
        for skill_id in writers:
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("knowledge_record_contract.md", text, skill_id)

        update = canonical("skills/management-knowledge-base-update/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("amend|observe|reverify|supersede|deprecate|relink", update)
        self.assertIn("Shared provenance roots remain dependent", update)
        self.assertIn("not merely that its source exists", update)
        maintenance = canonical("skills/management-knowledge-base-maintenance/SKILL.md").read_text(
            encoding="utf-8"
        )
        for operation in ("relation-check", "history-check", "overlap-check", "recurrence-report"):
            self.assertIn(operation, maintenance)
        read = canonical("skills/management-knowledge-base-read/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("source --relation--> target", read)
        self.assertIn("never load the whole store as a graph dump", read)
        contract = canonical("shared/docs/knowledge_record_contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`knowledge_root` and `knowledge_index`", contract)
        self.assertIn("The resolved root may be anywhere", contract)
        self.assertIn("records both bound values explicitly", contract)
        for skill_id in (
            "management-knowledge-base-record",
            "management-knowledge-base-init",
            "management-knowledge-base-read",
            "management-knowledge-base-update",
            "management-knowledge-base-maintenance",
        ):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("`knowledge_root`", text, skill_id)
            self.assertIn("`knowledge_index`", text, skill_id)

        init = canonical("skills/management-knowledge-base-init/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("materializes the bound index value", init)

        manifest = canonical("shared/docs/project_context_manifest.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("knowledge_root  :=", manifest)
        self.assertIn("knowledge_index :=", manifest)
        self.assertIn("resolves outside `knowledge_root`", manifest)

        resolver = canonical("runtime/go/internal/projectcontext/resolver.go").read_text(
            encoding="utf-8"
        )
        self.assertIn('json:"index_path,omitempty"', resolver)
        self.assertIn('json:"index_exists,omitempty"', resolver)

    def test_project_context_bootstrap_and_doctor_remain_explicit(self) -> None:
        skill = canonical("skills/management-project-context/SKILL.md").read_text(encoding="utf-8")
        modes = canonical("skills/management-project-context/references/manifest-modes.md").read_text(
            encoding="utf-8"
        )
        for mode in ("`manifest-init`", "`doctor`", "`bootstrap`"):
            self.assertIn(mode, skill)
        self.assertIn("one exact transaction decision", skill)
        self.assertIn("all or a stated subset", modes)
        self.assertIn("Do not pre-write the same section through two owners", modes)
        self.assertIn("`initialized-empty`", modes)
        self.assertIn("both `knowledge_root` and `knowledge_index`", skill)
        self.assertIn("ordinary work", skill)
        self.assertIn("Do not scan elsewhere", skill)

    def test_workflow_topology_and_delivery_shapes_do_not_orchestrate(self) -> None:
        registry = canonical("shared/docs/skill_registry.md").read_text(encoding="utf-8")
        self.assertNotIn("## Main Flow Navigator", registry)
        horizon = canonical("shared/docs/work_horizon_model.md").read_text(encoding="utf-8")
        planning = canonical("shared/docs/planning_state_model.md").read_text(encoding="utf-8")
        self.assertIn("## Question Ownership And Non-Executing Topology", horizon)
        self.assertIn("This is explanatory topology, not an orchestrator", horizon)
        self.assertIn("a read-only “what next?” request receives a recommendation", horizon)
        self.assertIn("stays outside this state machine", planning)
        self.assertIn("does not need a synthetic", planning)
        self.assertIn("`deactivate_scratch_for_direct_work`", planning)
        self.assertIn("it never deletes a file", planning)
        self.assertIn("cannot turn a required `fail`, `unverified`, batch, or exit gate", planning)

        slices = canonical("shared/docs/delivery_slice_contract.md").read_text(
            encoding="utf-8"
        )
        for shape in ("`single_batch`", "`vertical_slice`", "`migration_sequence`", "`evidence_unit`"):
            self.assertIn(shape, slices)
        self.assertIn("stop without loading, recording, or applying", slices)
        self.assertIn("Thin Observable Path", slices)
        self.assertIn("expand -> migrate -> contract", slices)
        self.assertIn("Do not interpret “vertical” as touching every architectural layer", slices)
        self.assertIn("does not mandate TDD", slices)
        for skill_id in (
            "plan-short-term-docs",
            "plan-long-term-package",
            "workflow-plan-runner",
            "workflow-implementation",
        ):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("delivery_slice_contract.md", text, skill_id)
            self.assertIn("non-feature decomposition", text, skill_id)

    def test_understanding_skills_are_bounded_and_reanchor_evidence(self) -> None:
        explainer = canonical("skills/report-implementation-explainer/SKILL.md").read_text(
            encoding="utf-8"
        )
        discovery = canonical("skills/plan-behavior-discovery/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertLessEqual(len(explainer.split()), 800)
        self.assertLessEqual(len(discovery.split()), 800)
        self.assertIn("derived index, never evidence", explainer)
        self.assertIn("navigation aid, not current-behavior evidence", discovery)
        self.assertIn("Re-open its cited production source/runtime/test anchors", discovery)
        self.assertIn("For irreversible/high-risk choices", discovery)
        self.assertIn("For reversible low-risk interaction choices", discovery)

    def test_global_review_axes_preserve_epistemic_independence(self) -> None:
        agents = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        rigor = canonical("skills/workflow-rigor/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("separate read-only review", agents)
        self.assertIn("`Contract/Spec`", agents)
        self.assertIn("`Repository/Constraints`", agents)
        self.assertIn("maker-authored implementation and checks", agents)
        self.assertIn("## Review Axes And Independence", rigor)
        self.assertIn("`Contract/Spec`", rigor)
        self.assertIn("`Repository/Constraints`", rigor)
        self.assertIn("separate independent read-only review", rigor)
        self.assertIn("do not reveal the intended verdict", rigor)
        self.assertIn("do not call the maker's second pass independent", rigor)
        self.assertIn("same mistaken interpretation can pass", rigor)
        self.assertIn("attach no rigor mode", rigor)
        self.assertIn("only when the accepted contract names review as an exit gate", rigor)
        implementation = canonical("skills/workflow-implementation/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("depends mainly on code and checks produced by the same agent", implementation)

    def test_support_and_design_outputs_are_not_forced_on_simple_tasks(self) -> None:
        ledger = canonical("skills/workflow-task-ledger/SKILL.md").read_text(encoding="utf-8")
        validation = canonical("skills/workflow-validation/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("do not create a ledger merely because", ledger)
        self.assertIn("ordinary focused checks stay with the primary owner", validation)
        for skill_id in ("design-layout-translator", "design-ui-decomposer"):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("Include at least three negative route checks", text)
            self.assertIn("omit empty", text.lower())

    def test_design_family_governance_has_behavior_cases_and_fail_closed_boundaries(self) -> None:
        frontend = canonical("skills/design-frontend/SKILL.md").read_text(encoding="utf-8")
        family = canonical(
            "skills/design-frontend/references/product-family-profile.md"
        ).read_text(encoding="utf-8")
        ux = canonical(
            "skills/design-frontend/references/ux-pattern-decision-guide.md"
        ).read_text(encoding="utf-8")
        guardrails = canonical(
            "skills/design-frontend/references/implementation-guardrails.md"
        ).read_text(encoding="utf-8")
        mapper = canonical("skills/design-component-mapper/SKILL.md").read_text(encoding="utf-8")
        visual = canonical("skills/design-visual-regression/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("resolve governance", frontend)
        self.assertIn("app-surface import/use evidence", frontend)
        self.assertIn("Do not invent a profile", frontend)
        self.assertIn("without a catalog", frontend)
        self.assertIn("task-bearing interactive route/screen", frontend)
        self.assertIn("governed sources to consume", guardrails)
        self.assertIn("Never fake persistence", guardrails)
        self.assertIn("A mutable path alone is not a stable claim", family)
        self.assertIn("Never claim “100% compliant”", family)
        for fallback_policy in ("approved_match_required", "native_when_unmapped", "explicit_exception_only"):
            self.assertIn(fallback_policy, family)
        self.assertIn("critical success path", ux)
        self.assertIn("Do not fill them with plausible product assumptions", ux)
        self.assertIn("Semantic HTML/native primitives", mapper)
        self.assertIn("export inventory alone cannot pass reuse", mapper)
        self.assertIn("Keep the verdicts separate", visual)
        self.assertIn("Do not apply full-screen pixel thresholds between unrelated screens", visual)
        self.assertIn("user-verification-needed", visual)

        data = yaml.safe_load(
            canonical("shared/eval/design_usage_cases.yaml").read_text(encoding="utf-8")
        )
        cases = {case["case_id"]: case for case in data["cases"]}
        expected_ids = {f"design-{number:03d}" for number in range(30, 39)}
        self.assertTrue(expected_ids.issubset(cases))
        required_evidence_types = {
            "design-030": {"command_exit", "component_reuse_report", "target_visual_comparison", "family_visual_comparison", "critical_path", "qualitative_review"},
            "design-031": {"command_exit", "component_reuse_report", "source_conflict_record", "qualitative_review"},
            "design-032": {"component_reuse_report", "fallback_policy_evidence", "qualitative_review"},
            "design-033": {"component_reuse_report", "source_scope_evidence", "qualitative_review"},
            "design-034": {"command_exit", "ux_pattern_decision", "critical_path", "qualitative_review"},
            "design-035": {"target_visual_comparison", "family_visual_comparison", "visual_lane_report", "qualitative_review"},
            "design-036": {"command_exit", "target_visual_comparison", "qualitative_review"},
            "design-037": {"command_exit", "governance_source_digest", "token_gap_report", "qualitative_review"},
            "design-038": {"integration_boundary_review", "critical_path", "qualitative_review"},
        }
        for case_id in expected_ids:
            case = cases[case_id]
            self.assertEqual(case.get("schema_version"), 2, case_id)
            self.assertEqual(case.get("required_eval_mode"), "host-assisted", case_id)
            self.assertTrue(case.get("expected_behaviors"), case_id)
            self.assertTrue(case.get("forbidden_behaviors"), case_id)
            self.assertTrue(case.get("required_evidence"), case_id)
            observed_types = {item.get("type") for item in case["required_evidence"]}
            self.assertTrue(required_evidence_types[case_id].issubset(observed_types), case_id)
            for evidence in case["required_evidence"]:
                if evidence.get("type") not in {"route_match", "qualitative_review"}:
                    self.assertIs(evidence.get("artifact_bound"), True, (case_id, evidence))
                if evidence.get("type") == "command_exit":
                    self.assertIs(evidence.get("declared_command"), True, (case_id, evidence))


if __name__ == "__main__":
    unittest.main()
