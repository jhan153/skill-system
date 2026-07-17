//go:build !darwin && !windows

package notify

func sendPlatform(message Message) Result {
	return Result{Status: "skipped", Platform: "unsupported", Reason: "unsupported platform"}
}
