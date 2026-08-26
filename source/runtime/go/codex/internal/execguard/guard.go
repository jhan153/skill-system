package execguard

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

const (
	schemaVersion = 1
	maxAttempts   = 64

	EffectObserve        = "observe"
	EffectBuildTest      = "build_test"
	EffectWorkspaceWrite = "workspace_write"
	EffectProcessLaunch  = "process_launch"
	EffectNetwork        = "network"
	EffectRuntimeWrite   = "runtime_write"
	EffectDelete         = "delete"
	EffectPublish        = "publish"
	EffectTerminate      = "terminate"

	GrantWorkspaceWrite = "workspace_write"
	GrantProcessLaunch  = "process_launch"
	GrantNetwork        = "network"
	GrantRuntimeWrite   = "runtime_write"
	GrantCodexHome      = "codex_home"
	GrantDelete         = "delete"
	GrantPublish        = "publish"
	GrantTerminate      = "terminate"

	AttemptProposed = "proposed"
	AttemptAllowed  = "allowed"
	AttemptPrompted = "prompted"
	AttemptExecuted = "executed"
	AttemptDenied   = "denied_terminal"
)

const terminalReason = "This action is terminal for the current turn. Do not retry it through another command form or analyze approval mechanics. Continue other authorized work; if none remains, report one concise blocked result."

type Event struct {
	HookEventName  string
	SessionID      string
	TurnID         string
	Cwd            string
	Prompt         string
	ToolName       string
	ToolInput      json.RawMessage
	ToolResponse   json.RawMessage
	ToolUseID      string
	PermissionMode string
}

type Decision struct {
	Deny            bool
	Rewrite         bool
	AllowPermission bool
	Reason          string
	SystemMessage   string
	UpdatedInput    map[string]any
}

type Attempt struct {
	PurposeKey  string `json:"purpose_key"`
	CommandHash string `json:"command_hash"`
	ToolUseHash string `json:"tool_use_hash"`
	Generation  int    `json:"generation"`
	Status      string `json:"status"`
}

type State struct {
	SchemaVersion int       `json:"schema_version"`
	SessionHash   string    `json:"session_hash"`
	TurnHash      string    `json:"turn_hash"`
	Revision      int       `json:"revision"`
	Generation    int       `json:"generation"`
	Grants        []string  `json:"grants"`
	TargetHashes  []string  `json:"target_hashes"`
	Attempts      []Attempt `json:"attempts"`
	UpdatedAt     string    `json:"updated_at"`
}

func newState(sessionID string) State {
	return State{
		SchemaVersion: schemaVersion,
		SessionHash:   digest(sessionID),
		Grants:        []string{},
		TargetHashes:  []string{},
		Attempts:      []Attempt{},
	}
}

// Capture compiles one user turn into a privacy-bounded execution grant set.
// It never stores prompt or command text.
func Capture(event Event) error {
	if strings.TrimSpace(event.SessionID) == "" || strings.TrimSpace(event.Prompt) == "" {
		return nil
	}
	compiled := compilePrompt(event.Prompt, event.Cwd)
	return updateState(event.SessionID, func(state *State) error {
		if state.SessionHash != digest(event.SessionID) {
			return errors.New("exec guard state belongs to a different session")
		}
		if compiled.Continuation {
			compiled.Grants = append(compiled.Grants, state.Grants...)
			compiled.TargetHashes = append(compiled.TargetHashes, state.TargetHashes...)
		}
		state.TurnHash = digest(event.TurnID)
		state.Grants = uniqueSorted(compiled.Grants)
		state.TargetHashes = uniqueSorted(compiled.TargetHashes)
		if !compiled.Continuation || compiled.ResetAttempts {
			state.Attempts = nil
			state.Generation = 0
		}
		state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
		return nil
	})
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

// Preflight normalizes a supported local command before host policy decides
// whether it can execute. Shape errors and exact repeated attempts terminate
// here, before an approval prompt can be created.
func Preflight(event Event) (Decision, error) {
	plan, input, applies, err := analyzeTool(event)
	if !applies {
		return Decision{}, nil
	}
	if err != nil {
		return deny("Malformed tool input: " + err.Error()), nil
	}
	if plan.InvalidReason != "" {
		return deny(plan.InvalidReason), nil
	}
	if plan.TextAuthoring {
		return deny("Repository text creation and edits must use apply_patch, not a shell writer or redirection."), nil
	}
	if plan.BroadDanger {
		return deny("The command resolves to a broad destructive target and cannot be admitted by a turn-level cleanup grant."), nil
	}

	state, stateErr := loadState(event.SessionID)
	if stateErr != nil && !errors.Is(stateErr, os.ErrNotExist) {
		state = newState(event.SessionID)
	}
	ensureTurn(&state, event.TurnID)
	authorized := isAuthorized(plan, state)
	mode := strings.ToLower(strings.TrimSpace(event.PermissionMode))
	if mode == "plan" && plan.hasSideEffect() {
		return deny("Side-effecting execution is unavailable in plan mode."), nil
	}
	if !authorized && (mode == "dontask" || mode == "bypasspermissions") {
		return deny("The command requires authority not present in the current user turn, and this permission mode forbids asking."), nil
	}
	if !authorized && plan.requiresExplicitPreflightGrant() {
		return deny("The current user turn does not authorize this local write or process launch."), nil
	}

	var decision Decision
	updateErr := updateState(event.SessionID, func(current *State) error {
		ensureTurn(current, event.TurnID)
		if repeated := repeatedAttempt(*current, plan, event.ToolUseID); repeated {
			decision = deny("The same command or semantic purpose has already been attempted without an intervening relevant change.")
			return nil
		}
		rememberAttempt(current, plan, event.ToolUseID, AttemptProposed)
		return nil
	})
	if updateErr != nil && strings.TrimSpace(event.SessionID) != "" {
		// Stateless shape enforcement remains active when bounded state is unavailable.
		decision = Decision{}
	}
	if decision.Deny {
		return decision, nil
	}
	if plan.RewrittenCommand != "" {
		input["command"] = plan.RewrittenCommand
		return Decision{
			Rewrite:      true,
			Reason:       "Removed an unnecessary login-shell wrapper and preserved the authorized inner command.",
			UpdatedInput: input,
		}, nil
	}
	return Decision{}, nil
}

// Permission decides whether a host approval request represents authority the
// user already granted for this turn. A truly new authority reaches the UI at
// most once in an interactive mode and terminates immediately in dontAsk.
func Permission(event Event) (Decision, error) {
	plan, _, applies, err := analyzeTool(event)
	if !applies {
		return Decision{}, nil
	}
	if err != nil {
		return deny("Malformed approval input: " + err.Error()), nil
	}
	if plan.InvalidReason != "" {
		return deny(plan.InvalidReason), nil
	}
	if plan.TextAuthoring {
		return deny("Repository text creation and edits must use apply_patch."), nil
	}
	if plan.BroadDanger {
		return deny("The command resolves to a broad destructive target and cannot be approved by this harness."), nil
	}

	state, stateErr := loadState(event.SessionID)
	if stateErr != nil && !errors.Is(stateErr, os.ErrNotExist) {
		state = newState(event.SessionID)
	}
	ensureTurn(&state, event.TurnID)
	authorized := isAuthorized(plan, state)
	mode := strings.ToLower(strings.TrimSpace(event.PermissionMode))
	var decision Decision
	updateErr := updateState(event.SessionID, func(current *State) error {
		ensureTurn(current, event.TurnID)
		if alreadyPrompted(*current, plan) {
			decision = deny("Approval for the same semantic purpose was already requested in this turn.")
			return nil
		}
		if authorized {
			setAttemptStatus(current, plan, event.ToolUseID, AttemptAllowed)
			decision = Decision{AllowPermission: true}
			return nil
		}
		if mode == "dontask" || mode == "bypasspermissions" || mode == "plan" {
			setAttemptStatus(current, plan, event.ToolUseID, AttemptDenied)
			decision = deny("This command needs new authority, but the current permission mode cannot ask for it.")
			return nil
		}
		setAttemptStatus(current, plan, event.ToolUseID, AttemptPrompted)
		decision.SystemMessage = "This is the only approval request allowed for this command purpose in the current turn. If it is denied or expires, treat that result as terminal: do not retry or analyze approval mechanics."
		return nil
	})
	if updateErr != nil && strings.TrimSpace(event.SessionID) != "" {
		if mode == "dontask" || mode == "bypasspermissions" || mode == "plan" {
			return deny("Execution authority state is unavailable and this permission mode cannot safely wait."), nil
		}
		if authorized {
			return Decision{AllowPermission: true}, nil
		}
	}
	return decision, nil
}

// Observe closes a proposed attempt and advances the workspace generation only
// after a successful state-changing tool result.
func Observe(event Event) error {
	plan, _, applies, err := analyzeTool(event)
	if err != nil || !applies {
		return err
	}
	return updateState(event.SessionID, func(state *State) error {
		ensureTurn(state, event.TurnID)
		setAttemptStatus(state, plan, event.ToolUseID, AttemptExecuted)
		if responseSucceeded(event.ToolResponse) && plan.changesWorkspaceGeneration() {
			state.Generation++
		}
		return nil
	})
}

func deny(reason string) Decision {
	reason = strings.TrimSpace(reason)
	if reason != "" {
		reason += " "
	}
	return Decision{Deny: true, Reason: reason + terminalReason}
}

func isAuthorized(plan CommandPlan, state State) bool {
	grants := stringSet(state.Grants)
	for _, effect := range plan.Effects {
		switch effect {
		case EffectObserve, EffectBuildTest:
			continue
		case EffectWorkspaceWrite:
			if !grants[GrantWorkspaceWrite] {
				return false
			}
		case EffectProcessLaunch:
			if !grants[GrantProcessLaunch] {
				return false
			}
		case EffectNetwork:
			if !grants[GrantNetwork] {
				return false
			}
		case EffectRuntimeWrite:
			if !grants[GrantRuntimeWrite] {
				return false
			}
		case EffectDelete:
			if !grants[GrantDelete] || plan.BroadDanger {
				return false
			}
		case EffectPublish:
			if !grants[GrantPublish] {
				return false
			}
		case EffectTerminate:
			if !grants[GrantTerminate] {
				return false
			}
		default:
			return false
		}
	}
	for _, target := range plan.TargetKinds {
		switch target {
		case TargetWorkspace:
			continue
		case TargetCodexHome:
			if !grants[GrantCodexHome] {
				return false
			}
		case TargetExternal:
			if !pathsAuthorized(plan.Paths, state.TargetHashes) {
				return false
			}
		}
	}
	return true
}

func pathsAuthorized(paths, hashes []string) bool {
	if len(paths) == 0 || len(hashes) == 0 {
		return false
	}
	allowed := stringSet(hashes)
	for _, path := range paths {
		matched := false
		for current := filepath.Clean(path); current != filepath.Dir(current); current = filepath.Dir(current) {
			if allowed[digest(current)] {
				matched = true
				break
			}
		}
		if !matched {
			return false
		}
	}
	return true
}

func ensureTurn(state *State, turnID string) {
	hash := digest(turnID)
	if state.TurnHash == hash {
		return
	}
	state.TurnHash = hash
	state.Attempts = nil
	state.Generation = 0
}

func repeatedAttempt(state State, plan CommandPlan, toolUseID string) bool {
	toolHash := digest(toolUseID)
	for _, attempt := range state.Attempts {
		if attempt.Generation != state.Generation {
			continue
		}
		if toolUseID != "" && attempt.ToolUseHash == toolHash {
			return false
		}
		if attempt.CommandHash == plan.CommandHash {
			return true
		}
	}
	return false
}

func alreadyPrompted(state State, plan CommandPlan) bool {
	for _, attempt := range state.Attempts {
		if attempt.Generation == state.Generation && attempt.PurposeKey == plan.PurposeKey && attempt.Status == AttemptPrompted {
			return true
		}
	}
	return false
}

func rememberAttempt(state *State, plan CommandPlan, toolUseID, status string) {
	state.Attempts = append(state.Attempts, Attempt{
		PurposeKey:  plan.PurposeKey,
		CommandHash: plan.CommandHash,
		ToolUseHash: digest(toolUseID),
		Generation:  state.Generation,
		Status:      status,
	})
	if len(state.Attempts) > maxAttempts {
		state.Attempts = append([]Attempt{}, state.Attempts[len(state.Attempts)-maxAttempts:]...)
	}
	state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
}

func setAttemptStatus(state *State, plan CommandPlan, toolUseID, status string) {
	toolHash := digest(toolUseID)
	for index := len(state.Attempts) - 1; index >= 0; index-- {
		attempt := &state.Attempts[index]
		if (toolUseID != "" && attempt.ToolUseHash == toolHash) ||
			(attempt.Generation == state.Generation && attempt.CommandHash == plan.CommandHash) {
			attempt.Status = status
			state.UpdatedAt = time.Now().UTC().Format(time.RFC3339)
			return
		}
	}
	rememberAttempt(state, plan, toolUseID, status)
}

func responseSucceeded(raw json.RawMessage) bool {
	if len(raw) == 0 {
		return true
	}
	var value any
	if json.Unmarshal(raw, &value) != nil {
		return true
	}
	return responseValueSucceeded(value)
}

func responseValueSucceeded(value any) bool {
	switch typed := value.(type) {
	case map[string]any:
		if failed, ok := typed["isError"].(bool); ok && failed {
			return false
		}
		if success, ok := typed["success"].(bool); ok {
			return success
		}
		if code, ok := typed["exit_code"].(float64); ok {
			return code == 0
		}
		if status, ok := typed["status"].(string); ok {
			status = strings.ToLower(status)
			if status == "error" || status == "failed" || status == "failure" {
				return false
			}
		}
		for _, nested := range typed {
			if child, ok := nested.(map[string]any); ok && !responseValueSucceeded(child) {
				return false
			}
		}
	}
	return true
}

func loadState(sessionID string) (State, error) {
	path := statePath(sessionID)
	if path == "" {
		return newState(sessionID), os.ErrNotExist
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		return newState(sessionID), err
	}
	var state State
	if err := json.Unmarshal(raw, &state); err != nil {
		return newState(sessionID), err
	}
	if state.SchemaVersion != schemaVersion || state.SessionHash != digest(sessionID) {
		return newState(sessionID), errors.New("invalid exec guard state")
	}
	return state, nil
}

func updateState(sessionID string, update func(*State) error) error {
	path := statePath(sessionID)
	if path == "" {
		return errors.New("exec guard state root unavailable")
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	unlock, err := acquireLock(path + ".lock")
	if err != nil {
		return err
	}
	defer unlock()
	state, err := loadState(sessionID)
	if errors.Is(err, os.ErrNotExist) {
		state = newState(sessionID)
	} else if err != nil {
		return err
	}
	if err := update(&state); err != nil {
		return err
	}
	state.SchemaVersion = schemaVersion
	state.SessionHash = digest(sessionID)
	state.Revision++
	state.Grants = uniqueSorted(state.Grants)
	state.TargetHashes = uniqueSorted(state.TargetHashes)
	if state.Attempts == nil {
		state.Attempts = []Attempt{}
	}
	return writeState(path, state)
}

func acquireLock(path string) (func(), error) {
	deadline := time.Now().Add(750 * time.Millisecond)
	for {
		err := os.Mkdir(path, 0o700)
		if err == nil {
			return func() { _ = os.Remove(path) }, nil
		}
		if !errors.Is(err, os.ErrExist) {
			return nil, err
		}
		if info, statErr := os.Stat(path); statErr == nil && time.Since(info.ModTime()) > 5*time.Second {
			_ = os.Remove(path)
			continue
		}
		if time.Now().After(deadline) {
			return nil, errors.New("exec guard state lock timeout")
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func writeState(path string, state State) error {
	raw, err := json.Marshal(state)
	if err != nil {
		return err
	}
	tmp, err := os.CreateTemp(filepath.Dir(path), ".exec-guard-*.tmp")
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

func statePath(sessionID string) string {
	if strings.TrimSpace(sessionID) == "" {
		return ""
	}
	return filepath.Join(stateRoot(), digest(sessionID)+".json")
}

func stateRoot() string {
	if value := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_STATE_DIR")); value != "" {
		return filepath.Join(value, "exec-guard")
	}
	if value := strings.TrimSpace(os.Getenv("CODEX_HOME")); value != "" {
		return filepath.Join(value, "harness", "exec-guard")
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}
	return filepath.Join(home, ".codex", "harness", "exec-guard")
}

func digest(value string) string {
	sum := sha256.Sum256([]byte(value))
	return hex.EncodeToString(sum[:])
}

func uniqueSorted(values []string) []string {
	set := stringSet(values)
	result := make([]string, 0, len(set))
	for value := range set {
		result = append(result, value)
	}
	sort.Strings(result)
	return result
}

func stringSet(values []string) map[string]bool {
	result := make(map[string]bool, len(values))
	for _, value := range values {
		if value != "" {
			result[value] = true
		}
	}
	return result
}
