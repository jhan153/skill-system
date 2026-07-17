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
        self.assertIn("investigation depth and answer length separately", text)
        self.assertIn("This gate applies even if no router or specialist activates", text)
        self.assertIn("direct source or runtime paths", text)
        self.assertIn("counterexample or disconfirming observation", text)
        self.assertIn("Do not finalize until", text)
        self.assertIn("evidence passes do not add owners", text)
        self.assertIn("up to three passes", text)
        self.assertIn("distinct hypotheses with material consequences", text)
        self.assertIn("owner retains scope, synthesis, and final judgment", text.lower())

    def test_analysis_router_treats_brevity_as_output_shape(self) -> None:
        router = canonical("skills/analysis-router/SKILL.md").read_text(encoding="utf-8")
        metadata = canonical("skills/analysis-router/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("requested brevity or conclusion-first formatting", router)
        self.assertNotIn("needs only a quick answer", router)
        self.assertIn("Treat requested brevity as output shape, not evidence scope", metadata)

    def test_routing_docs_do_not_own_eval_payloads(self) -> None:
        routing = canonical("platform/codex/context-routing.md").read_text(encoding="utf-8")
        research = canonical("platform/codex/research-routing.md").read_text(encoding="utf-8")
        self.assertNotIn(".codex/eval/", routing)
        self.assertNotIn("routing_smoke_tests:", routing)
        self.assertIn(".codex/eval/research_regression_cases.yaml", research)
        self.assertNotIn("research_route_smoke_tests:", research)

    def test_legacy_skill_aliases_map_to_current_owners_without_stub_packages(self) -> None:
        expected = {
            "coordination-brief": ("coordination-handoff", "brief"),
            "coordination-multi-agent": ("coordination-handoff", "multi_agent"),
            "report-artifact-inventory": ("coordination-handoff", "artifact_inventory"),
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
                self.assertIn(
                    "skill-system-repo-adapter", alias_case.get("expected_supporting_skills", [])
                )
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

    def test_research_router_disambiguates_search_and_development(self) -> None:
        text = canonical("skills/research-router/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Explicit paper-only acquisition", text)
        self.assertIn("lane-ambiguous evidence search belongs to `search-router`", text)
        self.assertIn("does not turn a concrete development request into research", text)
        self.assertIn("## Stage Decision", text)

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

    def test_recovery_keeps_one_hypothesis_and_original_signal(self) -> None:
        text = canonical("skills/workflow-recovery/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("exactly one active hypothesis", text.lower())
        self.assertIn("original success check", text)
        self.assertIn("If `unchanged` occurs twice", text)

    def test_execution_modifiers_own_only_their_distinctive_delta(self) -> None:
        rigor = canonical("skills/workflow-rigor/SKILL.md").read_text(encoding="utf-8")
        minimal = canonical(
            "skills/workflow-minimal-implementation/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("lite", rigor)
        self.assertIn("standard", rigor)
        self.assertIn("strict", rigor)
        self.assertIn("do not re-plan or reimplement", rigor)
        self.assertIn("Stop at the first rung", minimal)
        self.assertIn("only where a real complexity choice exists", minimal)
        self.assertIn("No material minimality cut.", minimal)
        self.assertIn("not a correctness or release verdict", minimal)

    def test_loop_quality_conditions_do_not_pass_from_report_presence(self) -> None:
        design = canonical(
            "skills/plan-loop-term/references/design-loop-contract.md"
        ).read_text(encoding="utf-8")
        catalog = canonical(
            "skills/loop-verifier-registry/references/verifier-catalog.md"
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
            "memory-bank-init",
            "memory-bank-update",
            "memory-bank-correction-capture",
            "memory-bank-maintenance",
        ):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("memory_mutation_contract.md", text, skill_id)
        init = canonical("skills/memory-bank-init/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never overwrite active history", init)

    def test_memory_context_uses_declared_narrow_current_slice(self) -> None:
        memory = canonical("skills/memory-bank-harness/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("project-context.yaml", memory)
        self.assertIn("active", memory)
        self.assertIn("candidate", memory)
        self.assertIn("deprecated", memory)
        self.assertIn("full `current.md`", memory)

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
        mapper = canonical("skills/design-component-mapper/SKILL.md").read_text(encoding="utf-8")
        visual = canonical("skills/design-visual-regression/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("resolve governance", frontend)
        self.assertIn("app-surface import/use evidence", frontend)
        self.assertIn("Do not invent a profile", frontend)
        self.assertIn("without a catalog", frontend)
        self.assertIn("task-bearing interactive route/screen", frontend)
        self.assertIn("governance sources, not convenient page-style write targets", frontend)
        self.assertIn("Never add a no-op, timer, local-success default", frontend)
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
