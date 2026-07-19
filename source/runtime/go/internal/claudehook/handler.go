package claudehook

import (
	"encoding/json"
	"path/filepath"
	"strings"

	"skill-system.local/harness/internal/kanboard"
	"skill-system.local/harness/internal/notify"
	"skill-system.local/harness/internal/projectcontext"
	"skill-system.local/harness/internal/responseguard"
)

var supportedEvents = map[string]bool{
	"SessionStart":     true,
	"UserPromptSubmit": true,
	"Stop":             true,
	"Notification":     true,
}

type Effort struct {
	Level string `json:"level"`
}

type Event struct {
	HookEventName        string            `json:"hook_event_name"`
	SessionID            string            `json:"session_id"`
	PromptID             string            `json:"prompt_id"`
	Cwd                  string            `json:"cwd"`
	Source               string            `json:"source"`
	Prompt               string            `json:"prompt"`
	LastAssistantMessage string            `json:"last_assistant_message"`
	Model                string            `json:"model"`
	TaskSubject          string            `json:"task_subject"`
	StopHookActive       bool              `json:"stop_hook_active"`
	NotificationType     string            `json:"notification_type"`
	Title                string            `json:"title"`
	Message              string            `json:"message"`
	Effort               Effort            `json:"effort"`
	BackgroundTasks      []json.RawMessage `json:"background_tasks"`
	SessionCrons         []json.RawMessage `json:"session_crons"`
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
	case "Stop":
		return stop(event)
	case "Notification":
		notification(event)
		return nil
	default:
		return nil
	}
}

func sessionStart(event Event) map[string]any {
	if event.Source == "startup" || event.Source == "clear" {
		_ = responseguard.Clear(event.SessionID)
		_ = clearTurnState(event.SessionID)
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
	turnKey, err := beginTurn(event.SessionID, event.PromptID)
	if err != nil {
		return nil
	}
	correction, err := responseguard.Prompt(event.SessionID, turnKey, event.Prompt)
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

func stop(event Event) map[string]any {
	if !event.StopHookActive {
		turnKey, err := currentTurn(event.SessionID, event.PromptID)
		if err == nil {
			blocked, guardErr := responseguard.Stop(event.SessionID, turnKey, event.LastAssistantMessage)
			if guardErr == nil && blocked {
				return map[string]any{
					"decision": "block",
					"reason":   "A user correction is pending, but the response only acknowledges it and promises later action. Re-answer the current correction now: state the corrected premise, invalidate affected conclusions, and provide the direct answer, completed action, or concrete requested plan.",
				}
			}
		}
	}
	kanboard.MaybeSync(event.Cwd, false)
	return nil
}

func notification(event Event) {
	message, ok := notificationMessage(event)
	if !ok {
		return
	}
	notify.Send(message)
}

func notificationMessage(event Event) (notify.Message, bool) {
	topic := ""
	title := strings.TrimSpace(event.Title)
	eventName := "claude-" + strings.TrimSpace(event.NotificationType)
	switch event.NotificationType {
	case "permission_prompt":
		topic = "approval"
		if title == "" {
			title = "Claude approval requested"
		}
	case "idle_prompt":
		topic = "done"
		if title == "" {
			title = "Claude is ready"
		}
	case "elicitation_dialog", "agent_needs_input":
		topic = "input"
		if title == "" {
			title = "Claude input needed"
		}
	case "agent_completed":
		topic = "done"
		if title == "" {
			title = "Claude background task complete"
		}
	default:
		return notify.Message{}, false
	}
	body := strings.TrimSpace(event.Message)
	if body == "" {
		body = strings.ReplaceAll(event.NotificationType, "_", " ")
	}
	return notify.Message{
		Event:   eventName,
		Topic:   topic,
		Title:   title,
		Body:    body,
		Model:   modelLabel(event),
		Session: sessionLabel(event),
	}, true
}

func modelLabel(event Event) string {
	model := strings.TrimSpace(event.Model)
	if index := strings.LastIndex(model, "/"); index >= 0 {
		model = model[index+1:]
	}
	if strings.HasPrefix(model, "claude-") {
		model = strings.TrimPrefix(model, "claude-")
	}
	if model == "" {
		model = "claude"
	}
	if effort := strings.TrimSpace(event.Effort.Level); effort != "" {
		model += "-" + effort
	}
	if len(model) > 24 {
		model = model[:24]
	}
	return model
}

func sessionLabel(event Event) string {
	if value := strings.TrimSpace(event.TaskSubject); value != "" {
		return notify.SafeText(value)
	}
	if value := strings.TrimSpace(event.Cwd); value != "" {
		return filepath.Base(value)
	}
	return ""
}
