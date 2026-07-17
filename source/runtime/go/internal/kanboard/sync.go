package kanboard

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"
)

type Result struct {
	Status    string `json:"status"`
	Mode      string `json:"mode,omitempty"`
	Workspace string `json:"workspace,omitempty"`
	Reason    string `json:"reason,omitempty"`
}

type stamp struct {
	Fingerprint string `json:"fingerprint"`
	Mode        string `json:"mode"`
}

type pendingLease struct {
	Token       string    `json:"token"`
	Fingerprint string    `json:"fingerprint"`
	Mode        string    `json:"mode"`
	AcquiredAt  time.Time `json:"acquired_at"`
	ExpiresAt   time.Time `json:"expires_at"`
}

const (
	workerTimeout  = 60 * time.Second
	leaseLifetime  = 120 * time.Second
	reaperLifetime = 10 * time.Second
)

func MaybeSync(workspace string, force bool) Result {
	mode := normalizeMode(env("KANBOARD_PLAN_AUTOSYNC", "apply"))
	if mode == "0" || mode == "false" || mode == "off" || mode == "none" || mode == "disabled" {
		return Result{Status: "disabled"}
	}
	if mode != "apply" && mode != "dry-run" {
		return Result{Status: "skipped", Reason: "invalid KANBOARD_PLAN_AUTOSYNC"}
	}
	workspace = strings.TrimSpace(workspace)
	if workspace == "" {
		return Result{Status: "skipped", Reason: "workspace unavailable"}
	}
	workspace, _ = filepath.Abs(workspace)
	if _, err := os.Stat(filepath.Join(workspace, ".kanboard-plan.yml")); err != nil {
		return Result{Status: "skipped", Workspace: workspace, Reason: "workspace has no .kanboard-plan.yml"}
	}
	fingerprint, err := planFingerprint(workspace)
	if err != nil {
		return Result{Status: "error", Workspace: workspace, Reason: err.Error()}
	}
	previous := readStamp(workspace)
	if !force && fingerprint != "" && previous.Fingerprint == fingerprint && previous.Mode == mode {
		return Result{Status: "unchanged", Mode: mode, Workspace: workspace}
	}
	root := integrationRoot(workspace)
	if root == "" {
		return Result{Status: "unavailable", Mode: mode, Workspace: workspace, Reason: "kanboard-plan-sync integration not found"}
	}
	if _, _, err := pythonCommand(); err != nil {
		return Result{Status: "unavailable", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	executable, err := harnessExecutable()
	if err != nil {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	lease, acquired, err := acquireLease(workspace, mode, fingerprint)
	if err != nil {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	if !acquired {
		return Result{Status: "pending", Mode: mode, Workspace: workspace, Reason: "Kanboard sync worker already pending"}
	}
	cmd := exec.Command(executable, "kanboard-sync-worker", "--workspace", workspace, "--mode", mode, "--fingerprint", fingerprint, "--lease-token", lease.Token)
	cmd.Dir = root
	cmd.Env = os.Environ()
	if err := cmd.Start(); err != nil {
		releaseLease(workspace, lease.Token)
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	if err := cmd.Process.Release(); err != nil {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	return Result{Status: "queued", Mode: mode, Workspace: workspace}
}

func RunWorker(workspace, mode, expectedFingerprint, leaseToken string) Result {
	mode = normalizeMode(mode)
	if mode != "apply" && mode != "dry-run" {
		return Result{Status: "error", Mode: mode, Reason: "invalid worker mode"}
	}
	workspace = strings.TrimSpace(workspace)
	if workspace == "" {
		return Result{Status: "error", Mode: mode, Reason: "workspace unavailable"}
	}
	workspace, _ = filepath.Abs(workspace)
	if !ownsLease(workspace, leaseToken, mode, expectedFingerprint) {
		return Result{Status: "skipped", Mode: mode, Workspace: workspace, Reason: "Kanboard sync lease not owned"}
	}
	defer releaseLease(workspace, leaseToken)
	current, err := planFingerprint(workspace)
	if err != nil {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	if expectedFingerprint == "" || current != expectedFingerprint {
		return Result{Status: "stale", Mode: mode, Workspace: workspace, Reason: "plan changed before sync"}
	}
	root := integrationRoot(workspace)
	if root == "" {
		return Result{Status: "unavailable", Mode: mode, Workspace: workspace, Reason: "kanboard-plan-sync integration not found"}
	}
	command, args, err := pythonCommand()
	if err != nil {
		return Result{Status: "unavailable", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	args = append(args, "-m", "kanboard_plan_sync", "sync-all", "--workspace", workspace)
	if mode == "apply" {
		args = append(args, "--apply")
	}
	ctx, cancel := context.WithTimeout(context.Background(), workerTimeout)
	defer cancel()
	cmd := exec.CommandContext(ctx, command, args...)
	cmd.Dir = root
	cmd.Env = append(os.Environ(), "PYTHONPATH="+filepath.Join(root, "src"))
	output, runErr := cmd.CombinedOutput()
	if ctx.Err() == context.DeadlineExceeded {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: "Kanboard sync timed out"}
	}
	if runErr != nil {
		reason := strings.TrimSpace(string(output))
		if len(reason) > 500 {
			reason = reason[:500]
		}
		if reason == "" {
			reason = runErr.Error()
		}
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: reason}
	}
	after, err := planFingerprint(workspace)
	if err != nil {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	if after != expectedFingerprint {
		return Result{Status: "stale", Mode: mode, Workspace: workspace, Reason: "plan changed during sync"}
	}
	if err := writeStamp(workspace, stamp{Fingerprint: expectedFingerprint, Mode: mode}); err != nil {
		return Result{Status: "error", Mode: mode, Workspace: workspace, Reason: err.Error()}
	}
	return Result{Status: "synced", Mode: mode, Workspace: workspace}
}

func normalizeMode(value string) string {
	mode := strings.ToLower(strings.TrimSpace(value))
	if mode == "dry_run" {
		return "dry-run"
	}
	return mode
}

func acquireLease(workspace, mode, fingerprint string) (pendingLease, bool, error) {
	path := leasePath(workspace)
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return pendingLease{}, false, err
	}
	now := time.Now().UTC()
	for attempt := 0; attempt < 3; attempt++ {
		if active, err := reaperActive(path, now); err != nil {
			return pendingLease{}, false, err
		} else if active {
			return pendingLease{}, false, nil
		}
		value, err := newLease(mode, fingerprint, now)
		if err != nil {
			return pendingLease{}, false, err
		}
		if err := createLease(path, value); err == nil {
			return value, true, nil
		} else if !errors.Is(err, os.ErrExist) {
			return pendingLease{}, false, err
		}
		current, readErr := readLeasePath(path)
		if readErr == nil && current.ExpiresAt.After(now) {
			return pendingLease{}, false, nil
		}
		reaped, err := reapStaleLease(path, now)
		if err != nil {
			return pendingLease{}, false, err
		}
		if !reaped {
			return pendingLease{}, false, nil
		}
		now = time.Now().UTC()
	}
	return pendingLease{}, false, nil
}

func newLease(mode, fingerprint string, now time.Time) (pendingLease, error) {
	random := make([]byte, 16)
	if _, err := rand.Read(random); err != nil {
		return pendingLease{}, err
	}
	return pendingLease{
		Token:       hex.EncodeToString(random),
		Fingerprint: fingerprint,
		Mode:        mode,
		AcquiredAt:  now,
		ExpiresAt:   now.Add(leaseLifetime),
	}, nil
}

func createLease(path string, value pendingLease) error {
	raw, err := json.Marshal(value)
	if err != nil {
		return err
	}
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		return err
	}
	ok := false
	defer func() {
		file.Close()
		if !ok {
			os.Remove(path)
		}
	}()
	if _, err := file.Write(append(raw, '\n')); err != nil {
		return err
	}
	if err := file.Sync(); err != nil {
		return err
	}
	if err := file.Close(); err != nil {
		return err
	}
	ok = true
	return nil
}

func readLeasePath(path string) (pendingLease, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return pendingLease{}, err
	}
	var value pendingLease
	if err := json.Unmarshal(raw, &value); err != nil {
		return pendingLease{}, err
	}
	if value.Token == "" || value.ExpiresAt.IsZero() {
		return pendingLease{}, errors.New("invalid Kanboard pending lease")
	}
	return value, nil
}

func ownsLease(workspace, token, mode, fingerprint string) bool {
	if token == "" {
		return false
	}
	value, err := readLeasePath(leasePath(workspace))
	return err == nil && value.Token == token && value.Mode == mode && value.Fingerprint == fingerprint
}

func releaseLease(workspace, token string) {
	if token == "" {
		return
	}
	path := leasePath(workspace)
	value, err := readLeasePath(path)
	if err == nil && value.Token == token {
		_ = os.Remove(path)
	}
}

func reaperActive(lease string, now time.Time) (bool, error) {
	path := lease + ".reap"
	info, err := os.Stat(path)
	if errors.Is(err, os.ErrNotExist) {
		return false, nil
	}
	if err != nil {
		return false, err
	}
	if now.Sub(info.ModTime()) <= reaperLifetime {
		return true, nil
	}
	if err := os.Remove(path); err != nil && !errors.Is(err, os.ErrNotExist) {
		return false, err
	}
	return false, nil
}

func reapStaleLease(path string, now time.Time) (bool, error) {
	guard := path + ".reap"
	file, err := os.OpenFile(guard, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if errors.Is(err, os.ErrExist) {
		return false, nil
	}
	if err != nil {
		return false, err
	}
	_ = file.Close()
	defer os.Remove(guard)
	current, err := readLeasePath(path)
	if errors.Is(err, os.ErrNotExist) {
		return true, nil
	}
	if err == nil && current.ExpiresAt.After(now) {
		return false, nil
	}
	if err != nil {
		info, statErr := os.Stat(path)
		if statErr != nil {
			if errors.Is(statErr, os.ErrNotExist) {
				return true, nil
			}
			return false, statErr
		}
		if now.Sub(info.ModTime()) <= reaperLifetime {
			return false, nil
		}
	}
	if err := os.Remove(path); err != nil && !errors.Is(err, os.ErrNotExist) {
		return false, err
	}
	return true, nil
}

func harnessExecutable() (string, error) {
	if configured := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_EXECUTABLE")); configured != "" {
		return configured, nil
	}
	return os.Executable()
}

func integrationRoot(workspace string) string {
	if value := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_KANBOARD_SYNC_ROOT")); value != "" {
		if info, err := os.Stat(filepath.Join(value, "src", "kanboard_plan_sync")); err == nil && info.IsDir() {
			return value
		}
		return ""
	}
	dir := workspace
	for {
		candidate := filepath.Join(dir, "integrations", "kanboard-plan-sync")
		if info, err := os.Stat(filepath.Join(candidate, "src", "kanboard_plan_sync")); err == nil && info.IsDir() {
			return candidate
		}
		if _, err := os.Stat(filepath.Join(dir, ".git")); err == nil {
			break
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	if home, err := os.UserHomeDir(); err == nil {
		candidate := filepath.Join(home, ".ai", "infra", "kanboard-plan-sync")
		if info, statErr := os.Stat(filepath.Join(candidate, "src", "kanboard_plan_sync")); statErr == nil && info.IsDir() {
			return candidate
		}
	}
	return ""
}

func planFingerprint(workspace string) (string, error) {
	paths := []string{filepath.Join(workspace, ".kanboard-plan.yml")}
	matches, err := filepath.Glob(filepath.Join(workspace, "docs", "plan", "*.md"))
	if err != nil {
		return "", err
	}
	paths = append(paths, matches...)
	sort.Strings(paths)
	hash := sha256.New()
	for _, path := range paths {
		info, statErr := os.Stat(path)
		if statErr != nil {
			if os.IsNotExist(statErr) {
				continue
			}
			return "", statErr
		}
		fmt.Fprintf(hash, "%s\x00%d\x00%d\n", path, info.Size(), info.ModTime().UnixNano())
	}
	return hex.EncodeToString(hash.Sum(nil)), nil
}

func statePath(workspace string) string {
	base := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_STATE_DIR"))
	if base == "" {
		base = strings.TrimSpace(os.Getenv("CODEX_HOME"))
		if base != "" {
			base = filepath.Join(base, "harness")
		}
	}
	if base == "" {
		if home, err := os.UserHomeDir(); err == nil {
			base = filepath.Join(home, ".codex", "harness")
		}
	}
	digest := sha256.Sum256([]byte(workspace))
	return filepath.Join(base, "kanboard-sync", hex.EncodeToString(digest[:])+".json")
}

func leasePath(workspace string) string {
	path := statePath(workspace)
	return strings.TrimSuffix(path, filepath.Ext(path)) + ".pending.json"
}

func readStamp(workspace string) stamp {
	raw, err := os.ReadFile(statePath(workspace))
	if err != nil {
		return stamp{}
	}
	var value stamp
	if json.Unmarshal(raw, &value) != nil {
		return stamp{}
	}
	return value
}

func writeStamp(workspace string, value stamp) error {
	path := statePath(workspace)
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	raw, err := json.Marshal(value)
	if err != nil {
		return err
	}
	tmp, err := os.CreateTemp(filepath.Dir(path), ".kanboard-sync-*.tmp")
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
	return "", nil, errors.New("Python runtime for explicit Kanboard integration not found")
}

func env(name, fallback string) string {
	if value, ok := os.LookupEnv(name); ok {
		return value
	}
	return fallback
}
