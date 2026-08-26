package claudehook

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

const turnStateSchemaVersion = 1

type turnState struct {
	SchemaVersion int    `json:"schema_version"`
	Sequence      uint64 `json:"sequence"`
	CurrentKey    string `json:"current_key"`
}

func beginTurn(sessionID, promptID string) (string, error) {
	if strings.TrimSpace(sessionID) == "" {
		return opaqueTurnKey(promptID), nil
	}
	state, err := readTurnState(sessionID)
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		return "", err
	}
	if state.SchemaVersion != turnStateSchemaVersion {
		state = turnState{SchemaVersion: turnStateSchemaVersion}
	}
	state.Sequence++
	seed := strings.TrimSpace(promptID)
	if seed == "" {
		seed = fmt.Sprintf("%s:%d", sessionID, state.Sequence)
	}
	state.CurrentKey = opaqueTurnKey(seed)
	if err := writeTurnState(sessionID, state); err != nil {
		return "", err
	}
	return state.CurrentKey, nil
}

func currentTurn(sessionID, promptID string) (string, error) {
	if value := strings.TrimSpace(promptID); value != "" {
		return opaqueTurnKey(value), nil
	}
	if strings.TrimSpace(sessionID) == "" {
		return "", nil
	}
	state, err := readTurnState(sessionID)
	if err != nil {
		return "", err
	}
	if state.SchemaVersion != turnStateSchemaVersion {
		return "", nil
	}
	return state.CurrentKey, nil
}

func clearTurnState(sessionID string) error {
	if strings.TrimSpace(sessionID) == "" {
		return nil
	}
	err := os.Remove(turnStatePath(sessionID))
	if errors.Is(err, os.ErrNotExist) {
		return nil
	}
	return err
}

func readTurnState(sessionID string) (turnState, error) {
	raw, err := os.ReadFile(turnStatePath(sessionID))
	if err != nil {
		return turnState{SchemaVersion: turnStateSchemaVersion}, err
	}
	var state turnState
	if err := json.Unmarshal(raw, &state); err != nil {
		return turnState{SchemaVersion: turnStateSchemaVersion}, err
	}
	return state, nil
}

func writeTurnState(sessionID string, state turnState) error {
	path := turnStatePath(sessionID)
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	raw, err := json.Marshal(state)
	if err != nil {
		return err
	}
	tmp, err := os.CreateTemp(filepath.Dir(path), ".turn-*.tmp")
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
	if err := os.Rename(tmpName, path); err == nil {
		return nil
	} else if runtime.GOOS != "windows" {
		return err
	}
	if err := os.Remove(path); err != nil && !errors.Is(err, os.ErrNotExist) {
		return err
	}
	return os.Rename(tmpName, path)
}

func turnStatePath(sessionID string) string {
	root := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_STATE_DIR"))
	if root == "" {
		root = strings.TrimSpace(os.Getenv("CLAUDE_CONFIG_DIR"))
		if root == "" {
			if home, err := os.UserHomeDir(); err == nil {
				root = filepath.Join(home, ".claude")
			}
		}
		root = filepath.Join(root, "harness")
	}
	digest := sha256.Sum256([]byte(sessionID))
	return filepath.Join(root, "claude-turns", hex.EncodeToString(digest[:])+".json")
}

func opaqueTurnKey(value string) string {
	if strings.TrimSpace(value) == "" {
		return ""
	}
	digest := sha256.Sum256([]byte(value))
	return hex.EncodeToString(digest[:])
}
