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

type declaredGrokHook struct {
	Matcher string `json:"matcher"`
	Hooks   []struct {
		Type    string `json:"type"`
		Command string `json:"command"`
		Timeout int    `json:"timeout"`
	} `json:"hooks"`
}

const grokHarnessCommand = "../bin/__SKILL_SYSTEM_GROK_HARNESS_FILENAME__"

func TestDeclaredGrokEventsMatchHandlerSurface(t *testing.T) {
	config := loadGrokHookConfig(t)
	declared := map[string]bool{}
	for event := range config {
		declared[normalizeEventName(event)] = true
	}
	if missing, unexpected := setDifference(declared, supportedEvents), setDifference(supportedEvents, declared); len(missing) > 0 || len(unexpected) > 0 {
		t.Fatalf("Grok hook events differ: missing=%v unexpected=%v", missing, unexpected)
	}
	if output := Handle(Event{HookEventName: "Stop"}); output != nil {
		t.Fatalf("unsupported event did not fail open: %#v", output)
	}
}

func TestDeclaredGrokHookCommandContract(t *testing.T) {
	config := loadGrokHookConfig(t)
	registrations := config["Notification"]
	if len(registrations) != 1 || len(registrations[0].Hooks) != 1 {
		t.Fatalf("unexpected Grok Notification registration: %#v", registrations)
	}
	command := registrations[0].Hooks[0]
	if command.Type != "command" || command.Command != grokHarnessCommand || command.Timeout != 5 {
		t.Fatalf("unexpected Grok hook command contract: %#v", command)
	}
}

func TestGrokNotificationMapping(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	config := loadGrokHookConfig(t)
	declaredTypes := map[string]bool{}
	for _, registration := range config["Notification"] {
		for _, value := range strings.Split(registration.Matcher, "|") {
			if value = strings.TrimSpace(value); value != "" {
				declaredTypes[value] = true
			}
		}
	}
	if len(declaredTypes) == 0 {
		t.Fatal("Grok Notification hook declares no notification types")
	}
	for notificationType := range declaredTypes {
		message, ok := notificationMessage(Event{NotificationType: notificationType, Message: "status", Cwd: "/tmp/demo"})
		if !ok || message.Topic == "" {
			t.Errorf("declared notification %s is not mapped: %#v ok=%v", notificationType, message, ok)
		}
	}
	if _, ok := notificationMessage(Event{NotificationType: "unsupported_notification"}); ok {
		t.Fatal("undeclared notification type was mapped")
	}

	if output := Handle(Event{HookEventName: "notification", NotificationType: "permission_prompt", Title: "Approve", Message: "run tests", Model: "grok-4.6", Cwd: "/tmp/demo"}); output != nil {
		t.Fatalf("notification handler must stay observe-only: %#v", output)
	}
}

func TestGrokNotificationAcceptsCamelAndSnakeCase(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	var camel Event
	if err := json.Unmarshal([]byte(`{"hookEventName":"notification","notificationType":"idle_prompt","title":"Ready","message":"turn ended","sessionId":"s1","cwd":"/tmp/demo","model":"grok-4.6"}`), &camel); err != nil {
		t.Fatal(err)
	}
	message, ok := notificationMessage(camel)
	if !ok || message.Topic != "done" || camel.HookEventName != "notification" {
		t.Fatalf("camelCase notification not mapped: %#v ok=%v", message, ok)
	}

	var snake Event
	if err := json.Unmarshal([]byte(`{"hook_event_name":"Notification","notification_type":"task_complete","message":"finished","session_id":"s1","cwd":"/tmp/demo"}`), &snake); err != nil {
		t.Fatal(err)
	}
	message, ok = notificationMessage(snake)
	if !ok || message.Topic != "done" || normalizeEventName(snake.HookEventName) != "notification" {
		t.Fatalf("snake_case notification not mapped: %#v ok=%v event=%q", message, ok, snake.HookEventName)
	}
}

func loadGrokHookConfig(t *testing.T) map[string][]declaredGrokHook {
	t.Helper()
	root := grokHookRepositoryRoot(t)
	raw, err := os.ReadFile(filepath.Join(root, "source/platform/grok/hooks/skill-system.json.in"))
	if err != nil {
		t.Fatal(err)
	}
	var config struct {
		Hooks map[string][]declaredGrokHook `json:"hooks"`
	}
	if err := json.Unmarshal(raw, &config); err != nil {
		t.Fatal(err)
	}
	return config.Hooks
}

func grokHookRepositoryRoot(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("cannot resolve Grok hook test path")
	}
	root, err := filepath.Abs(filepath.Join(filepath.Dir(file), "../../../../../.."))
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func setDifference(left, right map[string]bool) []string {
	var result []string
	for value := range left {
		if !right[value] {
			result = append(result, value)
		}
	}
	sort.Strings(result)
	return result
}
