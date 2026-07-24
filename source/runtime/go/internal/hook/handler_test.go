package hook

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
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

func TestWorkContractBlocksApprovalWithoutWaiting(t *testing.T) {
	state := t.TempDir()
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", state)
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	prompt := Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "contract-session",
		TurnID:        "turn-1",
		Prompt:        "/goal 무인 장시간 작업으로 핵심 구현만 하고 검증은 내가 할게. 추가 승인 요청하지 마.",
	})
	if prompt == nil {
		t.Fatal("work-contract context missing")
	}
	context := prompt["hookSpecificOutput"].(map[string]any)["additionalContext"].(string)
	if !strings.Contains(context, "Verification owner: user") ||
		!strings.Contains(context, "Additional interaction: forbidden") ||
		!strings.Contains(context, "Execution mode: unattended_goal_loop") {
		t.Fatalf("unexpected contract context: %q", context)
	}
	toolInput, _ := json.Marshal(map[string]any{
		"command":     "run runtime validation",
		"description": "verify the changed behavior",
	})
	output := Handle(Event{
		HookEventName: "PermissionRequest",
		SessionID:     "contract-session",
		TurnID:        "turn-1",
		ToolName:      "Bash",
		ToolInput:     toolInput,
	})
	if output == nil {
		t.Fatal("permission request was left undecided")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	decision := specific["decision"].(map[string]any)
	if decision["behavior"] != "deny" || decision["message"] == "" {
		t.Fatalf("unexpected permission decision: %#v", output)
	}
}

func TestExcludedValidationIsRemovedFromPlanWithoutBlocking(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "plan-session",
		TurnID:        "turn-1",
		Prompt:        "구현에만 집중하고 테스트와 검증은 내가 맡을게.",
	})
	planInput, _ := json.Marshal(map[string]any{
		"plan": []map[string]string{
			{"step": "production parser implementation", "status": "in_progress"},
			{"step": "run validation tests", "status": "pending"},
		},
	})
	output := Handle(Event{
		HookEventName: "PreToolUse",
		SessionID:     "plan-session",
		ToolName:      "update_plan",
		ToolInput:     planInput,
	})
	if output == nil {
		t.Fatal("mixed plan was not rewritten")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	if specific["permissionDecision"] != "allow" || specific["additionalContext"] == "" {
		t.Fatalf("unexpected pre-tool decision: %#v", output)
	}
	updated := specific["updatedInput"].(map[string]any)
	plan := updated["plan"].([]any)
	if len(plan) != 1 || plan[0].(map[string]any)["step"] != "production parser implementation" {
		t.Fatalf("unexpected rewritten plan: %#v", updated)
	}
}

func TestAllExcludedPlanStillUsesLastResortDeny(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "plan-session",
		TurnID:        "turn-1",
		Prompt:        "구현에만 집중하고 테스트와 검증은 내가 맡을게.",
	})
	planInput, _ := json.Marshal(map[string]any{
		"plan": []map[string]string{
			{"step": "run validation tests", "status": "in_progress"},
		},
	})
	output := Handle(Event{
		HookEventName: "PreToolUse",
		SessionID:     "plan-session",
		ToolName:      "update_plan",
		ToolInput:     planInput,
	})
	if output == nil {
		t.Fatal("all-excluded plan was left undecided")
	}
	specific := output["hookSpecificOutput"].(map[string]any)
	if specific["permissionDecision"] != "deny" {
		t.Fatalf("unexpected pre-tool decision: %#v", output)
	}
}

func TestContractSurvivesCompactionAndDefersBlockingQuestion(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "compact-session",
		TurnID:        "turn-1",
		Prompt:        "/goal 무인 장시간 루프로 진행해. 검증은 내가 할게. 추가 질문하지 말고 계속 진행해.",
	})
	compact := Handle(Event{
		HookEventName: "PostCompact",
		SessionID:     "compact-session",
		TurnID:        "turn-1",
		Trigger:       "auto",
	})
	if compact == nil || !strings.Contains(compact["systemMessage"].(string), "work contract") {
		t.Fatalf("contract missing after compact: %#v", compact)
	}
	resumed := Handle(Event{
		HookEventName: "SessionStart",
		SessionID:     "compact-session",
		Source:        "compact",
	})
	if resumed == nil {
		t.Fatal("compact SessionStart did not restore contract context")
	}
	stop := Handle(Event{
		HookEventName:        "Stop",
		SessionID:            "compact-session",
		TurnID:               "turn-1",
		LastAssistantMessage: "Which validation path should I run?",
	})
	if stop == nil || stop["decision"] != "block" {
		t.Fatalf("blocking question was not converted to continuation: %#v", stop)
	}
}

func TestDirectWorkContractSurvivesStopAndUserContinuation(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "continued-session",
		TurnID:        "turn-1",
		Prompt:        "/goal 무인 장시간 작업으로 핵심 구현만 진행해. 검증은 내가 하고 추가 승인 요청은 하지 마.",
	})

	if output := Handle(Event{
		HookEventName:        "Stop",
		SessionID:            "continued-session",
		TurnID:               "turn-1",
		LastAssistantMessage: "첫 구현 묶음을 완료했습니다.",
	}); output != nil {
		t.Fatalf("ordinary completion unexpectedly changed Stop behavior: %#v", output)
	}

	continuation := Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "continued-session",
		TurnID:        "turn-2",
		Prompt:        "계속 진행해.",
	})
	if continuation == nil {
		t.Fatal("direct work contract was lost across Stop and continuation")
	}
	context := continuation["hookSpecificOutput"].(map[string]any)["additionalContext"].(string)
	if !strings.Contains(context, "Verification owner: user") ||
		!strings.Contains(context, "Additional interaction: forbidden") ||
		!strings.Contains(context, "Execution mode: unattended_goal_loop") {
		t.Fatalf("continued contract context was not preserved: %q", context)
	}

	toolInput, _ := json.Marshal(map[string]any{"command": "install required dependency"})
	permission := Handle(Event{
		HookEventName: "PermissionRequest",
		SessionID:     "continued-session",
		TurnID:        "turn-2",
		ToolName:      "Bash",
		ToolInput:     toolInput,
	})
	if permission == nil {
		t.Fatal("continued unattended contract left permission undecided")
	}
	decision := permission["hookSpecificOutput"].(map[string]any)["decision"].(map[string]any)
	if decision["behavior"] != "deny" {
		t.Fatalf("unexpected continued permission decision: %#v", permission)
	}
}

func TestAttendedTaskLeavesPermissionRequestUndecided(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "attended-session",
		TurnID:        "turn-1",
		Prompt:        "일반 대화형 작업이야. 구현을 진행해.",
	})
	toolInput, _ := json.Marshal(map[string]any{"command": "install dependency"})
	output := Handle(Event{
		HookEventName: "PermissionRequest",
		SessionID:     "attended-session",
		TurnID:        "turn-1",
		ToolName:      "Bash",
		ToolInput:     toolInput,
	})
	if output != nil {
		t.Fatalf("attended approval should use the normal host flow: %#v", output)
	}
}

func TestInteractionEnabledGoalLeavesPermissionRequestUndecided(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	Handle(Event{
		HookEventName: "UserPromptSubmit",
		SessionID:     "interactive-goal-session",
		TurnID:        "turn-1",
		Prompt:        "/goal 장시간 루프로 진행하되 승인이나 질문을 요청해도 돼.",
	})
	toolInput, _ := json.Marshal(map[string]any{"command": "install required dependency"})
	output := Handle(Event{
		HookEventName: "PermissionRequest",
		SessionID:     "interactive-goal-session",
		TurnID:        "turn-1",
		ToolName:      "Bash",
		ToolInput:     toolInput,
	})
	if output != nil {
		t.Fatalf("interaction-enabled Goal approval should use the normal host flow: %#v", output)
	}
}

func TestAcceptedLoopContractScopesAutomaticPermissionDenial(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	cases := []struct {
		name        string
		execution   string
		interaction string
		wantDeny    bool
	}{
		{"unattended-forbidden", "unattended_goal_loop", "forbidden", true},
		{"attended-forbidden", "attended", "forbidden", false},
		{"unattended-allowed", "unattended_goal_loop", "allowed", false},
	}
	for _, test := range cases {
		t.Run(test.name, func(t *testing.T) {
			loop := filepath.Join(t.TempDir(), "loop")
			if err := os.MkdirAll(loop, 0o755); err != nil {
				t.Fatal(err)
			}
			contract := "schema_version: 3\n" +
				"work_contract:\n" +
				"  execution:\n" +
				"    mode: " + test.execution + "\n" +
				"  verification:\n" +
				"    owner: agent\n" +
				"  interaction:\n" +
				"    mode: " + test.interaction + "\n" +
				"  scope:\n" +
				"    excluded_action_classes: []\n"
			if err := os.WriteFile(filepath.Join(loop, "contract.yaml"), []byte(contract), 0o600); err != nil {
				t.Fatal(err)
			}
			sum := sha256.Sum256([]byte(contract))
			state := "schema_version: 2\n" +
				"status: active\n" +
				"contract_ref: contract.yaml\n" +
				"contract_hash: " + hex.EncodeToString(sum[:]) + "\n"
			if err := os.WriteFile(filepath.Join(loop, "state.yaml"), []byte(state), 0o600); err != nil {
				t.Fatal(err)
			}
			toolInput, _ := json.Marshal(map[string]any{"command": "install required dependency"})
			output := Handle(Event{
				HookEventName:         "PermissionRequest",
				SessionID:             "projection-" + test.name,
				ToolName:              "Bash",
				ToolInput:             toolInput,
				SkillSystemLoopRunDir: loop,
			})
			if test.wantDeny {
				if output == nil {
					t.Fatal("unattended no-interaction LoopRun left permission undecided")
				}
				decision := output["hookSpecificOutput"].(map[string]any)["decision"].(map[string]any)
				if decision["behavior"] != "deny" {
					t.Fatalf("unexpected decision: %#v", output)
				}
			} else if output != nil {
				t.Fatalf("normal host approval was overridden: %#v", output)
			}
		})
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
