#!/usr/bin/env python3
"""Focused tests for the context-pressure Recovery Guard."""

from __future__ import annotations

import json
import importlib.util
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recovery_guard import (  # noqa: E402
    AUDIT_FIELDS,
    GuardThresholds,
    detect_correction,
    detect_explicit_stop,
    detect_recovery_audit_packet,
    detect_recovery_rhetoric,
    detect_substantive_response,
    load_state,
    new_state,
    reduce_event,
    state_path_for_session,
    update_state_atomic,
)

ADAPTER_PATH = Path(__file__).resolve().parents[2] / "hooks" / "codex_hook_adapter.py"
ADAPTER_SPEC = importlib.util.spec_from_file_location("recovery_guard_test_adapter", ADAPTER_PATH)
if ADAPTER_SPEC is None or ADAPTER_SPEC.loader is None:  # pragma: no cover - import contract failure.
    raise RuntimeError(f"cannot load Codex hook adapter: {ADAPTER_PATH}")
ADAPTER = importlib.util.module_from_spec(ADAPTER_SPEC)
ADAPTER_SPEC.loader.exec_module(ADAPTER)


SESSION = "session-secret-id"


def event(name: str, **values: object) -> dict[str, object]:
    return {"hook_event_name": name, "session_id": SESSION, **values}


def reduce_many(events, thresholds=None):
    state = None
    decision = None
    for payload in events:
        state, decision = reduce_event(state, payload, thresholds)
    return state, decision


class DetectorTests(unittest.TestCase):
    def test_correction_detector_is_conservative(self) -> None:
        self.assertTrue(detect_correction("그게 아니잖아. 로직의 차이를 봐야 해."))
        self.assertTrue(detect_correction("That's not what I asked; compare the behavior."))
        self.assertFalse(detect_correction("아니면 A와 B 중 어느 쪽이 맞나요?"))
        self.assertFalse(detect_correction("왜 이 알고리즘은 O(n)인가요?"))
        self.assertFalse(detect_correction("아니요, 추가 작업은 필요 없습니다."))
        self.assertFalse(detect_correction("아니요, 멈춰주세요."))
        self.assertFalse(detect_correction("아니, 하지 마."))
        self.assertFalse(detect_correction("아니요, 감사합니다."))
        self.assertFalse(detect_correction("아니요, 괜찮습니다."))
        self.assertFalse(detect_correction("No, thanks. That is all."))
        self.assertFalse(detect_correction("No, stop here."))
        self.assertFalse(detect_correction("No, do not do anything else."))
        self.assertTrue(detect_correction("No, thanks. That is not what I asked."))
        self.assertTrue(detect_correction("아니요, 추가 설명 말고 실제 로직을 고쳐주세요."))
        self.assertTrue(detect_correction("아니요, 더 이상 약속하지 말고 구현해요."))
        self.assertTrue(detect_correction("No more plans; implement the fix."))
        self.assertTrue(detect_correction("No additional promises; show evidence."))
        self.assertTrue(detect_correction("아니요, 됐고 실제 구현을 고쳐주세요."))
        self.assertTrue(detect_correction("아니요, 감사합니다만 제가 요청한 내용과 다릅니다."))
        self.assertTrue(detect_correction("로직 부분의 차이를 보고 싶은 거지 QT와 .net 차이를 보고 싶은 게 아니야."))
        self.assertTrue(detect_correction("그런 차이를 말한 게 아니야. 런타임 로직을 비교해줘."))
        self.assertTrue(detect_correction("내가 원한 건 파일 목록이 아니라 실제 동작 차이야."))

    def test_recovery_rhetoric_requires_opener_and_promise(self) -> None:
        self.assertTrue(detect_recovery_rhetoric("맞습니다. 이제 제대로 수정하겠습니다."))
        self.assertTrue(detect_recovery_rhetoric("You're right. I'll start over and fix it."))
        self.assertFalse(detect_recovery_rhetoric("맞습니다. 테스트 12개가 통과했습니다."))
        self.assertFalse(detect_recovery_rhetoric("수정하겠습니다."))
        self.assertFalse(detect_recovery_rhetoric("You are right. Let me clarify the runtime difference."))

    def test_short_concrete_answer_and_explicit_stop(self) -> None:
        self.assertTrue(detect_substantive_response("맞습니다. 이제 설명하겠습니다. A는 예외를 던지지만 B는 null을 반환합니다."))
        self.assertTrue(detect_substantive_response("맞습니다. 이제 설명하겠습니다. 핵심 차이는 오류 경계입니다."))
        self.assertTrue(detect_substantive_response(
            "You are right. I will explain. The key difference is error propagation."
        ))
        self.assertTrue(detect_explicit_stop("아니요, 멈춰주세요."))
        self.assertTrue(detect_explicit_stop("아니, 하지 마."))
        self.assertTrue(detect_explicit_stop("아니요, 추가 작업은 필요 없습니다."))
        self.assertTrue(detect_explicit_stop("아니요, 감사합니다."))
        self.assertTrue(detect_explicit_stop("아니요, 괜찮습니다."))
        self.assertTrue(detect_explicit_stop("그만."))
        self.assertTrue(detect_explicit_stop("No, stop here."))
        self.assertTrue(detect_explicit_stop("No, do not do anything else."))
        self.assertTrue(detect_explicit_stop("No further work is needed."))
        self.assertFalse(detect_explicit_stop("No, thanks. That is not what I asked."))

    def test_substantive_correction_is_not_rhetoric_only(self) -> None:
        answer = (
            "맞습니다. 이제 실제 런타임 계약을 기준으로 설명하겠습니다. "
            "A는 오류를 호출자에게 그대로 전파하지만 B는 예외를 결과 값으로 변환합니다. "
            "따라서 핵심 차이는 프레임워크 이름이 아니라 오류 경계와 반환 계약입니다."
        )
        self.assertTrue(detect_recovery_rhetoric(answer))
        self.assertTrue(detect_substantive_response(answer))
        self.assertFalse(detect_substantive_response(
            "You are right. I will fix it. I will inspect the current runtime state, contract, and error behavior, "
            "then perform the correct validation."
        ))
        self.assertFalse(detect_substantive_response(
            "맞습니다. 이제 수정하겠습니다. 런타임 상태와 오류 계약을 먼저 세밀하게 검토하고 실제 동작을 "
            "다시 확인한 뒤 올바른 방향으로 구현과 검증을 계속 진행할 계획입니다."
        ))
        self.assertFalse(detect_substantive_response(
            "맞습니다. 이제 설명하겠습니다. 핵심 차이는 추가로 확인할 예정입니다."
        ))
        self.assertFalse(detect_substantive_response(
            "You are right. I will explain. The key difference is something I will verify."
        ))
        self.assertTrue(detect_substantive_response(
            "맞습니다. 이제 설명하겠습니다. 이 루프는 입력 배열을 한 번만 순회하므로 시간 복잡도는 "
            "O(n)입니다. 별도 정렬이 없기 때문에 입력 크기에 비례해서 실행 시간이 증가합니다."
        ))
        self.assertTrue(detect_substantive_response(
            "맞습니다. 이제 실제 화면 흐름을 설명하겠습니다. 사용자가 저장 버튼을 누르면 입력 데이터가 "
            "검증되고, 그 결과 오류가 있으면 현재 화면에 표시되지만 성공하면 목록 화면으로 이동합니다."
        ))

        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 로직을 설명해줘.")]
        )
        state, decision = reduce_event(state, event("Stop", last_assistant_message=answer))
        self.assertEqual(decision["action"], "allow")
        self.assertFalse(state["correction_pending"])

    def test_explicit_stop_cancels_pending_episode(self) -> None:
        state, _ = reduce_many([event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니야. 다시 확인해줘.")])
        state, decision = reduce_event(state, event("UserPromptSubmit", prompt="아니요, 멈춰주세요."))
        self.assertEqual(decision["action"], "allow")
        self.assertFalse(state["correction_pending"])

    def test_explicit_stop_variants_cancel_pending_episode(self) -> None:
        prompts = [
            "아니, 하지 마.",
            "아니요, 추가 작업은 필요 없습니다.",
            "아니요, 감사합니다.",
            "그만.",
            "No, do not do anything else.",
            "No further work is needed.",
        ]
        for index, prompt in enumerate(prompts):
            with self.subTest(prompt=prompt):
                state, _ = reduce_many(
                    [
                        event("PostCompact", turn_id=f"compact-{index}"),
                        event(
                            "UserPromptSubmit",
                            turn_id=f"correction-{index}",
                            prompt="그게 아니야. 다시 확인해줘.",
                        ),
                    ]
                )
                state, decision = reduce_event(
                    state, event("UserPromptSubmit", turn_id=f"stop-{index}", prompt=prompt)
                )
                self.assertEqual(decision["action"], "allow")
                self.assertIn("explicit_stop", decision["reason_codes"])
                self.assertFalse(state["correction_pending"])

    def test_recovery_packet_requires_all_structural_fields(self) -> None:
        packet = """recovery_audit:
  goal_anchor: original goal
  latest_user_delta: compare logic
  observed_changes: []
  verified_progress: []
  open_gap_and_next_action: inspect runtime behavior
"""
        self.assertTrue(detect_recovery_audit_packet(packet))
        self.assertFalse(detect_recovery_audit_packet("recovery_audit:\n  goal_anchor: only"))
        self.assertFalse(detect_recovery_audit_packet("prefix\n" + packet))
        self.assertFalse(detect_recovery_audit_packet(packet + "extra_field: invented\n"))
        self.assertFalse(detect_recovery_audit_packet(packet.replace("goal_anchor: original goal", "goal_anchor: <original goal>")))


class ReducerTests(unittest.TestCase):
    def test_short_session_stays_passive(self) -> None:
        state, decision = reduce_many(
            [
                event("UserPromptSubmit", prompt="그게 아니잖아. 다시 확인해줘."),
                event("Stop", last_assistant_message="맞습니다. 이제 다시 수정하겠습니다."),
            ]
        )
        self.assertFalse(state["armed"])
        self.assertEqual(decision["action"], "allow")
        self.assertTrue(state["correction_pending"])

    def test_post_compact_arms_and_audits_once(self) -> None:
        state, _ = reduce_many(
            [
                event("UserPromptSubmit", prompt="그게 아니잖아. 핵심 로직을 봐줘."),
                event("PreCompact"),
                event("PostCompact"),
            ]
        )
        state, first = reduce_event(
            state, event("Stop", turn_id="one", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다.")
        )
        state, second = reduce_event(
            state,
            event(
                "Stop",
                turn_id="two",
                stop_hook_active=True,
                last_assistant_message="죄송합니다. 바로 다시 고치겠습니다.",
            ),
        )
        self.assertTrue(state["armed"])
        self.assertEqual(first["action"], "audit")
        self.assertEqual(first["required_fields"], list(AUDIT_FIELDS))
        self.assertEqual(second["action"], "handoff")
        self.assertEqual(state["phase"], "awaiting_user")
        self.assertIn("audit_packet_unstructured", second["reason_codes"])

    def test_default_user_turn_threshold_arms(self) -> None:
        prompts = [event("UserPromptSubmit", turn_id=str(i), prompt="계속") for i in range(5)]
        prompts.append(event("UserPromptSubmit", turn_id="correction", prompt="그게 아니에요. 다시 봐줘."))
        state, _ = reduce_many(prompts)
        self.assertEqual(state["user_turns"], 6)
        self.assertTrue(state["armed"])

    def test_tool_event_threshold_is_configurable(self) -> None:
        thresholds = GuardThresholds(user_turns=99, tool_events=2, correction_episodes=99)
        state, _ = reduce_many(
            [event("PreToolUse", tool_use_id="one"), event("PreToolUse", tool_use_id="two")], thresholds
        )
        self.assertEqual(state["tool_events"], 2)
        self.assertTrue(state["armed"])

    def test_post_tool_event_observes_progress_without_double_counting_call(self) -> None:
        state, _ = reduce_many(
            [
                event("UserPromptSubmit", prompt="그게 아니잖아. 구현을 고쳐줘."),
                event("PreToolUse", tool_use_id="one"),
                event(
                    "PostToolUse",
                    tool_use_id="one",
                    tool_response={"exit_code": 0, "changed_files": ["source/a.py"]},
                ),
            ]
        )
        self.assertEqual(state["tool_events"], 1)
        self.assertTrue(state["progress_since_correction"])

    def test_successful_write_tool_is_progress_without_changed_files_field(self) -> None:
        state, _ = reduce_many(
            [
                event("UserPromptSubmit", prompt="그게 아니잖아. 구현을 고쳐줘."),
                event("PostToolUse", tool_name="apply_patch", tool_response={"success": True}),
            ]
        )
        self.assertTrue(state["progress_since_correction"])

    def test_second_correction_episode_arms(self) -> None:
        state, _ = reduce_many(
            [
                event("UserPromptSubmit", turn_id="one", prompt="그게 아니잖아."),
                event("UserPromptSubmit", turn_id="two", prompt="That's not what I asked."),
            ]
        )
        self.assertEqual(state["correction_episodes"], 2)
        self.assertEqual(state["episode"], 2)
        self.assertTrue(state["armed"])

    def test_progress_evidence_after_correction_prevents_audit(self) -> None:
        state, _ = reduce_many(
            [
                event("PostCompact"),
                event("UserPromptSubmit", prompt="그게 아니잖아. 구현을 고쳐줘."),
                event(
                    "PostToolUse",
                    tool_use_id="write-one",
                    tool_response={"exit_code": 0, "changed_files": ["source/a.py"]},
                ),
            ]
        )
        state, decision = reduce_event(
            state, event("Stop", last_assistant_message="맞습니다. 앞으로는 제대로 수정하겠습니다.")
        )
        self.assertEqual(decision["action"], "allow")
        self.assertFalse(state["correction_pending"])

    def test_generic_success_is_not_progress_evidence(self) -> None:
        state, _ = reduce_many(
            [
                event("PostCompact"),
                event("UserPromptSubmit", prompt="그게 아니잖아. 구현을 고쳐줘."),
                event("PostToolUse", tool_response={"exit_code": 0, "stdout": "listed files"}),
            ]
        )
        state, decision = reduce_event(
            state, event("Stop", last_assistant_message="맞습니다. 이제 다시 수정하겠습니다.")
        )
        self.assertEqual(decision["action"], "audit")

    def test_non_rhetorical_answer_resolves_pending_correction(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 설명을 바로잡아줘.")]
        )
        state, decision = reduce_event(
            state, event("Stop", last_assistant_message="두 구현의 런타임 계약 차이는 오류 전파 방식입니다.")
        )
        self.assertEqual(decision["action"], "allow")
        self.assertFalse(state["correction_pending"])

    def test_short_direct_conclusion_resolves_instead_of_auditing(self) -> None:
        for index, answer in enumerate(
            [
                "맞습니다. 이제 설명하겠습니다. 핵심 차이는 오류 경계입니다.",
                "You are right. I will explain. The key difference is error propagation.",
            ]
        ):
            with self.subTest(answer=answer):
                state, _ = reduce_many(
                    [
                        event("PostCompact", turn_id=f"compact-{index}"),
                        event(
                            "UserPromptSubmit",
                            turn_id=f"correction-{index}",
                            prompt="그게 아니잖아. 로직을 설명해줘.",
                        ),
                    ]
                )
                state, decision = reduce_event(
                    state, event("Stop", turn_id=f"answer-{index}", last_assistant_message=answer)
                )
                self.assertEqual(decision["action"], "allow")
                self.assertTrue(state["last_stop_substantive"])
                self.assertFalse(state["correction_pending"])

    def test_future_only_direct_conclusion_remains_an_audit_candidate(self) -> None:
        state, _ = reduce_many(
            [
                event("PostCompact"),
                event("UserPromptSubmit", prompt="그게 아니잖아. 로직을 설명해줘."),
            ]
        )
        state, decision = reduce_event(
            state,
            event(
                "Stop",
                last_assistant_message="맞습니다. 이제 설명하겠습니다. 핵심 차이는 추가로 확인할 예정입니다.",
            ),
        )
        self.assertEqual(decision["action"], "audit")
        self.assertFalse(state["last_stop_substantive"])

    def test_duplicate_event_does_not_increment_counters(self) -> None:
        payload = event("PreToolUse", tool_use_id="same")
        state, _ = reduce_event(None, payload)
        state, decision = reduce_event(state, payload)
        self.assertEqual(state["tool_events"], 1)
        self.assertEqual(decision["reason_codes"], ["duplicate_event"])
        self.assertEqual(decision["action"], "duplicate")

    def test_nonconsecutive_duplicate_event_is_suppressed(self) -> None:
        first = event("PreToolUse", tool_use_id="one")
        state, _ = reduce_event(None, first)
        state, _ = reduce_event(state, event("PreToolUse", tool_use_id="two"))
        state, decision = reduce_event(state, first)
        self.assertEqual(state["tool_events"], 2)
        self.assertEqual(decision["reason_codes"], ["duplicate_event"])
        self.assertEqual(decision["action"], "duplicate")

    def test_session_start_compact_arms_and_clear_resets(self) -> None:
        state, _ = reduce_event(None, event("SessionStart", source="compact"))
        self.assertTrue(state["armed"])
        self.assertTrue(state["post_compact_seen"])
        state, _ = reduce_event(state, event("SessionStart", source="clear", turn_id="clear"))
        self.assertFalse(state["armed"])
        self.assertEqual(state["user_turns"], 0)

    def test_repeated_clear_always_resets_even_after_new_events(self) -> None:
        clear = event("SessionStart", source="clear", turn_id="clear")
        state, _ = reduce_event(None, clear)
        state, _ = reduce_event(state, event("UserPromptSubmit", turn_id="later", prompt="continue"))
        self.assertEqual(state["user_turns"], 1)
        state, _ = reduce_event(state, clear)
        self.assertEqual(state["user_turns"], 0)

    def test_valid_audit_packet_moves_to_awaiting_user(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 다시 봐줘.")]
        )
        state, decision = reduce_event(
            state, event("Stop", turn_id="risk", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다.")
        )
        self.assertEqual(decision["action"], "audit")
        packet = """recovery_audit:
  goal_anchor: original
  latest_user_delta: correction
  observed_changes: []
  verified_progress: []
  open_gap_and_next_action: ask user
"""
        state, decision = reduce_event(
            state, event("Stop", turn_id="audit", stop_hook_active=True, last_assistant_message=packet)
        )
        self.assertEqual(decision["action"], "handoff")
        self.assertTrue(state["audit_packet_valid"])
        self.assertEqual(state["phase"], "awaiting_user")

        state, decision = reduce_event(
            state, event("UserPromptSubmit", turn_id="resume", prompt="이제 확인 작업을 계속해줘.")
        )
        self.assertEqual(decision["action"], "allow")
        self.assertFalse(state["correction_pending"])
        self.assertFalse(state["audit_blocked_for_episode"])

    def test_inactive_near_duplicate_stop_cannot_consume_audit_response(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 다시 봐줘.")]
        )
        risky = "맞습니다. 이제 다시 시작하겠습니다."
        state, decision = reduce_event(
            state,
            event("Stop", turn_id="risk", stop_hook_active=False, last_assistant_message=risky),
        )
        self.assertEqual(decision["action"], "audit")
        self.assertEqual(state["phase"], "audit_requested")

        state, decision = reduce_event(
            state,
            event(
                "Stop",
                turn_id="risk",
                stop_hook_active=False,
                last_assistant_message=risky,
                hook_source="near-duplicate",
            ),
        )
        self.assertEqual(decision["action"], "audit")
        self.assertIn("awaiting_active_audit_response", decision["reason_codes"])
        self.assertEqual(state["phase"], "audit_requested")
        self.assertTrue(state["correction_pending"])
        self.assertEqual(state["audit_blocks"], 1)
        self.assertEqual(state["audit_responses"], 0)

        packet = """recovery_audit:
  goal_anchor: original
  latest_user_delta: correction
  observed_changes: []
  verified_progress: []
  open_gap_and_next_action: ask user
"""
        state, decision = reduce_event(
            state,
            event("Stop", turn_id="audit", stop_hook_active=True, last_assistant_message=packet),
        )
        self.assertEqual(decision["action"], "handoff")
        self.assertEqual(state["phase"], "awaiting_user")

    def test_audit_phase_survives_incidental_events_but_new_user_input_cancels_it(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 다시 봐줘.")]
        )
        state, _ = reduce_event(
            state, event("Stop", turn_id="risk", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다.")
        )
        self.assertEqual(state["phase"], "audit_requested")
        state, _ = reduce_event(state, event("PreCompact", turn_id="between"))
        self.assertEqual(state["phase"], "audit_requested")
        state, _ = reduce_event(state, event("UserPromptSubmit", turn_id="override", prompt="새 지시대로 계속해줘."))
        self.assertNotEqual(state["phase"], "audit_requested")
        self.assertFalse(state["audit_blocked_for_episode"])

    def test_observe_only_audit_never_creates_handoff_state(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 다시 봐줘.")]
        )
        state, decision = reduce_event(
            state,
            event("Stop", turn_id="risk", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다."),
            block_audit=False,
        )
        self.assertEqual(decision["action"], "audit")
        self.assertFalse(state["audit_blocked_for_episode"])
        state, decision = reduce_event(
            state,
            event("Stop", turn_id="next", stop_hook_active=True, last_assistant_message="죄송합니다. 바로 고치겠습니다."),
            block_audit=False,
        )
        self.assertEqual(decision["action"], "allow")
        self.assertNotEqual(state["phase"], "awaiting_user")

    def test_suppressed_loop_audit_is_reconsidered_after_precedence_ends(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 다시 봐줘.")]
        )
        risky_stop = event("Stop", turn_id="risk", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다.")
        state, decision = reduce_event(
            state,
            risky_stop,
            block_audit=False,
            consume_audit=False,
        )
        self.assertEqual(decision["action"], "audit")
        self.assertFalse(state["audit_issued_for_episode"])
        state, decision = reduce_event(state, risky_stop, block_audit=True, consume_audit=True)
        self.assertEqual(decision["action"], "audit")
        self.assertTrue(state["audit_blocked_for_episode"])

    def test_session_audit_blocks_are_bounded(self) -> None:
        state, _ = reduce_event(None, event("PostCompact"))
        packet = """recovery_audit:
  goal_anchor: original
  latest_user_delta: correction
  observed_changes: []
  verified_progress: []
  open_gap_and_next_action: wait for user
"""
        for index in range(3):
            state, _ = reduce_event(
                state,
                event("UserPromptSubmit", turn_id=f"u{index}", prompt="그게 아니잖아. 다시 봐줘."),
            )
            state, decision = reduce_event(
                state,
                event("Stop", turn_id=f"s{index}", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다."),
            )
            self.assertEqual(decision["action"], "audit")
            state, _ = reduce_event(
                state,
                event("Stop", turn_id=f"h{index}", stop_hook_active=True, last_assistant_message=packet),
            )
        self.assertEqual(state["audit_blocks"], 3)
        state, _ = reduce_event(
            state,
            event("UserPromptSubmit", turn_id="u4", prompt="그게 아니잖아. 다시 봐줘."),
        )
        state, decision = reduce_event(
            state,
            event("Stop", turn_id="s4", last_assistant_message="맞습니다. 이제 다시 시작하겠습니다."),
        )
        self.assertEqual(decision["action"], "allow")
        self.assertIn("session_audit_limit_reached", decision["reason_codes"])
        self.assertEqual(state["audit_blocks"], 3)

    def test_empty_stop_does_not_resolve_pending_correction(self) -> None:
        state, _ = reduce_many(
            [event("PostCompact"), event("UserPromptSubmit", prompt="그게 아니잖아. 다시 봐줘.")]
        )
        state, decision = reduce_event(state, event("Stop", last_assistant_message=""))
        self.assertEqual(decision["action"], "allow")
        self.assertTrue(state["correction_pending"])

    def test_state_never_persists_raw_text_or_session_id(self) -> None:
        secret_prompt = "그게 아니잖아 secret-marker-123"
        secret_answer = "맞습니다. 이제 secret-answer-456을 수정하겠습니다."
        state, _ = reduce_many(
            [
                event("PostCompact"),
                event("UserPromptSubmit", prompt=secret_prompt),
                event("Stop", last_assistant_message=secret_answer),
            ]
        )
        serialized = json.dumps(state, ensure_ascii=False)
        self.assertNotIn(secret_prompt, serialized)
        self.assertNotIn(secret_answer, serialized)
        self.assertNotIn(SESSION, serialized)
        self.assertNotIn("prompt", serialized)
        self.assertNotIn("assistant", serialized)

    def test_state_rejects_cross_session_events(self) -> None:
        state = new_state(SESSION)
        with self.assertRaisesRegex(ValueError, "different session"):
            reduce_event(state, {"hook_event_name": "PreCompact", "session_id": "other"})

    def test_state_rejects_extra_fields_that_could_retain_raw_text(self) -> None:
        state = new_state(SESSION)
        state["prompt"] = "must-not-survive"
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            reduce_event(state, event("PreCompact"))


class PersistenceTests(unittest.TestCase):
    def test_atomic_update_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recovery.json"
            state, decision = update_state_atomic(path, event("PostCompact"))
            self.assertEqual(decision["action"], "allow")
            self.assertTrue(state["armed"])
            self.assertEqual(load_state(path, SESSION), state)
            self.assertTrue(path.with_suffix(".json.lock").exists())
            self.assertFalse(list(path.parent.glob("*.tmp")))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_session_state_path_does_not_expose_session_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = state_path_for_session(SESSION, Path(directory))
            self.assertNotIn(SESSION, path.name)
            self.assertRegex(path.name, r"^[0-9a-f]{64}\.json$")

    def test_invalid_persisted_state_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recovery.json"
            path.write_text('{"prompt":"raw"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing fields"):
                load_state(path, SESSION)

    def test_clear_event_recovers_corrupt_persisted_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recovery.json"
            path.write_text('{"prompt":"raw"}', encoding="utf-8")
            state, decision = update_state_atomic(path, event("SessionStart", source="clear"))
            self.assertEqual(decision["action"], "allow")
            self.assertEqual(state["phase"], "passive")
            self.assertEqual(load_state(path, SESSION), state)


class AdapterModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous = os.environ.pop("SKILL_SYSTEM_RECOVERY_GUARD", None)

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("SKILL_SYSTEM_RECOVERY_GUARD", None)
        else:
            os.environ["SKILL_SYSTEM_RECOVERY_GUARD"] = self.previous

    def test_default_mode_remains_observe(self) -> None:
        self.assertEqual(ADAPTER.recovery_guard_mode({}), "observe")

    def test_explicit_off_is_an_emergency_kill_switch(self) -> None:
        os.environ["SKILL_SYSTEM_RECOVERY_GUARD"] = "off"
        self.assertEqual(
            ADAPTER.recovery_guard_mode({"skill_system_recovery_guard": "audit"}),
            "off",
        )
        self.assertIsNone(
            ADAPTER.observe_recovery_guard(
                {
                    "hook_event_name": "Stop",
                    "session_id": SESSION,
                    "skill_system_recovery_guard": "audit",
                },
                block_allowed=True,
            )
        )

    def test_explicit_audit_mode_still_requires_opt_in(self) -> None:
        self.assertEqual(
            ADAPTER.recovery_guard_mode({"skill_system_recovery_guard": "audit"}),
            "audit",
        )


if __name__ == "__main__":
    unittest.main()
