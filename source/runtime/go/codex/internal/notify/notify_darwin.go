//go:build darwin

package notify

import (
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

func sendPlatform(message Message) Result {
	overlay := strings.TrimSpace(os.Getenv("SKILL_SYSTEM_NOTIFY_OVERLAY"))
	if overlay == "" {
		if executable, err := os.Executable(); err == nil {
			overlay = filepath.Join(filepath.Dir(executable), "skill-system-notify-overlay")
		}
	}
	if overlay == "" {
		return Result{Status: "error", Platform: "darwin", Method: "swift_overlay", Reason: "overlay path unavailable"}
	}
	if info, err := os.Stat(overlay); err != nil || info.IsDir() {
		return Result{Status: "error", Platform: "darwin", Method: "swift_overlay", Reason: "overlay binary unavailable"}
	}
	duration := 4.0
	if value, err := strconv.ParseFloat(strings.TrimSpace(env("SKILL_SYSTEM_NOTIFY_DURATION", "4")), 64); err == nil && value >= 0.5 && value <= 30 {
		duration = value
	}
	command := exec.Command(overlay, message.Title, message.Body, strconv.FormatFloat(duration, 'f', 1, 64), message.Topic, message.Metadata, message.SessionID)
	command.Dir = "/"
	if err := command.Start(); err != nil {
		return Result{Status: "error", Platform: "darwin", Method: "swift_overlay", Reason: sanitize(err.Error(), 160)}
	}
	if err := command.Process.Release(); err != nil {
		return Result{Status: "error", Platform: "darwin", Method: "swift_overlay", Reason: sanitize(err.Error(), 160)}
	}
	return Result{Status: "sent", Platform: "darwin", Method: "swift_overlay"}
}
