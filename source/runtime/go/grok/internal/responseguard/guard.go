package responseguard

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const schemaVersion = 1

const CorrectionContext = "User correction gate: treat this message as a correction, not as new authority to inspect or change unrelated state. Re-evaluate the affected assumptions and invalidate dependent conclusions before answering. Do not reply with apology/agreement plus a future promise alone; give the corrected premise and the direct answer or action now, within the user's requested scope."

var (
	repeatedMistake = regexp.MustCompile(`(?:이런|또|같은|동일한|기본적인|이것도|그것도)[^.!?？\n]{0,30}실수`)
	fencedBlock     = regexp.MustCompile("(?s)```.*?```")
	markdownLink    = regexp.MustCompile(`\[[^]]*\]\([^)]+\)`)
)

type State struct {
	SchemaVersion     int    `json:"schema_version"`
	TurnKey           string `json:"turn_key"`
	CorrectionPending bool   `json:"correction_pending"`
	StopBlockUsed     bool   `json:"stop_block_used"`
}

func defaultState() State { return State{SchemaVersion: schemaVersion} }

func IsCorrection(prompt string) bool {
	text := normalize(prompt)
	if text == "" {
		return false
	}
	prefixes := []string{"아니 ", "아니,", "아니.", "아니요", "아뇨", "no ", "no,", "no.", "nope"}
	for _, prefix := range prefixes {
		if strings.HasPrefix(text, prefix) {
			return true
		}
	}
	markers := []string{
		"그게 아니", "이게 아니", "그 뜻이 아니", "요청한 게 아니", "요청한건 아니", "말한 게 아니",
		"하지 말라고 했", "하라고 한 게 아니", "잘못 이해", "잘못 판단", "잘못 답", "오해했",
		"틀렸잖", "틀렸어", "망가뜨렸잖", "망가 뜨렸잖", "수습형 답변", "수습형 패턴",
		"not what i asked", "not what i said", "not what i meant", "you misunderstood", "you ignored my request",
	}
	for _, marker := range markers {
		if strings.Contains(text, marker) {
			return true
		}
	}
	return repeatedMistake.MatchString(text)
}

func IsRecoveryOnly(message string) bool {
	text := normalize(message)
	if text == "" || !hasRecoveryOpener(text) || !hasFuturePromise(text) {
		return false
	}
	return !hasDirectResolution(text)
}

func Prompt(sessionID, turnID, prompt string) (bool, error) {
	correction := IsCorrection(prompt)
	if sessionID == "" || !correction {
		return correction, nil
	}
	state := defaultState()
	state.TurnKey = hash(turnID)
	state.CorrectionPending = correction
	return correction, writeState(sessionID, state)
}

func Stop(sessionID, turnID, message string) (bool, error) {
	if sessionID == "" {
		return false, nil
	}
	state, err := readState(sessionID)
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		return false, err
	}
	if state.SchemaVersion != schemaVersion || state.TurnKey != hash(turnID) || !state.CorrectionPending {
		return false, nil
	}
	if state.StopBlockUsed || !IsRecoveryOnly(message) {
		_ = clearState(sessionID)
		return false, nil
	}
	state.StopBlockUsed = true
	if err := writeState(sessionID, state); err != nil {
		return false, err
	}
	return true, nil
}

func Clear(sessionID string) error {
	if sessionID == "" {
		return nil
	}
	return clearState(sessionID)
}

func stateRoot() string {
	if value := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_STATE_DIR")); value != "" {
		return filepath.Join(value, "correction-gate")
	}
	if value := strings.TrimSpace(os.Getenv("GROK_HOME")); value != "" {
		return filepath.Join(value, "harness", "correction-gate")
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}
	return filepath.Join(home, ".grok", "harness", "correction-gate")
}

func statePath(sessionID string) string {
	root := stateRoot()
	if root == "" {
		return ""
	}
	return filepath.Join(root, hash(sessionID)+".json")
}

func readState(sessionID string) (State, error) {
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
	return state, nil
}

func writeState(sessionID string, state State) error {
	path := statePath(sessionID)
	if path == "" {
		return errors.New("state root unavailable")
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	raw, err := json.Marshal(state)
	if err != nil {
		return err
	}
	tmp, err := os.CreateTemp(filepath.Dir(path), ".correction-*.tmp")
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

func clearState(sessionID string) error {
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

func hash(value string) string {
	digest := sha256.Sum256([]byte(value))
	return hex.EncodeToString(digest[:])
}

func normalize(value string) string {
	return strings.ToLower(strings.Join(strings.Fields(value), " "))
}

func hasRecoveryOpener(text string) bool {
	openers := []string{"맞습니다", "맞아요", "그렇습니다", "죄송", "미안", "제가 잘못", "you're right", "you are right", "sorry", "my mistake"}
	for _, opener := range openers {
		if strings.HasPrefix(text, opener) {
			return true
		}
	}
	return false
}

func hasFuturePromise(text string) bool {
	markers := []string{"하겠습니다", "할게요", "해보겠습니다", "보겠습니다", "지금부터", "앞으로", "이제부터", "바로 다시", "i will", "i'll", "from now on", "going forward", "let me"}
	for _, marker := range markers {
		if strings.Contains(text, marker) {
			return true
		}
	}
	return false
}

func hasDirectResolution(text string) bool {
	text = fencedBlock.ReplaceAllString(text, " ")
	text = markdownLink.ReplaceAllString(text, " ")
	text = strings.NewReplacer("**", "", "__", "", "~~", "", "`", "").Replace(text)
	segments := strings.FieldsFunc(text, func(r rune) bool {
		return r == '.' || r == '!' || r == '?' || r == '？' || r == '\n' || r == '\r'
	})
	for _, segment := range segments {
		segment = normalize(segment)
		if segment == "" || isRecoveryBoilerplate(segment) {
			continue
		}
		if substantiveResolution(segment) {
			return true
		}
	}
	return false
}

func substantiveResolution(segment string) bool {
	prefixMarkers := []string{
		"결론은", "답은", "원인은", "이유는", "핵심은", "현재 상태는", "복구 계획은", "수정 범위는",
		"구현 결과는", "검증 결과는", "the answer is", "the cause is", "the reason is", "the result is",
	}
	for _, marker := range prefixMarkers {
		if index := strings.Index(segment, marker); index >= 0 {
			remainder := strings.TrimSpace(segment[index+len(marker):])
			if substantiveRemainder(remainder) {
				return true
			}
		}
	}
	actionMarkers := []string{
		"수정했습니다", "반영했습니다", "구현했습니다", "삭제했습니다", "복구했습니다", "완료했습니다",
		"fixed", "implemented", "completed", "verified",
	}
	for _, marker := range actionMarkers {
		if index := strings.Index(segment, marker); index >= 0 {
			detail := strings.TrimSpace(segment[:index] + " " + segment[index+len(marker):])
			if substantiveRemainder(detail) {
				return true
			}
		}
	}
	return false
}

func substantiveRemainder(value string) bool {
	value = strings.Trim(strings.TrimSpace(value), ":-–— ")
	if len([]rune(value)) < 8 {
		return false
	}
	for _, generic := range []string{
		"다음과 같습니다", "아래와 같습니다", "확인하겠습니다", "검토하겠습니다", "다시 확인하겠습니다",
		"다시 검토하겠습니다", "as follows", "i will check", "i will review", "let me check",
	} {
		if value == generic {
			return false
		}
	}
	return true
}

func isRecoveryBoilerplate(segment string) bool {
	segment = strings.TrimSpace(segment)
	for _, opener := range []string{"맞습니다", "맞아요", "그렇습니다", "죄송합니다", "죄송", "미안합니다", "제가 잘못했습니다", "you're right", "you are right", "sorry", "my mistake"} {
		if segment == opener {
			return true
		}
	}
	if hasFuturePromise(segment) {
		for _, marker := range []string{"결론은", "답은", "원인은", "이유는", "핵심은", "복구 계획은", "수정 범위는", "수정했습니다", "반영했습니다", "구현했습니다", "the answer is", "the cause is", "the reason is", "fixed", "implemented"} {
			if strings.Contains(segment, marker) {
				return false
			}
		}
		return true
	}
	return false
}
