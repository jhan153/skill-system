package execguard

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestSafeShellWrapperIsRewrittenBeforeApproval(t *testing.T) {
	stateRoot, workspace, _ := testEnvironment(t)
	event := Event{
		SessionID: "wrapper", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
		ToolInput: commandJSON(t, `zsh -lc "rg -n execguard source"`),
	}
	decision, err := Preflight(event)
	if err != nil {
		t.Fatal(err)
	}
	if !decision.Rewrite || decision.Deny {
		t.Fatalf("unexpected decision: %#v", decision)
	}
	if command := decision.UpdatedInput["command"]; command != "rg -n execguard source" {
		t.Fatalf("unexpected rewrite: %#v", command)
	}
	if entries, err := os.ReadDir(filepath.Join(stateRoot, "exec-guard")); err != nil || len(entries) != 1 {
		t.Fatalf("bounded attempt state missing: entries=%v err=%v", entries, err)
	}
}

func TestShellSpecificWrapperAndTextAuthoringAreDenied(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	cases := []string{
		`zsh -lc 'prompt=$1; shift; exec codex "$@" < "$prompt"'`,
		`cat > notes.md`,
		`python3 -`,
	}
	for index, command := range cases {
		decision, err := Preflight(Event{
			SessionID: "deny", TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-" + string(rune('a'+index)),
			PermissionMode: "default", ToolInput: commandJSON(t, command),
		})
		if err != nil {
			t.Fatal(err)
		}
		if !decision.Deny || !strings.Contains(decision.Reason, "terminal") {
			t.Fatalf("command %q was not terminally denied: %#v", command, decision)
		}
	}
}

func TestInlineInterpreterEvaluatorsAreDeniedBeforeApproval(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{
		SessionID: "inline-eval", TurnID: "turn", Cwd: workspace,
		Prompt: "프로젝트 명령을 실행해",
	}); err != nil {
		t.Fatal(err)
	}
	cases := []string{
		`python3 -c 'import os; os.execv("./dentru", ["./dentru", os.getenv("SERVICE_TOKEN", "")])'`,
		`/usr/bin/python3.12 -I -c 'print("opaque")'`,
		`env python3 -c 'print("opaque")'`,
		`node --eval 'process.exit(0)'`,
		`ruby -e 'exec("true")'`,
		`perl -e 'exec "true"'`,
		`osascript -e 'do shell script "true"'`,
		`pwsh -Command 'Start-Process true'`,
		`zsh -ic 'rg -n execguard source'`,
		`bash --noprofile -c 'rg -n execguard source'`,
	}
	for index, command := range cases {
		decision, err := Preflight(Event{
			SessionID: "inline-eval", TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-" + string(rune('a'+index)),
			PermissionMode: "default", ToolInput: commandJSON(t, command),
		})
		if err != nil {
			t.Fatal(err)
		}
		if !decision.Deny || !strings.Contains(strings.ToLower(decision.Reason), "opaque") {
			t.Fatalf("inline evaluator %q reached approval: %#v", command, decision)
		}
	}
}

func TestAuditableInterpreterEntrypointsRemainAdmitted(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	commands := []string{
		"python3 source/tools/generate_targets.py --target runtime",
		"python3 -m pytest source/runtime/tests",
		"node scripts/check.js",
	}
	for index, command := range commands {
		decision, err := Preflight(Event{
			SessionID: "auditable-interpreter-" + string(rune('a'+index)), TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
			ToolInput: commandJSON(t, command),
		})
		if err != nil || decision.Deny {
			t.Fatalf("auditable interpreter entrypoint was denied for %q: decision=%#v err=%v", command, decision, err)
		}
	}
}

func TestTurnGrantAutoAllowsRuntimeInstallation(t *testing.T) {
	_, workspace, codexHome := testEnvironment(t)
	if err := Capture(Event{
		SessionID: "install", TurnID: "turn", Cwd: workspace,
		Prompt: "Skill System runtime companion을 Codex 홈에 설치하고 동기화해",
	}); err != nil {
		t.Fatal(err)
	}
	command := "rsync -a build/ " + codexHome + "/"
	event := Event{
		SessionID: "install", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-install", PermissionMode: "default",
		ToolInput: commandJSON(t, command),
	}
	if decision, err := Preflight(event); err != nil || decision.Deny {
		t.Fatalf("authorized preflight failed: decision=%#v err=%v", decision, err)
	}
	decision, err := Permission(event)
	if err != nil {
		t.Fatal(err)
	}
	if !decision.AllowPermission || decision.Deny {
		t.Fatalf("authorized installation did not bypass UI approval: %#v", decision)
	}
}

func TestUngrantableApprovalPromptsOnceAndDontAskNeverWaits(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "prompt", TurnID: "turn", Cwd: workspace, Prompt: "코드를 읽어봐"}); err != nil {
		t.Fatal(err)
	}
	event := Event{
		SessionID: "prompt", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-network", PermissionMode: "default",
		ToolInput: commandJSON(t, "curl https://example.com/archive"),
	}
	if decision, err := Preflight(event); err != nil || decision.Deny {
		t.Fatalf("interactive risk should reach one approval: decision=%#v err=%v", decision, err)
	}
	first, err := Permission(event)
	if err != nil {
		t.Fatal(err)
	}
	if first.Deny || first.AllowPermission || first.SystemMessage == "" {
		t.Fatalf("unexpected first permission decision: %#v", first)
	}
	second, err := Permission(event)
	if err != nil {
		t.Fatal(err)
	}
	if !second.Deny {
		t.Fatalf("same purpose requested approval twice: %#v", second)
	}

	if err := Capture(Event{SessionID: "dont-ask", TurnID: "turn", Cwd: workspace, Prompt: "코드를 읽어봐"}); err != nil {
		t.Fatal(err)
	}
	dontAsk, err := Preflight(Event{
		SessionID: "dont-ask", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-network", PermissionMode: "dontAsk",
		ToolInput: commandJSON(t, "curl https://example.com/archive"),
	})
	if err != nil {
		t.Fatal(err)
	}
	if !dontAsk.Deny {
		t.Fatalf("dontAsk attempted to wait for approval: %#v", dontAsk)
	}

	if err := Capture(Event{SessionID: "bypass", TurnID: "turn", Cwd: workspace, Prompt: "코드를 읽어봐"}); err != nil {
		t.Fatal(err)
	}
	bypass, err := Preflight(Event{
		SessionID: "bypass", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-network", PermissionMode: "bypassPermissions",
		ToolInput: commandJSON(t, "curl https://example.com/archive"),
	})
	if err != nil {
		t.Fatal(err)
	}
	if !bypass.Deny {
		t.Fatalf("bypassPermissions broadened the user task scope: %#v", bypass)
	}
}

func TestProjectLaunchRequiresTurnGrant(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	executable := filepath.Join(workspace, "Bin", "Editor")
	if err := Capture(Event{SessionID: "launch", TurnID: "turn", Cwd: workspace, Prompt: "Engine 먹통을 조사하고 실행해서 재현해"}); err != nil {
		t.Fatal(err)
	}
	event := Event{
		SessionID: "launch", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-launch", PermissionMode: "default",
		ToolInput: commandJSON(t, executable+" --smoke-frames=240"),
	}
	if decision, err := Preflight(event); err != nil || decision.Deny {
		t.Fatalf("authorized project launch failed: decision=%#v err=%v", decision, err)
	}
	if decision, err := Permission(event); err != nil || !decision.AllowPermission {
		t.Fatalf("authorized project launch did not auto-allow: decision=%#v err=%v", decision, err)
	}

	if err := Capture(Event{SessionID: "no-launch", TurnID: "turn", Cwd: workspace, Prompt: "코드를 설명해"}); err != nil {
		t.Fatal(err)
	}
	denied, err := Preflight(Event{
		SessionID: "no-launch", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-launch", PermissionMode: "default",
		ToolInput: commandJSON(t, executable+" --smoke-frames=240"),
	})
	if err != nil {
		t.Fatal(err)
	}
	if !denied.Deny {
		t.Fatalf("unrequested project launch was allowed: %#v", denied)
	}
}

func TestHistoricalCommandFamiliesUseTurnAuthorityInsteadOfExactPrefixes(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	cases := []struct {
		name    string
		prompt  string
		command string
	}{
		{name: "git network read", prompt: "현재 저장소를 업데이트하고 pull해", command: "git pull origin main"},
		{name: "host dependency install", prompt: "Go를 brew로 설치해", command: "brew install go"},
		{name: "scoped cleanup", prompt: "불필요한 cache 파일을 삭제하고 정리해", command: "rm -f cache.bin"},
		{name: "debugger attach", prompt: "Engine 프로세스를 디버그해서 먹통을 조사해", command: "lldb --attach-pid 1234"},
	}
	for index, testCase := range cases {
		session := "historical-" + string(rune('a'+index))
		if err := Capture(Event{SessionID: session, TurnID: "turn", Cwd: workspace, Prompt: testCase.prompt}); err != nil {
			t.Fatal(err)
		}
		event := Event{
			SessionID: session, TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
			ToolInput: commandJSON(t, testCase.command),
		}
		if decision, err := Preflight(event); err != nil || decision.Deny {
			t.Fatalf("%s preflight failed: decision=%#v err=%v", testCase.name, decision, err)
		}
		if decision, err := Permission(event); err != nil || !decision.AllowPermission || decision.Deny {
			t.Fatalf("%s did not auto-allow: decision=%#v err=%v", testCase.name, decision, err)
		}
	}
}

func TestNormalBuildAndGenerationCommandsNeverNeedTurnSpecificApproval(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	commands := []string{
		"go test ./internal/execguard ./internal/hook",
		"python3 source/tools/generate_targets.py --target runtime",
		"python3 source/tools/generate_targets.py --target plugins",
	}
	for index, command := range commands {
		event := Event{
			SessionID: "normal-build-" + string(rune('a'+index)), TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
			ToolInput: commandJSON(t, command),
		}
		if decision, err := Preflight(event); err != nil || decision.Deny {
			t.Fatalf("normal build preflight failed for %q: decision=%#v err=%v", command, decision, err)
		}
		if decision, err := Permission(event); err != nil || !decision.AllowPermission || decision.Deny {
			t.Fatalf("normal build command needed approval for %q: decision=%#v err=%v", command, decision, err)
		}
	}
}

func TestBenignDiagnosticAndBuildRedirectionDoesNotBecomeTextAuthoring(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	commands := []string{
		"ps -axo pid,command 2>/dev/null",
		"go test ./internal/execguard > test-report.txt",
	}
	for index, command := range commands {
		decision, err := Preflight(Event{
			SessionID: "redirect-" + string(rune('a'+index)), TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
			ToolInput: commandJSON(t, command),
		})
		if err != nil || decision.Deny {
			t.Fatalf("benign redirection was denied for %q: decision=%#v err=%v", command, decision, err)
		}
	}
	writer, err := Preflight(Event{
		SessionID: "redirect-writer", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
		ToolInput: commandJSON(t, "echo generated > source.txt"),
	})
	if err != nil || !writer.Deny {
		t.Fatalf("shell text authoring escaped apply_patch enforcement: decision=%#v err=%v", writer, err)
	}
}

func TestOpaqueShellAndFindExecCannotBypassPreflight(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "shell-bypass", TurnID: "turn", Cwd: workspace, Prompt: "프로젝트 명령을 실행해"}); err != nil {
		t.Fatal(err)
	}
	for index, command := range []string{"bash", `find . -exec sh -c 'rm -f hidden' \;`} {
		decision, err := Preflight(Event{
			SessionID: "shell-bypass", TurnID: "turn", Cwd: workspace,
			ToolName: "Bash", ToolUseID: "tool-" + string(rune('a'+index)), PermissionMode: "default",
			ToolInput: commandJSON(t, command),
		})
		if err != nil || !decision.Deny {
			t.Fatalf("opaque shell bypass was not denied for %q: decision=%#v err=%v", command, decision, err)
		}
	}
	checkedIn, err := Preflight(Event{
		SessionID: "shell-script", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-script", PermissionMode: "default",
		ToolInput: commandJSON(t, "bash scripts/check.sh"),
	})
	if err != nil {
		t.Fatal(err)
	}
	if !checkedIn.Deny {
		t.Fatalf("script launch without a turn grant should be denied, got %#v", checkedIn)
	}
}

func TestFindExecAndRebaseDoNotInheritReadOrOrdinaryWriteAuthority(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "find-exec", TurnID: "turn", Cwd: workspace, Prompt: "파일 목록을 읽어봐"}); err != nil {
		t.Fatal(err)
	}
	findEvent := Event{
		SessionID: "find-exec", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-find", PermissionMode: "default",
		ToolInput: commandJSON(t, `find . -exec rm -f {} \;`),
	}
	if decision, err := Preflight(findEvent); err != nil || decision.Deny {
		t.Fatalf("scoped find exec should reach one authority decision: decision=%#v err=%v", decision, err)
	}
	if decision, err := Permission(findEvent); err != nil || decision.AllowPermission || decision.Deny || decision.SystemMessage == "" {
		t.Fatalf("find exec inherited read authority: decision=%#v err=%v", decision, err)
	}

	if err := Capture(Event{SessionID: "rebase", TurnID: "turn", Cwd: workspace, Prompt: "코드를 구현해"}); err != nil {
		t.Fatal(err)
	}
	rebaseEvent := Event{
		SessionID: "rebase", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-rebase", PermissionMode: "default",
		ToolInput: commandJSON(t, "git rebase main"),
	}
	if decision, err := Preflight(rebaseEvent); err != nil || decision.Deny {
		t.Fatalf("rebase should reach one history-rewrite decision: decision=%#v err=%v", decision, err)
	}
	if decision, err := Permission(rebaseEvent); err != nil || decision.AllowPermission || decision.Deny || decision.SystemMessage == "" {
		t.Fatalf("rebase inherited ordinary workspace-write authority: decision=%#v err=%v", decision, err)
	}
}

func TestContinuationPreservesTerminalApprovalStateUntilExplicitRetry(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "continuation", TurnID: "turn-1", Cwd: workspace, Prompt: "코드를 읽어봐"}); err != nil {
		t.Fatal(err)
	}
	event := Event{
		SessionID: "continuation", TurnID: "turn-1", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "default",
		ToolInput: commandJSON(t, "curl https://example.com/archive"),
	}
	if decision, err := Permission(event); err != nil || decision.Deny || decision.SystemMessage == "" {
		t.Fatalf("first approval request was not recorded: decision=%#v err=%v", decision, err)
	}
	if err := Capture(Event{SessionID: "continuation", TurnID: "turn-2", Cwd: workspace, Prompt: "Continue other authorized work"}); err != nil {
		t.Fatal(err)
	}
	event.TurnID = "turn-2"
	event.ToolUseID = "tool-2"
	if decision, err := Permission(event); err != nil || !decision.Deny {
		t.Fatalf("continuation reopened a terminal approval: decision=%#v err=%v", decision, err)
	}
	if err := Capture(Event{SessionID: "continuation", TurnID: "turn-3", Cwd: workspace, Prompt: "다시 시도해"}); err != nil {
		t.Fatal(err)
	}
	event.TurnID = "turn-3"
	event.ToolUseID = "tool-3"
	if decision, err := Permission(event); err != nil || decision.Deny || decision.SystemMessage == "" {
		t.Fatalf("explicit retry did not reset the attempt: decision=%#v err=%v", decision, err)
	}
}

func TestNewSubstantiveTurnDoesNotInheritPriorAuthority(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "new-task", TurnID: "turn-1", Cwd: workspace, Prompt: "dependency를 설치하고 업데이트해"}); err != nil {
		t.Fatal(err)
	}
	if err := Capture(Event{SessionID: "new-task", TurnID: "turn-2", Cwd: workspace, Prompt: "새 기능을 구현해봐"}); err != nil {
		t.Fatal(err)
	}
	decision, err := Preflight(Event{
		SessionID: "new-task", TurnID: "turn-2", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "tool-1", PermissionMode: "dontAsk",
		ToolInput: commandJSON(t, "curl https://example.com/archive"),
	})
	if err != nil || !decision.Deny {
		t.Fatalf("new task inherited prior network authority: decision=%#v err=%v", decision, err)
	}
}

func TestExactRepeatStopsUntilRelevantChange(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "repeat", TurnID: "turn", Cwd: workspace, Prompt: "검색하고 구현해"}); err != nil {
		t.Fatal(err)
	}
	search := Event{
		SessionID: "repeat", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "search-1", PermissionMode: "default",
		ToolInput: commandJSON(t, "rg -n execguard source"),
	}
	if first, err := Preflight(search); err != nil || first.Deny {
		t.Fatalf("first search failed: decision=%#v err=%v", first, err)
	}
	search.ToolUseID = "search-2"
	if repeated, err := Preflight(search); err != nil || !repeated.Deny {
		t.Fatalf("unchanged repeat was not denied: decision=%#v err=%v", repeated, err)
	}

	patch := Event{
		SessionID: "repeat", TurnID: "turn", Cwd: workspace,
		ToolName: "apply_patch", ToolUseID: "patch-1", PermissionMode: "default",
		ToolInput:    commandJSON(t, "*** Begin Patch\n*** Update File: source/x.go\n@@\n-old\n+new\n*** End Patch"),
		ToolResponse: json.RawMessage(`{"success":true}`),
	}
	if err := Observe(patch); err != nil {
		t.Fatal(err)
	}
	search.ToolUseID = "search-3"
	if afterChange, err := Preflight(search); err != nil || afterChange.Deny {
		t.Fatalf("search after relevant change was denied: decision=%#v err=%v", afterChange, err)
	}
}

func TestBroadDeletionIsTerminalEvenWhenCleanupWasRequested(t *testing.T) {
	_, workspace, _ := testEnvironment(t)
	if err := Capture(Event{SessionID: "delete", TurnID: "turn", Cwd: workspace, Prompt: "불필요한 파일을 삭제하고 정리해"}); err != nil {
		t.Fatal(err)
	}
	decision, err := Preflight(Event{
		SessionID: "delete", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "delete-1", PermissionMode: "default",
		ToolInput: commandJSON(t, "rm -rf /"),
	})
	if err != nil {
		t.Fatal(err)
	}
	if !decision.Deny {
		t.Fatalf("broad deletion was not denied: %#v", decision)
	}
}

func TestPersistedStateContainsNoPromptOrCommandText(t *testing.T) {
	stateRoot, workspace, _ := testEnvironment(t)
	secret := "raw-secret-value"
	if err := Capture(Event{SessionID: "privacy", TurnID: "turn", Cwd: workspace, Prompt: "이 코드를 구현해 " + secret}); err != nil {
		t.Fatal(err)
	}
	if _, err := Preflight(Event{
		SessionID: "privacy", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "privacy-1", PermissionMode: "default",
		ToolInput: commandJSON(t, "rg -n another-secret source"),
	}); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(statePath("privacy"))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(raw), secret) || strings.Contains(string(raw), "another-secret") || !strings.HasPrefix(statePath("privacy"), stateRoot) {
		t.Fatalf("raw execution data leaked into state: %s", raw)
	}
}

func testEnvironment(t *testing.T) (stateRoot, workspace, codexHome string) {
	t.Helper()
	stateRoot = t.TempDir()
	workspace = filepath.Join(stateRoot, "workspace")
	codexHome = filepath.Join(stateRoot, "codex-home")
	for _, path := range []string{filepath.Join(workspace, ".git"), filepath.Join(workspace, "Bin"), codexHome} {
		if err := os.MkdirAll(path, 0o700); err != nil {
			t.Fatal(err)
		}
	}
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", stateRoot)
	t.Setenv("CODEX_HOME", codexHome)
	return stateRoot, workspace, codexHome
}

func commandJSON(t *testing.T, command string) json.RawMessage {
	t.Helper()
	raw, err := json.Marshal(map[string]any{"command": command})
	if err != nil {
		t.Fatal(err)
	}
	return raw
}
