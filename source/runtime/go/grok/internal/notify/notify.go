package notify

import (
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
)

type Message struct {
	Event   string `json:"event"`
	Topic   string `json:"topic"`
	Title   string `json:"title"`
	Body    string `json:"message"`
	Model   string `json:"model,omitempty"`
	Session string `json:"session,omitempty"`
}

type Result struct {
	Status   string `json:"status"`
	Platform string `json:"platform"`
	Method   string `json:"method,omitempty"`
	Reason   string `json:"reason,omitempty"`
}

var (
	markdownLink  = regexp.MustCompile(`\[([^]]+)\]\([^)]+\)`)
	sensitiveWord = regexp.MustCompile(`(?i)\b(api[_-]?key|authorization|bearer|cookie|password|passwd|secret|token|client[_-]?secret|database[_-]?url)\b`)
	secretValue   = regexp.MustCompile(`(?i)sk-[A-Za-z0-9_-]{12,}|[A-Za-z0-9_+/=-]{32,}`)
	bareURL       = regexp.MustCompile(`(?i)https?://[^\s)\]}>]+`)
	quotedPosix   = regexp.MustCompile(`(?:"/[^"]+"|'\/[^']+')`)
	quotedWindows = regexp.MustCompile(`(?i)(?:"(?:[a-z]:\\|\\\\)[^"]+"|'(?:[a-z]:\\|\\\\)[^']+')`)
	posixPath     = regexp.MustCompile(`(^|[^A-Za-z0-9._~+-])\/[^\s)\]}>,'\"]+`)
	windowsPath   = regexp.MustCompile(`(?i)(?:[a-z]:\\|\\\\)[^\s)\]}>,'\"]+`)
)

func Send(message Message) Result {
	mode := strings.ToLower(strings.TrimSpace(env("SKILL_SYSTEM_DESKTOP_NOTIFY", "on")))
	if mode == "0" || mode == "false" || mode == "off" || mode == "disabled" || mode == "none" {
		return Result{Status: "disabled", Platform: runtime.GOOS}
	}
	message.Title = sanitize(message.Title, 100)
	message.Body = sanitize(message.Body, 240)
	if message.Model != "" || message.Session != "" {
		segments := make([]string, 0, 3)
		for _, value := range []string{message.Topic, message.Model, message.Session} {
			if cleaned := sanitize(value, 24); cleaned != "" {
				segments = append(segments, "["+cleaned+"]")
			}
		}
		if len(segments) > 0 {
			message.Title = strings.Join(segments, "-")
		}
	}
	if mode == "dry-run" || mode == "dry_run" || mode == "test" {
		return Result{Status: "dry_run", Platform: runtime.GOOS, Method: "none"}
	}
	return sendPlatform(message)
}

func SafeText(value string) string {
	return sanitize(value, 240)
}

func SafePath(value string) string {
	value = strings.TrimSpace(value)
	if value == "" {
		return ""
	}
	path := filepath.Clean(value)
	if !filepath.IsAbs(path) {
		return sanitize(path, 120)
	}
	root := strings.TrimSpace(os.Getenv("CODEX_HOME"))
	if root == "" {
		if home, err := os.UserHomeDir(); err == nil {
			root = filepath.Join(home, ".codex")
		}
	}
	if root != "" {
		if relative, err := filepath.Rel(filepath.Clean(root), path); err == nil && relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
			return sanitize(filepath.ToSlash(relative), 120)
		}
	}
	return "<external-path>"
}

func sanitize(value string, limit int) string {
	value = markdownLink.ReplaceAllString(value, "$1")
	for _, token := range []string{"**", "__", "~~", "`", "*"} {
		value = strings.ReplaceAll(value, token, "")
	}
	value = bareURL.ReplaceAllString(value, "<url>")
	value = quotedPosix.ReplaceAllString(value, "<path>")
	value = quotedWindows.ReplaceAllString(value, "<path>")
	value = posixPath.ReplaceAllString(value, "$1<path>")
	value = windowsPath.ReplaceAllString(value, "<path>")
	value = secretValue.ReplaceAllString(value, "<redacted>")
	if sensitiveWord.MatchString(value) {
		value = "<redacted-sensitive>"
	}
	value = strings.Join(strings.Fields(value), " ")
	runes := []rune(value)
	if len(runes) <= limit {
		return value
	}
	if limit < 4 {
		return string(runes[:limit])
	}
	return strings.TrimSpace(string(runes[:limit-3])) + "..."
}
