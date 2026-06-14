#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


GENERIC_DIRS = {
    "src",
    "app",
    "apps",
    "lib",
    "libs",
    "pkg",
    "packages",
    "internal",
    "cmd",
}

CONTAINER_LABELS = {
    "api": "API Container",
    "frontend": "Frontend Container",
    "cli": "CLI Container",
    "worker": "Worker Container",
    "core": "Core Library",
    "test": "Test Harness",
    "deployment": "Deployment Config",
}

ENTRYPOINT_KIND_PRIORITY = {
    "http-route": 0,
    "cli-command": 1,
    "cli-startup": 2,
    "queue-consumer": 3,
    "scheduled-job": 4,
    "worker-task": 5,
    "event-handler": 6,
}

HTTP_LIB_PATTERNS = [
    ("requests", "External HTTP API"),
    ("httpx", "External HTTP API"),
    ("axios", "External HTTP API"),
    ("fetch", "External HTTP API"),
    ("urllib", "External HTTP API"),
    ("aiohttp", "External HTTP API"),
    ("grpc", "gRPC Service"),
]

EXTERNAL_INTERFACE_HINTS = {
    "database": {
        "label": "Database",
        "modules": {"sqlalchemy", "psycopg", "psycopg2", "postgres", "mysql", "sqlite3", "pymongo", "motor", "prisma", "sequelize", "typeorm", "knex", "gorm", "jdbc"},
        "references": {"session.execute", "engine.connect", "db.query", "db.execute", "cursor.execute", "repository.save"},
        "envs": {"DATABASE_URL", "DB_URL", "DB_HOST", "POSTGRES_URL", "POSTGRES_DSN", "MYSQL_URL", "MONGO_URL", "SQLITE_URL"},
    },
    "cache": {
        "label": "Cache",
        "modules": {"redis", "memcache", "memcached", "cachetools"},
        "references": {"redis.get", "redis.set", "cache.get", "cache.set", "lru_cache"},
        "envs": {"REDIS_URL", "CACHE_URL", "MEMCACHE_URL", "MEMCACHED_SERVERS"},
    },
    "messaging": {
        "label": "Message Broker",
        "modules": {"kafka", "rabbitmq", "amqp", "sqs", "pubsub", "nats", "celery"},
        "references": {"producer.send", "consumer.poll", "channel.publish", "subscribe", "publish"},
        "envs": {"BROKER_URL", "AMQP_URL", "RABBITMQ_URL", "KAFKA_BOOTSTRAP_SERVERS", "SQS_QUEUE_URL", "PUBSUB_TOPIC", "NATS_URL"},
    },
    "object-storage": {
        "label": "Object Storage",
        "modules": {"s3", "boto3", "minio", "gcs", "blob", "azure.storage"},
        "references": {"bucket.upload", "bucket.download", "blob.upload", "blob.download"},
        "envs": {"S3_BUCKET", "AWS_S3_BUCKET", "GCS_BUCKET", "AZURE_STORAGE_ACCOUNT", "MINIO_ENDPOINT"},
    },
    "observability": {
        "label": "Observability",
        "modules": {"opentelemetry", "otel", "prometheus", "sentry"},
        "references": {"meter.create", "counter.add", "histogram.record", "sentry.capture", "tracer.start"},
        "envs": {"SENTRY_DSN", "OTEL_EXPORTER_OTLP_ENDPOINT", "PROMETHEUS_PUSHGATEWAY_URL", "DATADOG_API_KEY"},
    },
    "external-http": {
        "label": "External HTTP API",
        "modules": set(),
        "references": set(),
        "envs": {"API_URL", "BASE_URL", "SERVICE_URL", "WEBHOOK_URL", "UPSTREAM_URL"},
    },
}

CROSSCUTTING_HINTS = {
    "auth": {
        "modules": {"jwt", "oauth", "oidc", "authlib", "passport", "spring.security"},
        "references": {"authenticate", "authorize", "token.verify", "jwt.decode", "jwt.encode"},
        "envs": {"JWT_SECRET", "JWT_PUBLIC_KEY", "OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "AUTH0_DOMAIN"},
    },
    "logging": {
        "modules": {"logging", "structlog", "winston", "logrus", "zap"},
        "references": {"logging.getlogger", "logger.info", "logger.error", "log.info", "log.error"},
    },
    "metrics": {
        "modules": {"prometheus", "opentelemetry", "otel", "statsd"},
        "references": {"counter.add", "histogram.record", "meter.create", "metrics.increment", "metrics.observe"},
        "envs": {"OTEL_EXPORTER_OTLP_ENDPOINT", "PROMETHEUS_MULTIPROC_DIR", "STATSD_HOST"},
    },
    "persistence": {
        "modules": {"sqlalchemy", "psycopg", "psycopg2", "prisma", "sequelize", "typeorm", "knex", "gorm", "jdbc", "pymongo", "motor"},
        "references": {"session.execute", "engine.connect", "repository.save", "repository.find", "db.query", "cursor.execute"},
    },
    "caching": {
        "modules": {"redis", "memcache", "memcached", "cachetools"},
        "references": {"redis.get", "redis.set", "cache.get", "cache.set", "lru_cache"},
    },
    "messaging": {
        "modules": {"kafka", "rabbitmq", "amqp", "sqs", "pubsub", "nats", "celery"},
        "references": {"producer.send", "channel.publish", "consumer.poll", "subscribe", "publish"},
        "envs": {"BROKER_URL", "KAFKA_BOOTSTRAP_SERVERS", "RABBITMQ_URL", "AMQP_URL", "NATS_URL"},
    },
    "config": {
        "modules": {"dotenv", "pydantic_settings"},
        "references": {"os.environ", "os.getenv", "process.env", "basesettings"},
        "envs": {"ENV", "NODE_ENV", "APP_ENV", "SETTINGS_MODULE"},
    },
    "retry": {
        "modules": {"tenacity", "backoff", "retry", "circuitbreaker"},
        "references": {"retry(", "backoff.on", "circuitbreaker", "retrying"},
    },
}

KNOWN_DEPLOYMENT_FILES = {
    "vercel.json": ("platform", "Vercel"),
    "render.yaml": ("platform", "Render"),
    "render.yml": ("platform", "Render"),
    "fly.toml": ("platform", "Fly.io"),
    "serverless.yml": ("platform", "Serverless"),
    "serverless.yaml": ("platform", "Serverless"),
    "skaffold.yaml": ("orchestrator", "Skaffold"),
    "skaffold.yml": ("orchestrator", "Skaffold"),
    "railway.json": ("platform", "Railway"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build architecture models from collector artifacts")
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--artifacts-dir", required=True)
    parser.add_argument("--policy", required=True)
    return parser.parse_args()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def slugify(value: str, fallback: str = "item") -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or fallback


def humanize_token(value: str) -> str:
    text = (value or "").strip()
    if text.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rb", ".php", ".cs", ".cpp", ".c", ".h")):
        text = text.rsplit(".", 1)[0]
    text = text.replace("_", " ").replace("-", " ").replace("/", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return "Unknown"
    return " ".join(part.capitalize() for part in text.split(" "))


def module_aliases(name: str) -> set[str]:
    raw = (name or "").strip().lower()
    if not raw:
        return set()
    raw = raw.lstrip(".")
    raw = raw.replace("\\", "/")
    aliases = {raw}
    if raw.startswith("@"):
        parts = [part for part in raw.split("/") if part]
        if len(parts) >= 2:
            aliases.add("/".join(parts[:2]))
    slash_parts = [part for part in raw.split("/") if part]
    if slash_parts:
        aliases.add(slash_parts[0])
    dot_parts = [part for part in raw.replace("/", ".").split(".") if part]
    for idx in range(1, min(len(dot_parts), 3) + 1):
        aliases.add(".".join(dot_parts[:idx]))
        aliases.add(dot_parts[idx - 1])
    return {alias for alias in aliases if alias}


def normalize_reference(value: str) -> str:
    cleaned = (value or "").strip().lower()
    cleaned = cleaned.replace("\\", ".").replace("/", ".")
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    if isinstance(node, ast.Subscript):
        return dotted_name(node.value)
    return ""


def strip_comments(text: str, ext: str) -> str:
    if ext in {".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".c", ".cc", ".cpp", ".h", ".hpp", ".php", ".cs"}:
        text = re.sub(r"//.*", "", text)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    elif ext in {".py", ".rb"}:
        text = re.sub(r"#.*", "", text)
    return text


def extract_signal_features(rel_path: str, text: str, ext: str) -> dict[str, Any]:
    modules: set[str] = set()
    references: set[str] = set()
    urls: set[str] = set()
    env_names: set[str] = set()

    if ext == ".py":
        try:
            tree = ast.parse(text)
        except Exception:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        modules.update(module_aliases(alias.name))
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module or ""
                    modules.update(module_aliases(module_name))
                    for alias in node.names:
                        modules.update(module_aliases(alias.name))
                elif isinstance(node, ast.Attribute):
                    dotted = normalize_reference(dotted_name(node))
                    if dotted:
                        references.add(dotted)
                elif isinstance(node, ast.Name):
                    references.add(normalize_reference(node.id))
                elif isinstance(node, ast.Call):
                    dotted = normalize_reference(dotted_name(node.func))
                    if dotted:
                        references.add(dotted)
                    if dotted in {"os.getenv", "getenv"} and node.args:
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                            env_names.add(first_arg.value)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if re.match(r"https?://", node.value):
                        urls.add(node.value.strip())
                    if re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", node.value):
                        env_names.add(node.value.strip())
                elif isinstance(node, ast.Subscript):
                    target = normalize_reference(dotted_name(node.value))
                    if target == "os.environ":
                        slice_node = node.slice
                        if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
                            env_names.add(slice_node.value)
    else:
        sanitized = strip_comments(text, ext)
        if ext in {".js", ".jsx", ".ts", ".tsx"}:
            for match in re.finditer(r"""from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)""", sanitized):
                modules.update(module_aliases(match.group(1) or match.group(2)))
            for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)", sanitized):
                references.add(normalize_reference(match.group(1)))
            for match in re.finditer(r"process\.env\.([A-Z][A-Z0-9_]+)", sanitized):
                env_names.add(match.group(1))
            for match in re.finditer(r"""process\.env\[['"]([A-Z][A-Z0-9_]+)['"]\]""", sanitized):
                env_names.add(match.group(1))
        elif ext == ".go":
            for match in re.finditer(r'import\s+"([^"]+)"', sanitized):
                modules.update(module_aliases(match.group(1)))
            for match in re.finditer(r'os\.Getenv\("([A-Z][A-Z0-9_]+)"\)', sanitized):
                env_names.add(match.group(1))
        elif ext == ".java":
            for match in re.finditer(r'import\s+([A-Za-z0-9_.*]+);', sanitized):
                modules.update(module_aliases(match.group(1).rstrip(".*")))
            for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)", sanitized):
                references.add(normalize_reference(match.group(1)))
            for match in re.finditer(r'System\.getenv\(\s*"([A-Z][A-Z0-9_]+)"\s*\)', sanitized):
                env_names.add(match.group(1))
        elif ext == ".rb":
            for match in re.finditer(r"require(?:_relative)?\s+[\"']([^\"']+)[\"']", sanitized):
                modules.update(module_aliases(match.group(1)))
            for match in re.finditer(r'ENV\[\s*[\"\']([A-Z][A-Z0-9_]+)[\"\']\s*\]', sanitized):
                env_names.add(match.group(1))
        elif ext in {".php", ".cs", ".c", ".cc", ".cpp", ".h", ".hpp"}:
            for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)", sanitized):
                references.add(normalize_reference(match.group(1)))
            for match in re.finditer(r'getenv\(\s*[\"\']([A-Z][A-Z0-9_]+)[\"\']\s*\)', sanitized):
                env_names.add(match.group(1))

        for match in re.finditer(r"https?://[A-Za-z0-9._:/?&=%#-]+", sanitized):
            urls.add(match.group(0))
        for match in re.finditer(r"""['"]([A-Z][A-Z0-9_]{2,}(?:_(?:URL|DSN|HOST|PORT|BUCKET|QUEUE|TOPIC|KEY|SECRET|ENDPOINT))?)['"]""", sanitized):
            env_names.add(match.group(1))

    return {
        "modules": modules,
        "references": references,
        "urls": sorted(urls),
        "env_names": sorted(env_names),
        "file_path": rel_path,
    }


def signal_has_module(signals: dict[str, Any], candidates: set[str]) -> bool:
    modules = {str(item).lower() for item in signals.get("modules", set())}
    return any(candidate in modules for candidate in candidates)


def signal_has_reference(signals: dict[str, Any], candidates: set[str]) -> bool:
    references = {str(item).lower() for item in signals.get("references", set())}
    for raw_candidate in candidates:
        candidate = normalize_reference(raw_candidate)
        if not candidate:
            continue
        if candidate.endswith("("):
            candidate = candidate[:-1]
        if candidate.endswith("."):
            if any(ref.startswith(candidate) for ref in references):
                return True
            continue
        if candidate in references:
            return True
    return False


def signal_has_env(signals: dict[str, Any], candidates: set[str]) -> bool:
    env_names = {str(item).upper() for item in signals.get("env_names", [])}
    wanted = {str(item).upper() for item in candidates}
    return any(candidate in env_names for candidate in wanted)


def read_classification(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for idx, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        if idx == 0 or not raw.strip():
            continue
        cols = raw.split("\t")
        if len(cols) < 5:
            continue
        rel, category, included, reason, ext = cols[:5]
        rows[rel] = {
            "category": category,
            "included": included.lower() == "true",
            "reason": reason,
            "ext": ext.lower(),
        }
    return rows


def component_prefix(rel_path: str, depth: int) -> str:
    parts = list(Path(rel_path).with_suffix("").parts[:-1])
    if not parts:
        return Path(rel_path).with_suffix("").name or rel_path
    trimmed = list(parts)
    while len(trimmed) > 1 and trimmed[0] in GENERIC_DIRS:
        trimmed.pop(0)
    return "/".join(trimmed[:depth] or parts[:depth] or parts)


def component_label(prefix: str) -> str:
    parts = [p for p in Path(prefix).parts if p]
    if not parts:
        return "Unknown Component"
    focus = parts[-2:] if len(parts) >= 2 else parts
    return " · ".join(humanize_token(part) for part in focus)


def load_file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def build_python_module_index(code_files: list[str]) -> dict[str, str]:
    modules: dict[str, str] = {}
    for rel_path in code_files:
        parts = list(Path(rel_path).with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        module_name = ".".join(parts)
        if module_name:
            modules[module_name] = rel_path
    return modules


def resolve_relative_import(importer: str, hint: str, code_files_by_noext: dict[str, str], code_exts: set[str]) -> str | None:
    importer_dir = Path(importer).parent
    target = (importer_dir / hint).resolve().as_posix()
    repo_free = None
    for rel_noext, rel_path in code_files_by_noext.items():
        abs_noext = (importer_dir / hint).with_suffix("").as_posix()
        if rel_noext == abs_noext:
            repo_free = rel_path
            break
    if repo_free:
        return repo_free

    base = str((importer_dir / hint).with_suffix(""))
    candidates = [code_files_by_noext.get(base)]
    candidates.extend(code_files_by_noext.get(f"{base}/index") for _ in [0])
    for candidate in candidates:
        if candidate:
            return candidate
    return None


def resolve_import_hint(
    importer: str,
    hint: str,
    *,
    code_files: set[str],
    code_files_by_noext: dict[str, str],
    py_modules: dict[str, str],
) -> str | None:
    normalized = (hint or "").strip().replace("\\", "/")
    if not normalized:
        return None

    if normalized.startswith("."):
        return resolve_relative_import(importer, normalized, code_files_by_noext, set())

    if normalized in py_modules:
        return py_modules[normalized]

    path_like = normalized.replace(".", "/")
    if path_like in code_files_by_noext:
        return code_files_by_noext[path_like]
    if f"{path_like}/index" in code_files_by_noext:
        return code_files_by_noext[f"{path_like}/index"]

    matches = [rel for rel in code_files if rel.endswith(f"/{path_like}.py") or rel.endswith(f"/{path_like}.ts") or rel.endswith(f"/{path_like}.tsx") or rel.endswith(f"/{path_like}.js") or rel.endswith(f"/{path_like}.jsx") or rel.endswith(f"/{path_like}.java") or rel.endswith(f"/{path_like}.go")]
    if len(matches) == 1:
        return matches[0]
    return None


def extract_import_targets(
    rel_path: str,
    text: str,
    ext: str,
    *,
    code_files: set[str],
    code_files_by_noext: dict[str, str],
    py_modules: dict[str, str],
) -> list[dict[str, Any]]:
    hints: list[tuple[str, str]] = []
    if ext == ".py":
        try:
            tree = ast.parse(text)
        except Exception:
            tree = None
        if tree is not None:
            current_parts = list(Path(rel_path).with_suffix("").parts)
            if current_parts and current_parts[-1] == "__init__":
                current_parts = current_parts[:-1]
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        hints.append((alias.name, "python-import"))
                elif isinstance(node, ast.ImportFrom):
                    level = int(getattr(node, "level", 0) or 0)
                    module_part = node.module or ""
                    base_parts = current_parts[:-level] if level > 0 and level <= len(current_parts) else []
                    resolved = ".".join([*base_parts, module_part]).strip(".")
                    if resolved:
                        hints.append((resolved, "python-import-from"))
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        candidate = f"{resolved}.{alias.name}".strip(".") if resolved else alias.name
                        hints.append((candidate, "python-import-from"))
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        for match in re.finditer(r"""from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)""", text):
            hints.append((match.group(1) or match.group(2), "module-import"))
    elif ext == ".go":
        for block in re.finditer(r'import\s*\((.*?)\)', text, re.S):
            for item in re.finditer(r'"([^"]+)"', block.group(1)):
                hints.append((item.group(1), "go-import"))
        for single in re.finditer(r'import\s+"([^"]+)"', text):
            hints.append((single.group(1), "go-import"))
    elif ext == ".java":
        for match in re.finditer(r'import\s+([A-Za-z0-9_.*]+);', text):
            hints.append((match.group(1).rstrip(".*"), "java-import"))
    elif ext == ".rb":
        for match in re.finditer(r'require_relative\s+[\'"]([^\'"]+)[\'"]', text):
            hints.append((match.group(1), "ruby-require-relative"))
    elif ext in {".c", ".cc", ".cpp", ".h", ".hpp"}:
        for match in re.finditer(r'#include\s+"([^"]+)"', text):
            hints.append((match.group(1), "include"))

    relations: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for hint, kind in hints:
        target = resolve_import_hint(
            rel_path,
            hint,
            code_files=code_files,
            code_files_by_noext=code_files_by_noext,
            py_modules=py_modules,
        )
        if not target or target == rel_path:
            continue
        sig = (target, kind)
        if sig in seen:
            continue
        seen.add(sig)
        relations.append({"target": target, "kind": kind})
    return relations


def detect_python_entrypoints(rel_path: str, text: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except Exception:
        tree = None
    if tree is None:
        return []

    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    has_main_guard = False
    main_function_name = "main"

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            try:
                test_text = ast.unparse(node.test).replace(" ", "")
            except Exception:
                test_text = ""
            if "__name__=='__main__'" in test_text or '__name__=="__main__"' in test_text:
                has_main_guard = True

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {"main", "cli", "run"}:
            main_function_name = node.name

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        try:
            decorators = [ast.unparse(d) for d in node.decorator_list]
        except Exception:
            decorators = []
        deco_text = " ".join(decorators).lower()
        route_match = re.search(r"\.(get|post|put|delete|patch|route|websocket)\(([^)]*)\)", deco_text)
        if route_match:
            method = route_match.group(1).upper()
            path_match = re.search(r"""['"]([^'"]+)['"]""", route_match.group(2))
            route = path_match.group(1) if path_match else f"/{node.name}"
            sig = ("http-route", method, route)
            if sig not in seen:
                seen.add(sig)
                items.append(
                    {
                        "kind": "http-route",
                        "label": f"{method} {route}",
                        "symbol": node.name,
                        "provenance": "python-decorator",
                        "route": route,
                        "method": method,
                        "evidence_refs": [rel_path],
                    }
                )

        if any(token in deco_text for token in ["command", "click", "typer"]):
            sig = ("cli-command", node.name, rel_path)
            if sig not in seen:
                seen.add(sig)
                items.append(
                    {
                        "kind": "cli-command",
                        "label": node.name,
                        "symbol": node.name,
                        "provenance": "python-decorator",
                        "evidence_refs": [rel_path],
                    }
                )

        if any(token in deco_text for token in ["task", "cron", "schedule", "job"]):
            sig = ("scheduled-job", node.name, rel_path)
            if sig not in seen:
                seen.add(sig)
                items.append(
                    {
                        "kind": "scheduled-job",
                        "label": node.name,
                        "symbol": node.name,
                        "provenance": "python-decorator",
                        "evidence_refs": [rel_path],
                    }
                )

        if any(token in deco_text for token in ["consumer", "listener", "subscribe", "on_event"]):
            sig = ("queue-consumer", node.name, rel_path)
            if sig not in seen:
                seen.add(sig)
                items.append(
                    {
                        "kind": "queue-consumer",
                        "label": node.name,
                        "symbol": node.name,
                        "provenance": "python-decorator",
                        "evidence_refs": [rel_path],
                    }
                )

    if has_main_guard:
        items.append(
            {
                "kind": "cli-startup",
                "label": f"{Path(rel_path).stem} {main_function_name}",
                "symbol": main_function_name,
                "provenance": "python-main-guard",
                "evidence_refs": [rel_path],
            }
        )

    return items


def detect_regex_entrypoints(rel_path: str, text: str, ext: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    def append(kind: str, label: str, provenance: str, symbol: str = "") -> None:
        items.append(
            {
                "kind": kind,
                "label": label,
                "symbol": symbol,
                "provenance": provenance,
                "evidence_refs": [rel_path],
            }
        )

    if ext in {".js", ".jsx", ".ts", ".tsx"}:
        for match in re.finditer(r"""(?:app|router)\.(get|post|put|delete|patch)\(\s*['"]([^'"]+)['"]""", text, re.I):
            append("http-route", f"{match.group(1).upper()} {match.group(2)}", "module-route")
        for match in re.finditer(r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)\b", text):
            append("http-route", f"{match.group(1).upper()} {Path(rel_path).parent.as_posix()}", "exported-route")
        if re.search(r"\bprocess\.argv\b|\b\.command\(", text):
            append("cli-command", Path(rel_path).stem, "cli-pattern")
        if re.search(r"@Cron\b|schedule\.", text):
            append("scheduled-job", Path(rel_path).stem, "scheduler-pattern")
        if re.search(r"@Processor\b|@OnEvent\b|consumer\b|subscribe\b", text):
            append("queue-consumer", Path(rel_path).stem, "queue-pattern")
    elif ext == ".go":
        if re.search(r"\bfunc\s+main\s*\(", text):
            append("cli-startup", f"{Path(rel_path).stem} main", "go-main", "main")
        for match in re.finditer(r"""(?:HandleFunc|GET|POST|PUT|DELETE)\s*\(\s*["`]([^"`]+)["`]""", text):
            append("http-route", match.group(1), "go-route")
    elif ext == ".java":
        if re.search(r"public\s+static\s+void\s+main\s*\(", text):
            append("cli-startup", f"{Path(rel_path).stem} main", "java-main", "main")
        for match in re.finditer(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(([^)]*)\)', text):
            method = match.group(1).replace("Mapping", "").upper()
            route_match = re.search(r"""['"]([^'"]+)['"]""", match.group(2))
            route = route_match.group(1) if route_match else Path(rel_path).stem
            append("http-route", f"{method} {route}", "java-route")
        if re.search(r"@Scheduled\b", text):
            append("scheduled-job", Path(rel_path).stem, "java-scheduled")
        if re.search(r"@KafkaListener\b|@RabbitListener\b", text):
            append("queue-consumer", Path(rel_path).stem, "java-listener")
    elif ext == ".rb":
        if re.search(r"\bOptionParser\b|\bARGV\b", text):
            append("cli-command", Path(rel_path).stem, "ruby-cli")
    elif ext == ".php":
        if re.search(r"\$argv\b|\bSymfony\\Component\\Console\\", text):
            append("cli-command", Path(rel_path).stem, "php-cli")

    return items


def detect_entrypoints(rel_path: str, text: str, ext: str) -> list[dict[str, Any]]:
    items = detect_python_entrypoints(rel_path, text) if ext == ".py" else []
    items.extend(detect_regex_entrypoints(rel_path, text, ext))
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        sig = (str(item.get("kind", "")), str(item.get("label", "")), str(item.get("symbol", "")))
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(item)
    return deduped


def guess_container_kind(rel_path: str, ext: str, entrypoints: list[dict[str, Any]]) -> str:
    path_text = rel_path.lower()
    kinds = {str(item.get("kind", "")) for item in entrypoints}
    if "http-route" in kinds:
        return "api"
    if any(kind in kinds for kind in {"scheduled-job", "queue-consumer", "worker-task", "event-handler"}):
        return "worker"
    if any(kind in kinds for kind in {"cli-command", "cli-startup"}):
        return "cli"
    if any(token in path_text for token in ["/worker/", "/workers/", "/job/", "/jobs/", "/queue/", "/consumer/", "/scheduler/", "/cron/"]):
        return "worker"
    if any(token in path_text for token in ["/api/", "/server/", "/routes/", "/controllers/", "/handlers/"]):
        return "api"
    if "test" in path_text or path_text.startswith("tests/"):
        return "test"
    if ext in {".tsx", ".jsx"} or any(token in path_text for token in ["/ui/", "/gui/", "/frontend/", "/pages/", "/components/", "/web/"]):
        return "frontend"
    if any(token in path_text for token in ["docker", "k8s", "kubernetes", "terraform", "helm"]):
        return "deployment"
    return "core"


def detect_external_interfaces(rel_path: str, signals: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for kind, config in EXTERNAL_INTERFACE_HINTS.items():
        if signal_has_module(signals, set(config.get("modules", set()))) or signal_has_reference(
            signals, set(config.get("references", set()))
        ) or signal_has_env(
            signals, set(config.get("envs", set()))
        ):
            label = str(config.get("label", humanize_token(kind)))
            sig = (kind, label)
            if sig in seen:
                continue
            seen.add(sig)
            findings.append(
                {
                    "kind": kind,
                    "label": label,
                    "provenance": "signal-match",
                    "evidence_refs": [rel_path],
                }
            )

    for pattern, label in HTTP_LIB_PATTERNS:
        if signal_has_module(signals, {pattern}) or signal_has_reference(signals, {pattern, f"{pattern}.get", f"{pattern}.post"}):
            sig = ("external-http", label)
            if sig in seen:
                continue
            seen.add(sig)
            findings.append(
                {
                    "kind": "external-http",
                    "label": label,
                    "provenance": "signal-match",
                    "evidence_refs": [rel_path],
                }
            )

    for url in signals.get("urls", []):
        findings.append(
            {
                "kind": "external-http",
                "label": url,
                "provenance": "literal-url",
                "evidence_refs": [rel_path],
            }
        )
    return findings


def detect_crosscutting(rel_path: str, signals: dict[str, Any]) -> dict[str, list[str]]:
    matched: dict[str, list[str]] = {}
    for concept, config in CROSSCUTTING_HINTS.items():
        if signal_has_module(signals, set(config.get("modules", set()))) or signal_has_reference(
            signals, set(config.get("references", set()))
        ) or signal_has_env(
            signals, set(config.get("envs", set()))
        ):
            matched.setdefault(concept, []).append(rel_path)
    return matched


def detect_deployment_units(files: dict[str, dict[str, Any]], repo_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []

    def add_node(kind: str, label: str, file_path: str) -> None:
        node_id = slugify(f"{kind}-{label}")
        if any(node["id"] == node_id for node in nodes):
            return
        nodes.append(
            {
                "id": node_id,
                "kind": kind,
                "label": label,
                "evidence_refs": [file_path],
            }
        )

    relation_keys: set[tuple[str, str, str]] = set()

    def add_relation(src: str, dst: str, label: str, refs: list[str]) -> None:
        key = (src, dst, label)
        if key in relation_keys:
            return
        relation_keys.add(key)
        relations.append(
            {
                "from": src,
                "to": dst,
                "label": label,
                "evidence_refs": sorted({ref for ref in refs if ref}),
            }
        )

    for rel_path in sorted(files):
        file_name = Path(rel_path).name.lower()
        lowered_rel = rel_path.lower()
        abs_path = repo_path / rel_path
        text = load_file_text(abs_path)
        if file_name in KNOWN_DEPLOYMENT_FILES:
            kind, label = KNOWN_DEPLOYMENT_FILES[file_name]
            add_node(kind, label, rel_path)
        if file_name.startswith("dockerfile"):
            add_node("container-image", "Application Image", rel_path)
        if file_name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            add_node("orchestrator", "Compose Stack", rel_path)
            stack_id = slugify("orchestrator-Compose Stack")
            for match in re.finditer(r"^\s{2}([A-Za-z0-9_-]+):\s*$", text, re.M):
                service_label = humanize_token(match.group(1))
                add_node("service", service_label, rel_path)
                add_relation(stack_id, slugify(f"service-{service_label}"), "manages", [rel_path])
        if file_name in {"chart.yaml", "values.yaml"} or "/helm/" in lowered_rel:
            add_node("orchestrator", "Helm Release", rel_path)
        if re.search(r"\.(ya?ml)$", file_name) and any(token in lowered_rel for token in ["k8s", "kubernetes", "manifests", "deploy"]):
            for match in re.finditer(r"kind:\s*([A-Za-z0-9]+)", text):
                add_node("k8s-resource", humanize_token(match.group(1)), rel_path)
        if file_name.endswith(".tf"):
            add_node("iac", "Terraform", rel_path)
            for match in re.finditer(r'resource\s+"([^"]+)"\s+"([^"]+)"', text):
                add_node("resource", humanize_token(match.group(1)), rel_path)
        if file_name == "procfile":
            add_node("process-manager", "Procfile", rel_path)
            manager_id = slugify("process-manager-Procfile")
            for match in re.finditer(r"^([A-Za-z0-9_-]+):", text, re.M):
                process_label = humanize_token(match.group(1))
                add_node("process", process_label, rel_path)
                add_relation(manager_id, slugify(f"process-{process_label}"), "defines", [rel_path])
        if lowered_rel.startswith(".github/workflows/") and file_name.endswith((".yml", ".yaml")):
            add_node("ci-pipeline", "GitHub Actions", rel_path)
            pipeline_id = slugify("ci-pipeline-GitHub Actions")
            if re.search(r"docker/build-push-action|docker build", text):
                add_node("container-image", "Application Image", rel_path)
                add_relation(pipeline_id, slugify("container-image-Application Image"), "builds", [rel_path])
            if re.search(r"kubectl|helm|kustomize", text):
                add_node("orchestrator", "Cluster Delivery", rel_path)
                add_relation(pipeline_id, slugify("orchestrator-Cluster Delivery"), "deploys", [rel_path])

    if not relations and len(nodes) >= 2:
        sorted_nodes = [node for node in nodes if node["kind"] not in {"resource", "k8s-resource"}]
        if len(sorted_nodes) >= 2:
            add_relation(
                sorted_nodes[0]["id"],
                sorted_nodes[1]["id"],
                "deploys to",
                [ref for node in sorted_nodes[:2] for ref in node.get("evidence_refs", [])],
            )

    return nodes, relations


def infer_container_kind_from_command(command: str) -> str:
    lowered = (command or "").lower()
    if any(token in lowered for token in ["uvicorn", "gunicorn", "flask", "django", "fastapi", "express", "koa", "nest", "spring", "serve", "start-server"]):
        return "api"
    if any(token in lowered for token in ["next", "vite", "webpack", "react", "nuxt", "svelte", "frontend", "webapp"]):
        return "frontend"
    if any(token in lowered for token in ["worker", "queue", "consumer", "celery", "beat", "cron", "scheduler"]):
        return "worker"
    return "cli"


def infer_container_kind_from_label(label: str) -> str | None:
    lowered = (label or "").lower()
    if any(token in lowered for token in ["web", "api", "server", "backend", "service"]):
        return "api"
    if any(token in lowered for token in ["front", "ui", "client", "webapp", "site"]):
        return "frontend"
    if any(token in lowered for token in ["worker", "queue", "consumer", "scheduler", "cron", "job", "beat"]):
        return "worker"
    if any(token in lowered for token in ["cli", "command", "tool"]):
        return "cli"
    return None


def infer_container_kind_from_path(path: str) -> str | None:
    lowered = (path or "").lower()
    if any(token in lowered for token in ["/worker/", "/workers/", "/job/", "/jobs/", "/queue/", "/consumer/", "/scheduler/", "/cron/"]):
        return "worker"
    if any(token in lowered for token in ["/api/", "/server/", "/routes/", "/controllers/", "/handlers/"]):
        return "api"
    if any(token in lowered for token in ["/ui/", "/frontend/", "/pages/", "/components/", "/web/"]):
        return "frontend"
    return None


def extract_command_paths(command: str) -> list[str]:
    paths: list[str] = []
    for match in re.finditer(r"([A-Za-z0-9_./-]+\.(?:py|js|jsx|ts|tsx|go|java|rb|php|sh))", command or ""):
        paths.append(match.group(1))
    return paths


def load_toml(path: Path) -> dict[str, Any]:
    if not tomllib or not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect_manifest_entrypoints(files: dict[str, dict[str, Any]], repo_path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def append(*, rel_path: str, kind: str, label: str, command: str, provenance: str, container_hint: str) -> None:
        sig = (rel_path, kind, label)
        if sig in seen:
            return
        seen.add(sig)
        items.append(
            {
                "kind": kind,
                "label": label,
                "symbol": label,
                "file": rel_path,
                "provenance": provenance,
                "evidence_refs": [rel_path],
                "command": command,
                "container_hint": container_hint,
                "command_paths": extract_command_paths(command),
            }
        )

    for rel_path in sorted(files):
        file_name = Path(rel_path).name.lower()
        abs_path = repo_path / rel_path
        if file_name == "package.json":
            payload = load_json(abs_path, {})
            scripts = payload.get("scripts", {}) if isinstance(payload, dict) else {}
            if isinstance(scripts, dict):
                for name, command in scripts.items():
                    if not isinstance(command, str):
                        continue
                    lowered = name.lower()
                    kind = "cli-startup" if lowered in {"start", "serve", "dev", "preview"} else "worker-task" if any(token in lowered for token in ["worker", "queue", "consumer", "cron", "job"]) else "cli-command"
                    append(
                        rel_path=rel_path,
                        kind=kind,
                        label=f"npm run {name}",
                        command=command,
                        provenance="package-json-script",
                        container_hint=infer_container_kind_from_command(command),
                    )
        elif file_name == "pyproject.toml":
            payload = load_toml(abs_path)
            project_scripts = payload.get("project", {}).get("scripts", {}) if isinstance(payload, dict) else {}
            poetry_scripts = payload.get("tool", {}).get("poetry", {}).get("scripts", {}) if isinstance(payload, dict) else {}
            for source_name, scripts in [("pyproject-project-script", project_scripts), ("poetry-script", poetry_scripts)]:
                if not isinstance(scripts, dict):
                    continue
                for name, command in scripts.items():
                    command_text = command if isinstance(command, str) else json.dumps(command, ensure_ascii=False)
                    append(
                        rel_path=rel_path,
                        kind="cli-command",
                        label=name,
                        command=command_text,
                        provenance=source_name,
                        container_hint=infer_container_kind_from_command(command_text),
                    )
        elif file_name == "procfile":
            text = load_file_text(abs_path)
            for match in re.finditer(r"^([A-Za-z0-9_-]+):\s*(.+)$", text, re.M):
                proc_name = match.group(1)
                command = match.group(2).strip()
                lowered = proc_name.lower()
                kind = "cli-startup" if lowered == "web" else "worker-task"
                append(
                    rel_path=rel_path,
                    kind=kind,
                    label=f"proc {proc_name}",
                    command=command,
                    provenance="procfile",
                    container_hint=infer_container_kind_from_label(proc_name) or infer_container_kind_from_command(command),
                )
        elif file_name == "makefile":
            text = load_file_text(abs_path)
            for match in re.finditer(r"^([A-Za-z0-9_.-]+):(?:\s|$)", text, re.M):
                target = match.group(1)
                lowered = target.lower()
                if lowered.startswith("."):
                    continue
                if lowered not in {"run", "serve", "start", "dev", "worker", "test"}:
                    continue
                kind = "cli-startup" if lowered in {"run", "serve", "start", "dev"} else "worker-task" if lowered == "worker" else "cli-command"
                append(
                    rel_path=rel_path,
                    kind=kind,
                    label=f"make {target}",
                    command=target,
                    provenance="make-target",
                    container_hint=infer_container_kind_from_command(target),
                )

    return items


def extract_trace_spans(payload: Any) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []

    def normalize_attributes(raw: Any) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                if isinstance(value, dict):
                    if "stringValue" in value:
                        result[key] = value["stringValue"]
                    elif "intValue" in value:
                        result[key] = value["intValue"]
                    elif "doubleValue" in value:
                        result[key] = value["doubleValue"]
                    elif "boolValue" in value:
                        result[key] = value["boolValue"]
                    elif "value" in value:
                        result[key] = value["value"]
                else:
                    result[key] = value
        elif isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                key = item.get("key")
                value = item.get("value")
                if not key:
                    continue
                if isinstance(value, dict):
                    if "stringValue" in value:
                        result[key] = value["stringValue"]
                    elif "intValue" in value:
                        result[key] = value["intValue"]
                    elif "doubleValue" in value:
                        result[key] = value["doubleValue"]
                    elif "boolValue" in value:
                        result[key] = value["boolValue"]
                else:
                    result[key] = value
        return result

    def walk(node: Any, inherited_trace_id: str = "", inherited_resource: dict[str, Any] | None = None) -> None:
        resource_attrs = dict(inherited_resource or {})
        if isinstance(node, dict):
            current_trace_id = str(node.get("traceId") or inherited_trace_id or "")
            if "resource" in node and isinstance(node["resource"], dict):
                resource_attrs.update(normalize_attributes(node["resource"].get("attributes")))
            if "resourceSpans" in node and isinstance(node["resourceSpans"], list):
                for item in node["resourceSpans"]:
                    walk(item, current_trace_id, resource_attrs)
            if "scopeSpans" in node and isinstance(node["scopeSpans"], list):
                for item in node["scopeSpans"]:
                    walk(item, current_trace_id, resource_attrs)
            if "instrumentationLibrarySpans" in node and isinstance(node["instrumentationLibrarySpans"], list):
                for item in node["instrumentationLibrarySpans"]:
                    walk(item, current_trace_id, resource_attrs)
            if "spans" in node and isinstance(node["spans"], list):
                for span in node["spans"]:
                    walk(span, current_trace_id, resource_attrs)
            if node.get("name") and ("spanId" in node or "id" in node):
                attrs = normalize_attributes(node.get("attributes"))
                merged_attrs = dict(resource_attrs)
                merged_attrs.update(attrs)
                spans.append(
                    {
                        "trace_id": str(node.get("traceId") or current_trace_id or ""),
                        "span_id": str(node.get("spanId") or node.get("id") or ""),
                        "parent_span_id": str(node.get("parentSpanId") or node.get("parent_id") or ""),
                        "name": str(node.get("name")),
                        "duration": safe_int(node.get("durationNanoseconds") or node.get("duration") or 0),
                        "attributes": merged_attrs,
                    }
                )
        elif isinstance(node, list):
            for item in node:
                walk(item, inherited_trace_id, inherited_resource)

    walk(payload)
    return [span for span in spans if span.get("span_id") or span.get("name")]


def build_trace_scenarios(
    *,
    trace_input: Any,
    entrypoints: list[dict[str, Any]],
    max_scenarios: int,
    max_steps: int,
) -> list[dict[str, Any]]:
    spans = extract_trace_spans(trace_input)
    if not spans:
        return []

    by_trace: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for span in spans:
        by_trace[str(span.get("trace_id") or "trace-unknown")].append(span)

    scenarios: list[dict[str, Any]] = []
    for trace_id, trace_spans in by_trace.items():
        children: dict[str, list[dict[str, Any]]] = defaultdict(list)
        ids = {str(span.get("span_id", "")) for span in trace_spans}
        roots: list[dict[str, Any]] = []
        for span in trace_spans:
            parent_id = str(span.get("parent_span_id", ""))
            if parent_id and parent_id in ids:
                children[parent_id].append(span)
            else:
                roots.append(span)
        for root in roots:
            path = [root]
            current = root
            visited = {str(root.get("span_id", ""))}
            while len(path) < max_steps and children.get(str(current.get("span_id", ""))):
                next_candidates = sorted(children[str(current.get("span_id", ""))], key=lambda item: item.get("duration", 0), reverse=True)
                next_span = None
                for candidate in next_candidates:
                    candidate_id = str(candidate.get("span_id", ""))
                    if candidate_id and candidate_id not in visited:
                        next_span = candidate
                        break
                if not next_span:
                    break
                visited.add(str(next_span.get("span_id", "")))
                path.append(next_span)
                current = next_span

            participants: list[str] = []
            steps: list[dict[str, Any]] = []
            for idx, span in enumerate(path):
                attrs = span.get("attributes", {})
                participant = (
                    str(attrs.get("service.name"))
                    or str(attrs.get("code.namespace"))
                    or str(attrs.get("http.route"))
                    or str(attrs.get("messaging.destination"))
                    or humanize_token(str(span.get("name", "Span")))
                )
                participant = humanize_token(participant)
                participants.append(participant)
                if idx == 0:
                    continue
                steps.append(
                    {
                        "from": participants[idx - 1],
                        "to": participant,
                        "action": humanize_token(str(span.get("name", "trace step"))),
                    }
                )

            root_name = str(root.get("name", "Trace"))
            linked_entrypoint = None
            for entrypoint in entrypoints:
                label = str(entrypoint.get("label", "")).lower()
                if label and label in root_name.lower():
                    linked_entrypoint = entrypoint
                    break

            scenarios.append(
                {
                    "title": humanize_token(root_name),
                    "entrypoint_id": linked_entrypoint.get("id") if linked_entrypoint else None,
                    "source": "trace",
                    "fallback": False,
                    "participants": list(dict.fromkeys(participants)),
                    "steps": steps,
                    "evidence_refs": ["artifacts/dynamic/trace-input.json"],
                    "provenance": [
                        {
                            "source": "trace-input",
                            "refs": ["artifacts/dynamic/trace-input.json"],
                        }
                    ],
                    "trace_id": trace_id,
                }
            )

    scenarios.sort(key=lambda item: len(item.get("steps", [])), reverse=True)
    return scenarios[:max_scenarios]


def build_static_scenarios(
    *,
    entrypoints: list[dict[str, Any]],
    component_relations: list[dict[str, Any]],
    component_nodes: dict[str, dict[str, Any]],
    interface_items: list[dict[str, Any]],
    max_scenarios: int,
    max_steps: int,
) -> list[dict[str, Any]]:
    adjacency: dict[str, list[tuple[str, int, str, list[str]]]] = defaultdict(list)
    for relation in component_relations:
        src = str(relation.get("from", ""))
        dst = str(relation.get("to", ""))
        if not src or not dst or src == dst:
            continue
        adjacency[src].append(
            (
                dst,
                safe_int(relation.get("weight", 1), 1),
                str(relation.get("label", "의존 호출")),
                list(relation.get("evidence_refs", [])),
            )
        )
    for src in list(adjacency.keys()):
        adjacency[src].sort(key=lambda item: item[1], reverse=True)

    interfaces_by_component: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in interface_items:
        if not isinstance(item, dict):
            continue
        component_id = str(item.get("source_component_id", "")).strip()
        if not component_id:
            continue
        interfaces_by_component[component_id].append(item)
    for component_id in list(interfaces_by_component.keys()):
        interfaces_by_component[component_id].sort(key=lambda item: safe_int(item.get("weight", 1), 1), reverse=True)

    def best_path(start: str) -> list[tuple[str, str, str, list[str]]]:
        current = start
        visited = {start}
        path: list[tuple[str, str, str, list[str]]] = []
        while len(path) < max_steps - 1 and adjacency.get(current):
            next_edge = None
            for dst, weight, label, refs in adjacency[current]:
                if dst not in visited:
                    next_edge = (current, dst, label, refs)
                    break
            if not next_edge:
                break
            _, dst, _, _ = next_edge
            visited.add(dst)
            path.append(next_edge)
            current = dst
        return path

    scored_entrypoints = sorted(
        entrypoints,
        key=lambda item: (
            ENTRYPOINT_KIND_PRIORITY.get(str(item.get("kind", "")), 99),
            -len(adjacency.get(str(item.get("component_id", "")), [])),
        ),
    )

    scenarios: list[dict[str, Any]] = []
    for entrypoint in scored_entrypoints[:max_scenarios]:
        start_component = str(entrypoint.get("component_id", ""))
        if not start_component or start_component not in component_nodes:
            continue
        path = best_path(start_component)

        participants = [component_nodes[start_component]["label"]]
        steps: list[dict[str, Any]] = []
        evidence_refs = list(entrypoint.get("evidence_refs", []))
        if not path:
            start_label = component_nodes[start_component]["label"]
            component_interfaces = interfaces_by_component.get(start_component, [])
            if component_interfaces:
                top_interfaces = component_interfaces[: min(2, max_steps - 1)]
                for idx, interface in enumerate(top_interfaces):
                    target_label = str(interface.get("target_label", interface.get("kind", "External System")))
                    if idx == 0:
                        steps.append(
                            {
                                "from": start_label,
                                "to": target_label,
                                "action": f"{entrypoint.get('label') or entrypoint.get('kind') or 'entrypoint'} 처리 후 {interface.get('kind', 'external')} 호출",
                            }
                        )
                    else:
                        steps.append(
                            {
                                "from": start_label,
                                "to": target_label,
                                "action": f"{interface.get('kind', 'external')} 연계",
                            }
                        )
                    participants.append(target_label)
                    evidence_refs.extend(interface.get("evidence_refs", []))
            else:
                steps.append(
                    {
                        "from": start_label,
                        "to": start_label,
                        "action": f"{entrypoint.get('label') or entrypoint.get('kind') or 'entrypoint'} 처리",
                    }
                )
        else:
            for src, dst, label, refs in path:
                participants.append(component_nodes[dst]["label"])
                steps.append(
                    {
                        "from": component_nodes[src]["label"],
                        "to": component_nodes[dst]["label"],
                        "action": label or "의존 호출",
                    }
                )
                evidence_refs.extend(refs)
            terminal_component = path[-1][1]
            terminal_interfaces = interfaces_by_component.get(terminal_component, [])
            if terminal_interfaces and len(steps) < max_steps:
                terminal_label = component_nodes[terminal_component]["label"]
                interface = terminal_interfaces[0]
                target_label = str(interface.get("target_label", interface.get("kind", "External System")))
                steps.append(
                    {
                        "from": terminal_label,
                        "to": target_label,
                        "action": f"{interface.get('kind', 'external')} 연계",
                    }
                )
                participants.append(target_label)
                evidence_refs.extend(interface.get("evidence_refs", []))

        scenarios.append(
            {
                "title": str(entrypoint.get("label") or entrypoint.get("symbol") or component_nodes[start_component]["label"]),
                "entrypoint_id": entrypoint.get("id"),
                "source": "static-entrypoint",
                "fallback": False,
                "participants": list(dict.fromkeys(participants)),
                "steps": steps,
                "evidence_refs": sorted({ref for ref in evidence_refs if ref}),
                "provenance": [
                    {
                        "source": "entrypoint+component-relations",
                        "refs": sorted({ref for ref in evidence_refs if ref}),
                    }
                ],
            }
        )

    return scenarios[:max_scenarios]


def dedupe_scenarios(scenarios: list[dict[str, Any]], max_scenarios: int) -> list[dict[str, Any]]:
    ranked = sorted(
        scenarios,
        key=lambda item: (
            1 if item.get("source") == "trace" else 0,
            0 if item.get("entrypoint_id") else -1,
            len(item.get("steps", [])),
            len(item.get("participants", [])),
        ),
        reverse=True,
    )
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for scenario in ranked:
        if not isinstance(scenario, dict):
            continue
        step_signature = tuple(
            f"{step.get('from','')}->{step.get('to','')}:{step.get('action','')}"
            for step in scenario.get("steps", [])
            if isinstance(step, dict)
        )
        key = (
            str(scenario.get("entrypoint_id") or ""),
            str(scenario.get("title") or ""),
            step_signature,
        )
        if key in seen:
            continue
        seen.add(key)
        selected.append(scenario)
        if len(selected) >= max_scenarios:
            break
    return selected


def main() -> int:
    args = parse_args()
    repo_path = Path(args.repo_path).expanduser().resolve()
    artifacts_dir = Path(args.artifacts_dir).expanduser().resolve()
    arch_dir = artifacts_dir / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)

    policy = load_json(Path(args.policy).expanduser().resolve(), {})
    arch_policy = policy.get("architecture_model", {}) if isinstance(policy, dict) else {}
    component_depth = safe_int(arch_policy.get("component_depth"), 3)
    max_components = safe_int(arch_policy.get("max_components"), 18)
    max_container_edges = safe_int(arch_policy.get("max_container_edges"), 16)
    max_component_edges = safe_int(arch_policy.get("max_component_edges"), 24)
    max_scenarios = safe_int(arch_policy.get("max_scenarios"), 4)
    max_scenario_steps = safe_int(arch_policy.get("max_scenario_steps"), 7)
    max_decision_candidates = safe_int(arch_policy.get("max_decision_candidates"), 6)

    classification = read_classification(artifacts_dir / "static" / "path-classification.tsv")
    complexity = load_json(artifacts_dir / "static" / "complexity.json", {})
    architecture = load_json(artifacts_dir / "static" / "architecture.json", {})
    trace_input = load_json(artifacts_dir / "dynamic" / "trace-input.json", {})

    complexity_rows = complexity.get("top_files", []) if isinstance(complexity, dict) else []
    complexity_by_file = {
        str(row.get("file")): row
        for row in complexity_rows
        if isinstance(row, dict) and row.get("file")
    }
    architecture_rows = architecture.get("all_files", []) if isinstance(architecture, dict) else []
    coupling_by_file = {
        str(row.get("file")): safe_int(row.get("coupling_score"), 0)
        for row in architecture_rows
        if isinstance(row, dict) and row.get("file")
    }

    code_exts = set(policy.get("collection", {}).get("code_extensions", [])) if isinstance(policy, dict) else set()
    code_files = [
        rel_path
        for rel_path, meta in classification.items()
        if meta.get("included") and meta.get("ext") in code_exts and meta.get("category") in {"code", "config", "test"}
    ]
    code_file_set = set(code_files)
    code_files_by_noext = {str(Path(rel).with_suffix("")): rel for rel in code_files}
    py_modules = build_python_module_index(code_files)

    file_records: dict[str, dict[str, Any]] = {}
    entrypoints: list[dict[str, Any]] = []
    all_internal_relations: list[dict[str, Any]] = []
    all_external_interfaces: list[dict[str, Any]] = []
    crosscutting_hits: dict[str, set[str]] = defaultdict(set)

    for rel_path in code_files:
        abs_path = repo_path / rel_path
        text = load_file_text(abs_path)
        ext = classification.get(rel_path, {}).get("ext", Path(rel_path).suffix.lower())
        signals = extract_signal_features(rel_path, text, ext)
        file_entrypoints = detect_entrypoints(rel_path, text, ext)
        container_kind = guess_container_kind(rel_path, ext, file_entrypoints)
        component_id = component_prefix(rel_path, component_depth)
        component_name = component_label(component_id)
        imports = extract_import_targets(
            rel_path,
            text,
            ext,
            code_files=code_file_set,
            code_files_by_noext=code_files_by_noext,
            py_modules=py_modules,
        )
        external_interfaces = detect_external_interfaces(rel_path, signals)
        crosscut = detect_crosscutting(rel_path, signals)

        file_records[rel_path] = {
            "file": rel_path,
            "ext": ext,
            "category": classification.get(rel_path, {}).get("category", "unknown"),
            "container_kind": container_kind,
            "component_id": component_id,
            "component_label": component_name,
            "entrypoints": file_entrypoints,
            "imports": imports,
            "external_interfaces": external_interfaces,
            "signals": signals,
            "coupling_score": coupling_by_file.get(rel_path, 0),
            "complexity_score": safe_int(complexity_by_file.get(rel_path, {}).get("complexity_score"), 0),
        }

        for item in file_entrypoints:
            entry_id = slugify(f"{item.get('kind', 'ep')}-{rel_path}-{item.get('label', '')}")
            entrypoints.append(
                {
                    "id": entry_id,
                    "kind": item.get("kind"),
                    "label": item.get("label"),
                    "symbol": item.get("symbol"),
                    "file": rel_path,
                    "container_id": container_kind,
                    "container_label": CONTAINER_LABELS.get(container_kind, humanize_token(container_kind)),
                    "component_id": component_id,
                    "component_label": component_name,
                    "provenance": item.get("provenance"),
                    "evidence_refs": item.get("evidence_refs", [rel_path]),
                }
            )

        for relation in imports:
            all_internal_relations.append(
                {
                    "source_file": rel_path,
                    "target_file": relation["target"],
                    "kind": relation["kind"],
                }
            )

        for interface in external_interfaces:
            all_external_interfaces.append(
                {
                    "source_file": rel_path,
                    "component_id": component_id,
                    "container_id": container_kind,
                    **interface,
                }
            )

        for concept, refs in crosscut.items():
            for ref in refs:
                crosscutting_hits[concept].add(ref)

    container_nodes: dict[str, dict[str, Any]] = {}
    for rel_path, record in file_records.items():
        container_id = record["container_kind"]
        node = container_nodes.setdefault(
            container_id,
            {
                "id": container_id,
                "label": CONTAINER_LABELS.get(container_id, humanize_token(container_id)),
                "kind": container_id,
                "file_count": 0,
                "languages": Counter(),
                "entrypoint_count": 0,
                "components": set(),
                "evidence_refs": set(),
            },
        )
        node["file_count"] += 1
        node["languages"][record["ext"]] += 1
        node["entrypoint_count"] += len(record["entrypoints"])
        node["components"].add(record["component_id"])
        node["evidence_refs"].add(rel_path)

    component_nodes: dict[str, dict[str, Any]] = {}
    for rel_path, record in file_records.items():
        component_id = record["component_id"]
        node = component_nodes.setdefault(
            component_id,
            {
                "id": component_id,
                "label": record["component_label"],
                "container_id": record["container_kind"],
                "file_count": 0,
                "entrypoint_count": 0,
                "languages": Counter(),
                "coupling_score": 0,
                "complexity_score": 0,
                "evidence_refs": set(),
            },
        )
        node["file_count"] += 1
        node["entrypoint_count"] += len(record["entrypoints"])
        node["languages"][record["ext"]] += 1
        node["coupling_score"] += safe_int(record["coupling_score"], 0)
        node["complexity_score"] += safe_int(record["complexity_score"], 0)
        node["evidence_refs"].add(rel_path)

    manifest_entrypoints = detect_manifest_entrypoints(classification, repo_path)
    if manifest_entrypoints:
        component_by_file = {
            str(record.get("file")): str(record.get("component_id"))
            for record in file_records.values()
        }

        def pick_component(container_hint: str) -> dict[str, Any] | None:
            same_container = [
                node
                for node in component_nodes.values()
                if str(node.get("container_id")) == container_hint
            ]
            candidates = same_container or list(component_nodes.values())
            if not candidates:
                return None
            return sorted(
                candidates,
                key=lambda item: (
                    safe_int(item.get("entrypoint_count"), 0),
                    safe_int(item.get("coupling_score"), 0),
                    safe_int(item.get("file_count"), 0),
                ),
                reverse=True,
            )[0]

        for item in manifest_entrypoints:
            if any(
                str(existing.get("file")) == str(item.get("file"))
                and str(existing.get("label")) == str(item.get("label"))
                for existing in entrypoints
            ):
                continue
            command_paths = [str(path) for path in item.get("command_paths", []) if str(path).strip()]
            resolved_component = None
            resolved_container = None
            for command_path in command_paths:
                normalized = command_path.lstrip("./")
                matched_component_id = component_by_file.get(normalized)
                if matched_component_id and matched_component_id in component_nodes:
                    resolved_component = component_nodes[matched_component_id]
                    resolved_container = str(resolved_component.get("container_id", "")) or infer_container_kind_from_path(normalized)
                    break

            path_container_hint = infer_container_kind_from_path(command_paths[0]) if command_paths else None
            container_hint = resolved_container or path_container_hint or str(item.get("container_hint", "cli") or "cli")
            component = resolved_component or pick_component(container_hint)
            if component is None:
                component_id = f"bootstrap/{container_hint}"
                component = component_nodes.setdefault(
                    component_id,
                    {
                        "id": component_id,
                        "label": f"Bootstrap · {humanize_token(container_hint)}",
                        "container_id": container_hint,
                        "file_count": 0,
                        "entrypoint_count": 0,
                        "languages": Counter(),
                        "coupling_score": 0,
                        "complexity_score": 0,
                        "evidence_refs": set(),
                    },
                )

            container_node = container_nodes.setdefault(
                container_hint,
                {
                    "id": container_hint,
                    "label": CONTAINER_LABELS.get(container_hint, humanize_token(container_hint)),
                    "kind": container_hint,
                    "file_count": 0,
                    "languages": Counter(),
                    "entrypoint_count": 0,
                    "components": set(),
                    "evidence_refs": set(),
                },
            )
            component["entrypoint_count"] += 1
            component["evidence_refs"].update(item.get("evidence_refs", []))
            container_node["entrypoint_count"] += 1
            container_node["components"].add(component["id"])
            container_node["evidence_refs"].update(item.get("evidence_refs", []))

            entry_id = slugify(f"{item.get('kind', 'ep')}-{item.get('file', '')}-{item.get('label', '')}")
            entrypoints.append(
                {
                    "id": entry_id,
                    "kind": item.get("kind"),
                    "label": item.get("label"),
                    "symbol": item.get("symbol"),
                    "file": item.get("file"),
                    "container_id": container_hint,
                    "container_label": container_node["label"],
                    "component_id": component["id"],
                    "component_label": component["label"],
                    "provenance": item.get("provenance"),
                    "evidence_refs": item.get("evidence_refs", []),
                }
            )

    component_edge_counter: dict[tuple[str, str], dict[str, Any]] = {}
    container_edge_counter: dict[tuple[str, str], dict[str, Any]] = {}
    interface_counter: dict[tuple[str, str, str], dict[str, Any]] = {}

    for relation in all_internal_relations:
        src_record = file_records.get(relation["source_file"])
        dst_record = file_records.get(relation["target_file"])
        if not src_record or not dst_record:
            continue

        src_component = src_record["component_id"]
        dst_component = dst_record["component_id"]
        if src_component != dst_component:
            edge_key = (src_component, dst_component)
            edge = component_edge_counter.setdefault(
                edge_key,
                {
                    "from": src_component,
                    "to": dst_component,
                    "label": "의존 호출",
                    "weight": 0,
                    "kinds": set(),
                    "evidence_refs": set(),
                },
            )
            edge["weight"] += 1
            edge["kinds"].add(relation["kind"])
            edge["evidence_refs"].update({relation["source_file"], relation["target_file"]})

        src_container = src_record["container_kind"]
        dst_container = dst_record["container_kind"]
        if src_container != dst_container:
            edge_key = (src_container, dst_container)
            edge = container_edge_counter.setdefault(
                edge_key,
                {
                    "from": src_container,
                    "to": dst_container,
                    "label": "module dependency",
                    "weight": 0,
                    "evidence_refs": set(),
                },
            )
            edge["weight"] += 1
            edge["evidence_refs"].update({relation["source_file"], relation["target_file"]})

    for interface in all_external_interfaces:
        key = (interface["component_id"], interface["kind"], interface["label"])
        row = interface_counter.setdefault(
            key,
            {
                "source_component_id": interface["component_id"],
                "source_container_id": interface["container_id"],
                "kind": interface["kind"],
                "label": interface["label"],
                "weight": 0,
                "provenance": interface.get("provenance"),
                "evidence_refs": set(),
            },
        )
        row["weight"] += 1
        row["evidence_refs"].update(interface.get("evidence_refs", []))

    sorted_components = sorted(
        component_nodes.values(),
        key=lambda item: (safe_int(item["entrypoint_count"]), safe_int(item["coupling_score"]), safe_int(item["complexity_score"]), safe_int(item["file_count"])),
        reverse=True,
    )[:max_components]
    selected_component_ids = {node["id"] for node in sorted_components}

    component_relations = []
    for edge in sorted(component_edge_counter.values(), key=lambda item: safe_int(item["weight"]), reverse=True):
        if edge["from"] not in selected_component_ids or edge["to"] not in selected_component_ids:
            continue
        component_relations.append(
            {
                "from": edge["from"],
                "to": edge["to"],
                "label": edge["label"],
                "weight": safe_int(edge["weight"], 1),
                "kinds": sorted(edge["kinds"]),
                "evidence_refs": sorted(edge["evidence_refs"]),
            }
        )
        if len(component_relations) >= max_component_edges:
            break

    container_relations = []
    for edge in sorted(container_edge_counter.values(), key=lambda item: safe_int(item["weight"]), reverse=True):
        container_relations.append(
            {
                "from": edge["from"],
                "to": edge["to"],
                "label": edge["label"],
                "weight": safe_int(edge["weight"], 1),
                "evidence_refs": sorted(edge["evidence_refs"]),
            }
        )
        if len(container_relations) >= max_container_edges:
            break

    external_systems: dict[str, dict[str, Any]] = {}
    interface_items = []
    for row in sorted(interface_counter.values(), key=lambda item: safe_int(item["weight"]), reverse=True):
        target_id = slugify(f"{row['kind']}-{row['label']}")
        external_systems.setdefault(
            target_id,
            {
                "id": target_id,
                "kind": row["kind"],
                "label": row["label"],
                "evidence_refs": sorted(row["evidence_refs"]),
            },
        )
        interface_items.append(
            {
                "source_component_id": row["source_component_id"],
                "source_component_label": component_nodes.get(row["source_component_id"], {}).get("label", row["source_component_id"]),
                "source_container_id": row["source_container_id"],
                "kind": row["kind"],
                "target_id": target_id,
                "target_label": row["label"],
                "weight": safe_int(row["weight"], 1),
                "provenance": row.get("provenance"),
                "evidence_refs": sorted(row["evidence_refs"]),
            }
        )

    context_elements = []
    context_relations = []

    actor_kinds = {
        "http-route": ("actor", "External Client"),
        "cli-command": ("actor", "Operator"),
        "cli-startup": ("actor", "Operator"),
        "queue-consumer": ("actor", "Message Producer"),
        "scheduled-job": ("actor", "Scheduler"),
        "worker-task": ("actor", "Scheduler"),
        "event-handler": ("actor", "Upstream Event Source"),
    }
    actor_nodes: dict[str, dict[str, Any]] = {}
    for entrypoint in entrypoints:
        actor_kind, actor_label = actor_kinds.get(str(entrypoint.get("kind")), ("actor", "Primary Actor"))
        actor_id = slugify(actor_label)
        actor_nodes.setdefault(
            actor_id,
            {
                "id": actor_id,
                "kind": actor_kind,
                "label": actor_label,
                "evidence_refs": set(),
            },
        )
        actor_nodes[actor_id]["evidence_refs"].update(entrypoint.get("evidence_refs", []))
        context_relations.append(
            {
                "from": actor_id,
                "to": str(entrypoint.get("container_id")),
                "label": str(entrypoint.get("label") or entrypoint.get("kind") or "entrypoint"),
                "evidence_refs": list(entrypoint.get("evidence_refs", [])),
            }
        )

    for actor in actor_nodes.values():
        context_elements.append(
            {
                "id": actor["id"],
                "kind": actor["kind"],
                "label": actor["label"],
                "evidence_refs": sorted(actor["evidence_refs"]),
            }
        )

    for node in container_nodes.values():
        context_elements.append(
            {
                "id": node["id"],
                "kind": "container",
                "label": node["label"],
                "evidence_refs": sorted(node["evidence_refs"]),
            }
        )

    for system in external_systems.values():
        context_elements.append(
            {
                "id": system["id"],
                "kind": "external-system",
                "label": system["label"],
                "evidence_refs": system["evidence_refs"],
            }
        )

    for interface in interface_items:
        container_id = str(interface.get("source_container_id"))
        if not container_id:
            continue
        context_relations.append(
            {
                "from": container_id,
                "to": str(interface.get("target_id")),
                "label": str(interface.get("kind")),
                "evidence_refs": list(interface.get("evidence_refs", [])),
            }
        )

    deployment_nodes, deployment_relations = detect_deployment_units(classification, repo_path)
    if deployment_nodes and container_nodes:
        existing_links = {
            (str(rel.get("from", "")), str(rel.get("to", "")), str(rel.get("label", "")))
            for rel in deployment_relations
            if isinstance(rel, dict)
        }
        for node in deployment_nodes:
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("id", ""))
            container_hint = infer_container_kind_from_label(str(node.get("label", "")))
            if not container_hint or container_hint not in container_nodes:
                continue
            link_key = (node_id, container_hint, "runs")
            if link_key in existing_links:
                continue
            existing_links.add(link_key)
            deployment_relations.append(
                {
                    "from": node_id,
                    "to": container_hint,
                    "label": "runs",
                    "evidence_refs": list(node.get("evidence_refs", [])),
                }
            )

    crosscutting_items = []
    for concept, refs in sorted(crosscutting_hits.items()):
        crosscutting_items.append(
            {
                "name": humanize_token(concept),
                "id": concept,
                "evidence_refs": sorted(refs)[:12],
                "occurrence_count": len(refs),
            }
        )

    scenarios = build_trace_scenarios(
        trace_input=trace_input,
        entrypoints=entrypoints,
        max_scenarios=max_scenarios,
        max_steps=max_scenario_steps,
    )
    if not scenarios:
        scenarios = build_static_scenarios(
            entrypoints=entrypoints,
            component_relations=component_relations,
            component_nodes=component_nodes,
            interface_items=interface_items,
            max_scenarios=max_scenarios,
            max_steps=max_scenario_steps,
        )
    scenarios = dedupe_scenarios(scenarios, max_scenarios=max_scenarios)

    decision_candidates = []
    if len(container_nodes) > 1:
        decision_candidates.append(
            {
                "title": "컨테이너 간 계약 명시",
                "type": "boundary",
                "confidence": 0.82,
                "summary": "복수 컨테이너가 관찰되어 통신 계약과 책임 경계를 명시할 필요가 있습니다.",
                "evidence_refs": sorted(
                    {ref for rel in container_relations for ref in rel.get("evidence_refs", [])}
                    or {ref for node in container_nodes.values() for ref in node.get("evidence_refs", [])}
                )[:12],
            }
        )
    if any(item.get("kind") in {"database", "cache", "messaging"} for item in interface_items):
        decision_candidates.append(
            {
                "title": "데이터/메시징 경계 소유권 정리",
                "type": "data-boundary",
                "confidence": 0.78,
                "summary": "데이터 저장소나 메시징 인터페이스가 관찰되어 소유권과 일관성 전략이 필요합니다.",
                "evidence_refs": sorted({ref for item in interface_items if item.get("kind") in {"database", "cache", "messaging"} for ref in item.get("evidence_refs", [])})[:12],
            }
        )
    if deployment_nodes:
        decision_candidates.append(
            {
                "title": "배포 단위와 런타임 책임 명시",
                "type": "deployment",
                "confidence": 0.84,
                "summary": "배포 관련 파일이 관찰되어 실행 단위와 운영 경계를 문서화할 필요가 있습니다.",
                "evidence_refs": sorted({ref for node in deployment_nodes for ref in node.get("evidence_refs", [])})[:12],
            }
        )
    language_count = Counter(node["ext"] for node in file_records.values())
    if len(language_count) > 1:
        decision_candidates.append(
            {
                "title": "다중 언어 경계 계약 표준화",
                "type": "runtime-contract",
                "confidence": 0.74,
                "summary": "여러 언어/런타임이 동시에 존재해 인터페이스 계약과 관측성을 표준화할 필요가 있습니다.",
                "evidence_refs": sorted(file_records)[:12],
            }
        )
    top_coupled_components = sorted(sorted_components, key=lambda item: safe_int(item["coupling_score"]), reverse=True)[:3]
    if top_coupled_components:
        decision_candidates.append(
            {
                "title": "고결합 컴포넌트 경계 분해",
                "type": "maintainability",
                "confidence": 0.71,
                "summary": "상위 컴포넌트의 결합도가 높아 책임 분리 또는 인터페이스 역전이 필요할 수 있습니다.",
                "evidence_refs": sorted({ref for node in top_coupled_components for ref in node.get("evidence_refs", [])})[:12],
            }
        )

    decision_candidates = decision_candidates[:max_decision_candidates]

    entrypoints_payload = {
        "status": "ok" if entrypoints else "Unverified",
        "summary": {
            "count": len(entrypoints),
            "kinds": dict(Counter(item.get("kind", "unknown") for item in entrypoints)),
        },
        "items": sorted(
            entrypoints,
            key=lambda item: (
                ENTRYPOINT_KIND_PRIORITY.get(str(item.get("kind")), 99),
                str(item.get("label", "")),
            ),
        ),
    }

    context_payload = {
        "status": "ok" if context_elements else "Unverified",
        "summary": {
            "elements": len(context_elements),
            "relationships": len(context_relations),
        },
        "elements": context_elements,
        "relationships": context_relations,
        "provenance": [
            {
                "source": "entrypoints+interfaces",
                "refs": sorted({ref for rel in context_relations for ref in rel.get("evidence_refs", [])})[:20],
            }
        ],
    }

    container_payload = {
        "status": "ok" if container_nodes else "Unverified",
        "summary": {
            "containers": len(container_nodes),
            "relationships": len(container_relations),
        },
        "containers": [
            {
                **node,
                "languages": dict(node["languages"]),
                "components": sorted(node["components"]),
                "evidence_refs": sorted(node["evidence_refs"]),
            }
            for node in sorted(container_nodes.values(), key=lambda item: item["label"])
        ],
        "relationships": container_relations,
        "provenance": [
            {
                "source": "static-relations",
                "refs": sorted(
                    {ref for rel in container_relations for ref in rel.get("evidence_refs", [])}
                    or {ref for node in container_nodes.values() for ref in node.get("evidence_refs", [])}
                )[:20],
            }
        ],
    }

    component_payload = {
        "status": "ok" if sorted_components else "Unverified",
        "summary": {
            "components": len(sorted_components),
            "relationships": len(component_relations),
        },
        "components": [
            {
                **node,
                "languages": dict(node["languages"]),
                "evidence_refs": sorted(node["evidence_refs"]),
            }
            for node in sorted_components
        ],
        "relationships": component_relations,
        "provenance": [
            {
                "source": "imports+complexity",
                "refs": sorted(
                    {ref for rel in component_relations for ref in rel.get("evidence_refs", [])}
                    or {ref for node in sorted_components for ref in node.get("evidence_refs", [])}
                )[:20],
            }
        ],
    }

    interface_payload = {
        "status": "ok" if interface_items else "Unverified",
        "summary": {
            "interfaces": len(interface_items),
            "external_systems": len(external_systems),
        },
        "external_systems": sorted(external_systems.values(), key=lambda item: item["label"]),
        "interfaces": interface_items,
        "provenance": [
            {
                "source": "signal-match",
                "refs": sorted({ref for item in interface_items for ref in item.get("evidence_refs", [])})[:20],
            }
        ],
    }

    scenario_payload = {
        "status": "ok" if scenarios else "Unverified",
        "summary": {
            "scenarios": len(scenarios),
            "trace_backed": len([item for item in scenarios if item.get("source") == "trace"]),
            "fallback_static": len([item for item in scenarios if item.get("fallback")]),
        },
        "scenarios": scenarios,
        "provenance": [
            {
                "source": "trace" if any(item.get("source") == "trace" for item in scenarios) else "static-entrypoint",
                "refs": sorted({ref for item in scenarios for ref in item.get("evidence_refs", [])})[:20],
            }
        ],
    }

    deployment_payload = {
        "status": "ok" if deployment_nodes else "Unverified",
        "summary": {
            "nodes": len(deployment_nodes),
            "relationships": len(deployment_relations),
        },
        "nodes": deployment_nodes,
        "relationships": deployment_relations,
        "provenance": [
            {
                "source": "repo-config",
                "refs": sorted({ref for node in deployment_nodes for ref in node.get("evidence_refs", [])})[:20],
            }
        ],
    }

    crosscutting_payload = {
        "status": "ok" if crosscutting_items else "Unverified",
        "summary": {
            "concepts": len(crosscutting_items),
        },
        "concepts": crosscutting_items,
        "provenance": [
            {
                "source": "signal-match",
                "refs": sorted({ref for item in crosscutting_items for ref in item.get("evidence_refs", [])})[:20],
            }
        ],
    }

    decision_payload = {
        "status": "ok" if decision_candidates else "Unverified",
        "summary": {
            "candidates": len(decision_candidates),
        },
        "candidates": decision_candidates,
        "provenance": [
            {
                "source": "model-heuristics",
                "refs": sorted({ref for item in decision_candidates for ref in item.get("evidence_refs", [])})[:20],
            }
        ],
    }

    summary_payload = {
        "status": "ok" if any(payload.get("status") == "ok" for payload in [context_payload, container_payload, component_payload, scenario_payload]) else "Unverified",
        "counts": {
            "entrypoints": len(entrypoints),
            "containers": len(container_nodes),
            "components": len(sorted_components),
            "interfaces": len(interface_items),
            "scenarios": len(scenarios),
            "deployment_nodes": len(deployment_nodes),
            "crosscutting": len(crosscutting_items),
            "decision_candidates": len(decision_candidates),
        },
        "warnings": [
            "trace-backed scenario 없음" if not any(item.get("source") == "trace" for item in scenarios) else "",
            "deployment evidence 없음" if not deployment_nodes else "",
            "entrypoint evidence 없음" if not entrypoints else "",
        ],
    }
    summary_payload["warnings"] = [item for item in summary_payload["warnings"] if item]

    write_json(arch_dir / "entrypoints.json", entrypoints_payload)
    write_json(arch_dir / "context-model.json", context_payload)
    write_json(arch_dir / "container-model.json", container_payload)
    write_json(arch_dir / "component-model.json", component_payload)
    write_json(arch_dir / "interface-model.json", interface_payload)
    write_json(arch_dir / "scenario-model.json", scenario_payload)
    write_json(arch_dir / "deployment-model.json", deployment_payload)
    write_json(arch_dir / "crosscutting-model.json", crosscutting_payload)
    write_json(arch_dir / "decision-candidates.json", decision_payload)
    write_json(arch_dir / "architecture-summary.json", summary_payload)

    print(f"entrypoints={len(entrypoints)}")
    print(f"containers={len(container_nodes)}")
    print(f"components={len(sorted_components)}")
    print(f"scenarios={len(scenarios)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
