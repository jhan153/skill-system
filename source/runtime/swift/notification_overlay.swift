import Cocoa

let title = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Codex notification"
let message = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "Permission needed."
let duration = CommandLine.arguments.count > 3 ? Double(CommandLine.arguments[3]) ?? 4.0 : 4.0
let topic = CommandLine.arguments.count > 4 ? CommandLine.arguments[4] : ""

func monokaiAccent(_ topic: String) -> NSColor {
    switch topic {
    case "done": return NSColor(srgbRed: 166/255.0, green: 226/255.0, blue: 46/255.0, alpha: 1.0)
    case "error": return NSColor(srgbRed: 249/255.0, green: 38/255.0, blue: 114/255.0, alpha: 1.0)
    case "approval", "input": return NSColor(srgbRed: 102/255.0, green: 217/255.0, blue: 239/255.0, alpha: 1.0)
    case "progress": return NSColor(srgbRed: 230/255.0, green: 219/255.0, blue: 116/255.0, alpha: 1.0)
    case "kanboard": return NSColor(srgbRed: 174/255.0, green: 129/255.0, blue: 255/255.0, alpha: 1.0)
    default: return NSColor(srgbRed: 248/255.0, green: 248/255.0, blue: 242/255.0, alpha: 1.0)
    }
}

let accent = monokaiAccent(topic)

final class OverlayApp: NSObject, NSApplicationDelegate {
    var window: NSWindow?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        let screen = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let width: CGFloat = 460
        let height: CGFloat = 92
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
        root.layer?.backgroundColor = NSColor(srgbRed: 39/255.0, green: 40/255.0, blue: 34/255.0, alpha: 0.97).cgColor
        root.layer?.borderWidth = 2.0
        root.layer?.borderColor = accent.withAlphaComponent(0.85).cgColor

        let titleField = NSTextField(labelWithString: title)
        titleField.frame = NSRect(x: 20, y: 52, width: width - 40, height: 24)
        titleField.font = NSFont.systemFont(ofSize: 15, weight: .semibold)
        titleField.textColor = accent
        titleField.lineBreakMode = .byTruncatingTail
        root.addSubview(titleField)

        let messageField = NSTextField(labelWithString: message)
        messageField.frame = NSRect(x: 20, y: 22, width: width - 40, height: 24)
        messageField.font = NSFont.systemFont(ofSize: 13, weight: .regular)
        messageField.textColor = NSColor(srgbRed: 248/255.0, green: 248/255.0, blue: 242/255.0, alpha: 1.0)
        messageField.lineBreakMode = .byTruncatingTail
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
app.run()
