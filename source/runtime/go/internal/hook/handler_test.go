package hook

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"testing"
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
	if output := Handle(Event{HookEventName: "PermissionRequest", SessionID: "normal", ToolName: "Bash"}); output != nil {
		t.Fatalf("permission without an active contract must use normal host flow: %#v", output)
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

func hookRepositoryRoot(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("cannot resolve hook test path")
	}
	root, err := filepath.Abs(filepath.Join(filepath.Dir(file), "../../../../.."))
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
