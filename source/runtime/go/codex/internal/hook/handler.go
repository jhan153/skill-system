package hook

import (
	"encoding/json"
	"path/filepath"
	"strings"

	"skill-system.local/harness/codex/internal/notify"
	"skill-system.local/harness/codex/internal/projectcontext"
	"skill-system.local/harness/codex/internal/responseguard"
	"skill-system.local/harness/codex/internal/workcontract"
)

var supportedEvents = map[string]bool{
	"SessionStart": true, "UserPromptSubmit": true, "PreToolUse": true,
	"PermissionRequest": true, "PostToolUse": true, "Stop": true,
	"PreCompact": true, "PostCompact": true,
}

type Event struct {
	HookEventName           string          `json:"hook_event_name"`
	SessionID               string          `json:"session_id"`
	TurnID                  string          `json:"turn_id"`
	Cwd                     string          `json:"cwd"`
	Source                  string          `json:"source"`
	Prompt                  string          `json:"prompt"`
	LastAssistantMessage    string          `json:"last_assistant_message"`
	ToolName                string          `json:"tool_name"`
	ToolInput               json.RawMessage `json:"tool_input"`
	ToolUseID               string          `json:"tool_use_id"`
	PermissionMode          string          `json:"permission_mode"`
	Trigger                 string          `json:"trigger"`
	Model                   string          `json:"model"`
	TaskSubject             string          `json:"task_subject"`
	SkillSystemNotifyDryRun bool            `json:"skill_system_notify_dry_run"`
}

func Handle(event Event) map[string]any {
	if !supportedEvents[event.HookEventName] {
		return nil
	}
	switch event.HookEventName {
	case "SessionStart":
		return sessionStart(event)
	case "UserPromptSubmit":
		return userPrompt(event)
	case "PreToolUse":
		return preToolUse(event)
	case "PermissionRequest":
		return nil
	case "Stop":
		return stop(event)
	case "PreCompact", "PostCompact":
		return compact(event)
	default:
		return nil
	}
}

func sessionStart(event Event) map[string]any {
	if event.Source == "startup" || event.Source == "clear" {
		_ = responseguard.Clear(event.SessionID)
		_ = workcontract.Clear(event.SessionID)
	}
	var contexts []string
	result, err := projectcontext.Resolve(event.Cwd, "")
	if err == nil {
		if context := projectcontext.Context(result); context != "" {
			contexts = append(contexts, context)
		}
	}
	if state, loadErr := workcontract.Load(event.SessionID); loadErr == nil {
		if context := workcontract.Context(state); context != "" {
			contexts = append(contexts, context)
		}
	}
	if len(contexts) == 0 {
		return nil
	}
	return map[string]any{
		"continue": true,
		"hookSpecificOutput": map[string]any{
			"hookEventName":     "SessionStart",
			"additionalContext": strings.Join(contexts, "\n\n"),
		},
	}
}

func userPrompt(event Event) map[string]any {
	correction, err := responseguard.Prompt(event.SessionID, event.TurnID, event.Prompt)
	var contexts []string
	if err == nil && correction {
		contexts = append(contexts, responseguard.CorrectionContext)
	}
	_, _, _ = workcontract.Capture(event.SessionID, event.Prompt)
	if state, contractErr := workcontract.Load(event.SessionID); contractErr == nil {
		if context := workcontract.Context(state); context != "" {
			contexts = append(contexts, context)
		}
	}
	if len(contexts) == 0 {
		return nil
	}
	return map[string]any{
		"continue": true,
		"hookSpecificOutput": map[string]any{
			"hookEventName":     "UserPromptSubmit",
			"additionalContext": strings.Join(contexts, "\n\n"),
		},
	}
}

func preToolUse(event Event) map[string]any {
	decision, err := workcontract.Preflight(event.SessionID, event.ToolName, event.ToolInput)
	if err != nil {
		return nil
	}
	if decision.Rewrite {
		return map[string]any{
			"hookSpecificOutput": map[string]any{
				"hookEventName":      "PreToolUse",
				"permissionDecision": "allow",
				"updatedInput":       decision.UpdatedInput,
				"additionalContext":  decision.Reason,
			},
		}
	}
	if !decision.Deny {
		return nil
	}
	return map[string]any{
		"hookSpecificOutput": map[string]any{
			"hookEventName":            "PreToolUse",
			"permissionDecision":       "deny",
			"permissionDecisionReason": decision.Reason,
		},
	}
}

func compact(event Event) map[string]any {
	state, err := workcontract.Load(event.SessionID)
	if err != nil {
		return nil
	}
	context := workcontract.Context(state)
	if context == "" {
		return nil
	}
	return map[string]any{
		"systemMessage": "Active user work contract remains in force through compaction.\n" + context,
	}
}

func stop(event Event) map[string]any {
	blocked, err := responseguard.Stop(event.SessionID, event.TurnID, event.LastAssistantMessage)
	if err == nil && blocked {
		return map[string]any{
			"decision": "block",
			"reason":   "A user correction is pending, but the response only acknowledges it and promises later action. Re-answer the current correction now: state the corrected premise, invalidate affected conclusions, and provide the direct answer, completed action, or concrete requested plan.",
		}
	}
	if needsInput(event.LastAssistantMessage) && !reportsBlocked(event.LastAssistantMessage) {
		if resume, contractErr := workcontract.ContinueWithoutInput(event.SessionID); contractErr == nil && resume {
			return map[string]any{
				"decision": "block",
				"reason": "The active user work contract forbids additional blocking questions. " +
					"Defer the blocked action without retrying its purpose, then continue any other required runnable work. " +
					"If none remains, return a concrete blocked result with the exact unmet requirement instead of asking.",
			}
		}
	}
	if needsInput(event.LastAssistantMessage) {
		notify.Send(notify.Message{Event: "input-needed", Topic: "input", Title: "Codex input needed", Body: notify.SafeText(firstLine(event.LastAssistantMessage)), Model: shortModel(event.Model), Session: label(event), SessionID: event.SessionID})
	} else {
		notify.Send(notify.Message{Event: "turn-complete", Topic: "done", Title: "Codex task complete", Body: completionMessage(event), Model: shortModel(event.Model), Session: label(event), SessionID: event.SessionID})
	}
	return nil
}

func reportsBlocked(message string) bool {
	text := strings.ToLower(message)
	return strings.Contains(text, "`blocked`") ||
		strings.Contains(text, "status: blocked") ||
		strings.Contains(text, "result: blocked") ||
		strings.Contains(text, "결과: blocked")
}

func needsInput(message string) bool {
	text := strings.ToLower(strings.TrimSpace(message))
	if text == "" {
		return false
	}
	if strings.HasSuffix(text, "?") || strings.HasSuffix(text, "？") {
		return true
	}
	for _, marker := range []string{"결정해 주세요", "선택해 주세요", "알려 주세요", "입력이 필요", "확인이 필요", "please choose", "need your input"} {
		if strings.Contains(text, marker) {
			return true
		}
	}
	return false
}

func completionMessage(event Event) string {
	if line := firstLine(event.LastAssistantMessage); line != "" {
		return line
	}
	return "Turn completed without a summary."
}

func firstLine(value string) string {
	for _, line := range strings.Split(value, "\n") {
		line = strings.TrimSpace(line)
		if line == "" || line == "```" || strings.HasPrefix(line, "```") {
			continue
		}
		return notify.SafeText(line)
	}
	return ""
}

func label(event Event) string {
	if value := strings.TrimSpace(event.TaskSubject); value != "" {
		return notify.SafeText(value)
	}
	workspace := workspaceName(event.Cwd)
	if workspace != "" {
		return workspace
	}
	return "unknown task"
}

func workspaceName(value string) string {
	value = strings.TrimSpace(value)
	if value == "" {
		return ""
	}
	return notify.SafeText(filepath.Base(filepath.Clean(value)))
}

func shortModel(value string) string {
	value = strings.TrimSpace(value)
	if index := strings.LastIndex(value, "/"); index >= 0 {
		value = value[index+1:]
	}
	runes := []rune(value)
	if len(runes) > 24 {
		runes = runes[:24]
	}
	return string(runes)
}
