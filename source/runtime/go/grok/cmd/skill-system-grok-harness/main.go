package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"

	"skill-system.local/harness/grok/internal/hook"
	"skill-system.local/harness/grok/internal/projectcontext"
)

var version = "dev"

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		hookCLI()
		return
	}
	switch args[0] {
	case "--version", "version":
		fmt.Println(version)
	case "context":
		contextCLI(args[1:])
	}
}

func hookCLI() {
	decoder := json.NewDecoder(io.LimitReader(os.Stdin, 1<<20))
	var event hook.Event
	if err := decoder.Decode(&event); err != nil {
		return
	}
	output := hook.Handle(event)
	if output == nil {
		return
	}
	_ = json.NewEncoder(os.Stdout).Encode(output)
}

func contextCLI(args []string) {
	if len(args) == 0 || args[0] != "resolve" {
		fmt.Fprintln(os.Stderr, "usage: skill-system-grok-harness context resolve [--start PATH] [--manifest PATH]")
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
