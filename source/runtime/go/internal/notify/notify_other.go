//go:build !darwin && !windows && !linux

package notify

func sendPlatform(message Message) Result {
	return Result{Status: "skipped", Platform: "unsupported", Reason: "unsupported platform"}
}
