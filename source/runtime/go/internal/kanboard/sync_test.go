package kanboard

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"sync"
	"testing"
	"time"
)

func TestUnconfiguredWorkspaceSkipsWithoutExternalProcess(t *testing.T) {
	t.Setenv("KANBOARD_PLAN_AUTOSYNC", "apply")
	result := MaybeSync(t.TempDir(), false)
	if result.Status != "skipped" {
		t.Fatalf("unexpected result: %#v", result)
	}
}

func TestQueuedSyncDoesNotWriteSuccessStamp(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("uses the POSIX true executable")
	}
	workspace, _ := configuredWorkspace(t)
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_HARNESS_EXECUTABLE", "/usr/bin/true")
	result := MaybeSync(workspace, false)
	if result.Status != "queued" {
		t.Fatalf("unexpected result: %#v", result)
	}
	if got := readStamp(workspace); got.Fingerprint != "" {
		t.Fatalf("queued sync wrote premature stamp: %#v", got)
	}
	second := MaybeSync(workspace, false)
	if second.Status != "pending" {
		t.Fatalf("duplicate event queued another worker: %#v", second)
	}
	if _, err := os.Stat(leasePath(workspace)); err != nil {
		t.Fatalf("queued sync did not retain pending lease: %v", err)
	}
}

func TestWorkerStampsOnlySuccessfulStableSync(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("uses POSIX true/false executables")
	}
	workspace, fingerprint := configuredWorkspace(t)
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_PYTHON", "/usr/bin/false")
	failedLease := mustAcquireLease(t, workspace, "apply", fingerprint)
	failed := RunWorker(workspace, "apply", fingerprint, failedLease.Token)
	if failed.Status != "error" {
		t.Fatalf("failed sync result: %#v", failed)
	}
	if got := readStamp(workspace); got.Fingerprint != "" {
		t.Fatalf("failed sync wrote stamp: %#v", got)
	}
	if _, err := os.Stat(leasePath(workspace)); !os.IsNotExist(err) {
		t.Fatalf("failed worker retained lease: %v", err)
	}

	t.Setenv("SKILL_SYSTEM_PYTHON", "/usr/bin/true")
	successLease := mustAcquireLease(t, workspace, "apply", fingerprint)
	succeeded := RunWorker(workspace, "apply", fingerprint, successLease.Token)
	if succeeded.Status != "synced" {
		t.Fatalf("successful sync result: %#v", succeeded)
	}
	if got := readStamp(workspace); got.Fingerprint != fingerprint || got.Mode != "apply" {
		t.Fatalf("successful sync stamp: %#v", got)
	}
}

func TestDryRunAliasReusesSuccessfulStamp(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("uses the POSIX true executable")
	}
	workspace, fingerprint := configuredWorkspace(t)
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	t.Setenv("SKILL_SYSTEM_PYTHON", "/usr/bin/true")
	lease := mustAcquireLease(t, workspace, "dry-run", fingerprint)
	result := RunWorker(workspace, "dry_run", fingerprint, lease.Token)
	if result.Status != "synced" {
		t.Fatalf("dry_run worker result: %#v", result)
	}
	t.Setenv("KANBOARD_PLAN_AUTOSYNC", "dry_run")
	if next := MaybeSync(workspace, false); next.Status != "unchanged" || next.Mode != "dry-run" {
		t.Fatalf("dry_run alias did not reuse stamp: %#v", next)
	}
}

func TestLeaseAcquisitionIsAtomicPerWorkspace(t *testing.T) {
	workspace, fingerprint := configuredWorkspace(t)
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	const contenders = 16
	start := make(chan struct{})
	results := make(chan pendingLease, contenders)
	errors := make(chan error, contenders)
	var wait sync.WaitGroup
	for index := 0; index < contenders; index++ {
		wait.Add(1)
		go func() {
			defer wait.Done()
			<-start
			lease, acquired, err := acquireLease(workspace, "apply", fingerprint)
			if err != nil {
				errors <- err
				return
			}
			if acquired {
				results <- lease
			}
		}()
	}
	close(start)
	wait.Wait()
	close(results)
	close(errors)
	for err := range errors {
		t.Fatalf("lease acquisition failed: %v", err)
	}
	var acquired []pendingLease
	for lease := range results {
		acquired = append(acquired, lease)
	}
	if len(acquired) != 1 {
		t.Fatalf("atomic lease winners=%d, want 1", len(acquired))
	}
	releaseLease(workspace, acquired[0].Token)
}

func TestExpiredLeaseCanBeReclaimed(t *testing.T) {
	workspace, fingerprint := configuredWorkspace(t)
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	stale := mustAcquireLease(t, workspace, "apply", fingerprint)
	stale.ExpiresAt = time.Now().UTC().Add(-time.Minute)
	raw, err := json.Marshal(stale)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(leasePath(workspace), append(raw, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
	replacement, acquired, err := acquireLease(workspace, "apply", fingerprint)
	if err != nil || !acquired {
		t.Fatalf("stale lease replacement acquired=%v err=%v", acquired, err)
	}
	if replacement.Token == stale.Token {
		t.Fatal("stale lease token was reused")
	}
	releaseLease(workspace, replacement.Token)
}

func TestWorkerCannotUseForeignLease(t *testing.T) {
	workspace, fingerprint := configuredWorkspace(t)
	t.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", t.TempDir())
	lease := mustAcquireLease(t, workspace, "apply", fingerprint)
	result := RunWorker(workspace, "apply", fingerprint, "foreign-token")
	if result.Status != "skipped" {
		t.Fatalf("foreign worker result: %#v", result)
	}
	if !ownsLease(workspace, lease.Token, "apply", fingerprint) {
		t.Fatal("foreign worker changed the owned lease")
	}
	releaseLease(workspace, lease.Token)
}

func mustAcquireLease(t *testing.T, workspace, mode, fingerprint string) pendingLease {
	t.Helper()
	lease, acquired, err := acquireLease(workspace, normalizeMode(mode), fingerprint)
	if err != nil || !acquired {
		t.Fatalf("lease acquired=%v err=%v", acquired, err)
	}
	return lease
}

func configuredWorkspace(t *testing.T) (string, string) {
	t.Helper()
	workspace := t.TempDir()
	if err := os.WriteFile(filepath.Join(workspace, ".kanboard-plan.yml"), []byte("workspace: test\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	integration := filepath.Join(t.TempDir(), "kanboard-plan-sync")
	if err := os.MkdirAll(filepath.Join(integration, "src", "kanboard_plan_sync"), 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("SKILL_SYSTEM_KANBOARD_SYNC_ROOT", integration)
	fingerprint, err := planFingerprint(workspace)
	if err != nil {
		t.Fatal(err)
	}
	return workspace, fingerprint
}

func TestPlanFingerprintChanges(t *testing.T) {
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "docs", "plan"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, ".kanboard-plan.yml"), []byte("workspace: test\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	plan := filepath.Join(root, "docs", "plan", "active.md")
	if err := os.WriteFile(plan, []byte("one\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	first, err := planFingerprint(root)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(plan, []byte("two two\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	second, err := planFingerprint(root)
	if err != nil {
		t.Fatal(err)
	}
	if first == second {
		t.Fatal("fingerprint did not change")
	}
}
