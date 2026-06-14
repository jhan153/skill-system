#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  collect.sh --repo-path <abs> [--commit-range <A..B|auto>] [--mode <static|dynamic|full>] [--output-dir <abs>] [--top-n <int>] [--policy <path>]

Options:
  --repo-path     Absolute or relative repository path (required)
  --commit-range  Git range (default: auto)
  --mode          static | dynamic | full (default: policy.collection.mode_default)
  --output-dir    Output directory (default: <repo>/artifacts/codebase-intel/<timestamp>)
  --top-n         Number of hotspot candidates (default: policy.collection.top_n_default)
  --policy        Policy JSON file path (default: <skill-root>/references/policy-default.json)
USAGE
}

REPO_PATH=""
COMMIT_RANGE="auto"
MODE=""
OUTPUT_DIR=""
TOP_N=""
POLICY_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-path)
      REPO_PATH="${2:-}"
      shift 2
      ;;
    --commit-range)
      COMMIT_RANGE="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --top-n)
      TOP_N="${2:-}"
      shift 2
      ;;
    --policy)
      POLICY_PATH="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_PATH" ]]; then
  echo "--repo-path is required" >&2
  usage
  exit 1
fi

if [[ ! -d "$REPO_PATH" ]]; then
  echo "Repository path does not exist: $REPO_PATH" >&2
  exit 1
fi

REPO_PATH="$(cd "$REPO_PATH" && pwd -P)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"

if [[ -z "$POLICY_PATH" ]]; then
  POLICY_PATH="$SKILL_ROOT/references/policy-default.json"
fi
if [[ ! -f "$POLICY_PATH" ]]; then
  echo "Policy file not found: $POLICY_PATH" >&2
  exit 1
fi

if [[ -z "$OUTPUT_DIR" ]]; then
  TS="$(date -u +%Y%m%dT%H%M%SZ)"
  OUTPUT_DIR="$REPO_PATH/artifacts/codebase-intel/$TS"
fi
OUTPUT_DIR="$(mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd -P)"

ARTIFACT_DIR="$OUTPUT_DIR/artifacts"
LOG_DIR="$OUTPUT_DIR/logs"
mkdir -p "$ARTIFACT_DIR/git" "$ARTIFACT_DIR/static" "$ARTIFACT_DIR/dynamic" "$ARTIFACT_DIR/architecture" "$ARTIFACT_DIR/notes" "$LOG_DIR"

TOOL_TSV="$ARTIFACT_DIR/tools.tsv"
UNVERIFIED_TSV="$ARTIFACT_DIR/notes/unverified.tsv"
printf "tool\tcategory\tstatus\toutput\tmessage\n" > "$TOOL_TSV"
printf "section\treason\n" > "$UNVERIFIED_TSV"

record_tool() {
  local tool="$1"
  local category="$2"
  local status="$3"
  local output="$4"
  local message="$5"
  message="$(printf '%s' "$message" | tr '\t\n\r' '   ')"
  printf "%s\t%s\t%s\t%s\t%s\n" "$tool" "$category" "$status" "$output" "$message" >> "$TOOL_TSV"
}

mark_unverified() {
  local section="$1"
  local reason="$2"
  reason="$(printf '%s' "$reason" | tr '\t\n\r' '   ')"
  printf "%s\t%s\n" "$section" "$reason" >> "$UNVERIFIED_TSV"
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

POLICY_EFFECTIVE="$ARTIFACT_DIR/policy-effective.json"
POLICY_META_RAW="$(python3 - "$POLICY_PATH" "$POLICY_EFFECTIVE" <<'PY'
import json
import sys
from pathlib import Path

src_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

try:
    policy = json.loads(src_path.read_text(encoding="utf-8"))
except Exception:
    raise SystemExit(f"Failed to parse policy file: {src_path}")

if not isinstance(policy, dict):
    raise SystemExit("Policy must be a JSON object")

required_top = ["collection", "priority_model", "action_profiles", "owners", "quality_gates", "diagram", "runtime"]
missing_top = [k for k in required_top if k not in policy]
if missing_top:
    raise SystemExit(f"Policy missing top-level keys: {', '.join(missing_top)}")

required_collection = [
    "top_n_default",
    "commit_depth_default",
    "mode_default",
    "analysis_categories",
    "code_extensions",
    "include_prefixes",
    "exclude_prefixes",
    "category_rules",
]
collection = policy.get("collection")
if not isinstance(collection, dict):
    raise SystemExit("Policy.collection must be an object")
missing_collection = [k for k in required_collection if k not in collection]
if missing_collection:
    raise SystemExit(f"Policy.collection missing keys: {', '.join(missing_collection)}")

if "tools" not in policy.get("runtime", {}):
    raise SystemExit("Policy.runtime.tools is required")

out_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2), encoding="utf-8")
print(policy["collection"]["top_n_default"])
print(policy["collection"]["mode_default"])
print(policy["collection"]["commit_depth_default"])
PY
)"

TOP_N_DEFAULT="$(printf '%s\n' "$POLICY_META_RAW" | sed -n '1p')"
MODE_DEFAULT="$(printf '%s\n' "$POLICY_META_RAW" | sed -n '2p')"
COMMIT_DEPTH_DEFAULT="$(printf '%s\n' "$POLICY_META_RAW" | sed -n '3p')"

if [[ -z "$TOP_N" ]]; then
  TOP_N="$TOP_N_DEFAULT"
fi
if [[ -z "$MODE" ]]; then
  MODE="$MODE_DEFAULT"
fi

if [[ "$MODE" != "static" && "$MODE" != "dynamic" && "$MODE" != "full" ]]; then
  echo "--mode must be one of: static, dynamic, full" >&2
  exit 1
fi
if ! [[ "$TOP_N" =~ ^[0-9]+$ ]] || [[ "$TOP_N" -lt 1 ]]; then
  echo "--top-n must be a positive integer" >&2
  exit 1
fi

IS_GIT_REPO=0
GIT_HEAD="Unverified"
GIT_BRANCH="Unverified"

if git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  IS_GIT_REPO=1
  GIT_HEAD="$(git -C "$REPO_PATH" rev-parse HEAD 2>/dev/null || echo Unverified)"
  GIT_BRANCH="$(git -C "$REPO_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo Unverified)"

  if [[ "$COMMIT_RANGE" == "auto" ]]; then
    START_COMMIT=""
    if [[ "$GIT_HEAD" != "Unverified" ]]; then
      if START_COMMIT_VAL="$(git -C "$REPO_PATH" rev-parse "HEAD~$COMMIT_DEPTH_DEFAULT" 2>/dev/null)"; then
        START_COMMIT="$START_COMMIT_VAL"
      else
        START_COMMIT="$(git -C "$REPO_PATH" rev-list --max-parents=0 HEAD 2>/dev/null | tail -n 1 || true)"
      fi
    fi
    if [[ -n "$START_COMMIT" && "$GIT_HEAD" != "Unverified" ]]; then
      COMMIT_RANGE="$START_COMMIT..$GIT_HEAD"
    else
      COMMIT_RANGE="Unverified"
      mark_unverified "git.commit_range" "Unable to resolve commit range automatically"
    fi
  fi
else
  if [[ "$COMMIT_RANGE" == "auto" ]]; then
    COMMIT_RANGE="Unverified"
  fi
  mark_unverified "git.repo" "Not a git repository"
fi

TRACKED_FILES="$LOG_DIR/tracked_files.txt"
collect_tracked_files() {
  if [[ "$IS_GIT_REPO" -eq 1 ]]; then
    git -C "$REPO_PATH" ls-files > "$TRACKED_FILES" 2> "$LOG_DIR/git_ls_files.err" || true
    if [[ -s "$TRACKED_FILES" ]]; then
      record_tool "tracked-files" "inventory" "ok" "logs/tracked_files.txt" "git tracked files collected"
      return
    fi
  fi
  if has_cmd rg; then
    rg --files "$REPO_PATH" > "$TRACKED_FILES" || true
  else
    find "$REPO_PATH" -type f > "$TRACKED_FILES"
  fi
  if [[ -s "$TRACKED_FILES" ]]; then
    record_tool "tracked-files" "inventory" "ok" "logs/tracked_files.txt" "fallback file list collected"
  else
    record_tool "tracked-files" "inventory" "failed" "" "tracked file list empty"
    mark_unverified "inventory.tracked_files" "No files collected"
  fi
}

collect_static_core() {
  python3 - "$REPO_PATH" "$TRACKED_FILES" "$ARTIFACT_DIR" "$TOP_N" "$POLICY_EFFECTIVE" > "$LOG_DIR/static_core.log" 2> "$LOG_DIR/static_core.err" <<'PY'
import ast
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

repo = Path(sys.argv[1])
tracked_path = Path(sys.argv[2])
artifacts = Path(sys.argv[3])
top_n = int(sys.argv[4])
policy_path = Path(sys.argv[5])

policy = json.loads(policy_path.read_text(encoding="utf-8"))
collection = policy.get("collection", {})
code_ext = {e.lower() for e in collection.get("code_extensions", [])}
include_prefixes = collection.get("include_prefixes", [])
exclude_prefixes = collection.get("exclude_prefixes", [])
category_rules = collection.get("category_rules", [])
analysis_categories = set(collection.get("analysis_categories", ["code", "config", "test"]))
max_sequence_steps = int(policy.get("diagram", {}).get("max_sequence_steps", 7))

static_dir = artifacts / "static"
static_dir.mkdir(parents=True, exist_ok=True)

classification_path = static_dir / "path-classification.tsv"
inventory_path = static_dir / "file_inventory.tsv"
complexity_path = static_dir / "complexity.json"
architecture_path = static_dir / "architecture.json"
class_hierarchy_path = static_dir / "class-hierarchy.json"
call_graph_path = static_dir / "call-graph.json"

if tracked_path.exists():
    files = [line.strip() for line in tracked_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
else:
    files = []

# Normalize fallback output from rg/find absolute paths.
normalized_files = []
for raw in files:
    p = Path(raw)
    if p.is_absolute():
        try:
            rel = str(p.relative_to(repo))
        except Exception:
            continue
        normalized_files.append(rel)
    else:
        normalized_files.append(raw)


def classify(path_str: str):
    path_str = path_str.replace("\\", "/")
    ext = Path(path_str).suffix.lower()

    for prefix in exclude_prefixes:
        if path_str.startswith(prefix):
            return {"category": "excluded", "included": False, "reason": f"exclude_prefix:{prefix}", "ext": ext}

    if include_prefixes and not any(path_str.startswith(prefix) for prefix in include_prefixes):
        return {"category": "excluded", "included": False, "reason": "outside_include_prefix", "ext": ext}

    for rule in category_rules:
        prefix = str(rule.get("prefix", ""))
        category = str(rule.get("category", "unknown"))
        if prefix and path_str.startswith(prefix):
            return {"category": category, "included": True, "reason": f"category_rule:{prefix}", "ext": ext}

    if ext in code_ext:
        return {"category": "code", "included": True, "reason": "fallback:code_ext", "ext": ext}
    return {"category": "unknown", "included": True, "reason": "fallback:unknown", "ext": ext}

classified = {}
for rel in sorted(set(normalized_files)):
    meta = classify(rel)
    classified[rel] = meta

with classification_path.open("w", encoding="utf-8") as f:
    f.write("path\tcategory\tincluded\treason\text\n")
    for rel, meta in classified.items():
        f.write(f"{rel}\t{meta['category']}\t{str(meta['included']).lower()}\t{meta['reason']}\t{meta['ext']}\n")

inventory = Counter()
for rel, meta in classified.items():
    if not meta["included"]:
        continue
    ext = meta["ext"] or "noext"
    inventory[ext] += 1

with inventory_path.open("w", encoding="utf-8") as f:
    for ext, count in sorted(inventory.items(), key=lambda x: x[1], reverse=True):
        f.write(f"{ext}\t{count}\n")

py_targets = []
complexity_rows = []
all_class_nodes = []
class_edges = []
imports_by_file = defaultdict(set)
module_index = {}


def to_module_name(rel_path: str) -> str:
    p = Path(rel_path)
    parts = list(p.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)

for rel, meta in classified.items():
    if not meta["included"]:
        continue
    ext = meta["ext"]
    category = meta["category"]
    if category not in analysis_categories:
        continue
    if ext not in code_ext:
        continue

    file_path = repo / rel
    if not file_path.exists() or not file_path.is_file():
        continue

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    loc = len(lines)
    if loc == 0:
        continue

    branches = 0
    functions = 0
    classes = []

    if ext == ".py":
        py_targets.append(rel)
        module_index[to_module_name(rel)] = rel
        try:
            tree = ast.parse(text)
        except Exception:
            tree = None

        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    bases = []
                    for base in node.bases:
                        parent = None
                        if isinstance(base, ast.Name):
                            parent = base.id
                        elif isinstance(base, ast.Attribute):
                            parent = base.attr
                        elif isinstance(base, ast.Subscript):
                            if isinstance(base.value, ast.Name):
                                parent = base.value.id
                            elif isinstance(base.value, ast.Attribute):
                                parent = base.value.attr
                        if parent and parent != "object":
                            bases.append(parent)
                            class_edges.append({"parent": parent, "child": node.name, "file": rel})
                    method_count = sum(1 for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)))
                    all_class_nodes.append(
                        {
                            "name": node.name,
                            "file": rel,
                            "bases": bases,
                            "method_count": method_count,
                        }
                    )

                if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.IfExp, ast.Match, ast.ExceptHandler)):
                    branches += 1
                elif isinstance(node, ast.BoolOp):
                    branches += max(1, len(node.values) - 1)
                elif isinstance(node, ast.comprehension):
                    branches += 1 + len(node.ifs)

            current_module = to_module_name(rel)
            current_parts = current_module.split(".") if current_module else []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports_by_file[rel].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    level = int(getattr(node, "level", 0) or 0)
                    module_part = node.module or ""
                    if level > 0:
                        if level <= len(current_parts):
                            base_parts = current_parts[:-level]
                        else:
                            base_parts = []
                    else:
                        base_parts = []
                    if module_part:
                        resolved = ".".join([*(base_parts), module_part]).strip(".")
                    else:
                        resolved = ".".join(base_parts).strip(".")
                    if resolved:
                        imports_by_file[rel].add(resolved)
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        candidate = f"{resolved}.{alias.name}".strip(".") if resolved else alias.name
                        imports_by_file[rel].add(candidate)
    else:
        branches = len(re.findall(r"\\b(if|elif|for|while|case|catch|switch|except)\\b|\\?|&&|\\|\\|", text))
        functions = len(re.findall(r"\\b(def|function|func|fn|void|int|bool|String|public|private|protected)\\b", text))
        classes = re.findall(r"\\bclass\\s+([A-Za-z_][A-Za-z0-9_]*)", text)
        for c in classes:
            all_class_nodes.append({"name": c, "file": rel, "bases": [], "method_count": 0})

    score = 1 + branches
    density = round(score / max(loc, 1), 4)

    complexity_rows.append(
        {
            "file": rel,
            "category": category,
            "loc": loc,
            "branches": branches,
            "functions": functions,
            "classes": classes,
            "complexity_score": score,
            "density": density,
        }
    )

complexity_rows.sort(key=lambda x: (x["complexity_score"], x["density"], x["loc"]), reverse=True)

complexity_payload = {
    "summary": {
        "files_analyzed": len(complexity_rows),
        "top_n": top_n,
        "avg_complexity_score": round(sum(r["complexity_score"] for r in complexity_rows) / max(len(complexity_rows), 1), 3),
        "categories": dict(Counter(r["category"] for r in complexity_rows)),
    },
    "top_files": complexity_rows[:top_n],
    "classes": all_class_nodes[:1000],
}
complexity_path.write_text(json.dumps(complexity_payload, indent=2, ensure_ascii=False), encoding="utf-8")

# Architecture signals from internal import graph.
module_to_file = module_index
file_to_targets = defaultdict(set)
for rel, modules in imports_by_file.items():
    for mod in modules:
        target = None
        if mod in module_to_file:
            target = module_to_file[mod]
        else:
            prefix = mod + "."
            candidates = [path for name, path in module_to_file.items() if name.startswith(prefix)]
            if len(candidates) == 1:
                target = candidates[0]
        if target and target != rel:
            file_to_targets[rel].add(target)

fan_out = {f: len(t) for f, t in file_to_targets.items()}
fan_in_counter = Counter()
for src, targets in file_to_targets.items():
    for dst in targets:
        fan_in_counter[dst] += 1

architecture_rows = []
for row in complexity_rows:
    rel = row["file"]
    out_v = fan_out.get(rel, 0)
    in_v = fan_in_counter.get(rel, 0)
    coupling = in_v + out_v
    architecture_rows.append(
        {
            "file": rel,
            "category": row["category"],
            "fan_in": in_v,
            "fan_out": out_v,
            "coupling_score": coupling,
            "complexity_score": row["complexity_score"],
        }
    )

architecture_rows.sort(key=lambda x: (x["coupling_score"], x["fan_in"], x["fan_out"]), reverse=True)
architecture_payload = {
    "summary": {
        "files_with_signals": len(architecture_rows),
        "avg_coupling_score": round(sum(r["coupling_score"] for r in architecture_rows) / max(len(architecture_rows), 1), 3),
        "edges": int(sum(len(v) for v in file_to_targets.values())),
    },
    "top_files": architecture_rows[:top_n],
    "all_files": architecture_rows,
}
architecture_path.write_text(json.dumps(architecture_payload, indent=2, ensure_ascii=False), encoding="utf-8")

# Class hierarchy artifact.
class_hierarchy_payload = {
    "summary": {
        "nodes": len(all_class_nodes),
        "edges": len(class_edges),
    },
    "nodes": all_class_nodes,
    "edges": class_edges,
}
class_hierarchy_path.write_text(json.dumps(class_hierarchy_payload, indent=2, ensure_ascii=False), encoding="utf-8")

# Call graph from Python AST.
function_nodes = {}
functions_by_name = defaultdict(list)
edges_counter = Counter()

for rel in py_targets:
    file_path = repo / rel
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text)
    except Exception:
        continue

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node_id = f"{rel}::{node.name}"
            function_nodes[node_id] = {"id": node_id, "file": rel, "symbol": node.name}
            functions_by_name[node.name].append(node_id)

for rel in py_targets:
    file_path = repo / rel
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text)
    except Exception:
        continue

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        src = f"{rel}::{node.name}"
        if src not in function_nodes:
            continue

        for call in [n for n in ast.walk(node) if isinstance(n, ast.Call)]:
            callee_name = None
            if isinstance(call.func, ast.Name):
                callee_name = call.func.id
            elif isinstance(call.func, ast.Attribute):
                callee_name = call.func.attr
            if not callee_name:
                continue

            same_file_target = f"{rel}::{callee_name}"
            if same_file_target in function_nodes:
                edges_counter[(src, same_file_target)] += 1
                continue

            candidates = functions_by_name.get(callee_name, [])
            if len(candidates) == 1:
                edges_counter[(src, candidates[0])] += 1

adj = defaultdict(list)
for (src, dst), weight in edges_counter.items():
    adj[src].append((dst, weight))

out_weight = {node: sum(w for _, w in edges) for node, edges in adj.items()}
start_node = max(out_weight.items(), key=lambda x: x[1])[0] if out_weight else None

paths = []
if start_node:
    path = [start_node]
    visited = {start_node}
    current = start_node
    for _ in range(max(1, max_sequence_steps - 1)):
        candidates = sorted(adj.get(current, []), key=lambda x: x[1], reverse=True)
        next_node = None
        for dst, _ in candidates:
            if dst not in visited:
                next_node = dst
                break
        if not next_node:
            break
        path.append(next_node)
        visited.add(next_node)
        current = next_node
    if len(path) >= 2:
        paths.append(path)

call_graph_payload = {
    "summary": {
        "nodes": len(function_nodes),
        "edges": len(edges_counter),
    },
    "nodes": list(function_nodes.values()),
    "edges": [{"from": s, "to": d, "weight": w} for (s, d), w in sorted(edges_counter.items(), key=lambda x: x[1], reverse=True)],
    "top_paths": paths,
}
call_graph_path.write_text(json.dumps(call_graph_payload, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"classified_files={len(classified)}")
print(f"complexity_rows={len(complexity_rows)}")
print(f"architecture_edges={architecture_payload['summary']['edges']}")
print(f"call_graph_nodes={len(function_nodes)}")
PY

  if [[ -s "$ARTIFACT_DIR/static/complexity.json" ]]; then
    record_tool "static-core" "static" "ok" "artifacts/static/complexity.json" "classification/complexity/architecture/call-graph generated"
  else
    record_tool "static-core" "static" "failed" "" "failed to generate static core artifacts"
    mark_unverified "static.core" "Failed to generate complexity/architecture artifacts"
  fi
}

collect_git_artifacts() {
  local churn_all="$ARTIFACT_DIR/git/churn_all.tsv"
  local churn_top="$ARTIFACT_DIR/git/churn_top.tsv"
  local commits_tsv="$ARTIFACT_DIR/git/recent_commits.tsv"
  local branches_tsv="$ARTIFACT_DIR/git/branches.tsv"

  if [[ "$IS_GIT_REPO" -ne 1 ]]; then
    record_tool "git" "git" "unverified" "" "git metadata unavailable"
    mark_unverified "git.artifacts" "Not a git repository"
    return
  fi

  if [[ "$COMMIT_RANGE" != "Unverified" ]]; then
    if git -C "$REPO_PATH" log --numstat --pretty=tformat: "$COMMIT_RANGE" > "$LOG_DIR/git_numstat.log" 2> "$LOG_DIR/git_numstat.err"; then
      awk 'NF==3 && $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {
          file=$3
          churn[file] += $1 + $2
        }
        END {
          for (f in churn) {
            printf "%d\t%s\n", churn[f], f
          }
        }
      ' "$LOG_DIR/git_numstat.log" | sort -k1,1nr > "$churn_all"

      if [[ -s "$churn_all" ]]; then
        head -n "$TOP_N" "$churn_all" > "$churn_top"
        record_tool "git-churn" "git" "ok" "artifacts/git/churn_all.tsv" "full churn list generated"
      else
        record_tool "git-churn" "git" "unverified" "" "no churn data in range"
        mark_unverified "git.churn" "No churn records for commit range"
      fi
    else
      record_tool "git-churn" "git" "failed" "" "git log --numstat failed"
      mark_unverified "git.churn" "Failed to collect churn from git"
    fi
  else
    record_tool "git-churn" "git" "unverified" "" "commit range unresolved"
    mark_unverified "git.churn" "Commit range unresolved"
  fi

  if [[ "$GIT_HEAD" == "Unverified" ]]; then
    record_tool "git-commits" "git" "unverified" "" "HEAD not available"
    mark_unverified "git.recent_commits" "HEAD not available"
  elif git -C "$REPO_PATH" log --pretty=format:'%H\t%ad\t%an\t%s' --date=iso -n "$TOP_N" > "$commits_tsv" 2> "$LOG_DIR/git_commits.err"; then
    record_tool "git-commits" "git" "ok" "artifacts/git/recent_commits.tsv" "recent commit list generated"
  else
    record_tool "git-commits" "git" "failed" "" "failed to collect recent commits"
    mark_unverified "git.recent_commits" "Failed to collect recent commits"
  fi

  if git -C "$REPO_PATH" for-each-ref --format='%(refname:short)\t%(committerdate:iso8601)\t%(authorname)' refs/heads > "$branches_tsv" 2> "$LOG_DIR/git_branches.err"; then
    record_tool "git-branches" "git" "ok" "artifacts/git/branches.tsv" "branch list generated"
  else
    record_tool "git-branches" "git" "failed" "" "failed to collect branch list"
    mark_unverified "git.branches" "Failed to collect branch list"
  fi
}

collect_coverage() {
  local coverage_json="$ARTIFACT_DIR/static/coverage-summary.json"
  local generated_xml="$ARTIFACT_DIR/static/coverage.xml"

  if ! has_cmd python3; then
    record_tool "coverage" "static" "unverified" "" "python3 is required for coverage summary"
    mark_unverified "static.coverage" "python3 not available"
    return
  fi

  if [[ "${CBIR_RUN_TESTS:-0}" == "1" ]]; then
    if has_cmd coverage && has_cmd pytest; then
      set +e
      (
        cd "$REPO_PATH" &&
        COVERAGE_FILE="$OUTPUT_DIR/.coverage" coverage run -m pytest > "$LOG_DIR/pytest.log" 2>&1 &&
        COVERAGE_FILE="$OUTPUT_DIR/.coverage" coverage xml -o "$generated_xml" >> "$LOG_DIR/pytest.log" 2>&1
      )
      local test_rc=$?
      set -e
      if [[ $test_rc -eq 0 && -s "$generated_xml" ]]; then
        record_tool "coverage-test-run" "static" "ok" "artifacts/static/coverage.xml" "coverage run via pytest completed"
      else
        record_tool "coverage-test-run" "static" "failed" "" "CBIR_RUN_TESTS requested but test run failed"
        mark_unverified "static.coverage_test_run" "Coverage test run failed"
      fi
    else
      record_tool "coverage-test-run" "static" "unverified" "" "CBIR_RUN_TESTS=1 but coverage/pytest missing"
      mark_unverified "static.coverage_test_run" "coverage or pytest not found"
    fi
  fi

  python3 - "$REPO_PATH" "$coverage_json" "$generated_xml" > "$LOG_DIR/coverage.log" 2> "$LOG_DIR/coverage.err" <<'PY'
import json
import re
import sys
from pathlib import Path

repo = Path(sys.argv[1])
out = Path(sys.argv[2])
generated_xml = Path(sys.argv[3])

result = {
    "status": "Unverified",
    "source": None,
    "line_coverage": None,
    "branch_coverage": None,
    "reason": "No known coverage file found",
}

xml = generated_xml if generated_xml.exists() else (repo / "coverage.xml")
lcov = repo / "coverage/lcov.info"

if xml.exists():
    text = xml.read_text(encoding="utf-8", errors="ignore")
    line_m = re.search(r'line-rate="([0-9.]+)"', text)
    branch_m = re.search(r'branch-rate="([0-9.]+)"', text)
    result.update(
        {
            "status": "ok",
            "source": str(xml.relative_to(repo)),
            "line_coverage": round(float(line_m.group(1)) * 100, 2) if line_m else None,
            "branch_coverage": round(float(branch_m.group(1)) * 100, 2) if branch_m else None,
            "reason": None,
        }
    )
elif lcov.exists():
    lines_found = 0
    lines_hit = 0
    for line in lcov.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("LF:"):
            lines_found += int(line.split(":", 1)[1])
        elif line.startswith("LH:"):
            lines_hit += int(line.split(":", 1)[1])
    coverage = (lines_hit / lines_found * 100) if lines_found else None
    result.update(
        {
            "status": "ok" if coverage is not None else "Unverified",
            "source": str(lcov.relative_to(repo)),
            "line_coverage": round(coverage, 2) if coverage is not None else None,
            "branch_coverage": None,
            "reason": None if coverage is not None else "Invalid lcov content",
        }
    )

out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out}")
PY

  if grep -q '"status": "ok"' "$coverage_json"; then
    record_tool "coverage" "static" "ok" "artifacts/static/coverage-summary.json" "coverage summary collected"
  else
    record_tool "coverage" "static" "unverified" "artifacts/static/coverage-summary.json" "coverage source missing"
    mark_unverified "static.coverage" "Coverage file not found (coverage.xml or coverage/lcov.info)"
  fi
}

collect_static_security() {
  local semgrep_out="$ARTIFACT_DIR/static/semgrep.json"
  local dep_out="$ARTIFACT_DIR/static/dependency-check-report.json"

  if has_cmd semgrep; then
    if [[ "${CBIR_RUN_SEMGREP:-0}" == "1" ]]; then
      set +e
      semgrep scan --config auto --json --output "$semgrep_out" "$REPO_PATH" > "$LOG_DIR/semgrep.log" 2> "$LOG_DIR/semgrep.err"
      local semgrep_rc=$?
      set -e
      if [[ $semgrep_rc -eq 0 || -s "$semgrep_out" ]]; then
        record_tool "semgrep" "sast" "ok" "artifacts/static/semgrep.json" "semgrep run completed"
      else
        record_tool "semgrep" "sast" "failed" "" "semgrep run failed"
        mark_unverified "static.semgrep" "semgrep execution failed"
      fi
    else
      record_tool "semgrep" "sast" "unverified" "" "Set CBIR_RUN_SEMGREP=1 to execute"
      mark_unverified "static.semgrep" "semgrep execution disabled"
    fi
  else
    record_tool "semgrep" "sast" "missing" "" "semgrep command not found"
    mark_unverified "static.semgrep" "semgrep command not found"
  fi

  if has_cmd dependency-check.sh; then
    if [[ "${CBIR_RUN_DEP_CHECK:-0}" == "1" ]]; then
      set +e
      dependency-check.sh --scan "$REPO_PATH" --format JSON --out "$ARTIFACT_DIR/static" > "$LOG_DIR/dependency-check.log" 2> "$LOG_DIR/dependency-check.err"
      local dep_rc=$?
      set -e
      if [[ $dep_rc -eq 0 || -s "$dep_out" ]]; then
        record_tool "dependency-check" "sca" "ok" "artifacts/static/dependency-check-report.json" "dependency-check run completed"
      else
        record_tool "dependency-check" "sca" "failed" "" "dependency-check failed"
        mark_unverified "static.sca" "dependency-check execution failed"
      fi
    else
      record_tool "dependency-check" "sca" "unverified" "" "Set CBIR_RUN_DEP_CHECK=1 to execute"
      mark_unverified "static.sca" "dependency-check execution disabled"
    fi
  else
    record_tool "dependency-check" "sca" "missing" "" "dependency-check.sh not found"
    mark_unverified "static.sca" "dependency-check.sh not found"
  fi
}

collect_dynamic_artifacts() {
  local runtime_json="$ARTIFACT_DIR/dynamic/runtime.json"
  local traces_json="$ARTIFACT_DIR/dynamic/trace-artifacts.json"

  if ! has_cmd python3; then
    record_tool "dynamic-runtime" "dynamic" "unverified" "" "python3 is required for dynamic summary"
    mark_unverified "dynamic.runtime" "python3 not available"
    return
  fi

  local workload_status="Unverified"
  local workload_message="CBIR_WORKLOAD_CMD not set"
  local workload_exit_code=""

  if [[ -n "${CBIR_WORKLOAD_CMD:-}" ]]; then
    set +e
    /usr/bin/time -p bash -lc "$CBIR_WORKLOAD_CMD" > "$LOG_DIR/workload.stdout.log" 2> "$LOG_DIR/workload.time.log"
    workload_exit_code="$?"
    set -e

    if [[ "$workload_exit_code" == "0" ]]; then
      workload_status="ok"
      workload_message="workload command executed"
    else
      workload_status="failed"
      workload_message="workload command returned non-zero"
      mark_unverified "dynamic.workload" "CBIR_WORKLOAD_CMD failed"
    fi
  else
    mark_unverified "dynamic.workload" "CBIR_WORKLOAD_CMD not set"
  fi

  if [[ -n "${CBIR_TRACE_FILE:-}" && -f "${CBIR_TRACE_FILE}" ]]; then
    cp "${CBIR_TRACE_FILE}" "$ARTIFACT_DIR/dynamic/trace-input.json"
    record_tool "trace-file" "dynamic" "ok" "artifacts/dynamic/trace-input.json" "trace file copied from CBIR_TRACE_FILE"
  else
    record_tool "trace-file" "dynamic" "unverified" "" "CBIR_TRACE_FILE not provided or missing"
    mark_unverified "dynamic.trace" "CBIR_TRACE_FILE not provided"
  fi

  python3 - "$runtime_json" "$workload_status" "$workload_message" "$workload_exit_code" "$POLICY_EFFECTIVE" <<'PY'
import json
import shutil
import sys
from datetime import datetime, timezone

runtime_path = sys.argv[1]
workload_status = sys.argv[2]
workload_message = sys.argv[3]
workload_exit_code = sys.argv[4]
policy_path = sys.argv[5]

try:
    policy = json.load(open(policy_path, "r", encoding="utf-8"))
except Exception:
    policy = {}

tools = {}
for name in policy.get("runtime", {}).get("tools", []):
    tools[name] = shutil.which(name) is not None

payload = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "workload": {
        "status": workload_status,
        "message": workload_message,
        "exit_code": int(workload_exit_code) if workload_exit_code not in ("", None) else None,
    },
    "tools_available": tools,
}

with open(runtime_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
PY

  record_tool "dynamic-runtime" "dynamic" "ok" "artifacts/dynamic/runtime.json" "runtime summary generated"

  if [[ -n "${CBIR_LATENCY_CSV:-}" && -f "${CBIR_LATENCY_CSV}" ]]; then
    python3 - "$CBIR_LATENCY_CSV" "$traces_json" <<'PY'
import csv
import json
import math
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
values = []

with src.open("r", encoding="utf-8", errors="ignore") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue
        try:
            values.append(float(row[0]))
        except ValueError:
            continue

values.sort()

def pct(sorted_values, p):
    if not sorted_values:
        return None
    idx = int(math.ceil((p / 100) * len(sorted_values))) - 1
    idx = max(0, min(idx, len(sorted_values) - 1))
    return sorted_values[idx]

payload = {
    "source": str(src),
    "count": len(values),
    "p50_ms": pct(values, 50),
    "p95_ms": pct(values, 95),
    "p99_ms": pct(values, 99),
}

out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
PY
    record_tool "latency-csv" "dynamic" "ok" "artifacts/dynamic/trace-artifacts.json" "latency percentiles extracted"
  else
    record_tool "latency-csv" "dynamic" "unverified" "" "CBIR_LATENCY_CSV not provided"
    mark_unverified "dynamic.latency" "CBIR_LATENCY_CSV not provided"
  fi
}

collect_architecture_models() {
  if ! has_cmd python3; then
    record_tool "architecture-model" "architecture" "unverified" "" "python3 is required for architecture model generation"
    mark_unverified "architecture.model" "python3 not available"
    return
  fi

  if [[ ! -s "$ARTIFACT_DIR/static/path-classification.tsv" ]]; then
    record_tool "architecture-model" "architecture" "unverified" "" "static classification missing"
    mark_unverified "architecture.model" "static/path-classification.tsv missing"
    return
  fi

  set +e
  python3 "$SCRIPT_DIR/build_architecture_models.py" \
    --repo-path "$REPO_PATH" \
    --artifacts-dir "$ARTIFACT_DIR" \
    --policy "$POLICY_EFFECTIVE" \
    > "$LOG_DIR/architecture_model.log" 2> "$LOG_DIR/architecture_model.err"
  local model_rc=$?
  set -e

  if [[ $model_rc -eq 0 && -s "$ARTIFACT_DIR/architecture/context-model.json" && -s "$ARTIFACT_DIR/architecture/component-model.json" ]]; then
    record_tool "architecture-model" "architecture" "ok" "artifacts/architecture/context-model.json" "context/container/component/scenario/deployment models generated"
  else
    record_tool "architecture-model" "architecture" "failed" "" "architecture model generation failed"
    mark_unverified "architecture.model" "Failed to generate architecture/*.json artifacts"
  fi
}

finalize_index() {
  python3 - "$OUTPUT_DIR" "$REPO_PATH" "$COMMIT_RANGE" "$MODE" "$TOP_N" "$GIT_HEAD" "$GIT_BRANCH" "$POLICY_EFFECTIVE" <<'PY'
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

output_dir = Path(sys.argv[1])
repo_path = sys.argv[2]
commit_range = sys.argv[3]
mode = sys.argv[4]
top_n = int(sys.argv[5])
git_head = sys.argv[6]
git_branch = sys.argv[7]
policy_path = Path(sys.argv[8])

artifacts_dir = output_dir / "artifacts"
policy = json.loads(policy_path.read_text(encoding="utf-8"))
analysis_categories = set(policy.get("collection", {}).get("analysis_categories", []))

# tools.json + unverified from TSV

def read_tsv(path):
    if not path.exists():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        if i == 0 or not line.strip():
            continue
        rows.append(line.split("\t"))
    return rows

tools = []
for cols in read_tsv(artifacts_dir / "tools.tsv"):
    while len(cols) < 5:
        cols.append("")
    tools.append(
        {
            "tool": cols[0],
            "category": cols[1],
            "status": cols[2],
            "output": cols[3],
            "message": cols[4],
        }
    )

unverified = []
for cols in read_tsv(artifacts_dir / "notes" / "unverified.tsv"):
    if len(cols) >= 2:
        unverified.append({"section": cols[0], "reason": cols[1]})

artifact_map = {}
for p in sorted(artifacts_dir.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(output_dir))
        key = str(p.relative_to(artifacts_dir)).replace(os.sep, ".")
        artifact_map[key] = rel

classification = {}
classification_path = artifacts_dir / "static" / "path-classification.tsv"
if classification_path.exists():
    lines = classification_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, line in enumerate(lines):
        if i == 0 or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        path, category, included, reason, ext = parts[:5]
        classification[path] = {
            "category": category,
            "included": included.lower() == "true",
            "reason": reason,
            "ext": ext,
        }

complexity_map = {}
complexity_path = artifacts_dir / "static" / "complexity.json"
if complexity_path.exists():
    try:
        comp = json.loads(complexity_path.read_text(encoding="utf-8"))
        for row in comp.get("top_files", []):
            f = row.get("file")
            if not f:
                continue
            complexity_map[f] = float(row.get("complexity_score", 0))
    except Exception:
        pass

architecture_map = {}
architecture_path = artifacts_dir / "static" / "architecture.json"
if architecture_path.exists():
    try:
        arch = json.loads(architecture_path.read_text(encoding="utf-8"))
        for row in arch.get("all_files", []):
            f = row.get("file")
            if not f:
                continue
            architecture_map[f] = float(row.get("coupling_score", 0))
    except Exception:
        pass

seed = []
churn_source = artifacts_dir / "git" / "churn_all.tsv"
if not churn_source.exists():
    churn_source = artifacts_dir / "git" / "churn_top.tsv"

if churn_source.exists():
    for line in churn_source.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or "\t" not in line:
            continue
        churn_raw, file_path = line.split("\t", 1)
        try:
            churn_value = int(churn_raw)
        except ValueError:
            continue

        meta = classification.get(file_path, {"category": "unknown", "included": True})
        category = meta.get("category", "unknown")
        included = bool(meta.get("included", True))
        if not included:
            continue
        if category not in analysis_categories:
            continue

        seed.append(
            {
                "rank": len(seed) + 1,
                "file": file_path,
                "category": category,
                "churn": churn_value,
                "complexity": complexity_map.get(file_path, 0),
                "architecture": architecture_map.get(file_path, 0),
                "evidence_refs": [
                    "artifacts/git/churn_all.tsv" if (artifacts_dir / "git" / "churn_all.tsv").exists() else "artifacts/git/churn_top.tsv",
                    "artifacts/static/complexity.json",
                    "artifacts/static/architecture.json",
                ],
            }
        )
        if len(seed) >= top_n:
            break

(artifacts_dir / "finding-seed.json").write_text(json.dumps(seed, indent=2, ensure_ascii=False), encoding="utf-8")

category_counter = Counter(item.get("category", "unknown") for item in seed)
metrics = {
    "seed_count": len(seed),
    "unverified_count": len(unverified),
    "tool_total": len(tools),
    "tool_missing_or_unverified": len([t for t in tools if t.get("status") in {"missing", "unverified", "failed"}]),
    "seed_category_distribution": dict(category_counter),
}
(artifacts_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

index = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "repo_path": repo_path,
    "commit_range": commit_range,
    "mode": mode,
    "top_n": top_n,
    "policy_path": str(policy_path),
    "git": {
        "head": git_head,
        "branch": git_branch,
    },
    "artifacts": artifact_map,
    "unverified": unverified,
}

(artifacts_dir / "tools.json").write_text(json.dumps(tools, indent=2, ensure_ascii=False), encoding="utf-8")
(artifacts_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
PY
}

collect_tracked_files
collect_git_artifacts

if [[ "$MODE" == "static" || "$MODE" == "full" ]]; then
  collect_static_core
  collect_coverage
  collect_static_security
else
  record_tool "static-track" "static" "unverified" "" "mode is dynamic"
  mark_unverified "static.track" "Static track skipped because mode=dynamic"
fi

if [[ "$MODE" == "dynamic" || "$MODE" == "full" ]]; then
  collect_dynamic_artifacts
else
  record_tool "dynamic-track" "dynamic" "unverified" "" "mode is static"
  mark_unverified "dynamic.track" "Dynamic track skipped because mode=static"
fi

collect_architecture_models

finalize_index

echo "Artifacts generated at: $OUTPUT_DIR"
echo "Index file: $ARTIFACT_DIR/index.json"
