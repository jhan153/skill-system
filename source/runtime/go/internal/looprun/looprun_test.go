package looprun

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestInactiveSessionDoesNotResolveLoop(t *testing.T) {
	t.Setenv("CODEX_HOME", t.TempDir())
	loop, pointer := activeLoop("missing", "")
	if loop != "" || pointer != "" {
		t.Fatalf("unexpected loop=%q pointer=%q", loop, pointer)
	}
}

func TestActivePointerResolution(t *testing.T) {
	home := t.TempDir()
	t.Setenv("CODEX_HOME", home)
	loop := filepath.Join(t.TempDir(), "loop")
	if err := os.MkdirAll(loop, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(loop, "contract.yaml"), []byte("schema_version: 2\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(loop, "state.yaml"), []byte("status: active\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	pointerDir := filepath.Join(home, "harness", "active-loops")
	if err := os.MkdirAll(pointerDir, 0o755); err != nil {
		t.Fatal(err)
	}
	raw, _ := json.Marshal(map[string]string{"status": "active", "loop_run_dir": loop})
	if err := os.WriteFile(filepath.Join(pointerDir, "session.json"), raw, 0o600); err != nil {
		t.Fatal(err)
	}
	resolved, pointer := activeLoop("session", "")
	if resolved != loop || pointer == "" {
		t.Fatalf("resolved=%q pointer=%q", resolved, pointer)
	}
}

func TestDeactivateMatchesExpectedLoop(t *testing.T) {
	home := t.TempDir()
	pointer := filepath.Join(home, "session.json")
	loop := filepath.Join(home, "loop")
	raw, _ := json.Marshal(map[string]string{"status": "active", "loop_run_dir": loop})
	if err := os.WriteFile(pointer, raw, 0o600); err != nil {
		t.Fatal(err)
	}
	deactivate(pointer, filepath.Join(home, "other"), "success")
	unchanged, _ := os.ReadFile(pointer)
	var value map[string]any
	if err := json.Unmarshal(unchanged, &value); err != nil || value["status"] != "active" {
		t.Fatalf("mismatched loop changed pointer: %s err=%v", unchanged, err)
	}
	deactivate(pointer, loop, "success")
	updated, _ := os.ReadFile(pointer)
	if err := json.Unmarshal(updated, &value); err != nil || value["status"] != "terminal" || value["final_action"] != "success" {
		t.Fatalf("matching loop did not terminate pointer: %s err=%v", updated, err)
	}
}
