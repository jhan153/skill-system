#!/usr/bin/env python3
"""Create placeholder research artifact workspace directories only.

This is not a lifecycle executor. It does not search the web, download
datasets, install dependencies, run training, run evaluation, or claim that any
research stage is complete. It creates empty directories and placeholder
template files only after explicit user request.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DIRS = [
    "papers", "papers/draft", "papers/draft/figures", "papers/draft/tables",
    "experiments", "experiments/configs", "experiments/data", "experiments/src", "experiments/tests",
    "analysis", "review",
]

PLACEHOLDERS = {
    "papers/literature_review.md": "# Literature Review\n\n## Scope\n\n## Search Strategy\n\n## Evidence Table\n\n## Synthesis\n\n## Gaps\n\n## References\n",
    "papers/ideation_output.json": "{}\n",
    "papers/research_plan.json": "{}\n",
    "papers/experiment_blueprint.json": "{}\n",
    "analysis/statistical_report.md": "# Statistical Report\n\n## Data Provenance\n\n## Analysis Question\n\n## Test Selection\n\n## Results\n\n## Limitations\n",
    "review/peer_review.md": "# Peer Review\n\n## Summary\n\n## Major Concerns\n\n## Minor Concerns\n\n## Reproducibility\n\n## Revision Advice\n",
    "experiments/README.md": "# Experiments\n\nDocument setup, data access, commands, and reproducibility notes here.\n",
}

def write_if_missing(path: Path, text: str) -> None:
    if not path.exists():
        path.write_text(text, encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--topic", default="")
    parser.add_argument("--mode", default="original")
    parser.add_argument("--domain", default="general")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for rel in DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "topic": args.topic,
        "mode": args.mode,
        "domain": args.domain,
        "network_used": False,
        "downloads_performed": False,
        "training_run": False,
    }
    write_if_missing(root / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for rel, text in PLACEHOLDERS.items():
        write_if_missing(root / rel, text)
    print(f"Initialized placeholder research workspace at {root}")

if __name__ == "__main__":
    main()
