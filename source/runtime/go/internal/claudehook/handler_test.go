package claudehook

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestClaudeEventSurfaceAndPromptIDCorrection(t *testing.T) {
	state := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", state)
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	want := map[string]bool{
		"SessionStart": true, "UserPromptSubmit": true, "Stop": true, "Notification": true,
	}
	if len(supportedEvents) != len(want) {
		t.Fatalf("event count=%d want=%d", len(supportedEvents), len(want))
	}
	for name := range want {
		if !supportedEvents[name] {
			t.Fatalf("missing event %s", name)
		}
	}
	for _, forbidden := range []string{"PreToolUse", "PermissionRequest", "PostToolUse", "PreCompact", "PostCompact"} {
		if supportedEvents[forbidden] {
			t.Fatalf("unexpected Claude event %s", forbidden)
		}
	}

	output := Handle(Event{HookEventName: "UserPromptSubmit", SessionID: "s", PromptID: "prompt-1", Prompt: "아니 그게 아니라 설명해"})
	if output == nil {
		t.Fatal("correction context missing")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	if specific["hookEventName"] != "UserPromptSubmit" || specific["additionalContext"] == "" {
		t.Fatalf("unexpected correction output: %#v", output)
	}
	output = Handle(Event{HookEventName: "Stop", SessionID: "s", PromptID: "prompt-1", LastAssistantMessage: "맞습니다. 지금부터 다시 확인하겠습니다."})
	if output == nil || output["decision"] != "block" || output["reason"] == "" {
		t.Fatalf("recovery stop was not blocked: %#v", output)
	}
	if _, present := output["continue"]; present {
		t.Fatalf("Stop continuation must use decision block: %#v", output)
	}
	output = Handle(Event{HookEventName: "Stop", SessionID: "s", PromptID: "prompt-1", StopHookActive: true, LastAssistantMessage: "원인은 요청을 잘못 분류한 것입니다."})
	if output != nil {
		t.Fatalf("active Stop hook was re-blocked: %#v", output)
	}
}

func TestClaudeFallbackSequenceDoesNotReuseOlderCorrection(t *testing.T) {
	state := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", state)
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	if Handle(Event{HookEventName: "UserPromptSubmit", SessionID: "legacy", Prompt: "아니 요청한 게 아니야"}) == nil {
		t.Fatal("legacy correction context missing")
	}
	if output := Handle(Event{HookEventName: "Stop", SessionID: "legacy", LastAssistantMessage: "맞습니다. 앞으로 다시 보겠습니다."}); output == nil || output["decision"] != "block" {
		t.Fatalf("legacy correction did not block: %#v", output)
	}
	if output := Handle(Event{HookEventName: "UserPromptSubmit", SessionID: "legacy", Prompt: "다음 작업을 시작해"}); output != nil {
		t.Fatalf("ordinary prompt produced context: %#v", output)
	}
	if output := Handle(Event{HookEventName: "Stop", SessionID: "legacy", LastAssistantMessage: "맞습니다. 앞으로 다시 보겠습니다."}); output != nil {
		t.Fatalf("older correction leaked into a later turn: %#v", output)
	}

	entries, err := os.ReadDir(filepath.Join(state, "claude-turns"))
	if err != nil || len(entries) != 1 {
		t.Fatalf("turn state entries=%d err=%v", len(entries), err)
	}
	raw, err := os.ReadFile(filepath.Join(state, "claude-turns", entries[0].Name()))
	if err != nil {
		t.Fatal(err)
	}
	if string(raw) == "" || json.Valid(raw) == false || containsRaw(string(raw), "legacy") {
		t.Fatalf("turn state is invalid or contains raw identity: %q", raw)
	}
}

func TestClaudeSessionContextAndNotificationMapping(t *testing.T) {
	state := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", state)
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	manifest := "schema_version: 1\nproject_id: demo\nknowledge_base:\n  root: docs/knowledge\n"
	if err := os.WriteFile(filepath.Join(root, "project-context.yaml"), []byte(manifest), 0o600); err != nil {
		t.Fatal(err)
	}
	output := Handle(Event{HookEventName: "SessionStart", SessionID: "s", Source: "startup", Cwd: root})
	if output == nil {
		t.Fatal("manifest context missing")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	if specific["hookEventName"] != "SessionStart" || specific["additionalContext"] == "" {
		t.Fatalf("unexpected context output: %#v", output)
	}

	for _, kind := range []string{"permission_prompt", "idle_prompt", "elicitation_dialog", "agent_needs_input", "agent_completed"} {
		message, ok := notificationMessage(Event{NotificationType: kind, Message: "status", Cwd: root, Effort: Effort{Level: "max"}})
		if !ok || message.Topic == "" || message.Model != "claude-max" {
			t.Fatalf("notification %s not mapped: %#v ok=%v", kind, message, ok)
		}
	}
	if _, ok := notificationMessage(Event{NotificationType: "auth_success"}); ok {
		t.Fatal("unregistered notification type was mapped")
	}
}

func containsRaw(value, part string) bool {
	for index := 0; index+len(part) <= len(value); index++ {
		if value[index:index+len(part)] == part {
			return true
		}
	}
	return false
}
