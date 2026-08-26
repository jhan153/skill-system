package claudehook

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"testing"
)

type declaredClaudeHook struct {
	Matcher string `json:"matcher"`
}

func TestDeclaredClaudeEventsMatchHandlerSurface(t *testing.T) {
	config := loadClaudeHookConfig(t)
	declared := map[string]bool{}
	for event := range config {
		declared[event] = true
	}
	if missing, unexpected := claudeSetDifference(declared, supportedEvents), claudeSetDifference(supportedEvents, declared); len(missing) > 0 || len(unexpected) > 0 {
		t.Fatalf("Claude hook events differ: missing=%v unexpected=%v", missing, unexpected)
	}
	if output := Handle(Event{HookEventName: "UnsupportedEvent"}); output != nil {
		t.Fatalf("unsupported event did not fail open: %#v", output)
	}
}

func TestClaudeSessionContextAndDeclaredNotifications(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	manifest := "schema_version: 1\nproject_id: demo\nknowledge_base:\n  root: private-knowledge\n"
	if err := os.WriteFile(filepath.Join(root, "project-context.yaml"), []byte(manifest), 0o600); err != nil {
		t.Fatal(err)
	}
	output := Handle(Event{HookEventName: "SessionStart", SessionID: "s", Source: "startup", Cwd: root})
	if output == nil {
		t.Fatal("manifest context missing")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	context := specific["additionalContext"].(string)
	if !strings.Contains(context, "project-context.yaml") || strings.Contains(context, "private-knowledge") {
		t.Fatalf("unexpected context output: %q", context)
	}

	config := loadClaudeHookConfig(t)
	declaredTypes := map[string]bool{}
	for _, registration := range config["Notification"] {
		for _, value := range strings.Split(registration.Matcher, "|") {
			if value = strings.TrimSpace(value); value != "" {
				declaredTypes[value] = true
			}
		}
	}
	if len(declaredTypes) == 0 {
		t.Fatal("Claude Notification hook declares no notification types")
	}
	for notificationType := range declaredTypes {
		message, ok := notificationMessage(Event{NotificationType: notificationType, Message: "status", Cwd: root, Effort: Effort{Level: "max"}})
		if !ok || message.Topic == "" {
			t.Errorf("declared notification %s is not mapped: %#v ok=%v", notificationType, message, ok)
		}
	}
	if _, ok := notificationMessage(Event{NotificationType: "unsupported_notification"}); ok {
		t.Fatal("undeclared notification type was mapped")
	}
}

func loadClaudeHookConfig(t *testing.T) map[string][]declaredClaudeHook {
	t.Helper()
	root := claudeHookRepositoryRoot(t)
	raw, err := os.ReadFile(filepath.Join(root, "source/platform/claude/hooks/settings.example.json"))
	if err != nil {
		t.Fatal(err)
	}
	var config struct {
		Hooks map[string][]declaredClaudeHook `json:"hooks"`
	}
	if err := json.Unmarshal(raw, &config); err != nil {
		t.Fatal(err)
	}
	return config.Hooks
}

func claudeHookRepositoryRoot(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("cannot resolve Claude hook test path")
	}
	root, err := filepath.Abs(filepath.Join(filepath.Dir(file), "../../../../../.."))
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func claudeSetDifference(left, right map[string]bool) []string {
	var result []string
	for value := range left {
		if !right[value] {
			result = append(result, value)
		}
	}
	sort.Strings(result)
	return result
}
