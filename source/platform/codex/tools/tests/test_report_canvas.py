from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def find_canvas_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        canonical = parent / "shared" / "report-canvas"
        if (canonical / "render_report.py").is_file():
            return canonical
        skills_root = parent / "skills"
        for generated in sorted(skills_root.glob("report-*/scripts/report-canvas")):
            if (generated / "render_report.py").is_file():
                return generated
    raise RuntimeError("Report Canvas root not found")


CANVAS = find_canvas_root()


def find_report_skill_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "skills"
        if any(candidate.glob("report-*/SKILL.md")):
            return candidate
    raise RuntimeError("Report skill root not found")


REPORT_SKILLS = find_report_skill_root()


def find_canvas_contract() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        for candidate in (
            parent / "shared" / "docs" / "report_canvas_contract.md",
            parent / "docs" / "report_canvas_contract.md",
        ):
            if candidate.is_file():
                return candidate
        skills_root = parent / "skills"
        for candidate in sorted(
            skills_root.glob("report-*/references/report_canvas_contract.md")
        ):
            if candidate.is_file():
                return candidate
    raise RuntimeError("Report Canvas contract not found")


CANVAS_CONTRACT = find_canvas_contract()
spec = importlib.util.spec_from_file_location(
    "skill_system_report_canvas_renderer",
    CANVAS / "render_report.py",
)
assert spec and spec.loader
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class ReportCanvasTests(unittest.TestCase):
    def load_example(self, name: str) -> dict[str, object]:
        return json.loads(
            (CANVAS / "examples" / f"{name}.json").read_text(encoding="utf-8")
        )

    def render_model(self, model: dict[str, object]) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            renderer.render(source, output)
            return output.read_text(encoding="utf-8")

    def render_example(self, name: str) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / f"{name}.html"
            renderer.render(CANVAS / "examples" / f"{name}.json", output)
            return output.read_text(encoding="utf-8")

    def assert_model_rejected(self, model: dict[str, object]) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "invalid.json"
            output = Path(temp_dir) / "invalid.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaises(renderer.ModelError):
                renderer.render(source, output)
            self.assertFalse(output.exists())

    @staticmethod
    def triangle_glb_base64() -> str:
        binary = struct.pack(
            "<9f3H",
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0,
            1,
            2,
        )
        document = {
            "asset": {"version": "2.0"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [
                {
                    "primitives": [
                        {
                            "attributes": {"POSITION": 0},
                            "indices": 1,
                        }
                    ]
                }
            ],
            "buffers": [{"byteLength": len(binary)}],
            "bufferViews": [
                {"buffer": 0, "byteOffset": 0, "byteLength": 36},
                {"buffer": 0, "byteOffset": 36, "byteLength": 6},
            ],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": 3,
                    "type": "VEC3",
                    "min": [0.0, 0.0, 0.0],
                    "max": [1.0, 1.0, 0.0],
                },
                {
                    "bufferView": 1,
                    "componentType": 5123,
                    "count": 3,
                    "type": "SCALAR",
                },
            ],
        }
        json_chunk = json.dumps(
            document,
            separators=(",", ":"),
        ).encode("utf-8")
        json_chunk += b" " * (-len(json_chunk) % 4)
        bin_chunk = binary + b"\0" * (-len(binary) % 4)
        payload_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
        payload = b"".join(
            (
                b"glTF",
                struct.pack("<II", 2, payload_length),
                struct.pack("<II", len(json_chunk), 0x4E4F534A),
                json_chunk,
                struct.pack("<II", len(bin_chunk), 0x004E4942),
                bin_chunk,
            )
        )
        return base64.b64encode(payload).decode("ascii")

    @classmethod
    def triangle_gltf_text(cls) -> str:
        payload = base64.b64decode(cls.triangle_glb_base64())
        json_length = int.from_bytes(payload[12:16], "little")
        document = json.loads(payload[20 : 20 + json_length].decode("utf-8"))
        bin_header = 20 + json_length
        bin_length = int.from_bytes(payload[bin_header : bin_header + 4], "little")
        binary = payload[bin_header + 8 : bin_header + 8 + bin_length]
        byte_length = document["buffers"][0]["byteLength"]
        document["buffers"][0]["uri"] = (
            "data:application/octet-stream;base64,"
            + base64.b64encode(binary[:byte_length]).decode("ascii")
        )
        return json.dumps(document, separators=(",", ":"))

    def test_non_spatial_examples_render_without_three(self) -> None:
        for name in ("decision", "compare", "trace"):
            with self.subTest(name=name):
                rendered = self.render_example(name)
                self.assertIn("<!doctype html>", rendered)
                self.assertIn("Oblivion Hagoromo", rendered)
                self.assertNotIn("SkillSystemSpatialDeps", rendered)
                self.assertNotIn("<script src=", rendered)
                self.assertNotIn("__REPORT_", rendered)

    def test_spatial_example_embeds_pinned_local_runtime(self) -> None:
        rendered = self.render_example("spatial")
        self.assertIn("SkillSystemSpatialDeps", rendered)
        self.assertIn("ReportCanvasSpatial", rendered)
        self.assertIn('"initial_state":"after"', rendered)
        self.assertIn('"kind":"non_manifold"', rendered)
        self.assertNotIn("<script src=", rendered)
        self.assertNotIn("unpkg.com", rendered)
        self.assertNotIn("cdn.jsdelivr.net", rendered)

    def test_renderer_sets_explicit_document_language(self) -> None:
        self.assertIn('<html lang="ko"', self.render_example("decision"))
        model = self.load_example("decision")
        model["language"] = "en"
        self.assertIn('<html lang="en"', self.render_model(model))

    def test_renderer_preserves_typed_lifecycle_status(self) -> None:
        model = self.load_example("trace")
        model["visual"]["trace_kind"] = "lifecycle"
        model["visual"]["nodes"][0]["lifecycle_status"] = "planned"
        model["visual"]["nodes"][1]["lifecycle_status"] = "user_verification_needed"
        model["visual"]["nodes"][2]["lifecycle_status"] = "evidence_unavailable"
        rendered = self.render_model(model)
        self.assertIn('"lifecycle_status":"planned"', rendered)
        self.assertIn('"lifecycle_status":"user_verification_needed"', rendered)
        self.assertIn("lifecycle · ${label(node.lifecycle_status)}", rendered)

    def test_renderer_accepts_structurally_valid_embedded_glb(self) -> None:
        model = self.load_example("spatial")
        model["visual"]["asset"] = {
            "format": "glb",
            "data_base64": self.triangle_glb_base64(),
        }
        model["visual"]["states"] = []
        model["visual"].pop("initial_state")
        model["visual"]["overlays"] = [
            {
                "kind": "selection",
                "label": "triangle edge",
                "edges": [0, 1],
                "faces": [0],
                "evidence_refs": ["issue-index"],
            }
        ]
        rendered = self.render_model(model)
        self.assertIn('"format":"glb"', rendered)

    def test_renderer_accepts_structurally_valid_embedded_gltf(self) -> None:
        model = self.load_example("spatial")
        model["visual"]["asset"] = {
            "format": "gltf",
            "data_text": self.triangle_gltf_text(),
        }
        model["visual"]["states"] = []
        model["visual"].pop("initial_state")
        model["visual"]["overlays"] = [
            {
                "kind": "selection",
                "label": "triangle face",
                "faces": [0],
                "evidence_refs": ["issue-index"],
            }
        ]
        rendered = self.render_model(model)
        self.assertIn('"format":"gltf"', rendered)

    def test_renderer_rejects_trace_identity_and_reference_drift(self) -> None:
        base = self.load_example("trace")
        invalid_models: list[tuple[str, dict[str, object]]] = []

        duplicate_node = copy.deepcopy(base)
        duplicate_node["visual"]["nodes"][1]["id"] = duplicate_node["visual"]["nodes"][0]["id"]
        invalid_models.append(("duplicate node id", duplicate_node))

        dangling_edge = copy.deepcopy(base)
        dangling_edge["visual"]["edges"][0]["to"] = "missing-node"
        invalid_models.append(("dangling edge", dangling_edge))

        dangling_node_evidence = copy.deepcopy(base)
        dangling_node_evidence["visual"]["nodes"][0]["evidence_refs"] = ["missing-evidence"]
        invalid_models.append(("dangling node evidence", dangling_node_evidence))

        dangling_finding_evidence = copy.deepcopy(base)
        dangling_finding_evidence["findings"][0]["evidence_refs"] = ["missing-evidence"]
        invalid_models.append(("dangling finding evidence", dangling_finding_evidence))

        invalid_lifecycle = copy.deepcopy(base)
        invalid_lifecycle["visual"]["nodes"][0]["lifecycle_status"] = "completed"
        invalid_models.append(("invalid lifecycle status", invalid_lifecycle))

        causal_lifecycle_status = copy.deepcopy(base)
        causal_lifecycle_status["visual"]["nodes"][0]["lifecycle_status"] = "planned"
        invalid_models.append(
            ("lifecycle status on causal trace", causal_lifecycle_status)
        )

        incomplete_lifecycle = copy.deepcopy(base)
        incomplete_lifecycle["visual"]["trace_kind"] = "lifecycle"
        incomplete_lifecycle["visual"]["nodes"][0]["lifecycle_status"] = "planned"
        invalid_models.append(("incomplete lifecycle trace", incomplete_lifecycle))

        for label, model in invalid_models:
            with self.subTest(case=label):
                self.assert_model_rejected(model)

    def test_renderer_rejects_spatial_semantic_drift(self) -> None:
        base = self.load_example("spatial")
        invalid_models: list[tuple[str, dict[str, object]]] = []

        invalid_base64 = copy.deepcopy(base)
        invalid_base64["visual"]["asset"] = {
            "format": "glb",
            "data_base64": "not base64!",
        }
        invalid_base64["visual"]["states"] = []
        invalid_base64["visual"].pop("initial_state")
        invalid_models.append(("invalid GLB base64", invalid_base64))

        invalid_glb = copy.deepcopy(base)
        invalid_glb["visual"]["asset"] = {
            "format": "glb",
            "data_base64": base64.b64encode(b"not a GLB").decode("ascii"),
        }
        invalid_glb["visual"]["states"] = []
        invalid_glb["visual"].pop("initial_state")
        invalid_models.append(("invalid GLB structure", invalid_glb))

        dataless_gltf = copy.deepcopy(base)
        dataless_gltf["visual"]["asset"] = {"format": "gltf"}
        invalid_models.append(("dataless glTF", dataless_gltf))

        missing_initial = copy.deepcopy(base)
        missing_initial["visual"]["initial_state"] = "missing-state"
        invalid_models.append(("missing initial state", missing_initial))

        duplicate_state = copy.deepcopy(base)
        duplicate_state["visual"]["states"][1]["id"] = "before"
        invalid_models.append(("duplicate state id", duplicate_state))

        out_of_range_overlay = copy.deepcopy(base)
        out_of_range_overlay["visual"]["overlays"][0]["vertices"] = [999]
        invalid_models.append(("out-of-range overlay", out_of_range_overlay))

        incomplete_edge = copy.deepcopy(base)
        incomplete_edge["visual"]["overlays"][0]["edges"] = [0]
        invalid_models.append(("incomplete overlay edge", incomplete_edge))

        dangling_overlay_evidence = copy.deepcopy(base)
        dangling_overlay_evidence["visual"]["overlays"][0]["evidence_refs"] = [
            "missing-evidence"
        ]
        invalid_models.append(("dangling overlay evidence", dangling_overlay_evidence))

        dangling_overlay_state = copy.deepcopy(base)
        dangling_overlay_state["visual"]["overlays"][0]["state_refs"] = [
            "missing-state"
        ]
        invalid_models.append(("dangling overlay state", dangling_overlay_state))

        for label, model in invalid_models:
            with self.subTest(case=label):
                self.assert_model_rejected(model)

    def test_model_content_is_data_not_html(self) -> None:
        model = json.loads((CANVAS / "examples" / "decision.json").read_text(encoding="utf-8"))
        model["title"] = "</title><script>window.injected=true</script>"
        model["summary"] = "<img src=x onerror=alert(1)>"
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            renderer.render(source, output)
            rendered = output.read_text(encoding="utf-8")
        self.assertIn("&lt;/title&gt;&lt;script&gt;", rendered)
        self.assertIn("<\\/title><script>window.injected=true<\\/script>", rendered)
        core_script = (CANVAS / "static" / "report-canvas.js").read_text(encoding="utf-8")
        spatial_script = (CANVAS / "static" / "report-spatial.js").read_text(encoding="utf-8")
        self.assertNotIn(".innerHTML", core_script)
        self.assertNotIn(".innerHTML", spatial_script)

    def test_renderer_rejects_more_than_three_findings(self) -> None:
        model = json.loads((CANVAS / "examples" / "decision.json").read_text(encoding="utf-8"))
        model["findings"] = [model["findings"][0]] * 4
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaises(renderer.ModelError):
                renderer.render(source, output)

    def test_renderer_supports_explicit_no_follow_up(self) -> None:
        model = json.loads((CANVAS / "examples" / "compare.json").read_text(encoding="utf-8"))
        model["next_action"] = {
            "kind": "none",
            "label": "추가 행동이 요청되지 않았습니다",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            renderer.render(source, output)
            rendered = output.read_text(encoding="utf-8")
        self.assertIn('"kind":"none"', rendered)

    def test_renderer_rejects_missing_action_kind(self) -> None:
        model = json.loads((CANVAS / "examples" / "decision.json").read_text(encoding="utf-8"))
        model["next_action"].pop("kind")
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaises(renderer.ModelError):
                renderer.render(source, output)

    def test_renderer_enforces_nested_schema_contract(self) -> None:
        invalid_models: list[tuple[str, dict[str, object]]] = []

        choices_type = json.loads(
            (CANVAS / "examples" / "decision.json").read_text(encoding="utf-8")
        )
        choices_type["visual"]["choices"] = "not-an-array"
        invalid_models.append(("nested type", choices_type))

        nested_required = json.loads(
            (CANVAS / "examples" / "decision.json").read_text(encoding="utf-8")
        )
        nested_required["visual"]["choices"][0].pop("description")
        invalid_models.append(("nested required", nested_required))

        nested_additional = json.loads(
            (CANVAS / "examples" / "decision.json").read_text(encoding="utf-8")
        )
        nested_additional["visual"]["choices"][0]["unexpected"] = True
        invalid_models.append(("nested additionalProperties", nested_additional))

        wrong_mode_visual = json.loads(
            (CANVAS / "examples" / "decision.json").read_text(encoding="utf-8")
        )
        compare_model = json.loads(
            (CANVAS / "examples" / "compare.json").read_text(encoding="utf-8")
        )
        wrong_mode_visual["visual"] = compare_model["visual"]
        invalid_models.append(("mode-specific visual", wrong_mode_visual))

        spatial_asset = json.loads(
            (CANVAS / "examples" / "spatial.json").read_text(encoding="utf-8")
        )
        spatial_asset["visual"]["asset"]["geometry"]["positions"][0] = "not-a-number"
        invalid_models.append(("spatial asset", spatial_asset))

        for label, model in invalid_models:
            with self.subTest(case=label):
                self.assert_model_rejected(model)

    def test_schema_keyword_drift_fails_closed(self) -> None:
        schema = json.loads(
            (CANVAS / "report-model.schema.json").read_text(encoding="utf-8")
        )
        schema["$defs"]["choice"]["minProperties"] = 3
        with self.assertRaisesRegex(renderer.ModelError, "minProperties"):
            renderer._validate_schema_definition(schema)

    def test_renderer_refuses_existing_output_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "existing.html"
            output.write_text("SENTINEL", encoding="utf-8")
            with self.assertRaisesRegex(renderer.ModelError, "--force"):
                renderer.render(CANVAS / "examples" / "decision.json", output)
            self.assertEqual(output.read_text(encoding="utf-8"), "SENTINEL")
            renderer.render(
                CANVAS / "examples" / "decision.json",
                output,
                force=True,
            )
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))

    def test_cli_force_is_required_to_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "existing.html"
            output.write_text("SENTINEL", encoding="utf-8")
            base_command = [
                sys.executable,
                str(CANVAS / "render_report.py"),
                "--input",
                str(CANVAS / "examples" / "decision.json"),
                "--output",
                str(output),
            ]
            denied = subprocess.run(
                base_command,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn("--force", denied.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "SENTINEL")

            replaced = subprocess.run(
                [*base_command, "--force"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                replaced.returncode,
                0,
                replaced.stdout + replaced.stderr,
            )
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))

    def test_renderer_rejects_identical_input_and_output_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "same.json"
            original = (CANVAS / "examples" / "decision.json").read_text(
                encoding="utf-8"
            )
            model_path.write_text(original, encoding="utf-8")
            with self.assertRaisesRegex(renderer.ModelError, "must be different"):
                renderer.render(model_path, model_path, force=True)
            self.assertEqual(model_path.read_text(encoding="utf-8"), original)

    def test_renderer_rejects_incomplete_spatial_coordinates(self) -> None:
        model = json.loads((CANVAS / "examples" / "spatial.json").read_text(encoding="utf-8"))
        model["visual"]["asset"]["geometry"]["positions"].pop()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaises(renderer.ModelError):
                renderer.render(source, output)

    def test_renderer_rejects_external_gltf_resources(self) -> None:
        model = json.loads((CANVAS / "examples" / "spatial.json").read_text(encoding="utf-8"))
        model["visual"]["asset"] = {
            "format": "gltf",
            "data_text": json.dumps(
                {
                    "asset": {"version": "2.0"},
                    "buffers": [{"uri": "mesh.bin", "byteLength": 12}],
                }
            ),
        }
        model["visual"]["states"] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "model.json"
            output = Path(temp_dir) / "report.html"
            source.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaises(renderer.ModelError):
                renderer.render(source, output)

    def test_vendored_assets_match_declared_hashes(self) -> None:
        versions = json.loads((CANVAS / "vendor" / "versions.json").read_text(encoding="utf-8"))
        expected = {
            "pico.min.css": versions["pico"]["sha256"],
            "three-spatial.min.js": versions["three_spatial_bundle"]["sha256"],
        }
        for name, digest in expected.items():
            with self.subTest(name=name):
                actual = hashlib.sha256((CANVAS / "vendor" / name).read_bytes()).hexdigest()
                self.assertEqual(digest, actual)

    def test_every_report_skill_defaults_to_canvas_html(self) -> None:
        skills = sorted(REPORT_SKILLS.glob("report-*/SKILL.md"))
        self.assertGreater(len(skills), 0)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                body = skill.read_text(encoding="utf-8")
                self.assertIn("For every admitted invocation", body)
                self.assertIn("references/report_canvas_contract.md", body)
                self.assertIn("scripts/report-canvas/render_report.py", body)
                self.assertIn("one self-contained report HTML by default", body)
                self.assertNotIn("../../docs/report_canvas_contract.md", body)
                self.assertNotIn("../../report-canvas", body)
                self.assertNotIn("For an explicitly requested persistent/HTML", body)
                self.assertNotIn("Default to concise chat", body)
                metadata = (skill.parent / "agents" / "openai.yaml").read_text(
                    encoding="utf-8"
                )
                self.assertIn("may_write: true", metadata)

    def test_generated_report_skills_are_self_contained(self) -> None:
        skills = sorted(REPORT_SKILLS.glob("report-*/SKILL.md"))
        local_payloads = [
            skill.parent / "scripts" / "report-canvas"
            for skill in skills
            if (skill.parent / "scripts" / "report-canvas" / "render_report.py").is_file()
        ]
        if not local_payloads:
            self.skipTest("canonical source projects Canvas payloads during generation")
        self.assertEqual(len(local_payloads), len(skills))
        expected_files = {
            path.relative_to(local_payloads[0]): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in local_payloads[0].rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                payload = skill.parent / "scripts" / "report-canvas"
                contract = skill.parent / "references" / "report_canvas_contract.md"
                self.assertTrue((payload / "render_report.py").is_file())
                self.assertTrue(contract.is_file())
                actual_files = {
                    path.relative_to(payload): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in payload.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts
                }
                self.assertEqual(expected_files, actual_files)
        runtime_root = REPORT_SKILLS.parent
        self.assertFalse((runtime_root / "report-canvas").exists())
        for skill in sorted(REPORT_SKILLS.iterdir()):
            if not skill.is_dir() or skill.name.startswith("report-"):
                continue
            self.assertFalse((skill / "scripts" / "report-canvas").exists())
            self.assertFalse(
                (skill / "references" / "report_canvas_contract.md").exists()
            )

    def test_detached_generated_report_skill_can_render(self) -> None:
        source_skill = next(
            (
                skill.parent
                for skill in sorted(REPORT_SKILLS.glob("report-*/SKILL.md"))
                if (
                    skill.parent
                    / "scripts"
                    / "report-canvas"
                    / "render_report.py"
                ).is_file()
            ),
            None,
        )
        if source_skill is None:
            self.skipTest("canonical source projects Canvas payloads during generation")
        with tempfile.TemporaryDirectory() as temp_dir:
            detached = Path(temp_dir) / source_skill.name
            shutil.copytree(source_skill, detached)
            canvas = detached / "scripts" / "report-canvas"
            output = detached / "detached-report.html"
            result = subprocess.run(
                [
                    sys.executable,
                    str(canvas / "render_report.py"),
                    "--input",
                    str(canvas / "examples" / "decision.json"),
                    "--output",
                    str(output),
                ],
                cwd=detached,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))

    def test_canvas_contract_declares_report_family_html_default(self) -> None:
        contract = CANVAS_CONTRACT.read_text(encoding="utf-8")
        self.assertIn(
            "Once a `report-*` skill admits a task, render its primary human-facing result",
            contract,
        )
        self.assertIn("explicit `chat-only`, `no file`", contract)
        self.assertIn("scripts/report-canvas/render_report.py", contract)

    def test_generated_plugins_keep_canvas_inside_report_skills(self) -> None:
        here = Path(__file__).resolve()
        repo_root = next(
            (
                parent
                for parent in here.parents
                if (parent / "source" / "tools" / "generate_targets.py").is_file()
                and (parent / "plugins").is_dir()
            ),
            None,
        )
        if repo_root is None:
            self.skipTest("source plugin packages are unavailable")
        package_roots = [
            path
            for base in (repo_root / "plugins", repo_root / "plugins" / "claude")
            if base.is_dir()
            for path in sorted(base.glob("skill-system-*"))
            if path.is_dir()
        ]
        self.assertGreater(len(package_roots), 0)
        report_skill_count = 0
        for package in package_roots:
            with self.subTest(package=package.as_posix()):
                self.assertFalse((package / "report-canvas").exists())
                self.assertFalse(
                    (package / "docs" / "report_canvas_contract.md").exists()
                )
                for skill in sorted((package / "skills").glob("*")):
                    if not skill.is_dir():
                        continue
                    payload = skill / "scripts" / "report-canvas"
                    contract = skill / "references" / "report_canvas_contract.md"
                    if skill.name.startswith("report-"):
                        report_skill_count += 1
                        self.assertTrue((payload / "render_report.py").is_file())
                        self.assertTrue(contract.is_file())
                    else:
                        self.assertFalse(payload.exists())
                        self.assertFalse(contract.exists())
        self.assertGreater(report_skill_count, 0)


if __name__ == "__main__":
    unittest.main()
