package main

import (
	"os"
	"os/exec"
	"testing"
	"time"
)

func TestUnknownArgumentDoesNotWaitForHookInput(t *testing.T) {
	if os.Getenv("SKILL_SYSTEM_GROK_MAIN_HELPER") == "1" {
		os.Args = []string{"skill-system-grok-harness", "--help"}
		main()
		return
	}

	command := exec.Command(os.Args[0], "-test.run=TestUnknownArgumentDoesNotWaitForHookInput")
	command.Env = append(os.Environ(), "SKILL_SYSTEM_GROK_MAIN_HELPER=1")
	if err := command.Start(); err != nil {
		t.Fatal(err)
	}
	done := make(chan error, 1)
	go func() { done <- command.Wait() }()
	select {
	case err := <-done:
		if err != nil {
			t.Fatalf("unknown argument exit: %v", err)
		}
	case <-time.After(2 * time.Second):
		_ = command.Process.Kill()
		t.Fatal("unknown argument waited for hook stdin")
	}
}
