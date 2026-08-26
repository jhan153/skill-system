package workcontract

import (
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
