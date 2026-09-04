//go:build linux

package notify

import "os/exec"

func sendPlatform(message Message) Result {
	executable, err := exec.LookPath("notify-send")
	if err != nil {
		return Result{Status: "skipped", Platform: "linux", Method: "notify-send", Reason: "notify-send unavailable"}
	}
	command := exec.Command(executable, "-a", "Grok", message.Title, message.Body)
	if err := command.Start(); err != nil {
		return Result{Status: "error", Platform: "linux", Method: "notify-send", Reason: sanitize(err.Error(), 160)}
	}
	if err := command.Process.Release(); err != nil {
		return Result{Status: "error", Platform: "linux", Method: "notify-send", Reason: sanitize(err.Error(), 160)}
	}
	return Result{Status: "sent", Platform: "linux", Method: "notify-send"}
}
