package systemcontract

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	pathpkg "path"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strings"
	"testing"

	"gopkg.in/yaml.v3"
)

var (
	localResourcePattern   = regexp.MustCompile("`((?:references|assets|scripts)/[^`]+)`")
	posixHomePattern       = regexp.MustCompile(`(?:^|[\\s\"'=])/(?:Users|home)/[^/\\s\"']+`)
	windowsHomePattern     = regexp.MustCompile(`(?i)[A-Z]:[\\\\/]Users[\\\\/][^\\\\/\\s\"']+`)
	routingFamilyIDPattern = regexp.MustCompile(`^[a-z][a-z0-9-]*$`)
)

type skillFrontmatter struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description"`
}

type skillResource struct {
	Source     string
	Target     string
	Projection string
	Load       string
	Condition  string
}

type resourceClaim struct {
	Skill      string
	Source     string
	Projection string
	Target     string
}

type skillDeclaration struct {
	skillFrontmatter
	Role          string
	Family        string
	RoutingCard   string
	Resources     []skillResource
	AllowImplicit bool
	SourceText    string
}

type routingFamilyCatalog struct {
	SchemaVersion int             `json:"schema_version"`
	Families      []routingFamily `json:"families"`
}

type routingFamily struct {
	ID          string   `json:"id"`
	DisplayName string   `json:"display_name"`
	EntryOwners string   `json:"entry_owners"`
	Aliases     []string `json:"aliases"`
}

type pluginManifest struct {
	Name              string   `yaml:"name"`
	Description       string   `yaml:"description"`
	ShortDescription  string   `yaml:"short_description"`
	CodexCatalogOrder int      `yaml:"codex_catalog_order"`
	Skills            []string `yaml:"skills"`
}

type distributionMetadata struct {
	SchemaVersion int    `json:"schema_version"`
	BundleVersion string `json:"bundle_version"`
	Publisher     struct {
		Name string `json:"name"`
	} `json:"publisher"`
	Marketplace struct {
		Name        string `json:"name"`
		DisplayName string `json:"display_name"`
		Description string `json:"description"`
		Category    string `json:"category"`
		CodexPolicy struct {
			Installation   string `json:"installation"`
			Authentication string `json:"authentication"`
		} `json:"codex_policy"`
	} `json:"marketplace"`
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
	families := loadRoutingFamilies(t, root)
	plugins := loadPluginManifests(t, root)
	owners := map[string][]string{}
	pluginNames := map[string]bool{}
	codexCatalogOrders := map[int]string{}
	if len(skills) != 67 {
		t.Errorf("canonical skill count %d != preserved identity count 67", len(skills))
	}
	for skillID, declaration := range skills {
		if _, exists := families[declaration.Family]; !exists {
			t.Errorf("canonical skill %s references unknown family %q", skillID, declaration.Family)
		}
	}

	for _, plugin := range plugins {
		if plugin.Name == "" {
			t.Errorf("plugin manifest has an empty name")
			continue
		}
		if pluginNames[plugin.Name] {
			t.Errorf("duplicate plugin name %q", plugin.Name)
		}
		pluginNames[plugin.Name] = true
		if strings.TrimSpace(plugin.ShortDescription) == "" {
			t.Errorf("plugin %s has an empty short_description", plugin.Name)
		}
		if plugin.CodexCatalogOrder <= 0 {
			t.Errorf("plugin %s has invalid codex_catalog_order %d", plugin.Name, plugin.CodexCatalogOrder)
		} else if previous := codexCatalogOrders[plugin.CodexCatalogOrder]; previous != "" {
			t.Errorf(
				"plugins %s and %s share codex_catalog_order %d",
				previous,
				plugin.Name,
				plugin.CodexCatalogOrder,
			)
		} else {
			codexCatalogOrders[plugin.CodexCatalogOrder] = plugin.Name
		}
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
	validateRoutingProjections(t, root, skills, families, owners)
	validateResourceClosureFalsifiers(t)
}

func TestProviderSkillPackages(t *testing.T) {
	root := repositoryRoot(t)
	skills := loadCanonicalSkills(t, root)
	plugins := loadPluginManifests(t, root)
	providers := loadProviderCatalog(t, root)
	distribution := loadDistributionMetadata(t, root)

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
			validateSkillResources(t, root, provider.ID, packageRoot, plugin.Skills, skills)
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
				plugin,
				distribution.BundleVersion,
			)
		}
	}
	validateCodexMarketplace(t, root, distribution, plugins)
	validateClaudeMarketplace(t, root, distribution, plugins)
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
		validateProviderRoutingOverlay(t, root, provider)

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
			validateRuntimeRoutingProjection(t, root, provider)
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

func validatePluginManifest(
	t *testing.T,
	providerID, path string,
	expected pluginManifest,
	bundleVersion string,
) {
	t.Helper()
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Errorf("provider %s plugin manifest %s: %v", providerID, filepath.ToSlash(path), err)
		return
	}
	var manifest struct {
		Name      string `json:"name"`
		Version   string `json:"version"`
		Interface struct {
			ShortDescription string `json:"shortDescription"`
		} `json:"interface"`
	}
	if err := json.Unmarshal(raw, &manifest); err != nil {
		t.Errorf("provider %s plugin manifest %s is invalid JSON: %v", providerID, filepath.ToSlash(path), err)
		return
	}
	if manifest.Name != expected.Name {
		t.Errorf(
			"provider %s plugin manifest %s name %q != %q",
			providerID,
			filepath.ToSlash(path),
			manifest.Name,
			expected.Name,
		)
	}
	if providerID == "codex" || providerID == "claude" {
		if manifest.Version != bundleVersion {
			t.Errorf(
				"provider %s plugin manifest %s version %q != bundle version %q",
				providerID,
				filepath.ToSlash(path),
				manifest.Version,
				bundleVersion,
			)
		}
	}
	if providerID == "codex" && manifest.Interface.ShortDescription != expected.ShortDescription {
		t.Errorf(
			"Codex plugin manifest %s shortDescription %q != %q",
			filepath.ToSlash(path),
			manifest.Interface.ShortDescription,
			expected.ShortDescription,
		)
	}
}

func validateCodexMarketplace(
	t *testing.T,
	root string,
	distribution distributionMetadata,
	plugins []pluginManifest,
) {
	t.Helper()
	path := filepath.Join(root, ".agents/plugins/marketplace.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Errorf("Codex marketplace: %v", err)
		return
	}
	var catalog struct {
		Name      string `json:"name"`
		Interface struct {
			DisplayName string `json:"displayName"`
		} `json:"interface"`
		Plugins []struct {
			Name   string `json:"name"`
			Source struct {
				Source string `json:"source"`
				Path   string `json:"path"`
			} `json:"source"`
			Policy struct {
				Installation   string `json:"installation"`
				Authentication string `json:"authentication"`
			} `json:"policy"`
			Category string `json:"category"`
		} `json:"plugins"`
	}
	if err := json.Unmarshal(raw, &catalog); err != nil {
		t.Errorf("Codex marketplace JSON: %v", err)
		return
	}
	if catalog.Name != distribution.Marketplace.Name {
		t.Errorf("Codex marketplace name %q != %q", catalog.Name, distribution.Marketplace.Name)
	}
	if catalog.Interface.DisplayName != distribution.Marketplace.DisplayName {
		t.Errorf(
			"Codex marketplace displayName %q != %q",
			catalog.Interface.DisplayName,
			distribution.Marketplace.DisplayName,
		)
	}
	expectedOrder := append([]pluginManifest(nil), plugins...)
	sort.Slice(expectedOrder, func(i, j int) bool {
		return expectedOrder[i].CodexCatalogOrder < expectedOrder[j].CodexCatalogOrder
	})
	actualNames := map[string]bool{}
	for index, entry := range catalog.Plugins {
		if actualNames[entry.Name] {
			t.Errorf("Codex marketplace duplicates plugin %s", entry.Name)
		}
		actualNames[entry.Name] = true
		if index >= len(expectedOrder) {
			continue
		}
		expected := expectedOrder[index]
		if entry.Name != expected.Name {
			t.Errorf(
				"Codex marketplace plugin %d name %q != ordered profile %q",
				index,
				entry.Name,
				expected.Name,
			)
		}
		if entry.Source.Source != "local" || entry.Source.Path != "./plugins/"+expected.Name {
			t.Errorf(
				"Codex marketplace plugin %s source=%q path=%q",
				entry.Name,
				entry.Source.Source,
				entry.Source.Path,
			)
		}
		if entry.Policy.Installation != distribution.Marketplace.CodexPolicy.Installation ||
			entry.Policy.Authentication != distribution.Marketplace.CodexPolicy.Authentication {
			t.Errorf("Codex marketplace plugin %s policy differs from distribution metadata", entry.Name)
		}
		if entry.Category != distribution.Marketplace.Category {
			t.Errorf(
				"Codex marketplace plugin %s category %q != %q",
				entry.Name,
				entry.Category,
				distribution.Marketplace.Category,
			)
		}
	}
	expectedNames := make([]string, 0, len(plugins))
	for _, plugin := range plugins {
		expectedNames = append(expectedNames, plugin.Name)
	}
	compareSets(t, "Codex marketplace profiles", boolSet(expectedNames), actualNames)
}

func validateClaudeMarketplace(
	t *testing.T,
	root string,
	distribution distributionMetadata,
	plugins []pluginManifest,
) {
	t.Helper()
	path := filepath.Join(root, "plugins/.claude-plugin/marketplace.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Errorf("Claude marketplace: %v", err)
		return
	}
	var catalog struct {
		Name  string `json:"name"`
		Owner struct {
			Name string `json:"name"`
		} `json:"owner"`
		Description string `json:"description"`
		Plugins     []struct {
			Name        string `json:"name"`
			Source      string `json:"source"`
			Description string `json:"description"`
			Version     string `json:"version"`
			Category    string `json:"category"`
		} `json:"plugins"`
	}
	if err := json.Unmarshal(raw, &catalog); err != nil {
		t.Errorf("Claude marketplace JSON: %v", err)
		return
	}
	if catalog.Name != distribution.Marketplace.Name {
		t.Errorf("Claude marketplace name %q != %q", catalog.Name, distribution.Marketplace.Name)
	}
	if catalog.Owner.Name != distribution.Publisher.Name {
		t.Errorf("Claude marketplace owner %q != %q", catalog.Owner.Name, distribution.Publisher.Name)
	}
	if catalog.Description != distribution.Marketplace.Description {
		t.Errorf(
			"Claude marketplace description %q != %q",
			catalog.Description,
			distribution.Marketplace.Description,
		)
	}
	expectedByName := map[string]pluginManifest{}
	expectedNames := make([]string, 0, len(plugins))
	for _, plugin := range plugins {
		expectedByName[plugin.Name] = plugin
		expectedNames = append(expectedNames, plugin.Name)
	}
	actualNames := map[string]bool{}
	for _, entry := range catalog.Plugins {
		if actualNames[entry.Name] {
			t.Errorf("Claude marketplace duplicates plugin %s", entry.Name)
		}
		actualNames[entry.Name] = true
		expected, exists := expectedByName[entry.Name]
		if !exists {
			continue
		}
		if entry.Source != "./claude/"+expected.Name {
			t.Errorf("Claude marketplace plugin %s source %q is invalid", entry.Name, entry.Source)
		}
		if entry.Description != expected.Description {
			t.Errorf("Claude marketplace plugin %s description differs from profile", entry.Name)
		}
		if entry.Version != distribution.BundleVersion {
			t.Errorf(
				"Claude marketplace plugin %s version %q != %q",
				entry.Name,
				entry.Version,
				distribution.BundleVersion,
			)
		}
		if entry.Category != distribution.Marketplace.Category {
			t.Errorf(
				"Claude marketplace plugin %s category %q != %q",
				entry.Name,
				entry.Category,
				distribution.Marketplace.Category,
			)
		}
	}
	compareSets(t, "Claude marketplace profiles", boolSet(expectedNames), actualNames)
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

func loadCanonicalSkills(t *testing.T, root string) map[string]skillDeclaration {
	t.Helper()
	skillRoot := filepath.Join(root, "source/skills")
	entries, err := os.ReadDir(skillRoot)
	if err != nil {
		t.Fatalf("canonical skill root: %v", err)
	}
	result := map[string]skillDeclaration{}
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
		declaration, parseErr := parseSkillDeclaration(raw)
		if parseErr != nil {
			t.Errorf("canonical skill %s declaration: %v", skillID, parseErr)
			continue
		}
		if declaration.Name != skillID {
			t.Errorf("canonical skill directory %s has frontmatter name %q", skillID, declaration.Name)
		}
		if strings.TrimSpace(declaration.Description) == "" {
			t.Errorf("canonical skill %s has an empty description", skillID)
		}
		implicit, implicitErr := loadImplicitInvocation(filepath.Join(skillRoot, skillID, "agents/openai.yaml"))
		if implicitErr != nil {
			t.Errorf("canonical skill %s invocation metadata: %v", skillID, implicitErr)
			continue
		}
		declaration.AllowImplicit = implicit
		declaration.SourceText = string(raw)
		if err := validateCanonicalResources(root, skillID, declaration); err != nil {
			t.Errorf("canonical skill %s resource closure: %v", skillID, err)
			continue
		}
		result[skillID] = declaration
	}
	return result
}

func parseSkillDeclaration(raw []byte) (skillDeclaration, error) {
	frontmatter, err := parseSkillFrontmatter(raw)
	if err != nil {
		return skillDeclaration{}, err
	}
	card, role, family, resources, err := parseRoutingCard(string(raw))
	if err != nil {
		return skillDeclaration{}, err
	}
	return skillDeclaration{
		skillFrontmatter: frontmatter,
		Role:             role,
		Family:           family,
		RoutingCard:      card,
		Resources:        resources,
	}, nil
}

func parseRoutingCard(text string) (string, string, string, []skillResource, error) {
	const heading = "## Routing Card"
	marker := "\n" + heading + "\n"
	if strings.Count(text, marker) != 1 {
		return "", "", "", nil, fmt.Errorf("expected exactly one %s", heading)
	}
	start := strings.Index(text, marker) + 1
	end := strings.Index(text[start+len(heading):], "\n## ")
	if end < 0 {
		end = len(text)
	} else {
		end += start + len(heading)
	}
	card := strings.TrimRight(text[start:end], "\n")
	requiredFields := []string{
		"role", "family", "intent_signature", "use_when", "do_not_use_when",
		"expected_inputs", "expected_outputs", "context_targets", "risk_profile", "entry_scene",
	}
	previous := -1
	prefixed := "\n" + card
	for _, field := range requiredFields {
		fieldMarker := "\n- " + field + ":"
		if strings.Count(prefixed, fieldMarker) != 1 {
			return "", "", "", nil, fmt.Errorf("routing field %s must appear exactly once", field)
		}
		position := strings.Index(prefixed, fieldMarker)
		if position <= previous {
			return "", "", "", nil, fmt.Errorf("routing field %s is out of order", field)
		}
		previous = position
	}
	role, err := routingScalar(card, "role")
	if err != nil {
		return "", "", "", nil, err
	}
	family, err := routingScalar(card, "family")
	if err != nil {
		return "", "", "", nil, err
	}
	closureMarker := "\n### Resource Closure\n\n```json\n"
	closureStart := strings.Index(card, closureMarker)
	if closureStart < 0 {
		return "", "", "", nil, fmt.Errorf("missing structured Resource Closure")
	}
	jsonStart := closureStart + len(closureMarker)
	jsonEnd := strings.Index(card[jsonStart:], "\n```")
	if jsonEnd < 0 {
		return "", "", "", nil, fmt.Errorf("unclosed Resource Closure JSON")
	}
	jsonEnd += jsonStart
	if strings.TrimSpace(card[jsonEnd+4:]) != "" {
		return "", "", "", nil, fmt.Errorf("Resource Closure must be the final Routing Card subsection")
	}
	resources, err := decodeResourceClosure([]byte(card[jsonStart:jsonEnd]))
	if err != nil {
		return "", "", "", nil, err
	}
	return strings.TrimRight(card[:closureStart], "\n"), role, family, resources, nil
}

func routingScalar(card, field string) (string, error) {
	prefix := "- " + field + ":"
	for _, line := range strings.Split(card, "\n") {
		if !strings.HasPrefix(line, prefix) {
			continue
		}
		value := strings.TrimSpace(strings.TrimPrefix(line, prefix))
		if value == "" {
			return "", fmt.Errorf("routing field %s must be a scalar", field)
		}
		return value, nil
	}
	return "", fmt.Errorf("missing routing scalar %s", field)
}

func decodeResourceClosure(raw []byte) ([]skillResource, error) {
	var objects []json.RawMessage
	decoder := json.NewDecoder(bytes.NewReader(raw))
	if err := decoder.Decode(&objects); err != nil {
		return nil, fmt.Errorf("invalid Resource Closure JSON: %w", err)
	}
	if err := requireJSONEnd(decoder); err != nil {
		return nil, err
	}
	resources := make([]skillResource, 0, len(objects))
	for index, object := range objects {
		fields, err := decodeStringObject(object)
		if err != nil {
			return nil, fmt.Errorf("resource %d: %w", index, err)
		}
		required := []string{"source", "target", "projection", "load", "condition"}
		if len(fields) != len(required) {
			return nil, fmt.Errorf("resource %d must contain exactly %v", index, required)
		}
		for _, key := range required {
			if _, exists := fields[key]; !exists {
				return nil, fmt.Errorf("resource %d is missing %s", index, key)
			}
		}
		resource := skillResource{
			Source: fields["source"], Target: fields["target"], Projection: fields["projection"],
			Load: fields["load"], Condition: fields["condition"],
		}
		if err := validateResourceShape(resource); err != nil {
			return nil, fmt.Errorf("resource %d: %w", index, err)
		}
		resources = append(resources, resource)
	}
	if err := validateTargetSet(resources); err != nil {
		return nil, err
	}
	return resources, nil
}

func decodeStringObject(raw []byte) (map[string]string, error) {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	token, err := decoder.Token()
	if err != nil {
		return nil, err
	}
	if delimiter, ok := token.(json.Delim); !ok || delimiter != '{' {
		return nil, fmt.Errorf("entry must be an object")
	}
	result := map[string]string{}
	for decoder.More() {
		keyToken, err := decoder.Token()
		if err != nil {
			return nil, err
		}
		key, ok := keyToken.(string)
		if !ok {
			return nil, fmt.Errorf("object key is not a string")
		}
		if _, exists := result[key]; exists {
			return nil, fmt.Errorf("duplicate key %q", key)
		}
		var value string
		if err := decoder.Decode(&value); err != nil {
			return nil, fmt.Errorf("field %s must be a string: %w", key, err)
		}
		result[key] = value
	}
	if _, err := decoder.Token(); err != nil {
		return nil, err
	}
	if err := requireJSONEnd(decoder); err != nil {
		return nil, err
	}
	return result, nil
}

func requireJSONEnd(decoder *json.Decoder) error {
	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		if err == nil {
			return fmt.Errorf("JSON contains a trailing value")
		}
		return fmt.Errorf("invalid trailing JSON: %w", err)
	}
	return nil
}

func validateResourceShape(resource skillResource) error {
	if err := validateClosurePath(resource.Source, false); err != nil {
		return fmt.Errorf("source: %w", err)
	}
	if !strings.HasPrefix(resource.Source, "shared/") {
		return fmt.Errorf("source %q is outside shared canonical input", resource.Source)
	}
	if err := validateClosurePath(resource.Target, true); err != nil {
		return fmt.Errorf("target: %w", err)
	}
	if resource.Projection != "verbatim" && resource.Projection != "tree" && resource.Projection != "execution-item-view" {
		return fmt.Errorf("unknown projection %q", resource.Projection)
	}
	if resource.Load != "must_read" && resource.Load != "read_if_needed" {
		return fmt.Errorf("unknown load class %q", resource.Load)
	}
	if strings.TrimSpace(resource.Condition) == "" {
		return fmt.Errorf("condition is empty")
	}
	if resource.Projection == "execution-item-view" &&
		(resource.Source != "shared/docs/execution_item_contract.md" || resource.Target != "references/execution_item_view.md") {
		return fmt.Errorf("execution-item-view uses an unrecognized source/target tuple")
	}
	return nil
}

func validateClosurePath(value string, target bool) error {
	raw := value
	pluginTarget := strings.HasPrefix(raw, "@plugin/")
	if pluginTarget {
		if !target {
			return fmt.Errorf("@plugin is valid only for targets")
		}
		raw = strings.TrimPrefix(raw, "@plugin/")
	}
	if raw == "" || strings.ContainsAny(raw, "\\\x00:") || strings.HasPrefix(raw, "/") || strings.HasSuffix(raw, "/") {
		return fmt.Errorf("%q is not a portable relative path", value)
	}
	parts := strings.Split(raw, "/")
	for _, part := range parts {
		if part == "" || part == "." || part == ".." {
			return fmt.Errorf("%q is not normalized", value)
		}
	}
	if pathpkg.Clean(raw) != raw {
		return fmt.Errorf("%q is not normalized", value)
	}
	if target {
		if pluginTarget && parts[0] != "shared" {
			return fmt.Errorf("plugin target %q is outside @plugin/shared", value)
		}
		if !pluginTarget && parts[0] != "references" && parts[0] != "assets" && parts[0] != "scripts" {
			return fmt.Errorf("skill target %q is outside references/assets/scripts", value)
		}
	}
	return nil
}

func validateTargetSet(resources []skillResource) error {
	claimed := map[string]string{}
	for _, resource := range resources {
		normalized := strings.ToLower(strings.TrimPrefix(resource.Target, "@plugin/"))
		for existing, original := range claimed {
			if normalized == existing || strings.HasPrefix(normalized, existing+"/") || strings.HasPrefix(existing, normalized+"/") {
				return fmt.Errorf("overlapping targets %q and %q", resource.Target, original)
			}
		}
		claimed[normalized] = resource.Target
	}
	return nil
}

func validateCanonicalResources(root, skillID string, declaration skillDeclaration) error {
	sharedRoot := filepath.Join(root, "source/shared")
	resolvedShared, err := filepath.EvalSymlinks(sharedRoot)
	if err != nil {
		return fmt.Errorf("shared source root: %w", err)
	}
	for _, resource := range declaration.Resources {
		canonical := filepath.Join(root, "source", filepath.FromSlash(resource.Source))
		resolved, resolveErr := filepath.EvalSymlinks(canonical)
		if resolveErr != nil {
			return fmt.Errorf("%s source %s: %w", skillID, resource.Source, resolveErr)
		}
		relative, relErr := filepath.Rel(resolvedShared, resolved)
		if relErr != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
			return fmt.Errorf("%s source %s resolves outside source/shared", skillID, resource.Source)
		}
		info, err := os.Stat(canonical)
		if err != nil {
			return fmt.Errorf("%s source %s: %w", skillID, resource.Source, err)
		}
		if resource.Projection == "tree" && !info.IsDir() {
			return fmt.Errorf("%s tree source %s is not a directory", skillID, resource.Source)
		}
		if resource.Projection != "tree" && !info.Mode().IsRegular() {
			return fmt.Errorf("%s file source %s is not a regular file", skillID, resource.Source)
		}
		if resource.Projection == "tree" {
			walkErr := filepath.WalkDir(canonical, func(path string, entry os.DirEntry, walkErr error) error {
				if walkErr != nil {
					return walkErr
				}
				if entry.Type()&os.ModeSymlink != 0 {
					return fmt.Errorf("tree source contains symlink %s", filepath.ToSlash(path))
				}
				return nil
			})
			if walkErr != nil {
				return fmt.Errorf("%s source %s: %w", skillID, resource.Source, walkErr)
			}
		}
		if !strings.HasPrefix(resource.Target, "@plugin/") {
			if load, found, loadErr := routingLoadClass(declaration.RoutingCard, resource.Target); loadErr != nil {
				return fmt.Errorf("%s target %s: %w", skillID, resource.Target, loadErr)
			} else if found && load != resource.Load {
				return fmt.Errorf(
					"%s target %s load %s does not match Routing Card %s",
					skillID, resource.Target, resource.Load, load,
				)
			}
			localTarget := filepath.Join(root, "source/skills", skillID, filepath.FromSlash(resource.Target))
			if _, statErr := os.Lstat(localTarget); statErr == nil {
				return fmt.Errorf("%s target %s overlaps canonical local content", skillID, resource.Target)
			} else if !errors.Is(statErr, os.ErrNotExist) {
				return fmt.Errorf("%s target %s: %w", skillID, resource.Target, statErr)
			}
		}
	}
	return nil
}

func routingLoadClass(card, target string) (string, bool, error) {
	inContext := false
	current := ""
	found := ""
	for _, line := range strings.Split(card, "\n") {
		if line == "- context_targets:" {
			inContext = true
			continue
		}
		if inContext && strings.HasPrefix(line, "- ") {
			break
		}
		if !inContext {
			continue
		}
		trimmed := strings.TrimSpace(line)
		trimmed = strings.TrimPrefix(trimmed, "- ")
		switch {
		case strings.HasPrefix(trimmed, "must_read:"):
			current = "must_read"
		case strings.HasPrefix(trimmed, "read_if_needed:"):
			current = "read_if_needed"
		case strings.HasPrefix(trimmed, "do_not_load_by_default:"):
			current = ""
		}
		if current != "" && strings.Contains(line, target) {
			if found != "" && found != current {
				return "", false, fmt.Errorf("Routing Card declares conflicting load classes")
			}
			found = current
		}
	}
	return found, found != "", nil
}

func loadImplicitInvocation(path string) (bool, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return false, err
	}
	var manifest struct {
		Policy struct {
			AllowImplicit *bool `yaml:"allow_implicit_invocation"`
		} `yaml:"policy"`
	}
	if err := yaml.Unmarshal(raw, &manifest); err != nil {
		return false, err
	}
	if manifest.Policy.AllowImplicit == nil {
		return false, fmt.Errorf("missing allow_implicit_invocation")
	}
	return *manifest.Policy.AllowImplicit, nil
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

func loadDistributionMetadata(t *testing.T, root string) distributionMetadata {
	t.Helper()
	path := filepath.Join(root, "source/distribution.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("distribution metadata: %v", err)
	}
	var metadata distributionMetadata
	if err := json.Unmarshal(raw, &metadata); err != nil {
		t.Fatalf("distribution metadata JSON: %v", err)
	}
	if metadata.SchemaVersion != 1 {
		t.Fatalf("distribution metadata schema_version %d != 1", metadata.SchemaVersion)
	}
	if strings.TrimSpace(metadata.BundleVersion) == "" {
		t.Fatal("distribution metadata has an empty bundle_version")
	}
	if strings.TrimSpace(metadata.Publisher.Name) == "" {
		t.Fatal("distribution metadata has an empty publisher name")
	}
	if strings.TrimSpace(metadata.Marketplace.Name) == "" ||
		strings.TrimSpace(metadata.Marketplace.DisplayName) == "" ||
		strings.TrimSpace(metadata.Marketplace.Description) == "" ||
		strings.TrimSpace(metadata.Marketplace.Category) == "" {
		t.Fatal("distribution metadata has incomplete marketplace identity")
	}
	if strings.TrimSpace(metadata.Marketplace.CodexPolicy.Installation) == "" ||
		strings.TrimSpace(metadata.Marketplace.CodexPolicy.Authentication) == "" {
		t.Fatal("distribution metadata has incomplete Codex marketplace policy")
	}
	return metadata
}

func loadRoutingFamilies(t *testing.T, root string) map[string]routingFamily {
	t.Helper()
	path := filepath.Join(root, "source/shared/routing/families.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("routing family declaration: %v", err)
	}
	var catalog routingFamilyCatalog
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&catalog); err != nil {
		t.Fatalf("routing family declaration JSON: %v", err)
	}
	if err := requireJSONEnd(decoder); err != nil {
		t.Fatalf("routing family declaration JSON: %v", err)
	}
	if catalog.SchemaVersion != 1 || len(catalog.Families) == 0 {
		t.Fatalf("routing family declaration schema=%d families=%d", catalog.SchemaVersion, len(catalog.Families))
	}
	result := map[string]routingFamily{}
	aliases := map[string]string{}
	for _, family := range catalog.Families {
		if !routingFamilyIDPattern.MatchString(family.ID) || strings.TrimSpace(family.DisplayName) == "" ||
			strings.TrimSpace(family.EntryOwners) == "" || len(family.Aliases) == 0 {
			t.Errorf("routing family has incomplete fields: %#v", family)
			continue
		}
		if _, exists := result[family.ID]; exists {
			t.Errorf("duplicate routing family %q", family.ID)
			continue
		}
		for _, alias := range family.Aliases {
			normalized := strings.ToLower(strings.TrimSpace(alias))
			if normalized == "" {
				t.Errorf("routing family %s has an empty alias", family.ID)
				continue
			}
			if previous := aliases[normalized]; previous != "" {
				t.Errorf("routing families %s and %s share alias %q", previous, family.ID, alias)
			}
			aliases[normalized] = family.ID
		}
		result[family.ID] = family
	}
	return result
}

func validateRoutingProjections(
	t *testing.T,
	root string,
	skills map[string]skillDeclaration,
	families map[string]routingFamily,
	owners map[string][]string,
) {
	t.Helper()
	registryPath := filepath.Join(root, "source/shared/docs/skill_registry.md")
	registryRaw, err := os.ReadFile(registryPath)
	if err != nil {
		t.Errorf("generated skill registry: %v", err)
		return
	}
	registry := string(registryRaw)
	if !strings.Contains(registry, "Generated from each canonical `source/skills/*/SKILL.md` Routing Card") {
		t.Errorf("generated skill registry lacks its source marker")
	}
	rowPattern := regexp.MustCompile("(?m)^\\| `([^`]+)` \\| `([^`]+)` \\| `([^`]+)` \\| `([^`]+)` \\| `(true|false)` \\|$")
	actualRows := map[string][]string{}
	for _, match := range rowPattern.FindAllStringSubmatch(registry, -1) {
		if _, exists := actualRows[match[1]]; exists {
			t.Errorf("generated skill registry duplicates %s", match[1])
		}
		actualRows[match[1]] = match[2:]
	}
	compareSets(t, "generated skill registry rows", boolSet(mapKeys(skills)), boolSet(mapKeys(actualRows)))
	for skillID, declaration := range skills {
		row := actualRows[skillID]
		owner := ""
		if len(owners[skillID]) == 1 {
			owner = owners[skillID][0]
		}
		expected := []string{declaration.Family, declaration.Role, owner, fmt.Sprint(declaration.AllowImplicit)}
		if strings.Join(row, "\x00") != strings.Join(expected, "\x00") {
			t.Errorf("generated registry row %s=%v expected %v", skillID, row, expected)
		}
	}
	for familyID, family := range families {
		expected := fmt.Sprintf(
			"| `%s` | %s | %s | %s |",
			familyID, family.DisplayName, family.EntryOwners, strings.Join(family.Aliases, ", "),
		)
		if strings.Count(registry, expected) != 1 {
			t.Errorf("generated registry family row mismatch for %s", familyID)
		}
	}

	indexPath := filepath.Join(root, "source/shared/docs/skill_routing.md")
	indexRaw, err := os.ReadFile(indexPath)
	if err != nil {
		t.Errorf("generated skill routing index: %v", err)
		return
	}
	index := string(indexRaw)
	for familyID, family := range families {
		expectedSkills := map[string]bool{}
		for skillID, declaration := range skills {
			if declaration.Family == familyID {
				expectedSkills[skillID] = true
			}
		}
		indexRow := fmt.Sprintf("| `%s` | `docs/routing/%s.md` | %d |", familyID, familyID, len(expectedSkills))
		if strings.Count(index, indexRow) != 1 {
			t.Errorf("generated routing index row mismatch for %s", familyID)
		}
		familyPath := filepath.Join(root, "source/shared/docs/routing", familyID+".md")
		raw, readErr := os.ReadFile(familyPath)
		if readErr != nil {
			t.Errorf("generated routing family %s: %v", familyID, readErr)
			continue
		}
		text := string(raw)
		if !strings.HasPrefix(text, "# "+family.DisplayName+" Routing\n") {
			t.Errorf("generated routing family %s has the wrong display name", familyID)
		}
		actualSkills := map[string]bool{}
		for _, match := range regexp.MustCompile("(?m)^## `([^`]+)`$").FindAllStringSubmatch(text, -1) {
			if actualSkills[match[1]] {
				t.Errorf("generated routing family %s duplicates skill %s", familyID, match[1])
			}
			actualSkills[match[1]] = true
		}
		compareSets(t, "generated routing family "+familyID, expectedSkills, actualSkills)
		for skillID := range expectedSkills {
			body := strings.TrimSpace(strings.TrimPrefix(skills[skillID].RoutingCard, "## Routing Card"))
			needle := "## `" + skillID + "`\n\n" + body
			if strings.Count(text, needle) != 1 {
				t.Errorf("generated routing family %s does not project %s exactly", familyID, skillID)
			}
		}
	}
}

func validateRuntimeRoutingProjection(t *testing.T, root string, provider providerContract) {
	t.Helper()
	canonicalDocs := filepath.Join(root, "source/shared/docs")
	runtimeDocs := filepath.Join(root, filepath.FromSlash(provider.RuntimeRoot), "docs")
	for _, name := range []string{"skill_registry.md", "skill_routing.md"} {
		compareRegularFile(
			t,
			provider.ID+" routing projection "+name,
			filepath.Join(canonicalDocs, name),
			filepath.Join(runtimeDocs, name),
		)
	}
	compareFileTree(
		t,
		provider.ID+" routing family projections",
		filepath.Join(canonicalDocs, "routing"),
		filepath.Join(runtimeDocs, "routing"),
	)
}

func validateProviderRoutingOverlay(t *testing.T, root string, provider providerContract) {
	t.Helper()
	contextPath := filepath.Join(root, filepath.FromSlash(provider.SourceRoot), "context-routing.md")
	raw, err := os.ReadFile(contextPath)
	if errors.Is(err, os.ErrNotExist) {
		globalSource := filepath.Join(root, filepath.FromSlash(provider.SourceRoot), filepath.Base(provider.GlobalRule))
		globalRaw, globalErr := os.ReadFile(globalSource)
		if globalErr != nil {
			t.Errorf("provider %s routing overlay: %v", provider.ID, globalErr)
			return
		}
		if !strings.Contains(string(globalRaw), "docs/skill_routing.md") {
			t.Errorf("provider %s global rule does not point to the generated routing index", provider.ID)
		}
		return
	}
	if err != nil {
		t.Errorf("provider %s routing overlay: %v", provider.ID, err)
		return
	}
	text := string(raw)
	if !strings.Contains(text, "docs/skill_routing.md") || !strings.Contains(text, "Resource Closure") {
		t.Errorf("provider %s routing overlay does not preserve generated lookup and late-binding boundaries", provider.ID)
	}
	for _, prohibited := range []string{
		"## Route Matrix", "## Design Cluster Routing", "## Work Horizon Decision Table",
		"## Routing Card Audit Shape", "## Group Alias Routing", "| Request type | Primary skill |",
	} {
		if strings.Contains(text, prohibited) {
			t.Errorf("provider %s routing overlay retains generated semantic surface %q", provider.ID, prohibited)
		}
	}
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

func validateSkillResources(
	t *testing.T,
	repositoryRoot, providerID, skillRoot string,
	skillIDs []string,
	declarations map[string]skillDeclaration,
) {
	t.Helper()
	claimedTargets := map[string]resourceClaim{}
	expectedPluginFiles := map[string]bool{}
	for _, skillID := range skillIDs {
		declaration, exists := declarations[skillID]
		if !exists {
			continue
		}
		skillDir := filepath.Join(skillRoot, skillID)
		raw, err := os.ReadFile(filepath.Join(skillDir, "SKILL.md"))
		if err != nil {
			t.Errorf("%s SKILL.md: %v", filepath.ToSlash(skillDir), err)
			continue
		}
		text := string(raw)
		if strings.Contains(text, "### Resource Closure") {
			t.Errorf("%s generated skill exposes build-only Resource Closure", filepath.ToSlash(skillDir))
		}
		expectedCard := declaration.RoutingCard
		if providerID != "codex" {
			expectedCard = strings.NewReplacer(
				".codex/docs/", ".claude/docs/",
				".codex/schemas/", ".claude/schemas/",
				".codex/skills/.system", ".claude/skills/.system",
			).Replace(expectedCard)
		}
		if strings.Count(text, expectedCard) != 1 {
			t.Errorf("%s does not preserve its canonical Routing Card projection", filepath.ToSlash(skillDir))
		}
		walkErr := filepath.WalkDir(skillDir, func(path string, entry os.DirEntry, walkErr error) error {
			if walkErr != nil {
				return walkErr
			}
			if entry.IsDir() || filepath.Ext(path) != ".md" {
				return nil
			}
			markdown, readErr := os.ReadFile(path)
			if readErr != nil {
				return readErr
			}
			for _, match := range localResourcePattern.FindAllStringSubmatch(string(markdown), -1) {
				reference := strings.SplitN(match[1], "#", 2)[0]
				if filepath.IsAbs(reference) || containsParent(reference) {
					t.Errorf("%s has non-local resource reference %q", filepath.ToSlash(path), match[1])
					continue
				}
				if _, statErr := os.Stat(filepath.Join(skillDir, filepath.FromSlash(reference))); statErr != nil {
					t.Errorf("%s references missing local resource %s", filepath.ToSlash(path), reference)
				}
			}
			return nil
		})
		if walkErr != nil {
			t.Errorf("%s Markdown resource scan: %v", filepath.ToSlash(skillDir), walkErr)
		}

		expectedSkillFiles := canonicalLocalResourceFiles(t, filepath.Join(repositoryRoot, "source/skills", skillID))
		for _, resource := range declaration.Resources {
			target, packageRelative := closurePackageTarget(skillRoot, skillID, resource.Target)
			claimPackageTarget(t, claimedTargets, packageRelative, skillID, resource)
			canonical := filepath.Join(repositoryRoot, "source", filepath.FromSlash(resource.Source))
			switch resource.Projection {
			case "verbatim":
				compareRegularFile(t, providerID+" "+skillID+" resource "+resource.Target, canonical, target)
			case "tree":
				compareFileTree(t, providerID+" "+skillID+" resource "+resource.Target, canonical, target)
			case "execution-item-view":
				validateExecutionItemView(t, target, declaration.SourceText)
			}
			if strings.HasPrefix(resource.Target, "@plugin/") {
				for relative := range projectedFiles(t, canonical, resource.Target, resource.Projection) {
					expectedPluginFiles[relative] = true
				}
				continue
			}
			for relative := range projectedFiles(t, canonical, resource.Target, resource.Projection) {
				expectedSkillFiles[relative] = true
			}
		}
		actualSkillFiles := packagedLocalResourceFiles(t, skillDir)
		compareSets(t, providerID+" "+skillID+" declared resource inventory", expectedSkillFiles, actualSkillFiles)
	}
	actualPluginFiles := map[string]bool{}
	sharedRoot := filepath.Join(filepath.Dir(skillRoot), "shared")
	if _, err := os.Stat(sharedRoot); err == nil {
		for relative := range walkRegularFiles(t, sharedRoot) {
			actualPluginFiles[pathpkg.Join("shared", relative)] = true
		}
	} else if !errors.Is(err, os.ErrNotExist) {
		t.Errorf("%s plugin shared resources: %v", providerID, err)
	}
	compareSets(t, providerID+" plugin shared resource inventory", expectedPluginFiles, actualPluginFiles)
}

func closurePackageTarget(skillRoot, skillID, target string) (string, string) {
	if strings.HasPrefix(target, "@plugin/") {
		relative := strings.TrimPrefix(target, "@plugin/")
		return filepath.Join(filepath.Dir(skillRoot), filepath.FromSlash(relative)), relative
	}
	relative := pathpkg.Join("skills", skillID, target)
	return filepath.Join(skillRoot, skillID, filepath.FromSlash(target)), relative
}

func claimPackageTarget(
	t *testing.T,
	claimed map[string]resourceClaim,
	target, skillID string,
	resource skillResource,
) {
	t.Helper()
	normalized := strings.ToLower(target)
	for existing, previous := range claimed {
		if normalized == existing {
			if strings.HasPrefix(resource.Target, "@plugin/") && target == previous.Target && resource.Source == previous.Source && resource.Projection == previous.Projection {
				return
			}
			t.Errorf("package resource target %s conflicts between %s and %s", target, previous.Skill, skillID)
			return
		}
		if strings.HasPrefix(normalized, existing+"/") || strings.HasPrefix(existing, normalized+"/") {
			t.Errorf("package resource targets overlap: %s (%s) and %s (%s)", target, skillID, existing, previous.Skill)
			return
		}
	}
	claimed[normalized] = resourceClaim{Skill: skillID, Source: resource.Source, Projection: resource.Projection, Target: target}
}

func canonicalLocalResourceFiles(t *testing.T, skillDir string) map[string]bool {
	t.Helper()
	result := map[string]bool{}
	for _, rootName := range []string{"references", "assets", "scripts"} {
		root := filepath.Join(skillDir, rootName)
		if _, err := os.Stat(root); errors.Is(err, os.ErrNotExist) {
			continue
		} else if err != nil {
			t.Errorf("canonical local resource root %s: %v", filepath.ToSlash(root), err)
			continue
		}
		for relative := range walkRegularFiles(t, root) {
			result[pathpkg.Join(rootName, relative)] = true
		}
	}
	return result
}

func packagedLocalResourceFiles(t *testing.T, skillDir string) map[string]bool {
	return canonicalLocalResourceFiles(t, skillDir)
}

func projectedFiles(t *testing.T, canonical, target, projection string) map[string]bool {
	t.Helper()
	base := strings.TrimPrefix(target, "@plugin/")
	result := map[string]bool{}
	if projection != "tree" {
		result[base] = true
		return result
	}
	for relative := range walkRegularFiles(t, canonical) {
		result[pathpkg.Join(base, relative)] = true
	}
	return result
}

func walkRegularFiles(t *testing.T, root string) map[string]bool {
	t.Helper()
	result := map[string]bool{}
	err := filepath.WalkDir(root, func(current string, entry os.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if current == root {
			return nil
		}
		if entry.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("symlink is not a packaged resource: %s", filepath.ToSlash(current))
		}
		if entry.IsDir() {
			return nil
		}
		if !entry.Type().IsRegular() {
			return fmt.Errorf("non-regular packaged resource: %s", filepath.ToSlash(current))
		}
		relative, err := filepath.Rel(root, current)
		if err != nil {
			return err
		}
		result[filepath.ToSlash(relative)] = true
		return nil
	})
	if err != nil {
		t.Errorf("resource tree %s: %v", filepath.ToSlash(root), err)
	}
	return result
}

func compareRegularFile(t *testing.T, label, expectedPath, actualPath string) {
	t.Helper()
	expected, expectedErr := os.ReadFile(expectedPath)
	actual, actualErr := os.ReadFile(actualPath)
	if expectedErr != nil || actualErr != nil {
		t.Errorf("%s read errors: expected=%v actual=%v", label, expectedErr, actualErr)
		return
	}
	if !bytes.Equal(expected, actual) {
		t.Errorf("%s differs: %s != %s", label, filepath.ToSlash(expectedPath), filepath.ToSlash(actualPath))
	}
}

func compareFileTree(t *testing.T, label, expectedRoot, actualRoot string) {
	t.Helper()
	expectedFiles := walkRegularFiles(t, expectedRoot)
	actualFiles := walkRegularFiles(t, actualRoot)
	compareSets(t, label+" files", expectedFiles, actualFiles)
	for relative := range expectedFiles {
		if !actualFiles[relative] {
			continue
		}
		compareRegularFile(
			t,
			label+" "+relative,
			filepath.Join(expectedRoot, filepath.FromSlash(relative)),
			filepath.Join(actualRoot, filepath.FromSlash(relative)),
		)
	}
}

func validateExecutionItemView(t *testing.T, path, sourceSkill string) {
	t.Helper()
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Errorf("execution-item-view %s: %v", filepath.ToSlash(path), err)
		return
	}
	text := string(raw)
	if !strings.HasPrefix(text, "# Core Execution Item Role View\n") ||
		!strings.Contains(text, "Generated from the canonical Core execution-item contract") {
		t.Errorf("execution-item-view %s lacks canonical projection markers", filepath.ToSlash(path))
	}
	for _, match := range regexp.MustCompile(`references/core-execution-items-v1/cards/([A-Za-z0-9][A-Za-z0-9_.-]*)\.md`).FindAllStringSubmatch(sourceSkill, -1) {
		if !strings.Contains(text, "### `"+match[1]+"`") {
			t.Errorf("execution-item-view %s omits selected kind %s", filepath.ToSlash(path), match[1])
		}
	}
}

func validateResourceClosureFalsifiers(t *testing.T) {
	t.Helper()
	valid := skillResource{
		Source: "shared/docs/example.md", Target: "references/example.md",
		Projection: "verbatim", Load: "read_if_needed", Condition: "matching condition",
	}
	cases := map[string]skillResource{
		"absolute source":    {Source: "/shared/docs/example.md", Target: valid.Target, Projection: valid.Projection, Load: valid.Load, Condition: valid.Condition},
		"parent target":      {Source: valid.Source, Target: "references/../example.md", Projection: valid.Projection, Load: valid.Load, Condition: valid.Condition},
		"empty segment":      {Source: valid.Source, Target: "references//example.md", Projection: valid.Projection, Load: valid.Load, Condition: valid.Condition},
		"backslash":          {Source: valid.Source, Target: `references\example.md`, Projection: valid.Projection, Load: valid.Load, Condition: valid.Condition},
		"drive target":       {Source: valid.Source, Target: "C:/example.md", Projection: valid.Projection, Load: valid.Load, Condition: valid.Condition},
		"outside namespace":  {Source: valid.Source, Target: "docs/example.md", Projection: valid.Projection, Load: valid.Load, Condition: valid.Condition},
		"unknown projection": {Source: valid.Source, Target: valid.Target, Projection: "copy-ish", Load: valid.Load, Condition: valid.Condition},
		"unknown load":       {Source: valid.Source, Target: valid.Target, Projection: valid.Projection, Load: "eager", Condition: valid.Condition},
		"empty condition":    {Source: valid.Source, Target: valid.Target, Projection: valid.Projection, Load: valid.Load, Condition: " "},
	}
	for name, resource := range cases {
		if err := validateResourceShape(resource); err == nil {
			t.Errorf("resource closure falsifier %s was accepted: %#v", name, resource)
		}
	}
	if _, err := decodeResourceClosure([]byte(`[{"source":"shared/docs/a.md","source":"shared/docs/b.md","target":"references/a.md","projection":"verbatim","load":"must_read","condition":"selected"}]`)); err == nil {
		t.Error("resource closure accepted a duplicate JSON key")
	}
	if _, err := decodeResourceClosure([]byte(`[] {}`)); err == nil {
		t.Error("resource closure accepted trailing JSON")
	}
	if err := validateTargetSet([]skillResource{
		valid,
		{Source: "shared/docs/child.md", Target: "references/example.md/child", Projection: "verbatim", Load: "must_read", Condition: "selected"},
	}); err == nil {
		t.Error("resource closure accepted ancestor target overlap")
	}
	if err := validateTargetSet([]skillResource{
		valid,
		{Source: "shared/docs/other.md", Target: "REFERENCES/EXAMPLE.MD", Projection: "verbatim", Load: "must_read", Condition: "selected"},
	}); err == nil {
		t.Error("resource closure accepted case-folded target collision")
	}
	for _, familyID := range []string{"../analysis", "analysis/child", `analysis\child`, "C:analysis"} {
		if routingFamilyIDPattern.MatchString(familyID) {
			t.Errorf("routing family id falsifier %q was accepted", familyID)
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

func mapKeys[V any](values map[string]V) []string {
	result := make([]string, 0, len(values))
	for key := range values {
		result = append(result, key)
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
