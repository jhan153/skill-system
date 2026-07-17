package hook

import (
	"os"
	"path/filepath"
	"testing"
)

func TestEightEventSurfaceAndCorrectionOutput(t *testing.T) {
	state := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", state)
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	events := []string{"SessionStart", "UserPromptSubmit", "PreToolUse", "PermissionRequest", "PostToolUse", "Stop", "PreCompact", "PostCompact"}
	for _, name := range events {
		if !supportedEvents[name] {
			t.Fatalf("missing event %s", name)
		}
	}
	output := Handle(Event{HookEventName: "UserPromptSubmit", SessionID: "s", TurnID: "t", Prompt: "아니 그게 아니라 설명해"})
	if output == nil {
		t.Fatal("correction output missing")
	}
	output = Handle(Event{HookEventName: "Stop", SessionID: "s", TurnID: "t", LastAssistantMessage: "맞습니다. 지금부터 다시 확인하겠습니다."})
	if output == nil || output["decision"] != "block" || output["reason"] == "" {
		t.Fatalf("recovery stop was not blocked: %#v", output)
	}
	if _, present := output["continue"]; present {
		t.Fatalf("Stop continuation must not use continue: %#v", output)
	}
}

func TestSessionStartAnnouncesOnlyManifestLocation(t *testing.T) {
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	content := "schema_version: 1\nproject_id: demo\nmemory_bank:\n  root: private-memory\n"
	if err := os.WriteFile(filepath.Join(root, "project-context.yaml"), []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
	output := Handle(Event{HookEventName: "SessionStart", SessionID: "s", Source: "startup", Cwd: root})
	if output == nil {
		t.Fatal("manifest context missing")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	context := specific["additionalContext"].(string)
	if context == "" || contains(context, "private-memory") {
		t.Fatalf("unexpected context: %q", context)
	}
}

func contains(value, part string) bool {
	for index := 0; index+len(part) <= len(value); index++ {
		if value[index:index+len(part)] == part {
			return true
		}
	}
	return false
}
