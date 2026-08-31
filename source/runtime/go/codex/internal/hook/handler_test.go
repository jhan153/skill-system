package hook

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"testing"
	"unicode/utf8"
)

func TestDeclaredHookEventsMatchHandlerSurface(t *testing.T) {
	root := hookRepositoryRoot(t)
	raw, err := os.ReadFile(filepath.Join(root, "source/platform/codex/hooks.json"))
	if err != nil {
		t.Fatal(err)
	}
	var config struct {
		Hooks map[string]json.RawMessage `json:"hooks"`
	}
	if err := json.Unmarshal(raw, &config); err != nil {
		t.Fatal(err)
	}
	declared := map[string]bool{}
	for event := range config.Hooks {
		declared[event] = true
	}
	if missing, unexpected := hookSetDifference(declared, supportedEvents), hookSetDifference(supportedEvents, declared); len(missing) > 0 || len(unexpected) > 0 {
		t.Fatalf("Codex hook events differ: missing=%v unexpected=%v", missing, unexpected)
	}
	if output := Handle(Event{HookEventName: "UnsupportedEvent"}); output != nil {
		t.Fatalf("unsupported event did not fail open: %#v", output)
	}

	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	if output := Handle(Event{
		HookEventName: "PermissionRequest", SessionID: "normal", TurnID: "turn", ToolName: "Bash",
		ToolInput: hookCommandJSON(t, "rg -n hook source"), PermissionMode: "default",
	}); output != nil {
		t.Fatalf("permission without an active work contract must use normal host flow: %#v", output)
	}
}

func TestExecutionAdmissionDoesNotPreemptHostFlow(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")

	cases := []struct {
		name      string
		toolName  string
		toolInput json.RawMessage
	}{
		{
			name:      "arbitrary apply patch",
			toolName:  "apply_patch",
			toolInput: json.RawMessage(`{"patch":"arbitrary patch payload"}`),
		},
		{
			name:      "unregistered read command",
			toolName:  "Bash",
			toolInput: hookCommandJSON(t, "git blame source/file.go"),
		},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			event := Event{
				SessionID: "host-flow-" + testCase.name, TurnID: "turn",
				ToolName: testCase.toolName, ToolInput: testCase.toolInput, PermissionMode: "default",
			}
			event.HookEventName = "PreToolUse"
			if output := Handle(event); output != nil {
				t.Fatalf("tool was preempted before host policy: %#v", output)
			}
			event.HookEventName = "PermissionRequest"
			if output := Handle(event); output != nil {
				t.Fatalf("permission did not remain on the normal host path: %#v", output)
			}
		})
	}
}

func TestUnattendedWorkContractDoesNotOverrideHostReviewer(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")

	Handle(Event{
		HookEventName: "UserPromptSubmit", SessionID: "unattended", TurnID: "turn",
		Prompt: "/goal 무인 장시간 구현으로 진행해. 승인이나 질문을 요청하지 마.",
	})
	output := Handle(Event{
		HookEventName: "PermissionRequest", SessionID: "unattended", TurnID: "turn",
		ToolName: "Bash", ToolInput: hookCommandJSON(t, "git blame source/file.go"),
	})
	if output != nil {
		t.Fatalf("work contract overrode the host auto-review path: %#v", output)
	}
}

func TestSessionStartInjectsOnlyManifestLocation(t *testing.T) {
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
	if !strings.Contains(context, "project-context.yaml") || strings.Contains(context, "private-memory") {
		t.Fatalf("unexpected context: %q", context)
	}

	empty := t.TempDir()
	if err := os.Mkdir(filepath.Join(empty, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	if output := Handle(Event{HookEventName: "SessionStart", SessionID: "empty", Source: "startup", Cwd: empty}); output != nil {
		t.Fatalf("missing manifest did not fail open: %#v", output)
	}
}

func TestNotificationLabelAndSummaryFallbackRemainIdentifiable(t *testing.T) {
	event := Event{
		SessionID: "01a0501a-493e-73c2-9798-540344484143",
		TurnID:    "01a05050-11a0-7052-89f9-57427b44e8ce",
		Cwd:       "/Users/example/repo/book-project",
	}
	if got := label(event); got != "book-project" {
		t.Fatalf("label=%q", got)
	}
	if got := completionMessage(event); got != "Turn completed without a summary." {
		t.Fatalf("completion fallback=%q", got)
	}
	event.Cwd = ""
	if got := label(event); got != "unknown task" {
		t.Fatalf("identifier-only label=%q", got)
	}
	event.TaskSubject = "CS315 로우레벨 반영도 확인"
	if got := label(event); got != event.TaskSubject {
		t.Fatalf("task subject label=%q", got)
	}

	line := firstLine(strings.Repeat("한", 300))
	if !utf8.ValidString(line) {
		t.Fatalf("first line is not valid UTF-8: %q", line)
	}
	if len([]rune(line)) > 240 {
		t.Fatalf("first line rune length=%d", len([]rune(line)))
	}
}

func hookRepositoryRoot(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("cannot resolve hook test path")
	}
	root, err := filepath.Abs(filepath.Join(filepath.Dir(file), "../../../../../.."))
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func hookSetDifference(left, right map[string]bool) []string {
	var result []string
	for value := range left {
		if !right[value] {
			result = append(result, value)
		}
	}
	sort.Strings(result)
	return result
}

func hookCommandJSON(t *testing.T, command string) json.RawMessage {
	t.Helper()
	raw, err := json.Marshal(map[string]any{"command": command})
	if err != nil {
		t.Fatal(err)
	}
	return raw
}
