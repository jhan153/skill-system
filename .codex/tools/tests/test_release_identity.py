from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def load_checker():
    path = Path(__file__).resolve().parents[1] / "check_release_identity.py"
    spec = importlib.util.spec_from_file_location("release_identity_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_checker()

    def build_fixture(self, root: Path) -> None:
        source_plugins = root / "source" / "plugins"
        source_plugins.mkdir(parents=True)
        marketplace_entries = []
        for plugin in self.checker.PLUGIN_NAMES:
            short_name = plugin.removeprefix("skill-system-")
            (source_plugins / f"{short_name}.yaml").write_text(
                f'name: {plugin}\nversion: "{self.checker.CURRENT_VERSION}"\n',
                encoding="utf-8",
            )
            for platform in (".codex-plugin", ".claude-plugin"):
                manifest = root / "plugins" / plugin / platform / "plugin.json"
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text(
                    json.dumps({"name": plugin, "version": self.checker.CURRENT_VERSION}),
                    encoding="utf-8",
                )
            marketplace_entries.append({"name": plugin, "version": self.checker.CURRENT_VERSION})
        marketplace = root / "plugins" / ".claude-plugin" / "marketplace.json"
        marketplace.parent.mkdir(parents=True)
        marketplace.write_text(json.dumps({"plugins": marketplace_entries}), encoding="utf-8")
        codex_marketplace = root / ".agents" / "plugins" / "marketplace.json"
        codex_marketplace.parent.mkdir(parents=True)
        codex_marketplace.write_text(
            json.dumps(
                {
                    "plugins": [
                        {
                            "name": plugin,
                            "source": {"source": "local", "path": f"./plugins/{plugin}"},
                        }
                        for plugin in self.checker.PLUGIN_NAMES
                    ]
                }
            ),
            encoding="utf-8",
        )

        eval_root = root / "source" / "shared" / "eval"
        eval_root.mkdir(parents=True)
        for name in self.checker.EVAL_MANIFESTS:
            (eval_root / name).write_text(
                f'version: "{self.checker.CURRENT_VERSION}"\n',
                encoding="utf-8",
            )
        claude_rules = root / "source" / "platform" / "claude" / "CLAUDE.md"
        claude_rules.parent.mkdir(parents=True)
        claude_rules.write_text(
            f'> Skill System bundle ({self.checker.CURRENT_VERSION})\n', encoding="utf-8"
        )

    def test_consistent_release_identity_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            self.build_fixture(root)
            self.assertEqual(self.checker.check(root), [])

    def test_stale_version_and_cachebuster_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            self.build_fixture(root)
            manifest = root / "source" / "plugins" / "core.yaml"
            manifest.write_text(
                'name: skill-system-core\nversion: "9.1.0+codex.local-stale"\n',
                encoding="utf-8",
            )
            errors = self.checker.check(root)
            self.assertTrue(any("version" in error and "core.yaml" in error for error in errors), errors)
            self.assertTrue(any("cachebuster" in error for error in errors), errors)

    def test_wrong_plugin_identity_and_marketplace_extra_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            self.build_fixture(root)
            source_manifest = root / "source" / "plugins" / "core.yaml"
            source_manifest.write_text(
                f'name: wrong-source-name\nversion: "{self.checker.CURRENT_VERSION}"\n',
                encoding="utf-8",
            )
            generated_manifest = root / "plugins" / "skill-system-core" / ".codex-plugin" / "plugin.json"
            generated_manifest.write_text(
                json.dumps({"name": "wrong-plugin", "version": self.checker.CURRENT_VERSION}),
                encoding="utf-8",
            )
            marketplace_path = root / "plugins" / ".claude-plugin" / "marketplace.json"
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
            marketplace["plugins"].append({"name": "skill-system-stale", "version": "9.1.0"})
            marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

            errors = self.checker.check(root)
            self.assertTrue(any("core.yaml name" in error for error in errors), errors)
            self.assertTrue(any("wrong-plugin" in error for error in errors), errors)
            self.assertTrue(any("Claude marketplace plugin set mismatch" in error for error in errors), errors)

    def test_codex_marketplace_requires_exact_unique_local_entries(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            self.build_fixture(root)
            marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
            marketplace["plugins"][0]["source"]["path"] = "./plugins/wrong-path"
            marketplace["plugins"].append(dict(marketplace["plugins"][0]))
            marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

            errors = self.checker.check(root)
            self.assertTrue(any("exactly 6" in error for error in errors), errors)
            self.assertTrue(any("duplicate plugin names" in error for error in errors), errors)
            self.assertTrue(any("source must be local" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
