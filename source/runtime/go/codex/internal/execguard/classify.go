package execguard

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"unicode"
)

const (
	TargetWorkspace = "workspace"
	TargetCodexHome = "codex_home"
	TargetExternal  = "external"
)

type CommandPlan struct {
	Command          string
	CommandHash      string
	PurposeKey       string
	Families         []string
	Effects          []string
	TargetKinds      []string
	Paths            []string
	RewrittenCommand string
	InvalidReason    string
	TextAuthoring    bool
	BroadDanger      bool
}

func (plan CommandPlan) hasSideEffect() bool {
	for _, effect := range plan.Effects {
		if effect != EffectObserve {
			return true
		}
	}
	return false
}

func (plan CommandPlan) requiresExplicitPreflightGrant() bool {
	localGrantRequired := false
	for _, effect := range plan.Effects {
		switch effect {
		case EffectWorkspaceWrite, EffectProcessLaunch:
			localGrantRequired = true
		case EffectNetwork, EffectRuntimeWrite, EffectDelete, EffectPublish, EffectTerminate:
			return false
		}
	}
	return localGrantRequired
}

func (plan CommandPlan) changesWorkspaceGeneration() bool {
	for _, effect := range plan.Effects {
		if effect == EffectWorkspaceWrite || effect == EffectDelete {
			return true
		}
	}
	return false
}

type promptProjection struct {
	Grants        []string
	TargetHashes  []string
	Continuation  bool
	ResetAttempts bool
}

func compilePrompt(prompt, cwd string) promptProjection {
	text := strings.ToLower(strings.Join(strings.Fields(prompt), " "))
	var projection promptProjection
	projection.Continuation = continuationPrompt(text)
	projection.ResetAttempts = containsAny(text, "다시 시도", "재시도") || containsWordAny(text, "retry", "try again")
	if containsAny(text, "수정", "구현", "추가", "만들", "작성", "고쳐", "변경", "적용") ||
		containsWordAny(text, "fix", "implement", "change", "edit", "add", "create", "write", "apply") {
		projection.Grants = append(projection.Grants, GrantWorkspaceWrite)
	}
	if containsAny(text, "실행", "돌려", "구동", "재현", "디버그", "프로파일", "스모크", "먹통", "멈춤", "열어", "보여줘") ||
		containsWordAny(text, "run", "launch", "execute", "reproduce", "debug", "profile", "smoke", "hang", "stuck", "open the", "reveal") {
		projection.Grants = append(projection.Grants, GrantProcessLaunch)
	}
	if containsAny(text, "설치", "업데이트", "동기화", "다운로드", "받아", "가져와", "최신") ||
		containsWordAny(text, "install", "update", "sync", "download", "fetch", "pull", "upgrade") {
		projection.Grants = append(projection.Grants, GrantNetwork)
	}
	if containsAny(text, "업데이트", "동기화") || containsWordAny(text, "update", "sync", "pull", "upgrade") {
		projection.Grants = append(projection.Grants, GrantWorkspaceWrite)
	}
	if containsAny(text, "설치", "패키지", "의존성") || containsWordAny(text, "install", "package", "dependency", "brew") {
		projection.Grants = append(projection.Grants, GrantRuntimeWrite)
	}
	if containsAny(text, "삭제", "제거", "정리", "비워") || containsWordAny(text, "cleanup", "clean up", "remove", "delete", "prune") {
		projection.Grants = append(projection.Grants, GrantDelete)
	}
	if containsAny(text, "배포", "게시", "퍼블리시", "릴리스 배포") || containsWordAny(text, "push", "publish", "deploy") {
		projection.Grants = append(projection.Grants, GrantPublish, GrantNetwork)
	}
	if containsAny(text, "프로세스 종료", "프로세스를 종료", "죽여") || containsWordAny(text, "kill", "terminate process", "stop process") {
		projection.Grants = append(projection.Grants, GrantTerminate)
	}
	runtimeIntent := containsAny(text,
		"runtime companion", "런타임 컴패니언", "런타임 보조", "플러그인", "plugin",
		"codex home", "코덱스 홈", ".codex", "skill system 설치", "skill system 업데이트",
		"launchctl", "setenv", "환경 변수", "호스트 설정", "host setting", "environment variable",
	)
	if runtimeIntent && (containsAny(text, "설치", "업데이트", "동기화", "적용", "추가", "설정", "구성", "삭제", "제거") ||
		containsWordAny(text, "install", "update", "sync", "apply", "add", "configure", "manage", "remove", "delete", "set")) {
		projection.Grants = append(projection.Grants, GrantRuntimeWrite, GrantCodexHome, GrantNetwork)
	}
	for _, field := range strings.Fields(prompt) {
		candidate := strings.Trim(field, "\"'`()[]{}<>,.;:!?，。")
		if filepath.IsAbs(candidate) {
			projection.TargetHashes = append(projection.TargetHashes, digest(filepath.Clean(candidate)))
		}
	}
	if cwd != "" {
		projection.TargetHashes = append(projection.TargetHashes, digest(filepath.Clean(cwd)))
	}
	return projection
}

func analyzeTool(event Event) (CommandPlan, map[string]any, bool, error) {
	tool := strings.ToLower(strings.TrimSpace(event.ToolName))
	switch tool {
	case "bash", "exec_command":
		input, command, err := commandInput(event.ToolInput)
		if err != nil {
			return CommandPlan{}, nil, true, err
		}
		plan, err := classifyCommand(command, event.Cwd)
		return plan, input, true, err
	case "apply_patch", "edit", "write":
		input, command, err := commandInput(event.ToolInput)
		if err != nil {
			return CommandPlan{}, nil, true, err
		}
		plan := CommandPlan{
			Command:     command,
			CommandHash: digest(strings.TrimSpace(command)),
			Families:    []string{"apply_patch"},
			Effects:     []string{EffectWorkspaceWrite},
			TargetKinds: []string{TargetWorkspace},
		}
		plan.PurposeKey = purposeKey(plan)
		return plan, input, true, nil
	default:
		return CommandPlan{}, nil, false, nil
	}
}

func commandInput(raw json.RawMessage) (map[string]any, string, error) {
	if len(raw) == 0 {
		return nil, "", errors.New("missing tool_input")
	}
	var input map[string]any
	if err := json.Unmarshal(raw, &input); err != nil {
		return nil, "", err
	}
	command, ok := input["command"].(string)
	if !ok || strings.TrimSpace(command) == "" {
		return nil, "", errors.New("tool_input.command must be a non-empty string")
	}
	return input, command, nil
}

func classifyCommand(command, cwd string) (CommandPlan, error) {
	plan := CommandPlan{Command: command}
	parsed, err := parseShell(command)
	if err != nil {
		return plan, err
	}
	if script, wrapped, safe := unwrapShell(parsed); wrapped {
		if !safe {
			plan.InvalidReason = "The opaque explicit shell wrapper depends on quoting, expansion, redirection, options, or positional arguments that cannot be preserved by a direct rewrite. Use a direct command or a checked-in script."
			plan.CommandHash = digest(strings.TrimSpace(command))
			plan.PurposeKey = digest("invalid-shell-wrapper")
			return plan, nil
		}
		inner, innerErr := parseShell(script)
		if innerErr != nil {
			return plan, innerErr
		}
		parsed = inner
		plan.RewrittenCommand = strings.TrimSpace(script)
	}
	if len(parsed.Segments) == 0 {
		return plan, errors.New("empty command")
	}

	effects := map[string]bool{}
	families := map[string]bool{}
	targetKinds := map[string]bool{TargetWorkspace: true}
	paths := map[string]bool{}
	for _, segment := range parsed.Segments {
		facts := classifyInvocation(segment, cwd)
		if plan.InvalidReason == "" && facts.InvalidReason != "" {
			plan.InvalidReason = facts.InvalidReason
		}
		for _, effect := range facts.Effects {
			effects[effect] = true
		}
		families[facts.Family] = true
		for _, kind := range facts.TargetKinds {
			targetKinds[kind] = true
		}
		for _, path := range facts.Paths {
			paths[path] = true
		}
		plan.TextAuthoring = plan.TextAuthoring || facts.TextAuthoring
		plan.BroadDanger = plan.BroadDanger || facts.BroadDanger
	}
	for _, redirect := range parsed.Redirects {
		kind, path := classifyPath(redirect.Target, cwd)
		if path != "" {
			targetKinds[kind] = true
			paths[path] = true
		}
		if redirect.Output && !isDeviceSink(redirect.Target) {
			if redirect.WriterLike {
				effects[EffectWorkspaceWrite] = true
				plan.TextAuthoring = true
			} else if !effects[EffectObserve] && !effects[EffectBuildTest] {
				effects[EffectWorkspaceWrite] = true
			}
		}
	}
	if parsed.HasExpansion && plan.RewrittenCommand != "" {
		plan.InvalidReason = "The shell wrapper contains expansion that cannot be safely normalized."
	}
	plan.Effects = sortedSet(effects)
	plan.Families = sortedSet(families)
	plan.TargetKinds = sortedSet(targetKinds)
	plan.Paths = sortedSet(paths)
	canonical := strings.TrimSpace(command)
	if plan.RewrittenCommand != "" {
		canonical = plan.RewrittenCommand
	}
	plan.CommandHash = digest(canonical)
	plan.PurposeKey = purposeKey(plan)
	return plan, nil
}

func purposeKey(plan CommandPlan) string {
	return digest(strings.Join(plan.Effects, ",") + "|" + strings.Join(plan.TargetKinds, ",") + "|" + strings.Join(plan.Families, ","))
}

type invocationFacts struct {
	Family        string
	Effects       []string
	TargetKinds   []string
	Paths         []string
	InvalidReason string
	TextAuthoring bool
	BroadDanger   bool
}

const opaqueEvaluatorReason = "Opaque shell or inline interpreter evaluation is not admitted. Invoke one direct executable or an existing auditable script."

func classifyInvocation(tokens []string, cwd string) invocationFacts {
	if len(tokens) == 0 {
		return invocationFacts{Family: "empty", Effects: []string{EffectObserve}}
	}
	index := commandIndex(tokens)
	if index >= len(tokens) {
		return invocationFacts{Family: "environment", Effects: []string{EffectObserve}}
	}
	executable := strings.ToLower(filepath.Base(tokens[index]))
	args := tokens[index+1:]
	facts := invocationFacts{Family: executable, TargetKinds: []string{TargetWorkspace}}
	if opaqueInterpreterEvaluation(executable, args) {
		facts.Family = "opaque_" + normalizedExecutable(executable)
		facts.Effects = []string{EffectProcessLaunch}
		facts.InvalidReason = opaqueEvaluatorReason
		return facts
	}
	for _, arg := range args {
		kind, path := classifyPath(arg, cwd)
		if path != "" {
			facts.TargetKinds = append(facts.TargetKinds, kind)
			facts.Paths = append(facts.Paths, path)
		}
	}

	switch executable {
	case "rg", "grep", "ls", "pwd", "cat", "head", "tail", "wc", "stat", "file", "shasum", "md5", "which", "ps", "pgrep", "lsof", "sample":
		facts.Effects = []string{EffectObserve}
	case "sed":
		if hasAnyArg(args, "-i", "--in-place") {
			facts.Effects = []string{EffectWorkspaceWrite}
			facts.TextAuthoring = true
		} else {
			facts.Effects = []string{EffectObserve}
		}
	case "perl":
		if hasArgPrefix(args, "-i") || hasArgPrefix(args, "-pi") {
			facts.Effects = []string{EffectWorkspaceWrite}
			facts.TextAuthoring = true
		} else {
			facts.Effects = []string{EffectProcessLaunch}
		}
	case "tee", "touch", "truncate":
		facts.Effects = []string{EffectWorkspaceWrite}
		facts.TextAuthoring = true
	case "echo", "printf":
		facts.Effects = []string{EffectObserve}
	case "find":
		if hasAnyArg(args, "-delete") {
			facts.Effects = []string{EffectDelete}
		} else if nested := findExecCommand(args); nested != "" {
			facts.Family = "find_exec_" + nested
			if nested == "sh" || nested == "bash" || nested == "zsh" {
				facts.InvalidReason = "find -exec may not launch an opaque shell evaluator; use a direct find action or checked-in script."
				facts.Effects = []string{EffectProcessLaunch}
			} else if nested == "rm" {
				facts.Effects = []string{EffectDelete}
			} else {
				facts.Effects = []string{EffectProcessLaunch}
			}
		} else {
			facts.Effects = []string{EffectObserve}
		}
	case "git":
		return mergeTargets(classifyGit(args), facts)
	case "cmake", "ctest", "make", "ninja", "xcodebuild", "mmdc":
		facts.Effects = []string{EffectBuildTest}
	case "go":
		return mergeTargets(classifyGo(args), facts)
	case "cargo":
		return mergeTargets(classifyCargo(args), facts)
	case "npm", "pnpm", "yarn", "bun":
		return mergeTargets(classifyPackageManager(executable, args), facts)
	case "python", "python3", "ruby", "node":
		if len(args) == 0 || args[0] == "-" {
			facts.Effects = []string{EffectProcessLaunch}
			facts.TextAuthoring = true
		} else if executable != "node" && len(args) >= 3 && args[0] == "-m" && args[1] == "pip" && args[2] == "install" {
			facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
			facts.Family = "package_install"
		} else if executable != "node" && len(args) >= 2 && args[0] == "-m" && scriptLooksLikeBuildTest(args[1]) {
			facts.Effects = []string{EffectBuildTest}
		} else if scriptLooksLikeBuildTest(args[0]) {
			facts.Effects = []string{EffectBuildTest}
		} else {
			facts.Effects = []string{EffectProcessLaunch}
		}
	case "uv":
		if len(args) >= 2 && args[0] == "pip" && args[1] == "install" {
			facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
			facts.Family = "package_install"
		} else {
			facts.Effects = []string{EffectProcessLaunch}
		}
	case "brew":
		if len(args) > 0 && (args[0] == "install" || args[0] == "upgrade") {
			facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
		} else {
			facts.Effects = []string{EffectObserve}
		}
	case "curl", "wget":
		facts.Effects = []string{EffectNetwork}
	case "rsync", "cp", "mv", "install":
		facts.Effects = []string{EffectWorkspaceWrite}
		if containsTarget(facts.TargetKinds, TargetCodexHome) || containsTarget(facts.TargetKinds, TargetExternal) {
			facts.Effects = []string{EffectRuntimeWrite}
		}
	case "mkdir":
		facts.Effects = []string{EffectWorkspaceWrite}
	case "rm":
		facts.Effects = []string{EffectDelete}
		facts.BroadDanger = broadRemoval(args)
	case "kill", "pkill":
		facts.Effects = []string{EffectTerminate}
	case "lldb":
		facts.Effects = []string{EffectProcessLaunch}
	case "launchctl":
		facts.Effects = []string{EffectRuntimeWrite}
	case "open":
		facts.Effects = []string{EffectProcessLaunch}
	case "sh", "bash", "zsh":
		facts.Effects = []string{EffectProcessLaunch}
		if len(args) == 0 {
			facts.InvalidReason = "Interactive shells are not admitted because later write_stdin input bypasses PreToolUse. Use a direct command or checked-in script."
		} else if shellEvalFlagIndex(args) >= 0 {
			facts.InvalidReason = opaqueEvaluatorReason
		}
	case "codex", "claude":
		if len(args) > 0 && (args[0] == "plugin" || args[0] == "mcp" || args[0] == "app-server") {
			facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
		} else {
			facts.Effects = []string{EffectProcessLaunch}
		}
	case "log":
		facts.Effects = []string{EffectObserve}
	default:
		facts.Effects = []string{EffectProcessLaunch}
		if filepath.IsAbs(tokens[index]) {
			kind, path := classifyPath(tokens[index], cwd)
			if path != "" {
				facts.TargetKinds = append(facts.TargetKinds, kind)
				facts.Paths = append(facts.Paths, path)
			}
		}
	}
	return facts
}

func classifyGit(args []string) invocationFacts {
	subcommand, rest := gitSubcommand(args)
	facts := invocationFacts{Family: "git_" + subcommand, TargetKinds: []string{TargetWorkspace}}
	switch subcommand {
	case "status", "diff", "log", "show", "merge-tree", "rev-parse", "ls-files", "remote":
		facts.Effects = []string{EffectObserve}
	case "fetch", "ls-remote":
		facts.Effects = []string{EffectNetwork}
	case "pull", "clone", "submodule":
		facts.Effects = []string{EffectNetwork, EffectWorkspaceWrite}
	case "push":
		facts.Effects = []string{EffectNetwork, EffectPublish}
	case "clean":
		facts.Effects = []string{EffectDelete}
		facts.BroadDanger = true
	case "reset":
		facts.Effects = []string{EffectWorkspaceWrite}
		if hasAnyArg(rest, "--hard") {
			facts.Effects = []string{EffectDelete}
			facts.BroadDanger = true
		}
	case "branch":
		facts.Effects = []string{EffectObserve}
		if hasAnyArg(rest, "-D", "-d", "-f", "-m") {
			facts.Effects = []string{EffectWorkspaceWrite, EffectDelete}
		}
	case "rebase":
		facts.Effects = []string{EffectWorkspaceWrite, EffectDelete}
	case "add", "apply", "commit", "switch", "checkout", "restore", "merge", "worktree":
		facts.Effects = []string{EffectWorkspaceWrite}
	default:
		facts.Effects = []string{EffectProcessLaunch}
	}
	return facts
}

func gitSubcommand(args []string) (string, []string) {
	for index := 0; index < len(args); index++ {
		arg := args[index]
		if (arg == "-C" || arg == "-c" || arg == "--git-dir" || arg == "--work-tree") && index+1 < len(args) {
			index++
			continue
		}
		if strings.HasPrefix(arg, "-") {
			continue
		}
		return strings.ToLower(arg), args[index+1:]
	}
	return "", nil
}

func classifyGo(args []string) invocationFacts {
	facts := invocationFacts{Family: "go", TargetKinds: []string{TargetWorkspace}}
	if len(args) == 0 {
		facts.Effects = []string{EffectObserve}
		return facts
	}
	facts.Family = "go_" + args[0]
	switch args[0] {
	case "test", "build", "vet", "list", "env", "version":
		facts.Effects = []string{EffectBuildTest}
	case "get", "install":
		facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
	default:
		facts.Effects = []string{EffectProcessLaunch}
	}
	return facts
}

func classifyCargo(args []string) invocationFacts {
	facts := invocationFacts{Family: "cargo", TargetKinds: []string{TargetWorkspace}}
	if len(args) == 0 {
		facts.Effects = []string{EffectObserve}
		return facts
	}
	facts.Family = "cargo_" + args[0]
	switch args[0] {
	case "test", "build", "check", "clippy", "fmt":
		facts.Effects = []string{EffectBuildTest}
	case "add", "install", "update":
		facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
	default:
		facts.Effects = []string{EffectProcessLaunch}
	}
	return facts
}

func classifyPackageManager(name string, args []string) invocationFacts {
	facts := invocationFacts{Family: name, TargetKinds: []string{TargetWorkspace}}
	if len(args) == 0 {
		facts.Effects = []string{EffectObserve}
		return facts
	}
	facts.Family = name + "_" + args[0]
	switch args[0] {
	case "test", "run", "check", "build", "lint":
		facts.Effects = []string{EffectBuildTest}
	case "install", "i", "add", "update", "upgrade":
		facts.Effects = []string{EffectNetwork, EffectRuntimeWrite}
	default:
		facts.Effects = []string{EffectProcessLaunch}
	}
	return facts
}

func mergeTargets(classified, targets invocationFacts) invocationFacts {
	classified.TargetKinds = append(classified.TargetKinds, targets.TargetKinds...)
	classified.Paths = append(classified.Paths, targets.Paths...)
	return classified
}

func commandIndex(tokens []string) int {
	index := 0
	if len(tokens) > 0 && strings.EqualFold(filepath.Base(tokens[0]), "env") {
		index++
		for index < len(tokens) && (strings.HasPrefix(tokens[index], "-") || isAssignment(tokens[index])) {
			index++
		}
	}
	for index < len(tokens) && isAssignment(tokens[index]) {
		index++
	}
	return index
}

func normalizedExecutable(value string) string {
	return strings.TrimSuffix(strings.ToLower(filepath.Base(value)), ".exe")
}

func opaqueInterpreterEvaluation(executable string, args []string) bool {
	name := normalizedExecutable(executable)
	switch {
	case isVersionedExecutable(name, "python"), isVersionedExecutable(name, "pythonw"), name == "py":
		return pythonInlineEvaluation(args)
	case isVersionedExecutable(name, "node"):
		return hasInlineEvaluation(args, []string{"-e", "--eval", "-p", "--print"}, "", nil, []string{"-r", "--require", "--loader", "--import"})
	case isVersionedExecutable(name, "ruby"):
		return hasInlineEvaluation(args, []string{"-e"}, "e", nil, []string{"-i", "-r"})
	case isVersionedExecutable(name, "perl"):
		return hasInlineEvaluation(args, []string{"-e", "-E"}, "eE", nil, []string{"-f", "-i"})
	case name == "osascript":
		return hasInlineEvaluation(args, []string{"-e"}, "", nil, []string{"-l"})
	case name == "powershell" || name == "pwsh":
		return hasInlineEvaluation(args, []string{"-c", "-command", "-encodedcommand"}, "", []string{"-file"}, nil)
	case name == "php":
		return hasInlineEvaluation(args, []string{"-r"}, "", []string{"-f"}, nil)
	case name == "rscript" || name == "lua":
		return hasInlineEvaluation(args, []string{"-e"}, "", nil, nil)
	case name == "deno":
		return len(args) > 0 && strings.EqualFold(args[0], "eval")
	case name == "bun":
		return hasInlineEvaluation(args, []string{"-e", "--eval", "-p", "--print"}, "", nil, nil)
	default:
		return false
	}
}

func pythonInlineEvaluation(args []string) bool {
	if len(args) == 0 || args[0] == "-" {
		return true
	}
	for index := 0; index < len(args); index++ {
		arg := args[index]
		if arg == "-c" {
			return true
		}
		if arg == "--" || arg == "-m" {
			return false
		}
		if arg == "-W" || arg == "-X" || arg == "--check-hash-based-pycs" {
			index++
			continue
		}
		if !strings.HasPrefix(arg, "-") {
			return false
		}
	}
	return false
}

func isVersionedExecutable(name, prefix string) bool {
	if name == prefix {
		return true
	}
	suffix := strings.TrimPrefix(name, prefix)
	if suffix == name || suffix == "" {
		return false
	}
	for _, character := range suffix {
		if (character < '0' || character > '9') && character != '.' {
			return false
		}
	}
	return true
}

func hasInlineEvaluation(args, evalOptions []string, shortEvalFlags string, stopOptions, valueOptions []string) bool {
	if len(args) == 0 || args[0] == "-" {
		return true
	}
	evalSet := lowerStringSet(evalOptions)
	stopSet := lowerStringSet(stopOptions)
	valueSet := lowerStringSet(valueOptions)
	for index := 0; index < len(args); index++ {
		arg := strings.ToLower(args[index])
		if evalSet[arg] || hasOptionAssignment(arg, evalSet) {
			return true
		}
		if shortEvalFlags != "" && strings.HasPrefix(arg, "-") && !strings.HasPrefix(arg, "--") {
			for _, flag := range shortEvalFlags {
				if strings.ContainsRune(strings.TrimPrefix(arg, "-"), flag) {
					return true
				}
			}
		}
		if arg == "--" || stopSet[arg] {
			return false
		}
		if valueSet[arg] {
			index++
			continue
		}
		if !strings.HasPrefix(arg, "-") {
			return false
		}
	}
	return false
}

func lowerStringSet(values []string) map[string]bool {
	result := make(map[string]bool, len(values))
	for _, value := range values {
		result[strings.ToLower(value)] = true
	}
	return result
}

func hasOptionAssignment(arg string, options map[string]bool) bool {
	if index := strings.IndexByte(arg, '='); index > 0 {
		return options[arg[:index]]
	}
	return false
}

func shellEvalFlagIndex(args []string) int {
	for index := 0; index < len(args); index++ {
		arg := args[index]
		if arg == "--" {
			return -1
		}
		if arg == "-o" || arg == "+o" || arg == "-O" || arg == "+O" {
			index++
			continue
		}
		if !strings.HasPrefix(arg, "-") && !strings.HasPrefix(arg, "+") {
			return -1
		}
		if !strings.HasPrefix(arg, "--") && strings.ContainsRune(strings.TrimLeft(arg, "-+"), 'c') {
			return index
		}
	}
	return -1
}

func isAssignment(value string) bool {
	index := strings.IndexByte(value, '=')
	return index > 0 && !strings.ContainsAny(value[:index], "/\\")
}

func scriptLooksLikeBuildTest(value string) bool {
	base := strings.ToLower(filepath.Base(value))
	for _, marker := range []string{"test", "verify", "check", "generate", "build", "lint", "format", "render"} {
		if strings.Contains(base, marker) {
			return true
		}
	}
	return false
}

func hasAnyArg(args []string, values ...string) bool {
	set := stringSet(values)
	for _, arg := range args {
		if set[arg] {
			return true
		}
	}
	return false
}

func hasArgPrefix(args []string, prefix string) bool {
	for _, arg := range args {
		if strings.HasPrefix(arg, prefix) {
			return true
		}
	}
	return false
}

func findExecCommand(args []string) string {
	for index, arg := range args {
		if arg != "-exec" && arg != "-execdir" && arg != "-ok" && arg != "-okdir" {
			continue
		}
		if index+1 < len(args) {
			return strings.ToLower(filepath.Base(args[index+1]))
		}
	}
	return ""
}

func containsTarget(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

func broadRemoval(args []string) bool {
	for _, arg := range args {
		cleaned := filepath.Clean(strings.TrimSpace(arg))
		if cleaned == "/" || cleaned == "." || cleaned == ".." || cleaned == "~" || cleaned == "$HOME" {
			return true
		}
	}
	return false
}

func isDeviceSink(value string) bool {
	cleaned := filepath.Clean(strings.TrimSpace(value))
	return cleaned == "/dev/stdout" || cleaned == "/dev/stderr" || cleaned == "/dev/null"
}

func classifyPath(value, cwd string) (string, string) {
	value = strings.TrimSpace(value)
	if value == "" || value == "-" || strings.HasPrefix(value, "-") || strings.Contains(value, "://") {
		return "", ""
	}
	if _, err := strconv.Atoi(value); err == nil {
		return "", ""
	}
	looksLikePath := filepath.IsAbs(value) || strings.HasPrefix(value, "~") || strings.HasPrefix(value, ".") || strings.ContainsAny(value, "/\\")
	if !looksLikePath {
		return "", ""
	}
	if strings.HasPrefix(value, "~") {
		home, err := os.UserHomeDir()
		if err == nil {
			value = filepath.Join(home, strings.TrimPrefix(strings.TrimPrefix(value, "~"), string(filepath.Separator)))
		}
	}
	if !filepath.IsAbs(value) {
		value = filepath.Join(cwd, value)
	}
	path := filepath.Clean(value)
	if path == "/dev/stdout" || path == "/dev/stderr" || path == "/dev/null" {
		return "", ""
	}
	root := workspaceRoot(cwd)
	if within(root, path) {
		return TargetWorkspace, path
	}
	if codexHome := resolvedCodexHome(); codexHome != "" && within(codexHome, path) {
		return TargetCodexHome, path
	}
	return TargetExternal, path
}

func workspaceRoot(cwd string) string {
	current := filepath.Clean(cwd)
	for current != "" {
		if _, err := os.Stat(filepath.Join(current, ".git")); err == nil {
			return current
		}
		parent := filepath.Dir(current)
		if parent == current {
			break
		}
		current = parent
	}
	return filepath.Clean(cwd)
}

func resolvedCodexHome() string {
	if value := strings.TrimSpace(os.Getenv("CODEX_HOME")); value != "" {
		return filepath.Clean(value)
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}
	return filepath.Join(home, ".codex")
}

func within(root, path string) bool {
	if root == "" || path == "" {
		return false
	}
	relative, err := filepath.Rel(filepath.Clean(root), filepath.Clean(path))
	if err != nil {
		return false
	}
	return relative == "." || (relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator)))
}

type shellParse struct {
	Segments     [][]string
	Operators    []string
	Redirects    []shellRedirect
	HasExpansion bool
}

type shellRedirect struct {
	Operator   string
	Target     string
	Output     bool
	WriterLike bool
}

func parseShell(command string) (shellParse, error) {
	var result shellParse
	var segment []string
	var token strings.Builder
	var quote rune
	escaped := false
	pendingRedirect := ""
	writerLike := false
	runes := []rune(command)

	finishToken := func() {
		if token.Len() == 0 {
			return
		}
		value := token.String()
		token.Reset()
		if pendingRedirect != "" {
			result.Redirects = append(result.Redirects, shellRedirect{
				Operator:   pendingRedirect,
				Target:     value,
				Output:     strings.Contains(pendingRedirect, ">"),
				WriterLike: writerLike,
			})
			pendingRedirect = ""
			return
		}
		segment = append(segment, value)
		if len(segment) == 1 {
			name := strings.ToLower(filepath.Base(value))
			writerLike = name == "echo" || name == "printf" || name == "cat" || name == "sed" || name == "awk" || name == "perl" || name == "python" || name == "python3" || name == "node"
		}
	}
	finishSegment := func(operator string) {
		finishToken()
		if pendingRedirect != "" {
			return
		}
		if len(segment) > 0 {
			result.Segments = append(result.Segments, segment)
			segment = nil
			writerLike = false
		}
		if operator != "" {
			result.Operators = append(result.Operators, operator)
		}
	}

	for index := 0; index < len(runes); index++ {
		current := runes[index]
		if escaped {
			token.WriteRune(current)
			escaped = false
			continue
		}
		if current == '\\' && quote != '\'' {
			escaped = true
			continue
		}
		if quote != 0 {
			if current == quote {
				quote = 0
				continue
			}
			if quote == '"' && (current == '$' || current == '`') {
				result.HasExpansion = true
			}
			token.WriteRune(current)
			continue
		}
		if current == '\'' || current == '"' {
			quote = current
			continue
		}
		if unicode.IsSpace(current) {
			if current == '\n' {
				finishSegment(";")
			} else {
				finishToken()
			}
			continue
		}
		if current == '$' || current == '`' || current == '*' || current == '?' {
			result.HasExpansion = true
			token.WriteRune(current)
			continue
		}
		if current == ';' || current == '|' || current == '&' {
			operator := string(current)
			if index+1 < len(runes) && runes[index+1] == current && (current == '|' || current == '&') {
				operator += string(current)
				index++
			}
			finishSegment(operator)
			continue
		}
		if current == '<' || current == '>' {
			finishToken()
			pendingRedirect = string(current)
			if index+1 < len(runes) && runes[index+1] == current {
				pendingRedirect += string(current)
				index++
			}
			continue
		}
		token.WriteRune(current)
	}
	if escaped || quote != 0 {
		return result, errors.New("unterminated shell quote or escape")
	}
	finishSegment("")
	if pendingRedirect != "" {
		return result, errors.New("redirection has no target")
	}
	return result, nil
}

func unwrapShell(parsed shellParse) (script string, wrapped, safe bool) {
	if len(parsed.Segments) != 1 || len(parsed.Operators) != 0 || len(parsed.Redirects) != 0 {
		return "", false, false
	}
	tokens := parsed.Segments[0]
	index := commandIndex(tokens)
	if index >= len(tokens) {
		return "", false, false
	}
	name := strings.ToLower(filepath.Base(tokens[index]))
	if name != "sh" && name != "bash" && name != "zsh" {
		return "", false, false
	}
	args := tokens[index+1:]
	evalIndex := shellEvalFlagIndex(args)
	if evalIndex < 0 {
		return "", false, false
	}
	if evalIndex != 0 || (args[0] != "-c" && args[0] != "-lc") || len(args) != 2 {
		return "", true, false
	}
	script = args[1]
	inner, err := parseShell(script)
	if err != nil || inner.HasExpansion || len(inner.Redirects) != 0 || len(inner.Segments) == 0 {
		return script, true, false
	}
	return script, true, true
}

func sortedSet(values map[string]bool) []string {
	result := make([]string, 0, len(values))
	for value, included := range values {
		if included && value != "" {
			result = append(result, value)
		}
	}
	sort.Strings(result)
	return result
}

func containsAny(text string, values ...string) bool {
	for _, value := range values {
		if strings.Contains(text, value) {
			return true
		}
	}
	return false
}

func continuationPrompt(text string) bool {
	for _, exact := range []string{
		"계속", "계속해", "계속 진행해", "진행해", "그대로 계속해", "그거 해봐", "그대로 해",
		"ㅇㅇ", "그래", "좋아", "continue", "go ahead", "proceed", "do it",
	} {
		if text == exact {
			return true
		}
	}
	return strings.HasPrefix(text, "continue other authorized work") ||
		strings.Contains(text, "defer the blocked action without retrying") ||
		strings.HasPrefix(text, "a user correction is pending")
}

func containsWordAny(text string, values ...string) bool {
	normalized := " " + strings.Join(strings.FieldsFunc(text, func(value rune) bool {
		return !unicode.IsLetter(value) && !unicode.IsDigit(value)
	}), " ") + " "
	for _, value := range values {
		term := strings.Join(strings.FieldsFunc(strings.ToLower(value), func(character rune) bool {
			return !unicode.IsLetter(character) && !unicode.IsDigit(character)
		}), " ")
		if term != "" && strings.Contains(normalized, " "+term+" ") {
			return true
		}
	}
	return false
}
