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

func TestNotificationTextRedactsPathOnlyInputs(t *testing.T) {
	tests := map[string][]string{
		"done /srv/customer-a/repo":                 {"/srv", "customer-a"},
		"read path=/etc/shadow;/workspace/client":   {"/etc", "shadow", "/workspace", "client"},
		`opened C:\\workspace\\client\\repo`:        {`C:\\workspace`, "client"},
		`opened \\\\server\\share\\client`:          {`\\\\server`, "share", "client"},
		`opened "/srv/Acme Project/client-a/repo"`:  {"Acme Project", "client-a"},
		`opened 'C:\\Acme Corp\\client-a\\repo'`:    {"Acme Corp", "client-a"},
		`opened "\\\\server\\Acme Share\\client-a"`: {"Acme Share", "client-a"},
	}
	for input, forbidden := range tests {
		cleaned := SafeText(input)
		if !strings.Contains(cleaned, "<path>") {
			t.Errorf("path was not redacted: input=%q cleaned=%q", input, cleaned)
		}
		for _, value := range forbidden {
			if strings.Contains(cleaned, value) {
				t.Errorf("notification leaked %q: input=%q cleaned=%q", value, input, cleaned)
			}
		}
	}
}

func TestNotificationTextDoesNotTreatFractionAsPath(t *testing.T) {
	if cleaned := SafeText("progress 1/2 complete"); cleaned != "progress 1/2 complete" {
		t.Fatalf("fraction changed: %q", cleaned)
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
