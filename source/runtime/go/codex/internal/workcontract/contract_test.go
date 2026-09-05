package workcontract

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
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
	if !contractIDPattern.MatchString(state.ContractID) || state.IdentityKind != IdentityExplicitGeneration {
		t.Fatalf("missing explicit contract identity: %#v", state)
	}
	contractID := state.ContractID
	for _, class := range []string{ActionAgentValidation, ActionTestAuthoring, ActionValidationArtifact, ActionMeta} {
		if !isExcluded(state, class) {
			t.Errorf("missing exclusion %s in %#v", class, state.ExcludedActionClasses)
		}
	}
	context := Context(state)
	if !strings.Contains(context, "user-verification-needed") ||
		!strings.Contains(context, "The host-selected reviewer owns approval decisions") ||
		!strings.Contains(context, "Do not ask a blocking question") {
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
	if state.ContractID != contractID {
		t.Fatalf("policy update changed generation: before=%q after=%q", contractID, state.ContractID)
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
	state, _, err := Capture("session", prompt)
	if err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(statePath("session"))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(raw), prompt) || strings.Contains(string(raw), "raw-secret-value") {
		t.Fatal("raw prompt was persisted")
	}
	if !strings.Contains(string(raw), state.ContractID) || strings.Contains(state.ContractID, digest(prompt)[:16]) {
		t.Fatalf("persisted identity is missing or prompt-derived: id=%q state=%s", state.ContractID, raw)
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

func TestUnmarkedPromptPreservesContractIDAndRestrictions(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	before := restrictedStateWithRuntimeHistory(t, "unmarked")

	after, active, err := Capture("unmarked", "이제 결제 파서를 만드는 완전히 다른 작업을 진행해")
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	if !reflect.DeepEqual(after, before) {
		t.Fatalf("unmarked prompt changed the generation:\nbefore=%#v\nafter=%#v", before, after)
	}
}

func TestExplicitGoalRebindChangesContractIDAndClearsPriorState(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	before := restrictedStateWithRuntimeHistory(t, "rebind")

	after, active, err := Capture("rebind", "/work-contract rebind 새 결제 파서 구현을 시작해")
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	if after.ContractID == before.ContractID || after.IdentityKind != IdentityExplicitGeneration {
		t.Fatalf("rebind did not create a fresh explicit generation: before=%#v after=%#v", before, after)
	}
	if after.Revision != 1 || after.VerificationOwner != VerificationAgent ||
		after.InteractionMode != InteractionAllowed || after.ExecutionMode != ExecutionAttended {
		t.Fatalf("rebind did not start from defaults: %#v", after)
	}
	if len(after.ExcludedActionClasses) != 0 || after.ActiveIntent != nil ||
		len(after.DeferredIntents) != 0 || after.InputContinuationCount != 0 {
		t.Fatalf("prior generation state leaked through rebind: %#v", after)
	}
}

func TestExplicitResetIsIdempotentAndRetiresGeneration(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	before, active, err := Capture("reset", "/goal 무인 장시간 작업으로 검증은 내가 할게")
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	for range 2 {
		state, active, err := Capture("reset", "/work-contract reset")
		if err != nil || active || Context(state) != "" {
			t.Fatalf("reset active=%v err=%v state=%#v", active, err, state)
		}
	}
	if _, err := os.Stat(statePath("reset")); !os.IsNotExist(err) {
		t.Fatalf("reset left state file: %v", err)
	}
	after, active, err := Capture("reset", "/goal 새 구현을 계속해")
	if err != nil || !active || after.ContractID == before.ContractID {
		t.Fatalf("reactivation reused retired identity: active=%v err=%v before=%q after=%q", active, err, before.ContractID, after.ContractID)
	}
}

func TestLegacyV1RestrictionsPersistUntilExplicitRebind(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	writeLegacyState(t, "legacy")

	legacy, err := Load("legacy")
	if err != nil {
		t.Fatal(err)
	}
	if legacy.SchemaVersion != schemaVersion || legacy.ContractID != legacyContractID ||
		legacy.IdentityKind != IdentityLegacySession || legacy.VerificationOwner != VerificationUser ||
		!isExcluded(legacy, ActionAgentValidation) {
		t.Fatalf("legacy restrictions were not preserved: %#v", legacy)
	}
	afterPrompt, active, err := Capture("legacy", "새로 보이는 일반 구현 요청")
	if err != nil || !active || afterPrompt.ContractID != legacyContractID ||
		afterPrompt.VerificationOwner != VerificationUser {
		t.Fatalf("unmarked prompt retired legacy state: active=%v err=%v state=%#v", active, err, afterPrompt)
	}

	rebound, active, err := Capture("legacy", "/goal 새 작업을 시작해")
	if err != nil || !active || rebound.ContractID == legacyContractID ||
		rebound.IdentityKind != IdentityExplicitGeneration || rebound.VerificationOwner != VerificationAgent ||
		len(rebound.ExcludedActionClasses) != 0 {
		t.Fatalf("explicit rebind did not retire legacy state: active=%v err=%v state=%#v", active, err, rebound)
	}
}

func TestExplicitResetAndRebindRecoverFromCorruptState(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	writeRawState(t, "corrupt-reset", []byte("{not-json"))
	if _, active, err := Capture("corrupt-reset", "ordinary prompt"); err == nil || active {
		t.Fatalf("corrupt state was treated as active: active=%v err=%v", active, err)
	}
	if _, active, err := Capture("corrupt-reset", "/work-contract reset"); err != nil || active {
		t.Fatalf("explicit reset did not recover corrupt state: active=%v err=%v", active, err)
	}

	writeRawState(t, "corrupt-rebind", []byte(`{"schema_version":2,"revision":1}`))
	if _, err := Load("corrupt-rebind"); err == nil {
		t.Fatal("missing current identity was accepted")
	}
	malformedBefore, err := os.ReadFile(statePath("corrupt-rebind"))
	if err != nil {
		t.Fatal(err)
	}
	if _, active, err := Capture("corrupt-rebind", "검증은 내가 할게"); err == nil || active {
		t.Fatalf("ordinary policy update replaced malformed identity: active=%v err=%v", active, err)
	}
	malformedAfter, err := os.ReadFile(statePath("corrupt-rebind"))
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(malformedAfter, malformedBefore) {
		t.Fatalf("malformed state changed without explicit rebind: before=%s after=%s", malformedBefore, malformedAfter)
	}
	rebound, active, err := Capture("corrupt-rebind", "/work-contract rebind")
	if err != nil || !active || rebound.IdentityKind != IdentityExplicitGeneration ||
		!contractIDPattern.MatchString(rebound.ContractID) {
		t.Fatalf("explicit rebind did not recover malformed identity: active=%v err=%v state=%#v", active, err, rebound)
	}
}

func TestConcurrentMutationCannotRestoreReboundOrResetGeneration(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	for index := range 32 {
		sessionID := fmt.Sprintf("concurrent-rebind-%d", index)
		before := restrictedStateWithRuntimeHistory(t, sessionID)
		start := make(chan struct{})
		rebindResult := make(chan State, 1)
		errResult := make(chan error, 2)
		go func() {
			<-start
			state, _, err := Capture(sessionID, "/work-contract rebind")
			rebindResult <- state
			errResult <- err
		}()
		go func() {
			<-start
			_, err := Preflight(sessionID, "Bash", json.RawMessage(`{"command":"run the tests"}`))
			errResult <- err
		}()
		close(start)
		rebound := <-rebindResult
		for range 2 {
			if err := <-errResult; err != nil {
				t.Fatal(err)
			}
		}
		after, err := Load(sessionID)
		if err != nil {
			t.Fatal(err)
		}
		if after.ContractID != rebound.ContractID || after.ContractID == before.ContractID ||
			after.IdentityKind != IdentityExplicitGeneration {
			t.Fatalf("generation-relative writer restored old state: before=%#v rebound=%#v after=%#v", before, rebound, after)
		}
	}

	for index := range 32 {
		sessionID := fmt.Sprintf("concurrent-reset-%d", index)
		if _, active, err := Capture(sessionID, "/goal 무인 장시간 작업으로 질문하지 마"); err != nil || !active {
			t.Fatalf("active=%v err=%v", active, err)
		}
		start := make(chan struct{})
		errResult := make(chan error, 2)
		go func() {
			<-start
			_, err := ContinueWithoutInput(sessionID)
			errResult <- err
		}()
		go func() {
			<-start
			_, _, err := Capture(sessionID, "/work-contract reset")
			errResult <- err
		}()
		close(start)
		for range 2 {
			if err := <-errResult; err != nil {
				t.Fatal(err)
			}
		}
		if _, err := Load(sessionID); !os.IsNotExist(err) {
			t.Fatalf("generation-relative writer recreated reset state: %v", err)
		}
	}
}

func TestStateWritesRequireOwningSessionLock(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	state, err := newGeneration()
	if err != nil {
		t.Fatal(err)
	}
	if err := writeState(nil, "unlocked", state); err == nil {
		t.Fatal("state write succeeded without a session lock")
	}
	wrongLock, err := acquireSessionLock("other-session")
	if err != nil {
		t.Fatal(err)
	}
	defer wrongLock.release()
	if err := writeState(wrongLock, "unlocked", state); err == nil {
		t.Fatal("state write succeeded with another session's lock")
	}
}

func TestQuotedLifecycleLanguageDoesNotActivateResetOrRebind(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	_, active, err := Capture("quoted", "문서에서 `/goal 무인 장시간`과 “do not ask questions” 예시를 설명해")
	if err != nil || active {
		t.Fatalf("quoted policy activated a contract: active=%v err=%v", active, err)
	}

	before, active, err := Capture("quoted", "/goal 무인 장시간 구현으로 검증은 내가 할게")
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	after, active, err := Capture("quoted", "Explain \"/work-contract rebind\" and “reset the work contract” as documentation examples")
	if err != nil || !active || !reflect.DeepEqual(after, before) {
		t.Fatalf("quoted lifecycle text changed active generation: active=%v err=%v before=%#v after=%#v", active, err, before, after)
	}
}

func TestPreflightAndContinuationPreserveContractID(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	initial, active, err := Capture("roundtrip", "/goal 무인 장시간 작업으로 검증은 내가 하고 질문하지 마")
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	decision, err := Preflight("roundtrip", "Bash", json.RawMessage(`{"command":"run the tests"}`))
	if err != nil || !decision.Deny {
		t.Fatalf("preflight decision=%#v err=%v", decision, err)
	}
	if resume, err := ContinueWithoutInput("roundtrip"); err != nil || !resume {
		t.Fatalf("resume=%v err=%v", resume, err)
	}
	after, err := Load("roundtrip")
	if err != nil || after.ContractID != initial.ContractID || after.IdentityKind != initial.IdentityKind {
		t.Fatalf("state mutation changed identity: err=%v initial=%#v after=%#v", err, initial, after)
	}
}

func TestSourceInspectionDoesNotInheritExcludedValidationIntent(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	const sessionID = "source-inspection"
	if _, active, err := Capture(sessionID, "/goal implement the parser"); err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	plan := json.RawMessage(`{"plan":[{"step":"run the tests","status":"in_progress"}]}`)
	if decision, err := Preflight(sessionID, "update_plan", plan); err != nil || decision.Deny {
		t.Fatalf("plan decision=%#v err=%v", decision, err)
	}
	before, _, err := Capture(sessionID, "검증은 내가 할게")
	if err != nil || before.ActiveIntent == nil || before.ActiveIntent.Class != ActionAgentValidation {
		t.Fatalf("missing retained validation intent: err=%v state=%#v", err, before)
	}

	// The User Work Contract reserves source-reading prerequisites for core
	// work; validation_artifact means artifacts created to validate.
	cases := []struct {
		name    string
		tool    string
		field   string
		command string
	}{
		{"original rg search", "Bash", "command", "rg -n 'validation|harness' source/runtime/go/codex/internal/workcontract/contract.go"},
		{"Bash read", "Bash", "command", "cat source/validation/harness.go"},
		{"namespaced command", "functions.exec_command", "cmd", "cat source/core.go"},
		{"sed range", "shell_command", "cmd", "sed -n '1,80p' source/validation/harness.go"},
		{"sed final range", "exec_command", "cmd", "sed -n '10,$p' source/validation/harness.go"},
		{"quoted literal", "exec_command", "cmd", "rg --no-config -n 'validation; $(harness)' source"},
		{"option argument", "exec_command", "cmd", "rg --no-config -g '*_test.go' -e 'validation|harness' source"},
		{"option terminator", "exec_command", "cmd", "rg --no-config -- '--pre=validation-harness' source"},
		{"absolute reader", "exec_command", "cmd", "/bin/cat 'source/validation harness.go'"},
		{"numbered source", "Bash", "command", "nl -ba source/validation/harness.go"},
		{"numbered range pipeline", "Bash", "command", "sed -n '1,80p' source/validation/harness.go | nl -ba"},
		{"three reader stages", "Bash", "command", "cat source/validation/harness.go | sed -n '1,80p' | nl -ba"},
		{"quoted pipe in reader pipeline", "Bash", "command", "rg -n 'validation|harness' source | nl -ba"},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			raw, err := json.Marshal(map[string]any{
				testCase.field:  testCase.command,
				"justification": "Inspect validation harness source before implementation.",
			})
			if err != nil {
				t.Fatal(err)
			}
			decision, err := Preflight(sessionID, testCase.tool, raw)
			if err != nil || decision.Deny || decision.Rewrite {
				t.Fatalf("source inspection was excluded: decision=%#v err=%v", decision, err)
			}
		})
	}
	after, err := Load(sessionID)
	if err != nil || !reflect.DeepEqual(after, before) {
		t.Fatalf("source inspection changed contract state: err=%v before=%#v after=%#v", err, before, after)
	}
}

func TestSourceInspectionExceptionPreservesExcludedActions(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	cases := []struct {
		name  string
		tool  string
		input map[string]any
		class string
	}{
		{"validation execution", "exec_command", map[string]any{"cmd": "pytest tests/test_parser.py"}, ActionAgentValidation},
		{"test authoring", "apply_patch", map[string]any{"patch": "*** Begin Patch\n*** Add File: tests/parser_test.go\n+package tests\n*** End Patch"}, ActionTestAuthoring},
		{"artifact creation", "exec_command", map[string]any{"cmd": "mkdir validation-harness"}, ActionValidationArtifact},
		{"compound execution", "exec_command", map[string]any{"cmd": "cat source/core.go && run the tests"}, ActionAgentValidation},
		{"reader later in command", "exec_command", map[string]any{"cmd": "run the tests; cat source/core.go"}, ActionAgentValidation},
		{"pipeline execution", "exec_command", map[string]any{"cmd": "cat source/core.go | validation-harness"}, ActionValidationArtifact},
		{"pipeline starts with execution", "exec_command", map[string]any{"cmd": "validation-harness | nl -ba"}, ActionValidationArtifact},
		{"pipeline executes middle stage", "exec_command", map[string]any{"cmd": "cat source/core.go | validation-harness | nl -ba"}, ActionValidationArtifact},
		{"pipeline executes sed stage", "exec_command", map[string]any{"cmd": "cat source/core.go | sed -n '1e validation-harness' | nl -ba"}, ActionValidationArtifact},
		{"compound after read pipeline", "exec_command", map[string]any{"cmd": "sed -n '1,80p' source/core.go | nl -ba && run the tests"}, ActionAgentValidation},
		{"logical or is not a read pipe", "exec_command", map[string]any{"cmd": "cat source/validation/harness.go || nl -ba source/core.go"}, ActionValidationArtifact},
		{"redirected read pipeline", "exec_command", map[string]any{"cmd": "cat source/core.go | nl -ba > validation-harness.go"}, ActionValidationArtifact},
		{"command substitution", "exec_command", map[string]any{"cmd": "cat $(validation-harness)"}, ActionValidationArtifact},
		{"double quoted substitution", "exec_command", map[string]any{"cmd": "cat \"$(validation-harness)\""}, ActionValidationArtifact},
		{"redirected artifact", "exec_command", map[string]any{"cmd": "cat source/core.go > validation-harness.go"}, ActionValidationArtifact},
		{"sed in place", "exec_command", map[string]any{"cmd": "sed -i 's/validation/harness/g' source/core.go"}, ActionValidationArtifact},
		{"sed executable script", "exec_command", map[string]any{"cmd": "sed -n '1e validation-harness' source/core.go"}, ActionValidationArtifact},
		{"sed script file", "exec_command", map[string]any{"cmd": "sed -n '1,80p' -f validation-harness.sed source/core.go"}, ActionValidationArtifact},
		{"rg preprocessor", "exec_command", map[string]any{"cmd": "rg --no-config --pre validation-harness query source"}, ActionValidationArtifact},
		{"custom executable", "exec_command", map[string]any{"cmd": "/bin/../custom/cat validation-harness.go"}, ActionValidationArtifact},
		{"custom shell", "exec_command", map[string]any{"cmd": "cat source/validation/harness.go", "shell": "custom-shell"}, ActionValidationArtifact},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			sessionID := t.Name()
			if _, active, err := Capture(sessionID, "검증은 내가 할게"); err != nil || !active {
				t.Fatalf("active=%v err=%v", active, err)
			}
			raw, err := json.Marshal(testCase.input)
			if err != nil {
				t.Fatal(err)
			}
			decision, err := Preflight(sessionID, testCase.tool, raw)
			if err != nil || !decision.Deny || decision.Intent.Class != testCase.class {
				t.Fatalf("excluded action became runnable: decision=%#v err=%v", decision, err)
			}
		})
	}
}

func restrictedStateWithRuntimeHistory(t *testing.T, sessionID string) State {
	t.Helper()
	_, active, err := Capture(sessionID, "/goal 무인 장시간 작업으로 검증은 내가 하고 질문하지 마")
	if err != nil || !active {
		t.Fatalf("active=%v err=%v", active, err)
	}
	plan := json.RawMessage(`{"plan":[{"step":"implement parser","status":"in_progress"}]}`)
	if decision, err := Preflight(sessionID, "update_plan", plan); err != nil || decision.Deny || decision.Rewrite {
		t.Fatalf("plan decision=%#v err=%v", decision, err)
	}
	if decision, err := Preflight(sessionID, "Bash", json.RawMessage(`{"command":"run the tests"}`)); err != nil || !decision.Deny {
		t.Fatalf("validation decision=%#v err=%v", decision, err)
	}
	if resume, err := ContinueWithoutInput(sessionID); err != nil || !resume {
		t.Fatalf("resume=%v err=%v", resume, err)
	}
	state, err := Load(sessionID)
	if err != nil {
		t.Fatal(err)
	}
	return state
}

func writeLegacyState(t *testing.T, sessionID string) {
	t.Helper()
	raw, err := json.Marshal(map[string]any{
		"schema_version": 1, "revision": 4, "source_digest": strings.Repeat("a", 64),
		"verification_owner": VerificationUser, "interaction_mode": InteractionForbidden,
		"execution_mode":           ExecutionUnattendedGoalLoop,
		"excluded_action_classes":  []string{ActionAgentValidation},
		"active_intent":            map[string]string{"key": digest("core:legacy"), "class": ActionCore, "reason": ""},
		"deferred_intents":         []map[string]string{{"key": digest("validation"), "class": ActionAgentValidation, "reason": "excluded"}},
		"input_continuation_count": 2, "updated_at": "2026-09-04T00:00:00Z",
	})
	if err != nil {
		t.Fatal(err)
	}
	writeRawState(t, sessionID, raw)
}

func writeRawState(t *testing.T, sessionID string, raw []byte) {
	t.Helper()
	path := statePath(sessionID)
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, raw, 0o600); err != nil {
		t.Fatal(err)
	}
}
