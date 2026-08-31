package workcontract

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

const schemaVersion = 1

const (
	VerificationAgent = "agent"
	VerificationUser  = "user"

	InteractionAllowed   = "allowed"
	InteractionForbidden = "forbidden"

	ExecutionAttended           = "attended"
	ExecutionUnattendedGoalLoop = "unattended_goal_loop"

	ActionCore               = "core"
	ActionRequiredPrereq     = "required_prerequisite"
	ActionAgentValidation    = "agent_validation"
	ActionTestAuthoring      = "test_authoring"
	ActionValidationArtifact = "validation_artifact"
	ActionMeta               = "meta"
)

var (
	testAuthoringPattern = regexp.MustCompile(`(?i)(?:^|[/_.-])(?:tests?|specs?|fixtures?|snapshots?)(?:[/_.-]|$)|(?:테스트|검증)[^.!?\n]{0,24}(?:작성|추가|생성)`)
	validationPattern    = regexp.MustCompile(`(?i)(?:\b(?:test|tests|testing|verify|verification|validate|validation|smoke|benchmark|trace|probe)\b|테스트|검증|검사|스모크|트레이스)`)
	executionPattern     = regexp.MustCompile(`(?i)(?:\b(?:run|execute|launch|invoke|start|rerun|re-run|pytest|ctest|jest)\b|실행|돌려|구동|재실행)`)
	artifactPattern      = regexp.MustCompile(`(?i)(?:\b(?:wrapper|harness|fixture|snapshot|probe|tracer?|testbed)\b|래퍼|하네스|픽스처|스냅샷|프로브|테스트베드)`)
	metaPattern          = regexp.MustCompile(`(?i)(?:\bgit\s+(?:add|commit)\b|\b(?:stage|staging|checkpoint)\b[^.!?\n]{0,24}\b(?:changes?|wip|status)\b|스테이징|커밋|wip\s*체크포인트)`)
	noInteractionPattern = regexp.MustCompile(`(?:추가\s*)?(?:승인\s*요청|질문)(?:은|을|도|이나|과|과의|에\s*대한)?\s*(?:하지\s*마|하지\s*말|하지\s*않|금지)|(?:승인|질문)[^.!?\n]{0,16}(?:기다리지\s*마|기다리지\s*말)`)
)

type Intent struct {
	Key    string `json:"key"`
	Class  string `json:"class"`
	Reason string `json:"reason"`
}

type State struct {
	SchemaVersion          int      `json:"schema_version"`
	Revision               int      `json:"revision"`
	SourceDigest           string   `json:"source_digest"`
	VerificationOwner      string   `json:"verification_owner"`
	InteractionMode        string   `json:"interaction_mode"`
	ExecutionMode          string   `json:"execution_mode"`
	ExcludedActionClasses  []string `json:"excluded_action_classes"`
	ActiveIntent           *Intent  `json:"active_intent,omitempty"`
	DeferredIntents        []Intent `json:"deferred_intents"`
	InputContinuationCount int      `json:"input_continuation_count"`
	UpdatedAt              string   `json:"updated_at"`
}

type Decision struct {
	Deny         bool
	Rewrite      bool
	Intent       Intent
	Reason       string
	UpdatedInput map[string]any
}

type promptSignals struct {
	seen              bool
	reset             bool
	verificationOwner string
	interactionMode   string
	executionMode     string
	addExclusions     []string
	removeExclusions  []string
}

func defaultState() State {
	return State{
		SchemaVersion:         schemaVersion,
		VerificationOwner:     VerificationAgent,
		InteractionMode:       InteractionAllowed,
		ExecutionMode:         ExecutionAttended,
		DeferredIntents:       []Intent{},
		ExcludedActionClasses: []string{},
	}
}

// Capture updates the privacy-safe runtime projection of an explicit user work
// contract. It stores normalized policy fields and a prompt digest, never raw
// prompt text.
func Capture(sessionID, prompt string) (State, bool, error) {
	signals := compilePrompt(prompt)
	current, err := Load(sessionID)
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		return defaultState(), false, err
	}
	if signals.reset {
		if err := Clear(sessionID); err != nil {
			return defaultState(), false, err
		}
		return defaultState(), false, nil
	}
	if !signals.seen {
		if err != nil {
			return defaultState(), false, nil
		}
		return current, true, nil
	}
	if err != nil {
		current = defaultState()
	}
	if signals.verificationOwner != "" {
		current.VerificationOwner = signals.verificationOwner
	}
	if signals.interactionMode != "" {
		current.InteractionMode = signals.interactionMode
	}
	if signals.executionMode != "" {
		current.ExecutionMode = signals.executionMode
	}
	excluded := make(map[string]bool, len(current.ExcludedActionClasses))
	for _, class := range current.ExcludedActionClasses {
		excluded[class] = true
	}
	for _, class := range signals.addExclusions {
		excluded[class] = true
	}
	for _, class := range signals.removeExclusions {
		delete(excluded, class)
	}
	current.ExcludedActionClasses = sortedKeys(excluded)
	if signals.interactionMode == InteractionAllowed || signals.verificationOwner == VerificationAgent {
		current.DeferredIntents = nil
		current.InputContinuationCount = 0
	}
	current.SchemaVersion = schemaVersion
	current.Revision++
	current.SourceDigest = digest(prompt)
	current.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
	if err := writeState(sessionID, current); err != nil {
		return defaultState(), false, err
	}
	return current, true, nil
}

func Load(sessionID string) (State, error) {
	path := statePath(sessionID)
	if path == "" {
		return defaultState(), os.ErrNotExist
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		return defaultState(), err
	}
	var state State
	if err := json.Unmarshal(raw, &state); err != nil {
		return defaultState(), err
	}
	if state.SchemaVersion != schemaVersion {
		return defaultState(), errors.New("unsupported work-contract state version")
	}
	if state.VerificationOwner == "" {
		state.VerificationOwner = VerificationAgent
	}
	if state.InteractionMode == "" {
		state.InteractionMode = InteractionAllowed
	}
	if state.ExecutionMode == "" {
		state.ExecutionMode = ExecutionAttended
	}
	if state.ExcludedActionClasses == nil {
		state.ExcludedActionClasses = []string{}
	}
	if state.DeferredIntents == nil {
		state.DeferredIntents = []Intent{}
	}
	return state, nil
}

func Clear(sessionID string) error {
	path := statePath(sessionID)
	if path == "" {
		return nil
	}
	err := os.Remove(path)
	if errors.Is(err, os.ErrNotExist) {
		return nil
	}
	return err
}

func Context(state State) string {
	if state.SchemaVersion != schemaVersion {
		return ""
	}
	lines := []string{
		"Active user work contract (runtime projection):",
		"- User-stated scope and exclusions outrank optional workflow, validation, and quality-improvement steps except safety or platform-enforced constraints.",
		"- Verification owner: " + state.VerificationOwner + ".",
		"- Additional interaction: " + state.InteractionMode + ".",
		"- Execution mode: " + state.ExecutionMode + ".",
	}
	if state.VerificationOwner == VerificationUser {
		lines = append(lines, "- Missing user-only evidence is a normal user-verification-needed handoff; do not create substitute tests or validation artifacts.")
	}
	lines = append(lines, "- The host-selected reviewer owns approval decisions; when Auto-review is effective, it replaces user-click waits. This projection only excludes or defers explicitly out-of-contract actions.")
	if state.ExecutionMode == ExecutionUnattendedGoalLoop && state.InteractionMode == InteractionForbidden {
		lines = append(lines, "- Do not ask a blocking question. Defer only the unavailable action and continue other in-contract work.")
	}
	if len(state.ExcludedActionClasses) > 0 {
		lines = append(lines, "- Excluded action classes: "+strings.Join(state.ExcludedActionClasses, ", ")+".")
		lines = append(lines, "- Omit excluded work from plans and tool calls instead of relying on a hook denial.")
	}
	if len(state.DeferredIntents) > 0 {
		classes := map[string]bool{}
		for _, intent := range state.DeferredIntents {
			if intent.Class != "" {
				classes[intent.Class] = true
			}
		}
		lines = append(
			lines,
			"- Deferred semantic intents remain non-runnable ("+
				strings.Join(sortedKeys(classes), ", ")+").",
		)
	}
	lines = append(lines,
		"- Do not retry a deferred purpose through another tool or command form.",
		"- Use blocked only when no required runnable work remains; otherwise reevaluate and continue.",
	)
	return strings.Join(lines, "\n")
}

func Preflight(sessionID, toolName string, raw json.RawMessage) (Decision, error) {
	state, err := Load(sessionID)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return Decision{}, nil
		}
		return Decision{}, err
	}
	if strings.EqualFold(strings.TrimSpace(toolName), "update_plan") {
		return preflightPlan(sessionID, &state, raw)
	}
	intent := classifyIntent(toolName, raw, state.ActiveIntent)
	if isExcluded(state, intent.Class) || hasDeferred(state, intent.Key) {
		if hasDeferred(state, intent.Key) {
			intent.Reason = "same-purpose action was already deferred"
		} else {
			intent.Reason = "action class is excluded by the active user work contract"
		}
		if err := deferIntent(sessionID, &state, intent); err != nil {
			return Decision{}, err
		}
		return Decision{Deny: true, Intent: intent, Reason: denialReason(intent)}, nil
	}
	return Decision{}, nil
}

func ContinueWithoutInput(sessionID string) (bool, error) {
	state, err := Load(sessionID)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return false, nil
		}
		return false, err
	}
	unattended := state.ExecutionMode == ExecutionUnattendedGoalLoop
	if !unattended || state.InteractionMode != InteractionForbidden {
		return false, nil
	}
	inputIntent := Intent{
		Key:    digest("human-input"),
		Class:  ActionRequiredPrereq,
		Reason: "blocking question is forbidden by the no-additional-interaction contract",
	}
	if !hasDeferred(state, inputIntent.Key) {
		state.DeferredIntents = append(state.DeferredIntents, inputIntent)
	}
	state.InputContinuationCount++
	state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
	return true, writeState(sessionID, state)
}

func compilePrompt(prompt string) promptSignals {
	text := normalize(prompt)
	var signals promptSignals
	if text == "" {
		return signals
	}
	if containsAny(text,
		"작업계약을 초기화", "작업 계약을 초기화", "제한을 초기화", "일반 작업으로 전환",
		"reset the work contract", "clear the work contract", "clear these restrictions",
	) {
		signals.seen = true
		signals.reset = true
		return signals
	}
	if strings.HasPrefix(text, "/goal") || containsAny(text,
		"무인 장시간 goal", "무인 장시간 골", "무인 장시간 loop", "무인 장시간 루프",
		"무인 장기 goal", "무인 장기 골", "무인 장기 loop", "무인 장기 루프",
		"장기간 작업하는 goal", "장기간 작업하는 골", "장기간 작업하는 loop", "장기간 작업하는 루프",
		"장시간 goal", "장시간 골", "장시간 loop", "장시간 루프", "장기 goal", "장기 골", "장기 loop", "장기 루프",
		"unattended goal", "unattended loop", "long-running goal", "long running goal",
		"long-running loop", "long running loop",
	) {
		signals.seen = true
		signals.executionMode = ExecutionUnattendedGoalLoop
	}
	if containsAny(text,
		"대화형 작업", "일반 대화형", "attended task", "interactive task",
	) {
		signals.seen = true
		signals.executionMode = ExecutionAttended
	}

	if containsAny(text,
		"검증은 내가", "테스트는 내가", "확인은 내가", "내가 검증", "내가 테스트",
		"사용자가 검증", "사용자가 테스트", "검증은 사용자", "테스트는 사용자",
		"leave verification to me", "leave testing to me", "i will verify", "i'll verify",
		"i will test", "i'll test", "user will verify", "user will test",
	) {
		signals.seen = true
		signals.verificationOwner = VerificationUser
		signals.addExclusions = append(signals.addExclusions,
			ActionAgentValidation, ActionTestAuthoring, ActionValidationArtifact,
		)
	}
	if containsAny(text,
		"에이전트가 검증", "에이전트가 테스트", "직접 검증해", "테스트도 실행해",
		"검증을 허용", "테스트를 허용", "you verify", "you test", "run the tests",
		"agent verification is allowed", "testing is allowed",
	) {
		signals.seen = true
		signals.verificationOwner = VerificationAgent
		signals.removeExclusions = append(signals.removeExclusions,
			ActionAgentValidation, ActionTestAuthoring, ActionValidationArtifact,
		)
	}

	if noInteractionPattern.MatchString(text) || containsAny(text,
		"승인 요청하지", "승인을 요청하지", "승인받지 말", "승인을 받지 말",
		"추가 승인 없이", "승인 없이 진행", "질문하지 말", "추가 질문하지",
		"승인이나 질문을 요청하지", "승인 또는 질문을 요청하지", "승인과 질문을 요청하지",
		"추가 상호작용 없이", "상호작용을 금지", "응답을 기다리지",
		"do not ask for approval", "don't ask for approval", "no approval requests",
		"without asking for approval", "do not ask questions", "don't ask questions",
		"no additional interaction", "do not wait for me",
	) {
		signals.seen = true
		signals.interactionMode = InteractionForbidden
	}
	if containsAny(text,
		"승인 요청해도", "승인을 요청해도", "추가 질문해도", "질문해도 돼",
		"승인이나 질문을 요청해도", "승인 또는 질문을 요청해도", "승인과 질문을 요청해도",
		"상호작용을 허용", "승인 요청을 허용", "you may ask for approval",
		"approval requests are allowed", "you may ask questions", "interaction is allowed",
	) {
		signals.seen = true
		signals.interactionMode = InteractionAllowed
	}

	if containsAny(text,
		"핵심 작업만", "핵심 구현만", "구현에만 집중", "제품 코드만", "프로덕션 코드만",
		"core work only", "implementation only", "production code only", "focus only on implementation",
	) {
		signals.seen = true
		signals.addExclusions = append(signals.addExclusions,
			ActionAgentValidation, ActionTestAuthoring, ActionValidationArtifact, ActionMeta,
		)
	}
	if containsAny(text,
		"테스트를 작성하지", "테스트 작성하지", "테스트를 추가하지", "새 테스트 금지",
		"검증 도구를 만들지", "검증용 도구를 만들지", "검증용 산출물 금지",
		"do not write tests", "do not add tests", "do not create tests",
		"do not create validation tools", "no validation artifacts",
	) {
		signals.seen = true
		signals.addExclusions = append(signals.addExclusions, ActionTestAuthoring, ActionValidationArtifact)
	}
	return signals
}

func preflightPlan(sessionID string, state *State, raw json.RawMessage) (Decision, error) {
	var input map[string]any
	if json.Unmarshal(raw, &input) != nil {
		return Decision{}, nil
	}
	items, ok := input["plan"].([]any)
	if !ok || len(items) == 0 {
		return Decision{}, nil
	}

	kept := make([]any, 0, len(items))
	filtered := make([]Intent, 0)
	var active *Intent
	for _, rawItem := range items {
		item, itemOK := rawItem.(map[string]any)
		step, stepOK := item["step"].(string)
		if !itemOK || !stepOK {
			kept = append(kept, rawItem)
			continue
		}
		intent := intentFromText("plan", step, nil)
		if isExcluded(*state, intent.Class) || hasDeferred(*state, intent.Key) {
			if hasDeferred(*state, intent.Key) {
				intent.Reason = "same-purpose plan item was already deferred"
			} else {
				intent.Reason = "plan item conflicts with the active user work contract"
			}
			filtered = append(filtered, intent)
			continue
		}
		kept = append(kept, rawItem)
		if status, _ := item["status"].(string); status == "in_progress" {
			copy := intent
			active = &copy
		}
	}

	// Every valid plan update replaces the previous active intent. Without this,
	// a completed or removed validation item can leak into later core tool calls.
	state.ActiveIntent = active
	if len(filtered) == 0 {
		state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
		return Decision{}, writeState(sessionID, *state)
	}
	for _, intent := range filtered {
		if !hasDeferred(*state, intent.Key) {
			state.DeferredIntents = append(state.DeferredIntents, intent)
		}
	}
	state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
	if err := writeState(sessionID, *state); err != nil {
		return Decision{}, err
	}

	if len(kept) == 0 {
		intent := filtered[0]
		intent.Reason = "every plan item conflicts with or repeats a deferral from the active user work contract"
		return Decision{Deny: true, Intent: intent, Reason: denialReason(intent)}, nil
	}
	input["plan"] = kept
	return Decision{
		Rewrite:      true,
		Reason:       "Removed contract-excluded or already-deferred plan items without blocking the remaining in-contract plan.",
		UpdatedInput: input,
	}, nil
}

func classifyIntent(toolName string, raw json.RawMessage, active *Intent) Intent {
	text := textualInput(raw)
	intent := intentFromText(toolName, text, active)
	if intent.Class == ActionCore && active != nil && active.Class != "" {
		intent.Class = active.Class
		intent.Key = active.Key
	}
	return intent
}

func intentFromText(toolName, text string, active *Intent) Intent {
	normalized := normalize(toolName + " " + text)
	class := ActionCore
	lowerTool := strings.ToLower(strings.TrimSpace(toolName))
	if metaPattern.MatchString(normalized) {
		class = ActionMeta
	} else if (lowerTool == "apply_patch" || strings.Contains(lowerTool, "write") || strings.Contains(lowerTool, "edit")) &&
		testAuthoringPattern.MatchString(normalized) {
		class = ActionTestAuthoring
	} else if validationPattern.MatchString(normalized) && artifactPattern.MatchString(normalized) {
		class = ActionValidationArtifact
	} else if validationPattern.MatchString(normalized) &&
		(executionPattern.MatchString(normalized) || strings.Contains(lowerTool, "computer") ||
			strings.Contains(lowerTool, "browser") || strings.Contains(lowerTool, "chrome")) {
		class = ActionAgentValidation
	} else if active != nil && active.Class != "" {
		class = active.Class
	}
	keyBasis := intentFamily(class)
	if class == ActionCore || class == ActionRequiredPrereq {
		keyBasis = class + ":" + semanticPurpose(normalized)
	}
	return Intent{Key: digest(keyBasis), Class: class}
}

func intentFamily(class string) string {
	switch class {
	case ActionAgentValidation, ActionTestAuthoring, ActionValidationArtifact:
		return "validation"
	default:
		return class
	}
}

func textualInput(raw json.RawMessage) string {
	if len(raw) == 0 {
		return ""
	}
	var value any
	if json.Unmarshal(raw, &value) != nil {
		return string(raw)
	}
	var parts []string
	collectStrings(value, &parts)
	return strings.Join(parts, " ")
}

func collectStrings(value any, parts *[]string) {
	switch typed := value.(type) {
	case string:
		*parts = append(*parts, typed)
	case []any:
		for _, item := range typed {
			collectStrings(item, parts)
		}
	case map[string]any:
		keys := make([]string, 0, len(typed))
		for key := range typed {
			keys = append(keys, key)
		}
		sort.Strings(keys)
		for _, key := range keys {
			collectStrings(typed[key], parts)
		}
	}
}

func semanticPurpose(text string) string {
	fields := strings.Fields(text)
	if len(fields) > 12 {
		fields = fields[:12]
	}
	return strings.Join(fields, " ")
}

func isExcluded(state State, class string) bool {
	for _, excluded := range state.ExcludedActionClasses {
		if class == excluded {
			return true
		}
	}
	return false
}

func hasDeferred(state State, key string) bool {
	if key == "" {
		return false
	}
	for _, intent := range state.DeferredIntents {
		if intent.Key == key {
			return true
		}
	}
	return false
}

func deferIntent(sessionID string, state *State, intent Intent) error {
	if !hasDeferred(*state, intent.Key) {
		state.DeferredIntents = append(state.DeferredIntents, intent)
	}
	state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
	return writeState(sessionID, *state)
}

func denialReason(intent Intent) string {
	return "Deferred by the active user work contract (" + intent.Class + "): " + intent.Reason +
		". Do not retry this purpose through another tool or command form. Continue other required runnable work; " +
		"return blocked only if none remains."
}

func stateRoot() string {
	if value := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_STATE_DIR")); value != "" {
		return filepath.Join(value, "work-contract")
	}
	if value := strings.TrimSpace(os.Getenv("CODEX_HOME")); value != "" {
		return filepath.Join(value, "harness", "work-contract")
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}
	return filepath.Join(home, ".codex", "harness", "work-contract")
}

func statePath(sessionID string) string {
	root := stateRoot()
	if root == "" || strings.TrimSpace(sessionID) == "" {
		return ""
	}
	return filepath.Join(root, digest(sessionID)+".json")
}

func writeState(sessionID string, state State) error {
	path := statePath(sessionID)
	if path == "" {
		return errors.New("work-contract state root unavailable")
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	raw, err := json.Marshal(state)
	if err != nil {
		return err
	}
	tmp, err := os.CreateTemp(filepath.Dir(path), ".work-contract-*.tmp")
	if err != nil {
		return err
	}
	tmpName := tmp.Name()
	defer os.Remove(tmpName)
	if err := tmp.Chmod(0o600); err != nil {
		tmp.Close()
		return err
	}
	if _, err := tmp.Write(append(raw, '\n')); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Sync(); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	return os.Rename(tmpName, path)
}

func normalize(value string) string {
	return strings.ToLower(strings.Join(strings.Fields(value), " "))
}

func containsAny(text string, values ...string) bool {
	for _, value := range values {
		if strings.Contains(text, value) {
			return true
		}
	}
	return false
}

func digest(value string) string {
	sum := sha256.Sum256([]byte(value))
	return hex.EncodeToString(sum[:])
}

func sortedKeys(values map[string]bool) []string {
	keys := make([]string, 0, len(values))
	for key, included := range values {
		if included {
			keys = append(keys, key)
		}
	}
	sort.Strings(keys)
	return keys
}
