package corecards

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
)

const (
	contractID   = "core-execution-items-v1"
	handoffSkill = "plan-execution-handoff"
)

var cardReferencePattern = regexp.MustCompile(
	`references/core-execution-items-v1/cards/[A-Za-z0-9][A-Za-z0-9_.-]*\.md`,
)

type cardMetadata struct {
	ContractID        string   `json:"contract_id"`
	CardType          string   `json:"card_type"`
	HandoffSection    string   `json:"handoff_section"`
	HandoffColumns    []string `json:"handoff_columns"`
	AllowedProducers  []string `json:"allowed_producers"`
	RequiredConsumers []string `json:"required_consumers"`
	Recorders         []string `json:"recorders"`
}

type cardDefinition struct {
	metadata cardMetadata
	path     string
	body     string
}

type schemaContract struct {
	Properties struct {
		ContractID struct {
			Const string `json:"const"`
		} `json:"contract_id"`
		Kind struct {
			Enum []string `json:"enum"`
		} `json:"kind"`
	} `json:"properties"`
}

type skillBindings struct {
	produces map[string]bool
	consumes map[string]bool
	records  map[string]bool
}

func TestCoreCardsMatchPlanExecutionHandoff(t *testing.T) {
	root := repositoryRoot(t)
	cards := loadCards(t, root)
	schema := loadSchema(t, root)
	handoffSections := loadHandoffSections(t, root)
	skills, bindings := loadSkillBindings(t, root, cards)

	if schema.Properties.ContractID.Const != contractID {
		t.Errorf("schema contract_id %q != %q", schema.Properties.ContractID.Const, contractID)
	}
	compareSets(t, "schema card kinds", stringSet(schema.Properties.Kind.Enum), cardTypeSet(cards))

	actualProducers := map[string]map[string]bool{}
	actualConsumers := map[string]map[string]bool{}
	actualRecorders := map[string]map[string]bool{}
	for skillID, binding := range bindings {
		addBindings(actualProducers, skillID, binding.produces)
		addBindings(actualConsumers, skillID, binding.consumes)
		addBindings(actualRecorders, skillID, binding.records)
	}

	for cardType, card := range cards {
		meta := card.metadata
		if meta.ContractID != contractID {
			t.Errorf("%s: contract_id %q != %q", card.path, meta.ContractID, contractID)
		}
		if meta.CardType != cardType {
			t.Errorf("%s: card_type %q != filename %q", card.path, meta.CardType, cardType)
		}
		validateUniqueSkillList(t, card.path+" allowed_producers", meta.AllowedProducers, skills)
		validateUniqueSkillList(t, card.path+" required_consumers", meta.RequiredConsumers, skills)
		validateUniqueSkillList(t, card.path+" recorders", meta.Recorders, skills)

		compareSets(
			t,
			cardType+" producers",
			stringSet(meta.AllowedProducers),
			actualProducers[cardType],
		)
		requireSubset(
			t,
			cardType+" consumers",
			stringSet(meta.RequiredConsumers),
			actualConsumers[cardType],
		)
		compareSets(
			t,
			cardType+" recorders",
			stringSet(meta.Recorders),
			actualRecorders[cardType],
		)
		if !stringSet(meta.Recorders)[handoffSkill] {
			t.Errorf("%s: %s must record every Core execution card", card.path, handoffSkill)
		}

		header, exists := handoffSections[meta.HandoffSection]
		if !exists {
			t.Errorf("%s: Handoff section %q does not exist", card.path, meta.HandoffSection)
			continue
		}
		if !equalStrings(meta.HandoffColumns, header) {
			t.Errorf(
				"%s: declared Handoff columns %v != actual %q header %v",
				card.path,
				meta.HandoffColumns,
				meta.HandoffSection,
				header,
			)
		}
		rows := markdownRows(card.body)
		if len(rows) != 1 {
			t.Errorf("%s: expected exactly one Handoff row template, found %d", card.path, len(rows))
			continue
		}
		if len(rows[0]) != len(header) {
			t.Errorf(
				"%s: %q row has %d columns; Handoff header has %d (%v)",
				card.path,
				meta.HandoffSection,
				len(rows[0]),
				len(header),
				header,
			)
		}
	}

	rejectLocalCardCopies(t, root)
}

func repositoryRoot(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("cannot resolve Core Card test path")
	}
	root, err := filepath.Abs(filepath.Join(filepath.Dir(file), "../../../../.."))
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func loadCards(t *testing.T, root string) map[string]cardDefinition {
	t.Helper()
	directory := filepath.Join(root, "source/shared/contracts/core-execution-items-v1/cards")
	entries, err := os.ReadDir(directory)
	if err != nil {
		t.Fatalf("Core Card directory: %v", err)
	}
	cards := map[string]cardDefinition{}
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".md" {
			continue
		}
		path := filepath.Join(directory, entry.Name())
		metadata, body, parseErr := parseCard(path)
		if parseErr != nil {
			t.Errorf("%s: %v", filepath.ToSlash(path), parseErr)
			continue
		}
		cardType := strings.TrimSuffix(entry.Name(), ".md")
		if previous, exists := cards[metadata.CardType]; exists {
			t.Errorf("duplicate card_type %q: %s and %s", metadata.CardType, previous.path, path)
		}
		cards[cardType] = cardDefinition{
			metadata: metadata,
			path:     filepath.ToSlash(path),
			body:     body,
		}
	}
	if len(cards) == 0 {
		t.Fatal("no Core Card Markdown files found")
	}
	return cards
}

func parseCard(path string) (cardMetadata, string, error) {
	var metadata cardMetadata
	raw, err := os.ReadFile(path)
	if err != nil {
		return metadata, "", err
	}
	text := string(raw)
	if !strings.HasPrefix(text, "---\n") {
		return metadata, "", fmt.Errorf("missing JSON frontmatter")
	}
	remainder := strings.TrimPrefix(text, "---\n")
	end := strings.Index(remainder, "\n---\n")
	if end < 0 {
		return metadata, "", fmt.Errorf("unclosed JSON frontmatter")
	}
	if err := json.Unmarshal([]byte(remainder[:end]), &metadata); err != nil {
		return metadata, "", fmt.Errorf("invalid JSON frontmatter: %w", err)
	}
	if metadata.CardType == "" || metadata.HandoffSection == "" || len(metadata.HandoffColumns) == 0 {
		return metadata, "", fmt.Errorf("card_type, handoff_section, and handoff_columns are required")
	}
	return metadata, strings.TrimSpace(remainder[end+len("\n---\n"):]), nil
}

func loadSchema(t *testing.T, root string) schemaContract {
	t.Helper()
	path := filepath.Join(root, "source/shared/schemas/execution/execution-item.schema.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("execution-item schema: %v", err)
	}
	var schema schemaContract
	if err := json.Unmarshal(raw, &schema); err != nil {
		t.Fatalf("execution-item schema JSON: %v", err)
	}
	return schema
}

func loadHandoffSections(t *testing.T, root string) map[string][]string {
	t.Helper()
	path := filepath.Join(root, "source/skills/plan-execution-handoff/assets/handoff.md.tpl")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("Handoff template: %v", err)
	}
	text := string(raw)
	sections := map[string][]string{}
	for _, heading := range []string{"Execution Items", "Deferred Items", "Known Bugs"} {
		rows := markdownRows(markdownSection(text, heading))
		if len(rows) == 0 {
			t.Errorf("Handoff template: section %q has no table header", heading)
			continue
		}
		sections[heading] = rows[0]
	}
	return sections
}

func loadSkillBindings(
	t *testing.T,
	root string,
	cards map[string]cardDefinition,
) (map[string]bool, map[string]skillBindings) {
	t.Helper()
	skillRoot := filepath.Join(root, "source/skills")
	entries, err := os.ReadDir(skillRoot)
	if err != nil {
		t.Fatalf("skill directory: %v", err)
	}
	skills := map[string]bool{}
	bindings := map[string]skillBindings{}
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		path := filepath.Join(skillRoot, entry.Name(), "SKILL.md")
		raw, readErr := os.ReadFile(path)
		if readErr != nil {
			continue
		}
		skillID := entry.Name()
		skills[skillID] = true
		text := string(raw)
		section := markdownSection(text, "Core Cards")
		binding := skillBindings{
			produces: map[string]bool{},
			consumes: map[string]bool{},
			records:  map[string]bool{},
		}
		sectionRefs := map[string]bool{}
		for _, line := range strings.Split(section, "\n") {
			trimmed := strings.TrimSpace(line)
			if !strings.HasPrefix(trimmed, "-") || !strings.Contains(trimmed, ":") {
				continue
			}
			label := strings.ToLower(strings.TrimSpace(strings.SplitN(strings.TrimPrefix(trimmed, "-"), ":", 2)[0]))
			for _, ref := range cardReferencePattern.FindAllString(trimmed, -1) {
				sectionRefs[ref] = true
				cardType := strings.TrimSuffix(filepath.Base(ref), ".md")
				if _, exists := cards[cardType]; !exists {
					t.Errorf("%s: Core Cards references unknown card %s", filepath.ToSlash(path), ref)
					continue
				}
				if strings.Contains(label, "produces") {
					binding.produces[cardType] = true
				}
				if strings.Contains(label, "consumes") {
					binding.consumes[cardType] = true
				}
				if strings.Contains(label, "records") {
					binding.records[cardType] = true
				}
			}
		}
		for _, ref := range cardReferencePattern.FindAllString(text, -1) {
			if !sectionRefs[ref] {
				t.Errorf("%s: Core Card reference %s must be declared under ## Core Cards", filepath.ToSlash(path), ref)
			}
		}
		bindings[skillID] = binding
	}
	return skills, bindings
}

func addBindings(target map[string]map[string]bool, skillID string, cardTypes map[string]bool) {
	for cardType := range cardTypes {
		if target[cardType] == nil {
			target[cardType] = map[string]bool{}
		}
		target[cardType][skillID] = true
	}
}

func validateUniqueSkillList(t *testing.T, label string, values []string, skills map[string]bool) {
	t.Helper()
	seen := map[string]bool{}
	for _, value := range values {
		if seen[value] {
			t.Errorf("%s: duplicate skill %q", label, value)
		}
		seen[value] = true
		if !skills[value] {
			t.Errorf("%s: skill %q does not exist", label, value)
		}
	}
}

func rejectLocalCardCopies(t *testing.T, root string) {
	t.Helper()
	skillRoot := filepath.Join(root, "source/skills")
	err := filepath.WalkDir(skillRoot, func(path string, entry os.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".md" || entry.Name() == "SKILL.md" {
			return nil
		}
		raw, readErr := os.ReadFile(path)
		if readErr != nil {
			return readErr
		}
		text := string(raw)
		if strings.HasPrefix(text, "---\n{") && strings.Contains(markdownFrontmatter(text), `"card_type"`) {
			t.Errorf("skill-local Core Card copy is forbidden: %s", filepath.ToSlash(path))
		}
		return nil
	})
	if err != nil {
		t.Errorf("scan skill-local references: %v", err)
	}
}

func markdownFrontmatter(text string) string {
	if !strings.HasPrefix(text, "---\n") {
		return ""
	}
	remainder := strings.TrimPrefix(text, "---\n")
	end := strings.Index(remainder, "\n---\n")
	if end < 0 {
		return ""
	}
	return remainder[:end]
}

func markdownSection(text, heading string) string {
	marker := "## " + heading
	start := strings.Index(text, marker)
	if start < 0 {
		return ""
	}
	remainder := text[start+len(marker):]
	for index, line := range strings.SplitAfter(remainder, "\n") {
		if index == 0 {
			continue
		}
		if strings.HasPrefix(line, "## ") {
			return strings.TrimSpace(remainder[:strings.Index(remainder, line)])
		}
	}
	return strings.TrimSpace(remainder)
}

func markdownRows(text string) [][]string {
	var rows [][]string
	for _, line := range strings.Split(text, "\n") {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "|") && strings.HasSuffix(trimmed, "|") {
			rows = append(rows, splitMarkdownRow(trimmed))
		}
	}
	return rows
}

func splitMarkdownRow(line string) []string {
	body := strings.TrimSuffix(strings.TrimPrefix(strings.TrimSpace(line), "|"), "|")
	var cells []string
	var current strings.Builder
	for index := 0; index < len(body); index++ {
		if body[index] == '\\' && index+1 < len(body) && body[index+1] == '|' {
			current.WriteByte('|')
			index++
			continue
		}
		if body[index] == '|' {
			cells = append(cells, strings.TrimSpace(current.String()))
			current.Reset()
			continue
		}
		current.WriteByte(body[index])
	}
	cells = append(cells, strings.TrimSpace(current.String()))
	return cells
}

func cardTypeSet(cards map[string]cardDefinition) map[string]bool {
	result := map[string]bool{}
	for cardType := range cards {
		result[cardType] = true
	}
	return result
}

func stringSet(values []string) map[string]bool {
	result := map[string]bool{}
	for _, value := range values {
		result[value] = true
	}
	return result
}

func compareSets(t *testing.T, label string, expected, actual map[string]bool) {
	t.Helper()
	missing := difference(expected, actual)
	unexpected := difference(actual, expected)
	if len(missing) > 0 || len(unexpected) > 0 {
		t.Errorf("%s differ: missing=%v unexpected=%v", label, missing, unexpected)
	}
}

func requireSubset(t *testing.T, label string, required, actual map[string]bool) {
	t.Helper()
	if missing := difference(required, actual); len(missing) > 0 {
		t.Errorf("%s missing required bindings: %v", label, missing)
	}
}

func difference(left, right map[string]bool) []string {
	var values []string
	for value := range left {
		if !right[value] {
			values = append(values, value)
		}
	}
	sort.Strings(values)
	return values
}

func equalStrings(left, right []string) bool {
	if len(left) != len(right) {
		return false
	}
	for index := range left {
		if left[index] != right[index] {
			return false
		}
	}
	return true
}
