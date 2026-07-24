package hook

import (
	"encoding/json"
	"path/filepath"
	"strings"

	"skill-system.local/harness/internal/kanboard"
	"skill-system.local/harness/internal/looprun"
	"skill-system.local/harness/internal/notify"
	"skill-system.local/harness/internal/projectcontext"
	"skill-system.local/harness/internal/responseguard"
	"skill-system.local/harness/internal/workcontract"
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
	SkillSystemLoopRunDir   string          `json:"skill_system_loop_run_dir"`
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
		return permission(event)
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
	syncLoopWorkContract(event)
	kanboard.MaybeSync(event.Cwd, false)
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
	syncLoopWorkContract(event)
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
	syncLoopWorkContract(event)
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

func permission(event Event) map[string]any {
	syncLoopWorkContract(event)
	decision, err := workcontract.Permission(event.SessionID, event.ToolName, event.ToolInput)
	if err == nil && decision.Deny {
		return map[string]any{
			"hookSpecificOutput": map[string]any{
				"hookEventName": "PermissionRequest",
				"decision": map[string]any{
					"behavior": "deny",
					"message":  decision.Reason,
				},
			},
		}
	}
	tool := strings.TrimSpace(event.ToolName)
	if tool == "" {
		tool = "A tool"
	}
	location := ""
	if event.Cwd != "" {
		location = " in " + notify.SafePath(event.Cwd)
	}
	notify.Send(notify.Message{
		Event: "approval-requested", Topic: "approval", Title: "Codex approval requested",
		Body: tool + " is waiting for approval" + location + ".", Model: shortModel(event.Model), Session: label(event),
	})
	return nil
}

func compact(event Event) map[string]any {
	syncLoopWorkContract(event)
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
	syncLoopWorkContract(event)
	if needsInput(event.LastAssistantMessage) && !reportsBlocked(event.LastAssistantMessage) {
		if resume, contractErr := workcontract.ContinueWithoutInput(event.SessionID); contractErr == nil && resume {
			return map[string]any{
				"decision": "block",
				"reason": "The active user work contract forbids additional questions or approval waits. " +
					"Defer the blocked action without retrying its purpose, then continue any other required runnable work. " +
					"If none remains, return a concrete blocked result with the exact unmet requirement instead of asking.",
			}
		}
	}
	report, loopOutput := looprun.Evaluate(event.SessionID, event.SkillSystemLoopRunDir)
	kanboard.MaybeSync(event.Cwd, false)
	if report.Status != "" {
		topic := "progress"
		if report.Status == "error" || report.Decision.Action == "recover" {
			topic = "error"
		} else if report.Decision.Action == "success" {
			topic = "done"
		} else if report.Decision.Action == "blocked" || report.Decision.Action == "user_verification_needed" {
			topic = "input"
		}
		body := strings.Trim(strings.Join([]string{
			report.LoopRunID,
			report.ResultLabel,
			report.Decision.Action,
			report.Decision.ReasonCode,
		}, " "), " ")
		if body == "" {
			body = report.Reason
		}
		notify.Send(notify.Message{Event: "loop-iteration", Topic: topic, Title: "Codex LoopRun", Body: notify.SafeText(body), Model: shortModel(event.Model), Session: label(event)})
	} else if needsInput(event.LastAssistantMessage) {
		notify.Send(notify.Message{Event: "input-needed", Topic: "input", Title: "Codex input needed", Body: notify.SafeText(firstLine(event.LastAssistantMessage)), Model: shortModel(event.Model), Session: label(event)})
	} else {
		notify.Send(notify.Message{Event: "turn-complete", Topic: "done", Title: "Codex task complete", Body: completionMessage(event), Model: shortModel(event.Model), Session: label(event)})
	}
	if loopOutput == nil {
		if report.Status != "" && terminalLoopAction(report.Decision.Action) {
			_ = workcontract.Clear(event.SessionID)
		}
		return nil
	}
	output := map[string]any{}
	if loopOutput.Continue != nil {
		output["continue"] = *loopOutput.Continue
	}
	if loopOutput.Decision != "" {
		output["decision"] = loopOutput.Decision
	}
	if loopOutput.Reason != "" {
		output["reason"] = loopOutput.Reason
	}
	if loopOutput.SystemMessage != "" {
		output["systemMessage"] = loopOutput.SystemMessage
	}
	return output
}

func syncLoopWorkContract(event Event) {
	projection, err := looprun.WorkContract(event.SessionID, event.SkillSystemLoopRunDir)
	if err != nil || !projection.Active || projection.ExecutionMode == "" {
		return
	}
	_, _, _ = workcontract.AdoptLoopContract(
		event.SessionID,
		workcontract.LoopProjection{
			SourceDigest:          projection.SourceDigest,
			ExecutionMode:         projection.ExecutionMode,
			VerificationOwner:     projection.VerificationOwner,
			InteractionMode:       projection.InteractionMode,
			ExcludedActionClasses: projection.ExcludedActionClasses,
		},
	)
}

func terminalLoopAction(action string) bool {
	switch action {
	case "success", "user_verification_needed", "blocked", "budget_exhausted", "unsafe", "fatal", "stalled":
		return true
	default:
		return false
	}
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
		return notify.SafeText(line)
	}
	if value := label(event); value != "" {
		return value
	}
	return "turn complete"
}

func firstLine(value string) string {
	for _, line := range strings.Split(value, "\n") {
		line = strings.TrimSpace(line)
		if line == "" || line == "```" || strings.HasPrefix(line, "```") {
			continue
		}
		if len(line) > 220 {
			line = line[:217] + "..."
		}
		return line
	}
	return ""
}

func label(event Event) string {
	if value := strings.TrimSpace(event.TaskSubject); value != "" {
		return notify.SafeText(value)
	}
	if value := strings.TrimSpace(event.Cwd); value != "" {
		return filepath.Base(value)
	}
	return ""
}

func shortModel(value string) string {
	value = strings.TrimSpace(value)
	if index := strings.LastIndex(value, "/"); index >= 0 {
		value = value[index+1:]
	}
	if len(value) > 24 {
		value = value[:24]
	}
	return value
}
