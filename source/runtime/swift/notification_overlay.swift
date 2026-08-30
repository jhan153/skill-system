import Cocoa
import Dispatch

let rawTitle = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Codex notification"
let message = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "Permission needed."
let duration = CommandLine.arguments.count > 3 ? Double(CommandLine.arguments[3]) ?? 4.0 : 4.0
let topic = CommandLine.arguments.count > 4 ? CommandLine.arguments[4] : ""
let passedMetadata = CommandLine.arguments.count > 5 ? CommandLine.arguments[5] : ""
let passedSessionID = CommandLine.arguments.count > 6 ? CommandLine.arguments[6] : ""

struct LegacyTitle {
    let topic: String
    let context: String
    let model: String
}

struct SessionMetadata {
    let sessionName: String
    let model: String
    let effort: String
    let threadSource: String
    let agentPath: String
    let hasParent: Bool
    let hasChildren: Bool
}

func statusTitle(_ topic: String) -> String {
    switch topic {
    case "done": return "Codex task complete"
    case "input": return "Codex input needed"
    case "approval": return "Codex approval requested"
    case "error": return "Codex task failed"
    default: return "Codex notification"
    }
}

func normalizedLegacyTitle(_ value: String) -> LegacyTitle? {
    guard value.hasPrefix("["), value.hasSuffix("]") else { return nil }
    let inner = String(value.dropFirst().dropLast())
    let parts = inner.components(separatedBy: "]-[")
    guard parts.count == 3 else { return nil }
    let legacyTopic = parts[0]
    let model = parts[1]
    let context = parts[2]
    return LegacyTitle(topic: legacyTopic, context: context, model: model)
}

func validIdentifier(_ value: String) -> Bool {
    guard !value.isEmpty, value.count <= 80 else { return false }
    let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "-_"))
    return value.unicodeScalars.allSatisfy { allowed.contains($0) }
}

func safeSessionName(_ value: String) -> String {
    let collapsed = value
        .split(whereSeparator: { $0.isWhitespace })
        .joined(separator: " ")
    guard !collapsed.isEmpty else { return "" }
    let lower = collapsed.lowercased()
    let unsafeMarkers = ["/users/", "/home/", "/private/", "/tmp/", "/var/", "/opt/", "/volumes/", "http://", "https://", "authorization", "bearer", "cookie", "password", "passwd", "secret", "token", "apikey", "api_key", "api-key", "clientsecret", "client_secret", "client-secret", "databaseurl", "database_url", "database-url"]
    guard !unsafeMarkers.contains(where: { lower.contains($0) }) else { return "" }
    let secretPatterns = [#"(?i)sk-[A-Za-z0-9_-]{12,}"#, #"[A-Za-z0-9_+/=-]{32,}"#, #"(?i)[A-Za-z]:\\[^\s]+"#]
    let range = NSRange(collapsed.startIndex..<collapsed.endIndex, in: collapsed)
    for pattern in secretPatterns {
        if let expression = try? NSRegularExpression(pattern: pattern), expression.firstMatch(in: collapsed, range: range) != nil {
            return ""
        }
    }
    if collapsed.count <= 48 { return collapsed }
    return String(collapsed.prefix(45)) + "..."
}

func decodeHex(_ value: String) -> String? {
    guard value.count.isMultiple(of: 2) else { return nil }
    var data = Data(capacity: value.count / 2)
    var index = value.startIndex
    while index < value.endIndex {
        let next = value.index(index, offsetBy: 2)
        guard let byte = UInt8(value[index..<next], radix: 16) else { return nil }
        data.append(byte)
        index = next
    }
    return String(data: data, encoding: .utf8)
}

func sessionMetadata(_ threadID: String) -> SessionMetadata? {
    guard validIdentifier(threadID) else { return nil }
    let environment = ProcessInfo.processInfo.environment
    let codexHome = environment["CODEX_HOME"] ?? FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".codex").path
    let database = URL(fileURLWithPath: codexHome).appendingPathComponent("state_5.sqlite").path
    guard FileManager.default.fileExists(atPath: database), FileManager.default.isExecutableFile(atPath: "/usr/bin/sqlite3") else { return nil }
    let query = """
    SELECT hex(substr(COALESCE(NULLIF(name,''),NULLIF(title,''),NULLIF(preview,''),''),1,80)), hex(substr(COALESCE(model,''),1,80)), hex(substr(COALESCE(reasoning_effort,''),1,32)), hex(substr(COALESCE(thread_source,''),1,64)), hex(substr(COALESCE(agent_path,''),1,256)), CASE WHEN EXISTS (SELECT 1 FROM thread_spawn_edges e WHERE e.child_thread_id=t.id) THEN '1' ELSE '0' END, CASE WHEN EXISTS (SELECT 1 FROM thread_spawn_edges e WHERE e.parent_thread_id=t.id) THEN '1' ELSE '0' END FROM threads t WHERE id='\(threadID)' LIMIT 1;
    """
    let task = Process()
    let output = Pipe()
    let finished = DispatchSemaphore(value: 0)
    task.executableURL = URL(fileURLWithPath: "/usr/bin/sqlite3")
    task.arguments = ["-readonly", "-cmd", ".timeout 100", "-separator", "\t", database, query]
    task.standardOutput = output
    task.standardError = FileHandle.nullDevice
    task.terminationHandler = { _ in finished.signal() }
    do {
        try task.run()
    } catch {
        return nil
    }
    if finished.wait(timeout: .now() + .milliseconds(400)) == .timedOut {
        task.terminate()
        _ = finished.wait(timeout: .now() + .milliseconds(100))
        return nil
    }
    guard task.terminationStatus == 0 else { return nil }
    let data = output.fileHandleForReading.readDataToEndOfFile()
    guard let row = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines), !row.isEmpty else { return nil }
    let fields = row.components(separatedBy: "\t")
    guard fields.count == 7,
          let sessionName = decodeHex(fields[0]),
          let model = decodeHex(fields[1]),
          let effort = decodeHex(fields[2]),
          let threadSource = decodeHex(fields[3]),
          let agentPath = decodeHex(fields[4]) else { return nil }
    return SessionMetadata(sessionName: safeSessionName(sessionName), model: model, effort: effort, threadSource: threadSource, agentPath: agentPath, hasParent: fields[5] == "1", hasChildren: fields[6] == "1")
}

func effortLabel(_ value: String) -> String {
    switch value.lowercased() {
    case "ultra": return "Ultra"
    case "max": return "max"
    case "": return "effort 미확인"
    default: return value
    }
}

func roleLabel(_ metadata: SessionMetadata?) -> String {
    guard let metadata else { return "역할 미확인" }
    let isChild = metadata.hasParent || metadata.threadSource == "subagent" || !metadata.agentPath.isEmpty
    if isChild && metadata.hasChildren { return "차일드·오케스트레이터" }
    if isChild { return "차일드" }
    if metadata.threadSource == "automation" && metadata.hasChildren { return "자동화·오케스트레이터" }
    if metadata.threadSource == "automation" { return "자동화" }
    if metadata.hasChildren { return "오케스트레이터" }
    return "메인"
}

let legacyTitle = normalizedLegacyTitle(rawTitle)
let environment = ProcessInfo.processInfo.environment
let ambientThreadID = environment["CODEX_THREAD_ID"] ?? environment["CODEX_SESSION_ID"] ?? ""
let threadID = validIdentifier(ambientThreadID) ? ambientThreadID : passedSessionID
let stateMetadata = sessionMetadata(threadID)
let passedParts = passedMetadata.components(separatedBy: " · ").filter { !$0.isEmpty }
let passedModel = passedParts.first { !$0.hasPrefix("#") } ?? ""
let model = stateMetadata?.model.isEmpty == false ? stateMetadata!.model : (legacyTitle?.model ?? passedModel)
let status = legacyTitle.map { statusTitle($0.topic) } ?? (topic.isEmpty ? rawTitle : statusTitle(topic))
let currentPrefix = status + " · "
let currentContext = rawTitle.hasPrefix(currentPrefix) ? String(rawTitle.dropFirst(currentPrefix.count)) : ""
let context = legacyTitle?.context ?? currentContext
let title = [status, context].filter { !$0.isEmpty }.joined(separator: " · ")
let sessionName = stateMetadata?.sessionName.isEmpty == false ? stateMetadata!.sessionName : "세션명 미확인"
let primaryMetadata = [model, effortLabel(stateMetadata?.effort ?? ""), roleLabel(stateMetadata)]
    .filter { !$0.isEmpty }
    .joined(separator: " · ")

func oblivionColor(_ hex: Int, alpha: CGFloat = 1.0) -> NSColor {
    return NSColor(
        srgbRed: CGFloat((hex >> 16) & 0xff) / 255.0,
        green: CGFloat((hex >> 8) & 0xff) / 255.0,
        blue: CGFloat(hex & 0xff) / 255.0,
        alpha: alpha
    )
}

func oblivionAccent(_ topic: String) -> NSColor {
    switch topic {
    case "done": return oblivionColor(0x73D216)
    case "error": return oblivionColor(0xF92672)
    case "approval", "input": return oblivionColor(0xEDD400)
    case "progress": return oblivionColor(0x729FCF)
    default: return oblivionColor(0xAD7FA8)
    }
}

let accent = oblivionAccent(topic)
let oblivionText = oblivionColor(0xD3D7CF)

final class OverlayApp: NSObject, NSApplicationDelegate {
    var window: NSWindow?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        let screen = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let width: CGFloat = 460
        let height: CGFloat = 138
        let rect = NSRect(x: screen.maxX - width - 24, y: screen.maxY - height - 24, width: width, height: height)
        let panel = NSPanel(contentRect: rect, styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.level = .floating
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .transient]
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = true
        panel.ignoresMouseEvents = false

        let root = NSView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        root.wantsLayer = true
        root.layer?.cornerRadius = 14
        root.layer?.backgroundColor = oblivionColor(0x303030, alpha: 0.97).cgColor
        root.layer?.borderWidth = 2.0
        root.layer?.borderColor = accent.withAlphaComponent(0.85).cgColor

        let titleField = NSTextField(labelWithString: title)
        titleField.frame = NSRect(x: 20, y: 98, width: width - 40, height: 24)
        titleField.font = NSFont.systemFont(ofSize: 15, weight: .semibold)
        titleField.textColor = accent
        titleField.lineBreakMode = .byTruncatingTail
        root.addSubview(titleField)

        let metadataFont = NSFont.systemFont(ofSize: 10.5, weight: .medium)
        let metadataColor = oblivionText.withAlphaComponent(0.76)
        let availableMetadataWidth = width - 40
        let minimumSessionWidth: CGFloat = 150
        let measuredPrimaryWidth = primaryMetadata.isEmpty ? 0 : ceil((primaryMetadata as NSString).size(withAttributes: [.font: metadataFont]).width) + 4
        let primaryWidth = min(measuredPrimaryWidth, availableMetadataWidth - minimumSessionWidth)

        let primaryMetadataField = NSTextField(labelWithString: primaryMetadata)
        primaryMetadataField.frame = NSRect(x: 20, y: 74, width: primaryWidth, height: 20)
        primaryMetadataField.font = metadataFont
        primaryMetadataField.textColor = metadataColor
        primaryMetadataField.lineBreakMode = .byTruncatingTail
        root.addSubview(primaryMetadataField)

        let sessionField = NSTextField(labelWithString: (primaryMetadata.isEmpty ? "" : " · ") + sessionName)
        sessionField.frame = NSRect(x: 20 + primaryWidth, y: 74, width: availableMetadataWidth - primaryWidth, height: 20)
        sessionField.font = metadataFont
        sessionField.textColor = metadataColor
        sessionField.lineBreakMode = .byTruncatingTail
        root.addSubview(sessionField)

        let messageField = NSTextField(labelWithString: message)
        messageField.frame = NSRect(x: 20, y: 18, width: width - 40, height: 50)
        messageField.font = NSFont.systemFont(ofSize: 13, weight: .regular)
        messageField.textColor = oblivionText
        messageField.lineBreakMode = .byTruncatingTail
        messageField.maximumNumberOfLines = 2
        messageField.cell?.wraps = true
        messageField.cell?.isScrollable = false
        root.addSubview(messageField)

        panel.contentView = root
        panel.alphaValue = 0
        panel.orderFrontRegardless()
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.12
            panel.animator().alphaValue = 1
        }
        self.window = panel

        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.18
                panel.animator().alphaValue = 0
            }, completionHandler: {
                panel.close()
                NSApp.terminate(nil)
            })
        }
    }
}

let app = NSApplication.shared
let delegate = OverlayApp()
app.delegate = delegate
DispatchQueue.main.asyncAfter(deadline: .now() + max(duration + 1.0, 2.0)) {
    app.terminate(nil)
}
app.run()
