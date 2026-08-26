package notify

import (
	"path/filepath"
	"strings"
	"testing"
)

func TestDryRunAndCleanup(t *testing.T) {
	t.Setenv("SKILL_SYSTEM_DESKTOP_NOTIFY", "dry-run")
	result := Send(Message{Event: "turn-complete", Topic: "done", Title: "**Done**", Body: "[result](https://example.test)"})
	if result.Status != "dry_run" {
		t.Fatalf("unexpected result: %#v", result)
	}
}

func TestNotificationTextRedactsSecretsPathsAndURLs(t *testing.T) {
	value := "done /Users/example/private/repo password=hunter2 sk-abcdefghijklmnop https://example.test?q=secret"
	cleaned := SafeText(value)
	for _, forbidden := range []string{"/Users/example", "hunter2", "sk-abcdefghijklmnop", "example.test"} {
		if strings.Contains(cleaned, forbidden) {
			t.Fatalf("notification leaked %q in %q", forbidden, cleaned)
		}
	}
	if cleaned != "<redacted-sensitive>" {
		t.Fatalf("unexpected sensitive redaction: %q", cleaned)
	}
}

func TestSafePathKeepsOnlyCodexRelativePath(t *testing.T) {
	home := t.TempDir()
	t.Setenv("CODEX_HOME", home)
	inside := filepath.Join(home, "harness", "state.json")
	if got := SafePath(inside); got != "harness/state.json" {
		t.Fatalf("inside path=%q", got)
	}
	if got := SafePath(filepath.Join(t.TempDir(), "project")); got != "<external-path>" {
		t.Fatalf("external path=%q", got)
	}
}
