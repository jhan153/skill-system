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

func TestFormatMessagePreservesStatusAndAddsTaskContext(t *testing.T) {
	formatted := formatMessage(Message{
		Event: "turn-complete", Topic: "done", Title: "Codex task complete", Body: "Updated the notification path.",
		Model: "gpt-5.6-sol", Session: "skill-system", SessionID: "01a0516f-78aa-70b2-9bf3-75b6073d9e73",
	})
	if formatted.Title != "Codex task complete · skill-system" {
		t.Fatalf("unexpected title: %q", formatted.Title)
	}
	if formatted.Metadata != "gpt-5.6-sol" {
		t.Fatalf("unexpected metadata: %q", formatted.Metadata)
	}
	if formatted.Body != "Updated the notification path." {
		t.Fatalf("unexpected body: %q", formatted.Body)
	}
}

func TestFormatMessageSuppliesSemanticAndBodyFallbacks(t *testing.T) {
	formatted := formatMessage(Message{Topic: "input", Model: "gpt-5.6-sol", Session: "session", SessionID: "01a0516f-78aa"})
	if formatted.Title != "Codex input needed · session" {
		t.Fatalf("unexpected fallback title: %q", formatted.Title)
	}
	if formatted.Metadata != "gpt-5.6-sol" {
		t.Fatalf("unexpected fallback metadata: %q", formatted.Metadata)
	}
	if formatted.Body != "No summary was provided for this event." {
		t.Fatalf("unexpected fallback body: %q", formatted.Body)
	}
}

func TestBodyWithMetadataKeepsContextOnSingleLinePlatforms(t *testing.T) {
	got := bodyWithMetadata(Message{Body: "Finished.", Metadata: "gpt-5.6-sol"})
	if got != "Finished. · gpt-5.6-sol" {
		t.Fatalf("body=%q", got)
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
