package hook

import (
	"bytes"
	"encoding/json"
	"path/filepath"
	"strings"

	"skill-system.local/harness/grok/internal/notify"
)

var supportedEvents = map[string]bool{
	"notification": true,
}

var declaredNotificationTypes = map[string]notificationSpec{
	"permission_prompt": {Topic: "approval", Event: "grok-permission_prompt", Title: "Grok approval requested"},
	"idle_prompt":       {Topic: "done", Event: "grok-idle_prompt", Title: "Grok is ready"},
	"task_complete":     {Topic: "done", Event: "grok-task_complete", Title: "Grok task complete"},
}

type notificationSpec struct {
	Topic string
	Event string
	Title string
}

type Event struct {
	HookEventName    string
	NotificationType string
	Title            string
	Message          string
	SessionID        string
	Cwd              string
	Model            string
	TaskSubject      string
}

func (event *Event) UnmarshalJSON(data []byte) error {
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	event.HookEventName = firstString(raw, "hookEventName", "hook_event_name")
	event.NotificationType = firstString(raw, "notificationType", "notification_type")
	event.Title = firstString(raw, "title")
	event.Message = firstString(raw, "message")
	event.SessionID = firstString(raw, "sessionId", "session_id")
	event.Cwd = firstString(raw, "cwd")
	event.Model = firstString(raw, "model")
	event.TaskSubject = firstString(raw, "taskSubject", "task_subject")
	return nil
}

func Handle(event Event) map[string]any {
	if !supportedEvents[normalizeEventName(event.HookEventName)] {
		return nil
	}
	message, ok := notificationMessage(event)
	if !ok {
		return nil
	}
	notify.Send(message)
	return nil
}

func notificationMessage(event Event) (notify.Message, bool) {
	spec, ok := declaredNotificationTypes[strings.TrimSpace(event.NotificationType)]
	if !ok {
		return notify.Message{}, false
	}
	title := strings.TrimSpace(event.Title)
	if title == "" {
		title = spec.Title
	}
	body := strings.TrimSpace(event.Message)
	if body == "" {
		body = strings.ReplaceAll(event.NotificationType, "_", " ")
	}
	return notify.Message{
		Event:   spec.Event,
		Topic:   spec.Topic,
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
	if strings.HasPrefix(model, "grok-") {
		model = strings.TrimPrefix(model, "grok-")
	}
	if model == "" {
		model = "grok"
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

func normalizeEventName(value string) string {
	value = strings.TrimSpace(value)
	if value == "" {
		return ""
	}
	var builder strings.Builder
	for _, char := range value {
		switch {
		case char >= 'A' && char <= 'Z':
			if builder.Len() > 0 {
				builder.WriteByte('_')
			}
			builder.WriteRune(char + ('a' - 'A'))
		case char == '-':
			builder.WriteByte('_')
		default:
			builder.WriteRune(char)
		}
	}
	return builder.String()
}

func firstString(raw map[string]json.RawMessage, keys ...string) string {
	for _, key := range keys {
		value, ok := raw[key]
		if !ok {
			continue
		}
		value = bytes.TrimSpace(value)
		if len(value) == 0 || bytes.Equal(value, []byte("null")) {
			continue
		}
		var text string
		if err := json.Unmarshal(value, &text); err == nil {
			return strings.TrimSpace(text)
		}
	}
	return ""
}
