package workcontract

import (
	"encoding/json"
	"os"
	"strings"
	"testing"
)

func TestNaturalLanguageContractCaptureAndExplicitAllow(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	state, active, err := Capture(
		"session",
		"/goal 무인 장시간 구현으로 핵심 작업만 진행해. 검증은 내가 할 테니 승인 요청하지 말고 질문하지 마.",
	)
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	if state.VerificationOwner != VerificationUser || state.InteractionMode != InteractionForbidden {
		t.Fatalf("unexpected contract: %#v", state)
	}
	if state.ExecutionMode != ExecutionUnattendedGoalLoop {
		t.Fatalf("unexpected execution mode: %#v", state)
	}
	for _, class := range []string{ActionAgentValidation, ActionTestAuthoring, ActionValidationArtifact, ActionMeta} {
		if !isExcluded(state, class) {
			t.Errorf("missing exclusion %s in %#v", class, state.ExcludedActionClasses)
		}
	}
	context := Context(state)
	if !strings.Contains(context, "user-verification-needed") || !strings.Contains(context, "Do not request approval") {
		t.Fatalf("incomplete context: %q", context)
	}

	state, active, err = Capture("session", "이번 일반 작업은 테스트와 승인 요청을 허용해. 에이전트가 검증해.")
	if err != nil || !active {
		t.Fatalf("allow active=%v err=%v", active, err)
	}
	if state.VerificationOwner != VerificationAgent || state.InteractionMode != InteractionAllowed {
		t.Fatalf("allow did not restore defaults: %#v", state)
	}
	if isExcluded(state, ActionAgentValidation) || isExcluded(state, ActionTestAuthoring) {
		t.Fatalf("verification exclusions survived explicit allow: %#v", state.ExcludedActionClasses)
	}
}

func TestOrdinaryPromptCreatesNoContract(t *testing.T) {
	root := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", root)
	_, active, err := Capture("session", "파서 구현을 시작해")
	if err != nil || active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	if _, err := os.Stat(statePath("session")); !os.IsNotExist(err) {
		t.Fatalf("ordinary prompt created state: %v", err)
	}
}

func TestMentioningGoalSyntaxDoesNotCreateUnattendedExecution(t *testing.T) {
	root := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", root)
	_, active, err := Capture("session", "문서에서 /goal 명령의 동작을 설명해")
	if err != nil || active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	if _, err := os.Stat(statePath("session")); !os.IsNotExist(err) {
		t.Fatalf("descriptive /goal mention created state: %v", err)
	}
}

func TestStatePersistsNoRawPrompt(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	prompt := "검증은 내가 할게. 승인 요청하지 마. raw-secret-value"
	if _, _, err := Capture("session", prompt); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(statePath("session"))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(raw), prompt) || strings.Contains(string(raw), "raw-secret-value") {
		t.Fatal("raw prompt was persisted")
	}
}

func TestExcludedPlanItemIsRemovedWithoutBlockingRemainingPlan(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture("session", "구현에만 집중하고 테스트는 내가 할게"); err != nil {
		t.Fatal(err)
	}
	input, _ := json.Marshal(map[string]any{
		"plan": []map[string]string{
			{"step": "핵심 파서 구현", "status": "in_progress"},
			{"step": "테스트를 실행해 검증", "status": "pending"},
		},
	})
	decision, err := Preflight("session", "update_plan", input)
	if err != nil {
		t.Fatal(err)
	}
	if decision.Deny || !decision.Rewrite {
		t.Fatalf("mixed plan was not rewritten without blocking: %#v", decision)
	}
	plan, ok := decision.UpdatedInput["plan"].([]any)
	if !ok || len(plan) != 1 {
		t.Fatalf("unexpected rewritten plan: %#v", decision.UpdatedInput)
	}
	item, _ := plan[0].(map[string]any)
	if item["step"] != "핵심 파서 구현" {
		t.Fatalf("core plan item was not preserved: %#v", item)
	}
	state, err := Load("session")
	if err != nil {
		t.Fatal(err)
	}
	if len(state.DeferredIntents) != 1 || state.DeferredIntents[0].Class != ActionAgentValidation {
		t.Fatalf("excluded plan purpose was not recorded once: %#v", state.DeferredIntents)
	}
	if state.ActiveIntent == nil || state.ActiveIntent.Class != ActionCore {
		t.Fatalf("remaining active core intent was not retained: %#v", state.ActiveIntent)
	}

	coreOnly, _ := json.Marshal(map[string]any{
		"plan": []map[string]string{{"step": "다음 핵심 파서 구현", "status": "pending"}},
	})
	decision, err = Preflight("session", "update_plan", coreOnly)
	if err != nil || decision.Deny || decision.Rewrite {
		t.Fatalf("core plan decision=%#v err=%v", decision, err)
	}
	state, err = Load("session")
	if err != nil {
		t.Fatal(err)
	}
	if state.ActiveIntent != nil {
		t.Fatalf("stale active intent survived a plan with no in-progress item: %#v", state.ActiveIntent)
	}
}

func TestPlanWithNoInContractItemStillUsesLastResortDeny(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture("session", "구현에만 집중하고 테스트는 내가 할게"); err != nil {
		t.Fatal(err)
	}
	input, _ := json.Marshal(map[string]any{
		"plan": []map[string]string{
			{"step": "테스트를 실행해 검증", "status": "in_progress"},
			{"step": "검증용 testbed wrapper 생성", "status": "pending"},
		},
	})
	decision, err := Preflight("session", "update_plan", input)
	if err != nil || !decision.Deny || decision.Rewrite {
		t.Fatalf("all-excluded plan should use the last-resort deny: %#v err=%v", decision, err)
	}
}

func TestNoInteractionPermissionDeniesAndDebouncesPurpose(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture("session", "/goal 무인 장시간 작업으로 추가 승인 없이 구현만 계속해"); err != nil {
		t.Fatal(err)
	}
	input := json.RawMessage(`{"command":"run runtime validation","description":"verify runtime behavior"}`)
	decision, err := Permission("session", "Bash", input)
	if err != nil || !decision.Deny {
		t.Fatalf("permission deny=%v err=%v", decision.Deny, err)
	}
	if decision.Intent.Class != ActionAgentValidation {
		t.Fatalf("unexpected action class: %#v", decision.Intent)
	}
	retry := json.RawMessage(`{"command":"execute smoke verification","description":"validate the same behavior"}`)
	decision, err = Preflight("session", "Bash", retry)
	if err != nil || !decision.Deny {
		t.Fatalf("same-purpose retry deny=%v err=%v", decision.Deny, err)
	}
	if !strings.Contains(decision.Reason, "same-purpose") {
		t.Fatalf("missing debounce reason: %q", decision.Reason)
	}
	alternate := json.RawMessage(`{"description":"create a validation testbed wrapper"}`)
	decision, err = Preflight("session", "apply_patch", alternate)
	if err != nil || !decision.Deny {
		t.Fatalf("alternate validation form deny=%v err=%v", decision.Deny, err)
	}
	if decision.Intent.Class != ActionValidationArtifact || !strings.Contains(decision.Reason, "same-purpose") {
		t.Fatalf("alternate form was not deduplicated by purpose: %#v", decision)
	}
}

func TestAttendedTaskKeepsNormalApprovalFlow(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture("session", "일반 대화형 작업이야. 승인 요청하지 말고 구현해."); err != nil {
		t.Fatal(err)
	}
	input := json.RawMessage(`{"command":"install required dependency","description":"required implementation prerequisite"}`)
	decision, err := Permission("session", "Bash", input)
	if err != nil {
		t.Fatal(err)
	}
	if decision.Deny {
		t.Fatalf("attended task must leave approval to the normal host flow: %#v", decision)
	}
}

func TestGoalLoopWithInteractionAllowedKeepsNormalApprovalFlow(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture(
		"session",
		"/goal 장시간 루프로 진행하되 승인이나 질문을 요청해도 돼.",
	); err != nil {
		t.Fatal(err)
	}
	input := json.RawMessage(`{"command":"install required dependency"}`)
	decision, err := Permission("session", "Bash", input)
	if err != nil {
		t.Fatal(err)
	}
	if decision.Deny {
		t.Fatalf("interaction-enabled Goal/Loop must preserve host approval: %#v", decision)
	}
}

func TestAcceptedLoopProjectionControlsPermissionBoundary(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	_, active, err := AdoptLoopContract(
		"unattended",
		LoopProjection{
			SourceDigest:          digest("loop-one"),
			ExecutionMode:         ExecutionUnattendedGoalLoop,
			VerificationOwner:     VerificationUser,
			InteractionMode:       InteractionForbidden,
			ExcludedActionClasses: []string{ActionAgentValidation},
		},
	)
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	input := json.RawMessage(`{"command":"install required dependency"}`)
	decision, err := Permission("unattended", "Bash", input)
	if err != nil || !decision.Deny {
		t.Fatalf("accepted unattended projection deny=%v err=%v", decision.Deny, err)
	}

	_, active, err = AdoptLoopContract(
		"attended",
		LoopProjection{
			SourceDigest:      digest("loop-two"),
			ExecutionMode:     ExecutionAttended,
			VerificationOwner: VerificationAgent,
			InteractionMode:   InteractionForbidden,
		},
	)
	if err != nil || !active {
		t.Fatalf("attended active=%v err=%v", active, err)
	}
	decision, err = Permission("attended", "Bash", input)
	if err != nil || decision.Deny {
		t.Fatalf("attended LoopRun must preserve normal approval: %#v err=%v", decision, err)
	}
}

func TestCombinedNoApprovalOrQuestionPhraseIsCaptured(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	state, active, err := Capture(
		"session",
		"/goal 무인 장시간 루프에서 승인이나 질문을 요청하지 말고 계속해.",
	)
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	if state.ExecutionMode != ExecutionUnattendedGoalLoop || state.InteractionMode != InteractionForbidden {
		t.Fatalf("combined interaction restriction was not captured: %#v", state)
	}
}

func TestForbiddenBlockingQuestionNeverBecomesAWaitState(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture(
		"session",
		"/goal 무인 장시간 루프에서 추가 질문하지 말고 계속해.",
	); err != nil {
		t.Fatal(err)
	}
	for attempt := 0; attempt < 3; attempt++ {
		resume, err := ContinueWithoutInput("session")
		if err != nil || !resume {
			t.Fatalf("attempt=%d resume=%v err=%v", attempt, resume, err)
		}
	}
	state, err := Load("session")
	if err != nil {
		t.Fatal(err)
	}
	if state.InputContinuationCount != 3 || len(state.DeferredIntents) != 1 {
		t.Fatalf("question deferral was not durable and deduplicated: %#v", state)
	}
}

func TestOneBlockedActionDoesNotExcludeCoreWork(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	if _, _, err := Capture("session", "검증은 내가 하고 구현에만 집중해"); err != nil {
		t.Fatal(err)
	}
	validation := json.RawMessage(`{"command":"execute smoke validation"}`)
	if decision, err := Preflight("session", "Bash", validation); err != nil || !decision.Deny {
		t.Fatalf("validation deny=%v err=%v", decision.Deny, err)
	}
	core := json.RawMessage(`{"command":"compile production source"}`)
	if decision, err := Preflight("session", "Bash", core); err != nil || decision.Deny {
		t.Fatalf("independent core work deny=%v err=%v", decision.Deny, err)
	}
}
