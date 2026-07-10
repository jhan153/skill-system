from __future__ import annotations

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
        self.assertEqual(len(skills), 66)
        audit = canonical("shared/docs/skill_quality_audit.md").read_text(encoding="utf-8")
        for skill in skills:
            self.assertIn(f"`{skill.parent.name}`", audit)
            agent = skill.parent / "agents" / "openai.yaml"
            self.assertTrue(agent.is_file(), skill.parent.name)
            for line in agent.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("short_description:"):
                    value = line.split(":", 1)[1].strip().strip('"')
                    self.assertLessEqual(len(value), 64, skill.parent.name)

    def test_every_current_skill_has_positive_and_negative_routing_coverage(self) -> None:
        skills = {path.parent.name for path in (SOURCE / "skills").glob("*/SKILL.md")}
        positive: set[str] = set()
        negative: set[str] = set()
        for path in (SOURCE / "shared" / "eval").glob("*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for case in data.get("cases", []) if isinstance(data, dict) else []:
                if not isinstance(case, dict):
                    continue
                primary = case.get("expected_primary_skill")
                if isinstance(primary, str):
                    positive.add(primary)
                positive.update(item for item in case.get("expected_supporting_skills", []) if isinstance(item, str))
                negative.update(item for item in case.get("should_not_trigger", []) if isinstance(item, str))
        self.assertEqual(skills - positive, set())
        self.assertEqual(skills - negative, set())

    def test_global_agents_stays_thin_and_delegates_routing(self) -> None:
        text = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertLess(len(text.split()), 900)
        self.assertNotIn("## Skill Alias Interpretation", text)
        self.assertNotIn("### Loop Readiness Gate", text)
        self.assertIn("blocked`, analysis-only", text)
        self.assertIn(".codex/context-routing.md", text)
        self.assertIn("Route explicit `/goal`", text)
        self.assertIn("unknown or stale explicit skill alias", text)

    def test_global_agents_requires_goal_first_proportional_depth(self) -> None:
        text = canonical("platform/codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("intended outcome before drafting", text)
        self.assertIn("## Goal And Depth", text)
        self.assertIn("Scale depth with ambiguity and consequence", text)
        self.assertIn("trace the relevant end-to-end behavior", text)
        self.assertIn("counterexamples or disconfirming evidence", text)
        self.assertIn("are leads, not semantic proof", text)
        self.assertIn("up to three independent evidence passes", text)
        self.assertIn("distinct hypotheses or evidence lanes", text)
        self.assertIn("primary retains scope, synthesis, and final judgment", text.lower())

    def test_routing_docs_do_not_embed_eval_payloads(self) -> None:
        routing = canonical("shared/context-routing.md").read_text(encoding="utf-8")
        research = canonical("platform/codex/research-routing.md").read_text(encoding="utf-8")
        self.assertIn(".codex/eval/routing_cases.yaml", routing)
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
            "create-skill-pack": ("skill-creator", "authoring_then_repository_integration"),
        }
        registry = canonical("shared/docs/skill_registry.md").read_text(encoding="utf-8")
        routing = canonical("shared/context-routing.md").read_text(encoding="utf-8")
        case_data = yaml.safe_load(
            canonical("shared/eval/routing_cases.yaml").read_text(encoding="utf-8")
        )
        cases = case_data["cases"]

        for legacy, (owner, mode) in expected.items():
            row = next(
                line for line in registry.splitlines() if line.startswith(f"| `{legacy}` |")
            )
            self.assertIn(f"`{owner}`", row)
            self.assertIn(f"`{mode}`", row)
            self.assertFalse((SOURCE / "skills" / legacy).exists(), legacy)
            alias_case = next(
                case
                for case in cases
                if case.get("legacy_alias") == legacy and not case.get("direct_invocation")
            )
            self.assertEqual(alias_case.get("expected_mode"), mode)
            if owner == "skill-creator":
                self.assertEqual(alias_case.get("expected_route_class"), "external_system_skill_creator")
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
        self.assertIn("Host-resolved direct slash/plugin invocations", routing)
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
        self.assertIn("reuse that ID", contract)
        for skill_id in (
            "memory-bank-init",
            "memory-bank-update",
            "memory-bank-correction-capture",
            "memory-bank-maintenance",
            "memory-bank-ingestion",
        ):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("memory_mutation_contract.md", text, skill_id)
        init = canonical("skills/memory-bank-init/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never delete or overwrite accepted history silently", init)

    def test_context_harness_uses_live_store_and_measured_context_size(self) -> None:
        knowledge = canonical("skills/knowledge-context-harness/SKILL.md").read_text(encoding="utf-8")
        memory = canonical("skills/memory-bank-harness/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("tests/fixtures/knowledge-store", knowledge)
        self.assertIn("--rebuild-projections --check", knowledge)
        self.assertIn("admitted words/UTF-8 bytes", knowledge)
        self.assertIn("admitted_words", memory)
        self.assertIn("advisory token estimate", memory)

    def test_support_and_design_outputs_are_not_forced_on_simple_tasks(self) -> None:
        ledger = canonical("skills/workflow-task-ledger/SKILL.md").read_text(encoding="utf-8")
        validation = canonical("skills/workflow-validation/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("do not create a ledger merely because", ledger)
        self.assertIn("ordinary focused checks stay with the primary owner", validation)
        for skill_id in ("design-layout-translator", "design-ui-decomposer"):
            text = canonical(f"skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("Include at least three negative route checks", text)
            self.assertIn("omit empty", text.lower())


if __name__ == "__main__":
    unittest.main()
