package systemcontract

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strings"
	"testing"

	"gopkg.in/yaml.v3"
)

var (
	localResourcePattern = regexp.MustCompile("`((?:references|assets|scripts)/[^`]+)`")
	posixHomePattern     = regexp.MustCompile(`(?:^|[\\s\"'=])/(?:Users|home)/[^/\\s\"']+`)
	windowsHomePattern   = regexp.MustCompile(`(?i)[A-Z]:[\\\\/]Users[\\\\/][^\\\\/\\s\"']+`)
)

type skillFrontmatter struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description"`
}

type pluginManifest struct {
	Name        string   `yaml:"name"`
	Version     string   `yaml:"version"`
	Description string   `yaml:"description"`
	Skills      []string `yaml:"skills"`
}

type providerCatalog struct {
	SchemaVersion int                `json:"schema_version"`
	Providers     []providerContract `json:"providers"`
}

type providerContract struct {
	ID                    string           `json:"id"`
	Status                string           `json:"status"`
	SourceRoot            string           `json:"source_root"`
	RuntimeRoot           string           `json:"runtime_root"`
	GlobalRule            string           `json:"global_rule"`
	PluginSkillPattern    string           `json:"plugin_skill_pattern"`
	PluginManifestPattern string           `json:"plugin_manifest_pattern"`
	Capabilities          []string         `json:"capabilities"`
	Harness               *harnessContract `json:"harness,omitempty"`
}

type harnessContract struct {
	Config               string   `json:"config"`
	ModuleRoot           string   `json:"module_root"`
	SourceEntrypoints    []string `json:"source_entrypoints"`
	GeneratedEntrypoints []string `json:"generated_entrypoints"`
	ConfigMarkers        []string `json:"config_markers"`
}

func TestCanonicalSkillCatalog(t *testing.T) {
	root := repositoryRoot(t)
	skills := loadCanonicalSkills(t, root)
	plugins := loadPluginManifests(t, root)
	owners := map[string][]string{}
	pluginNames := map[string]bool{}

	for _, plugin := range plugins {
		if plugin.Name == "" {
			t.Errorf("plugin manifest has an empty name")
			continue
		}
		if pluginNames[plugin.Name] {
			t.Errorf("duplicate plugin name %q", plugin.Name)
		}
		pluginNames[plugin.Name] = true
		seen := map[string]bool{}
		for _, skillID := range plugin.Skills {
			if seen[skillID] {
				t.Errorf("plugin %s lists skill %s more than once", plugin.Name, skillID)
				continue
			}
			seen[skillID] = true
			if _, exists := skills[skillID]; !exists {
				t.Errorf("plugin %s references missing canonical skill %s", plugin.Name, skillID)
			}
			owners[skillID] = append(owners[skillID], plugin.Name)
		}
	}

	for skillID := range skills {
		sort.Strings(owners[skillID])
		switch len(owners[skillID]) {
		case 0:
			t.Errorf("canonical skill %s has no plugin owner", skillID)
		case 1:
		default:
			t.Errorf("canonical skill %s has multiple plugin owners: %v", skillID, owners[skillID])
		}
	}
}

func TestProviderSkillPackages(t *testing.T) {
	root := repositoryRoot(t)
	plugins := loadPluginManifests(t, root)
	providers := loadProviderCatalog(t, root)

	for _, provider := range providers {
		if provider.Status != "active" {
			continue
		}
		if !contains(provider.Capabilities, "plugins") {
			continue
		}
		if strings.Count(provider.PluginSkillPattern, "{plugin}") != 1 {
			t.Errorf("provider %s plugin_skill_pattern must contain one {plugin}", provider.ID)
			continue
		}
		if strings.Count(provider.PluginManifestPattern, "{plugin}") != 1 {
			t.Errorf("provider %s plugin_manifest_pattern must contain one {plugin}", provider.ID)
			continue
		}
		for _, plugin := range plugins {
			relative := strings.Replace(provider.PluginSkillPattern, "{plugin}", plugin.Name, 1)
			packageRoot := filepath.Join(root, filepath.FromSlash(relative))
			actualPackage := skillIDsAtRoot(t, packageRoot)
			compareSets(
				t,
				fmt.Sprintf("%s plugin %s skills", provider.ID, plugin.Name),
				boolSet(plugin.Skills),
				actualPackage,
			)
			validateSkillResources(t, packageRoot)
			validateSharedReportPayload(t, packageRoot, plugin.Skills)
			manifestRelative := strings.Replace(
				provider.PluginManifestPattern,
				"{plugin}",
				plugin.Name,
				1,
			)
			validatePluginManifest(
				t,
				provider.ID,
				filepath.Join(root, filepath.FromSlash(manifestRelative)),
				plugin.Name,
			)
		}
	}
}

func TestProviderHarnessWiring(t *testing.T) {
	root := repositoryRoot(t)
	providers := loadProviderCatalog(t, root)
	seenProviders := map[string]bool{}

	for _, provider := range providers {
		if provider.ID == "" {
			t.Errorf("provider declaration has an empty id")
			continue
		}
		if seenProviders[provider.ID] {
			t.Errorf("duplicate provider id %q", provider.ID)
		}
		seenProviders[provider.ID] = true
		if provider.Status != "active" {
			continue
		}

		validateRelativeRepoPath(t, provider.ID+" source_root", provider.SourceRoot)
		if provider.PluginSkillPattern != "" {
			validateRelativeRepoPath(
				t,
				provider.ID+" plugin_skill_pattern",
				strings.Replace(provider.PluginSkillPattern, "{plugin}", "plugin", 1),
			)
		}
		if provider.PluginManifestPattern != "" {
			validateRelativeRepoPath(
				t,
				provider.ID+" plugin_manifest_pattern",
				strings.Replace(provider.PluginManifestPattern, "{plugin}", "plugin", 1),
			)
		}
		if _, err := os.Stat(filepath.Join(root, filepath.FromSlash(provider.SourceRoot))); err != nil {
			t.Errorf("provider %s source_root: %v", provider.ID, err)
		}

		capabilities := map[string]bool{}
		for _, capability := range provider.Capabilities {
			if capabilities[capability] {
				t.Errorf("provider %s duplicates capability %s", provider.ID, capability)
			}
			capabilities[capability] = true
		}
		if capabilities["global_rules"] {
			validateRelativeRepoPath(t, provider.ID+" runtime_root", provider.RuntimeRoot)
			validateRelativeRepoPath(t, provider.ID+" global_rule", provider.GlobalRule)
			if _, err := os.Stat(filepath.Join(root, filepath.FromSlash(provider.GlobalRule))); err != nil {
				t.Errorf("provider %s global_rule: %v", provider.ID, err)
			}
		} else if provider.RuntimeRoot != "" || provider.GlobalRule != "" {
			t.Errorf("provider %s declares runtime/global rule paths without global_rules capability", provider.ID)
		}
		hasHarness := capabilities["runtime_harness"] || capabilities["common_harness"]
		if !hasHarness {
			if provider.Harness != nil {
				t.Errorf("provider %s declares harness data without a harness capability", provider.ID)
			}
			continue
		}
		if provider.Harness == nil {
			t.Errorf("provider %s declares a harness capability without harness data", provider.ID)
			continue
		}

		harness := provider.Harness
		validateRelativeRepoPath(t, provider.ID+" harness config", harness.Config)
		validateRelativeRepoPath(t, provider.ID+" harness module_root", harness.ModuleRoot)
		moduleRoot := filepath.Join(root, filepath.FromSlash(harness.ModuleRoot))
		if _, err := os.Stat(filepath.Join(moduleRoot, "go.mod")); err != nil {
			t.Errorf("provider %s harness module_root: %v", provider.ID, err)
		}
		configPath := filepath.Join(root, filepath.FromSlash(harness.Config))
		configRaw, err := os.ReadFile(configPath)
		if err != nil {
			t.Errorf("provider %s harness config: %v", provider.ID, err)
			continue
		}
		var config any
		if err := json.Unmarshal(configRaw, &config); err != nil {
			t.Errorf("provider %s harness config is invalid JSON: %v", provider.ID, err)
			continue
		}
		checkMachineStrings(t, provider.ID+" harness config", config)

		for _, marker := range harness.ConfigMarkers {
			if marker == "" || !strings.Contains(string(configRaw), marker) {
				t.Errorf("provider %s harness config missing marker %q", provider.ID, marker)
			}
		}
		for _, relative := range append(
			append([]string{}, harness.SourceEntrypoints...),
			harness.GeneratedEntrypoints...,
		) {
			validateRelativeRepoPath(t, provider.ID+" harness entrypoint", relative)
			if _, err := os.Stat(filepath.Join(root, filepath.FromSlash(relative))); err != nil {
				t.Errorf("provider %s harness entrypoint %s: %v", provider.ID, relative, err)
			}
		}
		for _, relative := range harness.SourceEntrypoints {
			entrypoint := filepath.Join(root, filepath.FromSlash(relative))
			withinModule, err := filepath.Rel(moduleRoot, entrypoint)
			if err != nil || withinModule == ".." || strings.HasPrefix(withinModule, ".."+string(filepath.Separator)) {
				t.Errorf("provider %s harness source entrypoint escapes module_root: %s", provider.ID, relative)
			}
		}
	}
}

func validatePluginManifest(t *testing.T, providerID, path, expectedName string) {
	t.Helper()
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Errorf("provider %s plugin manifest %s: %v", providerID, filepath.ToSlash(path), err)
		return
	}
	var manifest struct {
		Name string `json:"name"`
	}
	if err := json.Unmarshal(raw, &manifest); err != nil {
		t.Errorf("provider %s plugin manifest %s is invalid JSON: %v", providerID, filepath.ToSlash(path), err)
		return
	}
	if manifest.Name != expectedName {
		t.Errorf(
			"provider %s plugin manifest %s name %q != %q",
			providerID,
			filepath.ToSlash(path),
			manifest.Name,
			expectedName,
		)
	}
}

func repositoryRoot(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("cannot resolve system contract test path")
	}
	root, err := filepath.Abs(filepath.Join(filepath.Dir(file), "../../../../.."))
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func loadCanonicalSkills(t *testing.T, root string) map[string]skillFrontmatter {
	t.Helper()
	skillRoot := filepath.Join(root, "source/skills")
	entries, err := os.ReadDir(skillRoot)
	if err != nil {
		t.Fatalf("canonical skill root: %v", err)
	}
	result := map[string]skillFrontmatter{}
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		skillID := entry.Name()
		path := filepath.Join(skillRoot, skillID, "SKILL.md")
		raw, readErr := os.ReadFile(path)
		if readErr != nil {
			t.Errorf("canonical skill %s has no readable SKILL.md: %v", skillID, readErr)
			continue
		}
		frontmatter, parseErr := parseSkillFrontmatter(raw)
		if parseErr != nil {
			t.Errorf("canonical skill %s frontmatter: %v", skillID, parseErr)
			continue
		}
		if frontmatter.Name != skillID {
			t.Errorf("canonical skill directory %s has frontmatter name %q", skillID, frontmatter.Name)
		}
		if strings.TrimSpace(frontmatter.Description) == "" {
			t.Errorf("canonical skill %s has an empty description", skillID)
		}
		result[skillID] = frontmatter
	}
	return result
}

func parseSkillFrontmatter(raw []byte) (skillFrontmatter, error) {
	var frontmatter skillFrontmatter
	text := string(raw)
	if !strings.HasPrefix(text, "---\n") {
		return frontmatter, fmt.Errorf("missing frontmatter start")
	}
	remainder := strings.TrimPrefix(text, "---\n")
	end := strings.Index(remainder, "\n---\n")
	if end < 0 {
		return frontmatter, fmt.Errorf("unclosed frontmatter")
	}
	if err := yaml.Unmarshal([]byte(remainder[:end]), &frontmatter); err != nil {
		return frontmatter, err
	}
	return frontmatter, nil
}

func loadPluginManifests(t *testing.T, root string) []pluginManifest {
	t.Helper()
	paths, err := filepath.Glob(filepath.Join(root, "source/plugins/*.yaml"))
	if err != nil {
		t.Fatal(err)
	}
	if len(paths) == 0 {
		t.Fatal("no plugin manifests found")
	}
	var result []pluginManifest
	for _, path := range paths {
		raw, readErr := os.ReadFile(path)
		if readErr != nil {
			t.Errorf("plugin manifest %s: %v", filepath.ToSlash(path), readErr)
			continue
		}
		var manifest pluginManifest
		if err := yaml.Unmarshal(raw, &manifest); err != nil {
			t.Errorf("plugin manifest %s: %v", filepath.ToSlash(path), err)
			continue
		}
		result = append(result, manifest)
	}
	return result
}

func loadProviderCatalog(t *testing.T, root string) []providerContract {
	t.Helper()
	path := filepath.Join(root, "source/platform/providers.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("provider catalog: %v", err)
	}
	var catalog providerCatalog
	if err := json.Unmarshal(raw, &catalog); err != nil {
		t.Fatalf("provider catalog JSON: %v", err)
	}
	if catalog.SchemaVersion != 1 {
		t.Fatalf("provider catalog schema_version %d != 1", catalog.SchemaVersion)
	}
	if len(catalog.Providers) == 0 {
		t.Fatal("provider catalog has no providers")
	}
	return catalog.Providers
}

func skillIDsAtRoot(t *testing.T, root string) map[string]bool {
	t.Helper()
	entries, err := os.ReadDir(root)
	if err != nil {
		t.Errorf("skill package root %s: %v", filepath.ToSlash(root), err)
		return map[string]bool{}
	}
	result := map[string]bool{}
	for _, entry := range entries {
		if entry.IsDir() {
			if _, err := os.Stat(filepath.Join(root, entry.Name(), "SKILL.md")); err == nil {
				result[entry.Name()] = true
			}
		}
	}
	return result
}

func validateSkillResources(t *testing.T, skillRoot string) {
	t.Helper()
	for skillID := range skillIDsAtRoot(t, skillRoot) {
		skillDir := filepath.Join(skillRoot, skillID)
		raw, err := os.ReadFile(filepath.Join(skillDir, "SKILL.md"))
		if err != nil {
			t.Errorf("%s SKILL.md: %v", filepath.ToSlash(skillDir), err)
			continue
		}
		for _, match := range localResourcePattern.FindAllStringSubmatch(string(raw), -1) {
			reference := strings.SplitN(match[1], "#", 2)[0]
			if filepath.IsAbs(reference) || containsParent(reference) {
				t.Errorf("%s has non-local resource reference %q", filepath.ToSlash(skillDir), match[1])
				continue
			}
			if _, err := os.Stat(filepath.Join(skillDir, filepath.FromSlash(reference))); err != nil {
				t.Errorf("%s references missing local resource %s", filepath.ToSlash(skillDir), reference)
			}
		}
	}
}

func validateSharedReportPayload(t *testing.T, skillRoot string, skills []string) {
	t.Helper()
	hasReport := false
	for _, skillID := range skills {
		if !strings.HasPrefix(skillID, "report-") {
			continue
		}
		hasReport = true
		legacy := filepath.Join(skillRoot, skillID, "scripts", "report-canvas")
		if _, err := os.Stat(legacy); err == nil {
			t.Errorf("report skill retains duplicated Canvas payload: %s", filepath.ToSlash(legacy))
		}
	}
	canvasRoot := filepath.Join(filepath.Dir(skillRoot), "shared", "report-canvas")
	if !hasReport {
		if _, err := os.Stat(canvasRoot); err == nil {
			t.Errorf("plugin without report skills contains Canvas payload: %s", filepath.ToSlash(canvasRoot))
		}
		return
	}
	for _, name := range []string{"render_report.py", "report-model.schema.json", "template.html"} {
		if _, err := os.Stat(filepath.Join(canvasRoot, name)); err != nil {
			t.Errorf("shared Report Canvas payload missing %s: %v", name, err)
		}
	}
}

func validateRelativeRepoPath(t *testing.T, label, value string) {
	t.Helper()
	if value == "" {
		t.Errorf("%s is empty", label)
		return
	}
	if filepath.IsAbs(filepath.FromSlash(value)) || containsParent(value) {
		t.Errorf("%s must be repository-relative, got %q", label, value)
	}
}

func containsParent(value string) bool {
	for _, part := range strings.Split(filepath.ToSlash(value), "/") {
		if part == ".." {
			return true
		}
	}
	return false
}

func checkMachineStrings(t *testing.T, label string, value any) {
	t.Helper()
	switch typed := value.(type) {
	case map[string]any:
		for key, child := range typed {
			checkMachineStrings(t, label+"."+key, child)
		}
	case []any:
		for index, child := range typed {
			checkMachineStrings(t, fmt.Sprintf("%s[%d]", label, index), child)
		}
	case string:
		if posixHomePattern.MatchString(typed) || windowsHomePattern.MatchString(typed) {
			t.Errorf("%s contains a machine-specific home path: %q", label, typed)
		}
	}
}

func boolSet(values []string) map[string]bool {
	result := map[string]bool{}
	for _, value := range values {
		result[value] = true
	}
	return result
}

func compareSets(t *testing.T, label string, expected, actual map[string]bool) {
	t.Helper()
	missing := setDifference(expected, actual)
	unexpected := setDifference(actual, expected)
	if len(missing) > 0 || len(unexpected) > 0 {
		t.Errorf("%s differ: missing=%v unexpected=%v", label, missing, unexpected)
	}
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

func contains(values []string, expected string) bool {
	for _, value := range values {
		if value == expected {
			return true
		}
	}
	return false
}
