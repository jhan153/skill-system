//go:build windows

package notify

import "os/exec"

func sendPlatform(message Message) Result {
	script := `Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $n = New-Object System.Windows.Forms.NotifyIcon; $n.Icon = [System.Drawing.SystemIcons]::Information; $n.BalloonTipTitle = $args[0]; $n.BalloonTipText = $args[1]; $n.Visible = $true; $n.ShowBalloonTip(4000); Start-Sleep -Milliseconds 4500; $n.Dispose()`
	command := exec.Command("powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script, message.Title, message.Body)
	if err := command.Start(); err != nil {
		return Result{Status: "error", Platform: "windows", Method: "powershell_notifyicon", Reason: sanitize(err.Error(), 160)}
	}
	if err := command.Process.Release(); err != nil {
		return Result{Status: "error", Platform: "windows", Method: "powershell_notifyicon", Reason: sanitize(err.Error(), 160)}
	}
	return Result{Status: "sent", Platform: "windows", Method: "powershell_notifyicon"}
}
