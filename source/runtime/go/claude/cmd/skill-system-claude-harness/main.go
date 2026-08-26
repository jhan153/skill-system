package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"skill-system.local/harness/claude/internal/claudehook"
	"skill-system.local/harness/claude/internal/projectcontext"
)

var version = "dev"

func main() {
	configureStateRoot()
	if len(os.Args) > 1 {
		switch os.Args[1] {
		case "--version", "version":
			fmt.Println(version)
			return
		case "context":
			contextCLI(os.Args[2:])
			return
		}
	}
	hookCLI()
}

func configureStateRoot() {
	if strings.TrimSpace(os.Getenv("SKILL_SYSTEM_HARNESS_STATE_DIR")) != "" {
		return
	}
	root := strings.TrimSpace(os.Getenv("CLAUDE_CONFIG_DIR"))
	if root == "" {
		if home, err := os.UserHomeDir(); err == nil {
			root = filepath.Join(home, ".claude")
		}
	}
	if root != "" {
		_ = os.Setenv("SKILL_SYSTEM_HARNESS_STATE_DIR", filepath.Join(root, "harness"))
	}
}

func hookCLI() {
	decoder := json.NewDecoder(io.LimitReader(os.Stdin, 1<<20))
	var event claudehook.Event
	if err := decoder.Decode(&event); err != nil {
		return
	}
	output := claudehook.Handle(event)
	if output == nil {
		return
	}
	_ = json.NewEncoder(os.Stdout).Encode(output)
}

func contextCLI(args []string) {
	if len(args) == 0 || args[0] != "resolve" {
		fmt.Fprintln(os.Stderr, "usage: skill-system-claude-harness context resolve [--start PATH] [--manifest PATH]")
		return
	}
	set := flag.NewFlagSet("context resolve", flag.ContinueOnError)
	set.SetOutput(io.Discard)
	start := set.String("start", "", "working path")
	manifest := set.String("manifest", "", "exact manifest path")
	if set.Parse(args[1:]) != nil {
		return
	}
	result, err := projectcontext.Resolve(*start, *manifest)
	if err != nil {
		_ = json.NewEncoder(os.Stdout).Encode(map[string]any{"status": "error", "reason": err.Error()})
		return
	}
	_ = json.NewEncoder(os.Stdout).Encode(result)
}
