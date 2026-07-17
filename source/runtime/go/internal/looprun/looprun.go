package looprun

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
)

var terminalActions = map[string]bool{
	"success": true, "blocked": true, "budget_exhausted": true,
	"unsafe": true, "fatal": true, "stalled": true,
}

type Decision struct {
	Action             string `json:"action"`
	ReasonCode         string `json:"reason_code"`
	ContinuationPrompt string `json:"continuation_prompt"`
}

type Report struct {
	Status    string   `json:"status"`
	LoopRunID string   `json:"loop_run_id"`
	Decision  Decision `json:"decision"`
	Reason    string   `json:"reason,omitempty"`
	LoopDir   string   `json:"-"`
}

type Output struct {
	Continue      *bool  `json:"continue,omitempty"`
	Decision      string `json:"decision,omitempty"`
	Reason        string `json:"reason,omitempty"`
	SystemMessage string `json:"systemMessage,omitempty"`
}

func Evaluate(sessionID, explicitDir string) (Report, *Output) {
	loopDir, pointer := activeLoop(sessionID, explicitDir)
	if loopDir == "" {
		return Report{}, nil
	}
	evaluator := filepath.Join(runtimeRoot(), "tools", "evaluate_loop_run.py")
	if _, err := os.Stat(evaluator); err != nil {
		return Report{Status: "error", LoopDir: loopDir, Reason: "evaluate_loop_run.py unavailable"}, nil
	}
	python, prefix, err := pythonCommand()
	if err != nil {
		return Report{Status: "error", LoopDir: loopDir, Reason: err.Error()}, nil
	}
	args := append(prefix, evaluator, loopDir)
	if continuationBlocking() {
		args = append(args, "--record-stop-continuation")
	}
	args = append(args, "--format", "json")
	ctx, cancel := context.WithTimeout(context.Background(), 8*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, python, args...)
	cmd.Dir = runtimeRoot()
	output, runErr := cmd.CombinedOutput()
	if errors.Is(ctx.Err(), context.DeadlineExceeded) {
		return Report{Status: "error", LoopDir: loopDir, Reason: "LoopRun evaluation timed out"}, nil
	}
	if runErr != nil {
		reason := strings.TrimSpace(string(output))
		if len(reason) > 500 {
			reason = reason[:500]
		}
		return Report{Status: "error", LoopDir: loopDir, Reason: reason}, nil
	}
	var report Report
	if err := json.Unmarshal(output, &report); err != nil {
		return Report{Status: "error", LoopDir: loopDir, Reason: "LoopRun evaluator returned invalid JSON"}, nil
	}
	report.LoopDir = loopDir
	if terminalActions[report.Decision.Action] && pointer != "" {
		deactivate(pointer, loopDir, report.Decision.Action)
	}
	if (report.Decision.Action == "continue" || report.Decision.Action == "recover") && report.Decision.ContinuationPrompt != "" {
		if continuationBlocking() {
			return report, &Output{Decision: "block", Reason: report.Decision.ContinuationPrompt}
		}
		value := true
		return report, &Output{Continue: &value, SystemMessage: "Loop continuation (observational): " + report.Decision.ContinuationPrompt}
	}
	return report, nil
}

func activeLoop(sessionID, explicitDir string) (string, string) {
	if strings.TrimSpace(explicitDir) == "" {
		explicitDir = strings.TrimSpace(os.Getenv("SKILL_SYSTEM_LOOP_RUN_DIR"))
	}
	if explicitDir != "" {
		if activeLoopDir(explicitDir) {
			return filepath.Clean(explicitDir), ""
		}
		return "", ""
	}
	if strings.TrimSpace(sessionID) == "" {
		return "", ""
	}
	pointer := filepath.Join(runtimeRoot(), "harness", "active-loops", safeID(sessionID)+".json")
	raw, err := os.ReadFile(pointer)
	if err != nil {
		return "", ""
	}
	var value struct {
		Status     string `json:"status"`
		LoopRunDir string `json:"loop_run_dir"`
	}
	if json.Unmarshal(raw, &value) != nil || value.Status != "active" || !activeLoopDir(value.LoopRunDir) {
		return "", ""
	}
	return filepath.Clean(value.LoopRunDir), pointer
}

func activeLoopDir(path string) bool {
	if path == "" {
		return false
	}
	if _, err := os.Stat(filepath.Join(path, "contract.yaml")); err != nil {
		return false
	}
	raw, err := os.ReadFile(filepath.Join(path, "state.yaml"))
	if err != nil {
		return false
	}
	if len(raw) > 8192 {
		raw = raw[:8192]
	}
	return strings.Contains(string(raw), "status: active")
}

func deactivate(pointer, expectedDir, action string) {
	raw, err := os.ReadFile(pointer)
	if err != nil {
		return
	}
	var value map[string]any
	if json.Unmarshal(raw, &value) != nil || value["status"] != "active" {
		return
	}
	if current, ok := value["loop_run_dir"].(string); ok && filepath.Clean(current) != filepath.Clean(expectedDir) {
		return
	}
	value["status"] = "terminal"
	value["final_action"] = action
	value["deactivated_at"] = time.Now().UTC().Format(time.RFC3339)
	encoded, err := json.Marshal(value)
	if err == nil {
		_ = os.WriteFile(pointer, append(encoded, '\n'), 0o600)
	}
}

func runtimeRoot() string {
	if value := strings.TrimSpace(os.Getenv("CODEX_HOME")); value != "" {
		return value
	}
	if executable, err := os.Executable(); err == nil {
		return filepath.Dir(filepath.Dir(executable))
	}
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, ".codex")
	}
	return "."
}

func continuationBlocking() bool {
	value := strings.ToLower(strings.TrimSpace(os.Getenv("SKILL_SYSTEM_LOOP_CONTINUATION")))
	return value != "observe" && value != "off" && value != "false" && value != "0"
}

func safeID(value string) string {
	var builder strings.Builder
	for _, char := range value {
		if (char >= 'a' && char <= 'z') || (char >= 'A' && char <= 'Z') || (char >= '0' && char <= '9') || strings.ContainsRune("._-", char) {
			builder.WriteRune(char)
		} else {
			builder.WriteByte('-')
		}
		if builder.Len() >= 96 {
			break
		}
	}
	result := strings.Trim(builder.String(), ".-")
	if result == "" {
		return "unknown-session"
	}
	return result
}

func pythonCommand() (string, []string, error) {
	if configured := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_PYTHON")); configured != "" {
		return configured, nil, nil
	}
	if runtime.GOOS == "windows" {
		if path, err := exec.LookPath("py.exe"); err == nil {
			return path, []string{"-3"}, nil
		}
		if path, err := exec.LookPath("python.exe"); err == nil {
			return path, nil, nil
		}
	} else if path, err := exec.LookPath("python3"); err == nil {
		return path, nil, nil
	}
	return "", nil, errors.New("Python runtime for active LoopRun not found")
}
