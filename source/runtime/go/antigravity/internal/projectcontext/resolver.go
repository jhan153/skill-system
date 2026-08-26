package projectcontext

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

const ManifestName = "project-context.yaml"

type Store struct {
	Root    string `yaml:"root" json:"root,omitempty"`
	Index   string `yaml:"index" json:"index,omitempty"`
	Storage string `yaml:"storage" json:"storage,omitempty"`
}

type Wiki struct {
	Root   string `yaml:"root" json:"root,omitempty"`
	Guide  string `yaml:"guide" json:"guide,omitempty"`
	Access string `yaml:"access" json:"access,omitempty"`
}

type Manifest struct {
	SchemaVersion int             `yaml:"schema_version" json:"schema_version"`
	ProjectID     string          `yaml:"project_id" json:"project_id"`
	SkillRoots    []string        `yaml:"skill_roots" json:"skill_roots,omitempty"`
	MemoryBank    *Store          `yaml:"memory_bank" json:"memory_bank,omitempty"`
	KnowledgeBase *Store          `yaml:"knowledge_base" json:"knowledge_base,omitempty"`
	Plans         *Store          `yaml:"plans" json:"plans,omitempty"`
	LLMWikis      map[string]Wiki `yaml:"llm_wikis" json:"llm_wikis,omitempty"`
}

type Location struct {
	Name        string `json:"name"`
	Path        string `json:"path"`
	Exists      bool   `json:"exists"`
	IndexPath   string `json:"index_path,omitempty"`
	IndexExists bool   `json:"index_exists,omitempty"`
}

type Result struct {
	Status        string     `json:"status"`
	ManifestPath  string     `json:"manifest_path,omitempty"`
	ProjectID     string     `json:"project_id,omitempty"`
	SkillRoots    []Location `json:"skill_roots,omitempty"`
	MemoryBank    *Location  `json:"memory_bank,omitempty"`
	KnowledgeBase *Location  `json:"knowledge_base,omitempty"`
	Plans         *Location  `json:"plans,omitempty"`
	LLMWikis      []Location `json:"llm_wikis,omitempty"`
}

func Resolve(start, exact string) (Result, error) {
	manifestPath, err := locate(start, exact)
	if err != nil {
		return Result{}, err
	}
	if manifestPath == "" {
		return Result{Status: "unavailable"}, nil
	}
	raw, err := os.ReadFile(manifestPath)
	if err != nil {
		return Result{}, fmt.Errorf("read manifest: %w", err)
	}
	var manifest Manifest
	if err := yaml.Unmarshal(raw, &manifest); err != nil {
		return Result{}, fmt.Errorf("parse manifest: %w", err)
	}
	if manifest.SchemaVersion != 1 {
		return Result{}, fmt.Errorf("unsupported schema_version %d", manifest.SchemaVersion)
	}
	manifest.ProjectID = strings.TrimSpace(manifest.ProjectID)
	if manifest.ProjectID == "" {
		return Result{}, errors.New("project_id is required")
	}
	base := filepath.Dir(manifestPath)
	result := Result{
		Status:       "available",
		ManifestPath: manifestPath,
		ProjectID:    manifest.ProjectID,
	}
	for _, root := range manifest.SkillRoots {
		if strings.TrimSpace(root) != "" {
			result.SkillRoots = append(result.SkillRoots, location(base, "skill_root", root))
		}
	}
	if manifest.MemoryBank != nil && strings.TrimSpace(manifest.MemoryBank.Root) != "" {
		item := location(base, "memory_bank", manifest.MemoryBank.Root)
		result.MemoryBank = &item
	}
	if manifest.KnowledgeBase != nil && strings.TrimSpace(manifest.KnowledgeBase.Root) != "" {
		item := location(base, "knowledge_base", manifest.KnowledgeBase.Root)
		index := strings.TrimSpace(manifest.KnowledgeBase.Index)
		if index == "" {
			index = filepath.Join(item.Path, "index.md")
		}
		indexLocation := location(base, "knowledge_index", index)
		item.IndexPath = indexLocation.Path
		item.IndexExists = indexLocation.Exists
		result.KnowledgeBase = &item
	}
	if manifest.Plans != nil && strings.TrimSpace(manifest.Plans.Root) != "" {
		item := location(base, "plans", manifest.Plans.Root)
		result.Plans = &item
	}
	for name, wiki := range manifest.LLMWikis {
		if strings.TrimSpace(wiki.Root) != "" {
			result.LLMWikis = append(result.LLMWikis, location(base, name, wiki.Root))
		}
	}
	sort.Slice(result.LLMWikis, func(i, j int) bool { return result.LLMWikis[i].Name < result.LLMWikis[j].Name })
	return result, nil
}

func locate(start, exact string) (string, error) {
	if strings.TrimSpace(exact) != "" {
		path, err := filepath.Abs(filepath.Clean(exact))
		if err != nil {
			return "", err
		}
		if info, err := os.Stat(path); err == nil && info.IsDir() {
			path = filepath.Join(path, ManifestName)
		}
		if _, err := os.Stat(path); err != nil {
			if os.IsNotExist(err) {
				return "", nil
			}
			return "", err
		}
		return path, nil
	}
	if strings.TrimSpace(start) == "" {
		var err error
		start, err = os.Getwd()
		if err != nil {
			return "", err
		}
	}
	dir, err := filepath.Abs(filepath.Clean(start))
	if err != nil {
		return "", err
	}
	if info, statErr := os.Stat(dir); statErr == nil && !info.IsDir() {
		dir = filepath.Dir(dir)
	}
	for {
		candidate := filepath.Join(dir, ManifestName)
		if info, statErr := os.Stat(candidate); statErr == nil && !info.IsDir() {
			return candidate, nil
		} else if statErr != nil && !os.IsNotExist(statErr) {
			return "", statErr
		}
		if _, gitErr := os.Stat(filepath.Join(dir, ".git")); gitErr == nil {
			return "", nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", nil
		}
		dir = parent
	}
}

func location(base, name, raw string) Location {
	path := strings.TrimSpace(raw)
	if !filepath.IsAbs(path) {
		path = filepath.Join(base, path)
	}
	path = filepath.Clean(path)
	_, err := os.Stat(path)
	return Location{Name: name, Path: path, Exists: err == nil}
}

func Context(result Result) string {
	if result.Status != "available" {
		return ""
	}
	stores := make([]string, 0, 3)
	if result.MemoryBank != nil {
		stores = append(stores, "memory_bank")
	}
	if result.KnowledgeBase != nil {
		stores = append(stores, "knowledge_base")
	}
	if result.Plans != nil {
		stores = append(stores, "plans")
	}
	wikis := make([]string, 0, len(result.LLMWikis))
	for _, wiki := range result.LLMWikis {
		wikis = append(wikis, wiki.Name)
	}
	parts := []string{fmt.Sprintf("Project context manifest: %s (project_id=%s).", result.ManifestPath, result.ProjectID)}
	if len(stores) > 0 {
		parts = append(parts, "Declared stores: "+strings.Join(stores, ", ")+".")
	}
	if len(wikis) > 0 {
		parts = append(parts, "Named LLM Wikis: "+strings.Join(wikis, ", ")+" (explicit selection only).")
	}
	parts = append(parts, "Use only task-relevant slices through their owning skills; do not auto-load or mutate store content.")
	return strings.Join(parts, " ")
}
