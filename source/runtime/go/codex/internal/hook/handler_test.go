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
	output := Handle(Event{
		HookEventName: "PermissionRequest", SessionID: "normal", TurnID: "turn", ToolName: "Bash",
		ToolInput: hookCommandJSON(t, "rg -n hook source"), PermissionMode: "default",
	})
	if output == nil {
		t.Fatal("stable local read did not bypass approval")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	decision := specific["decision"].(map[string]any)
	if decision["behavior"] != "allow" {
		t.Fatalf("stable local read was not allowed: %#v", output)
	}
}

func TestExecGuardRewritesAndAppliesTurnAuthority(t *testing.T) {
	root := t.TempDir()
	workspace := filepath.Join(root, "workspace")
	codexHome := filepath.Join(root, "codex-home")
	for _, path := range []string{filepath.Join(workspace, ".git"), codexHome} {
		if err := os.MkdirAll(path, 0o700); err != nil {
			t.Fatal(err)
		}
	}
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", root)
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	t.Setenv("CODEX_HOME", codexHome)

	if output := Handle(Event{
		HookEventName: "UserPromptSubmit", SessionID: "install", TurnID: "turn", Cwd: workspace,
		Prompt: "Skill System runtime companion을 Codex 홈에 설치하고 동기화해",
	}); output != nil {
		if _, ok := output["hookSpecificOutput"]; !ok {
			t.Fatalf("unexpected prompt output: %#v", output)
		}
	}
	permission := Handle(Event{
		HookEventName: "PermissionRequest", SessionID: "install", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "install-1", PermissionMode: "default",
		ToolInput: hookCommandJSON(t, "rsync -a build/ "+codexHome+"/"),
	})
	if permission == nil {
		t.Fatal("turn-authorized installation reached the approval UI")
	}
	permissionSpecific := permission["hookSpecificOutput"].(map[string]any)
	if permissionSpecific["decision"].(map[string]any)["behavior"] != "allow" {
		t.Fatalf("turn-authorized installation was not allowed: %#v", permission)
	}

	rewrite := Handle(Event{
		HookEventName: "PreToolUse", SessionID: "wrapper", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "wrapper-1", PermissionMode: "default",
		ToolInput: hookCommandJSON(t, `zsh -lc "rg -n execguard source"`),
	})
	if rewrite == nil {
		t.Fatal("safe wrapper was not rewritten")
	}
	rewriteSpecific := rewrite["hookSpecificOutput"].(map[string]any)
	updated := rewriteSpecific["updatedInput"].(map[string]any)
	if updated["command"] != "rg -n execguard source" {
		t.Fatalf("unexpected wrapper rewrite: %#v", rewrite)
	}

	Handle(Event{
		HookEventName: "UserPromptSubmit", SessionID: "inline-eval", TurnID: "turn", Cwd: workspace,
		Prompt: "프로젝트 명령을 실행해",
	})
	opaque := Handle(Event{
		HookEventName: "PreToolUse", SessionID: "inline-eval", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "inline-1", PermissionMode: "default",
		ToolInput: hookCommandJSON(t, `python3 -c 'import os; os.execv("./dentru", ["./dentru"])'`),
	})
	if opaque == nil {
		t.Fatal("inline interpreter evaluator reached host approval")
	}
	opaqueSpecific := opaque["hookSpecificOutput"].(map[string]any)
	if opaqueSpecific["permissionDecision"] != "deny" || !strings.Contains(strings.ToLower(opaqueSpecific["permissionDecisionReason"].(string)), "opaque") {
		t.Fatalf("inline interpreter evaluator was not denied by PreToolUse: %#v", opaque)
	}

	Handle(Event{
		HookEventName: "UserPromptSubmit", SessionID: "no-wait", TurnID: "turn", Cwd: workspace,
		Prompt: "코드를 읽어봐",
	})
	denied := Handle(Event{
		HookEventName: "PreToolUse", SessionID: "no-wait", TurnID: "turn", Cwd: workspace,
		ToolName: "Bash", ToolUseID: "network-1", PermissionMode: "dontAsk",
		ToolInput: hookCommandJSON(t, "curl https://example.com/archive"),
	})
	if denied == nil || denied["hookSpecificOutput"].(map[string]any)["permissionDecision"] != "deny" {
		t.Fatalf("dontAsk attempted to wait for approval: %#v", denied)
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
