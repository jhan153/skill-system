package projectcontext

import (
	"os"
	"path/filepath"
	"testing"
)

func TestResolveNearestAndNoParentMerge(t *testing.T) {
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	child := filepath.Join(root, "packages", "app")
	if err := os.MkdirAll(filepath.Join(child, "src"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, ManifestName), []byte("schema_version: 1\nproject_id: root\nmemory_bank:\n  root: memory\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(child, ManifestName), []byte("schema_version: 1\nproject_id: child\nplans:\n  root: docs/plan\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	result, err := Resolve(filepath.Join(child, "src"), "")
	if err != nil {
		t.Fatal(err)
	}
	if result.ProjectID != "child" || result.MemoryBank != nil || result.Plans == nil {
		t.Fatalf("unexpected nearest result: %#v", result)
	}
}

func TestResolveStopsAtRepositoryRoot(t *testing.T) {
	parent := t.TempDir()
	root := filepath.Join(parent, "repo")
	if err := os.MkdirAll(filepath.Join(root, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(parent, ManifestName), []byte("schema_version: 1\nproject_id: wrong\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	result, err := Resolve(root, "")
	if err != nil {
		t.Fatal(err)
	}
	if result.Status != "unavailable" {
		t.Fatalf("escaped repository root: %#v", result)
	}
}

func TestResolveExactAndRelativePaths(t *testing.T) {
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "kb"), 0o755); err != nil {
		t.Fatal(err)
	}
	manifest := filepath.Join(root, "custom.yaml")
	content := "schema_version: 1\nproject_id: exact\nknowledge_base:\n  root: kb\nllm_wikis:\n  book:\n    root: ../wiki\n"
	if err := os.WriteFile(manifest, []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
	result, err := Resolve("", manifest)
	if err != nil {
		t.Fatal(err)
	}
	if result.KnowledgeBase == nil || !result.KnowledgeBase.Exists {
		t.Fatalf("knowledge path not resolved: %#v", result)
	}
	if len(result.LLMWikis) != 1 || result.LLMWikis[0].Name != "book" {
		t.Fatalf("wiki not resolved: %#v", result.LLMWikis)
	}
}
