package hook

import (
	"path/filepath"
	"strings"

	"skill-system.local/harness/internal/kanboard"
	"skill-system.local/harness/internal/looprun"
	"skill-system.local/harness/internal/notify"
	"skill-system.local/harness/internal/projectcontext"
	"skill-system.local/harness/internal/responseguard"
)

var supportedEvents = map[string]bool{
	"SessionStart": true, "UserPromptSubmit": true, "PreToolUse": true,
	"PermissionRequest": true, "PostToolUse": true, "Stop": true,
	"PreCompact": true, "PostCompact": true,
}

type Event struct {
	HookEventName           string `json:"hook_event_name"`
	SessionID               string `json:"session_id"`
	TurnID                  string `json:"turn_id"`
	Cwd                     string `json:"cwd"`
	Source                  string `json:"source"`
	Prompt                  string `json:"prompt"`
	LastAssistantMessage    string `json:"last_assistant_message"`
	ToolName                string `json:"tool_name"`
	Model                   string `json:"model"`
	TaskSubject             string `json:"task_subject"`
	SkillSystemLoopRunDir   string `json:"skill_system_loop_run_dir"`
	SkillSystemNotifyDryRun bool   `json:"skill_system_notify_dry_run"`
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
	case "PermissionRequest":
		permission(event)
		return nil
	case "Stop":
		return stop(event)
	default:
		return nil
	}
}

func sessionStart(event Event) map[string]any {
	if event.Source == "startup" || event.Source == "clear" {
		_ = responseguard.Clear(event.SessionID)
	}
	kanboard.MaybeSync(event.Cwd, false)
	result, err := projectcontext.Resolve(event.Cwd, "")
	if err != nil {
		return nil
	}
	context := projectcontext.Context(result)
	if context == "" {
		return nil
	}
	return map[string]any{
		"continue": true,
		"hookSpecificOutput": map[string]any{
			"hookEventName":     "SessionStart",
			"additionalContext": context,
		},
	}
}

func userPrompt(event Event) map[string]any {
	correction, err := responseguard.Prompt(event.SessionID, event.TurnID, event.Prompt)
	if err != nil || !correction {
		return nil
	}
	return map[string]any{
		"continue": true,
		"hookSpecificOutput": map[string]any{
			"hookEventName":     "UserPromptSubmit",
			"additionalContext": responseguard.CorrectionContext,
		},
	}
}

func permission(event Event) {
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
}

func stop(event Event) map[string]any {
	blocked, err := responseguard.Stop(event.SessionID, event.TurnID, event.LastAssistantMessage)
	if err == nil && blocked {
		return map[string]any{
			"decision": "block",
			"reason":   "A user correction is pending, but the response only acknowledges it and promises later action. Re-answer the current correction now: state the corrected premise, invalidate affected conclusions, and provide the direct answer, completed action, or concrete requested plan.",
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
		} else if report.Decision.Action == "blocked" {
			topic = "input"
		}
		body := strings.Trim(strings.Join([]string{report.LoopRunID, report.Decision.Action, report.Decision.ReasonCode}, " "), " ")
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
