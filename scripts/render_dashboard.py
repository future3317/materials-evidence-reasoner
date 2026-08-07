#!/usr/bin/env python3
"""Render a standalone offline HTML dashboard from Materials Evidence JSON."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "viewer" / "index.html"
MARKER = '<script id="embedded-data" type="application/json"></script>'


def rebase_relative_paths(data: dict, source_root: Path, target_root: Path) -> None:
    """Make embedded artifact/input links relative to the generated HTML."""
    manifest = data.get("artifact_manifest", [])
    if isinstance(manifest, list):
        for item in manifest:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                continue
            path = Path(item["path"])
            if path.is_absolute() or (len(path.parts) > 0 and ":" in path.parts[0]):
                continue
            item["path"] = os.path.relpath(source_root / path, target_root).replace(os.sep, "/")
    assessment = data.get("input_assessment", {})
    inputs = assessment.get("received_inputs", []) if isinstance(assessment, dict) else []
    if isinstance(inputs, list):
        for item in inputs:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                continue
            path = Path(item["path"])
            if path.is_absolute() or (len(path.parts) > 0 and ":" in path.parts[0]):
                continue
            item["path"] = os.path.relpath(source_root / path, target_root).replace(os.sep, "/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Materials Evidence JSON")
    parser.add_argument("-o", "--output", type=Path, default=Path("materials-dashboard.html"))
    parser.add_argument("--skip-validation", action="store_true", help="Render even if validate_output.py fails")
    args = parser.parse_args()

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR cannot read JSON: {exc}", file=sys.stderr)
        return 2

    if not args.skip_validation:
        validator = ROOT / "scripts" / "validate_output.py"
        result = subprocess.run([sys.executable, str(validator), str(args.input)], cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            if result.stdout:
                print(result.stdout.rstrip(), file=sys.stderr)
            if result.stderr:
                print(result.stderr.rstrip(), file=sys.stderr)
            print("ERROR dashboard was not rendered because JSON validation failed. Use --skip-validation only for inspection.", file=sys.stderr)
            return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        print("ERROR viewer template marker is missing or duplicated", file=sys.stderr)
        return 3
    rebase_relative_paths(data, args.input.resolve().parent, args.output.resolve().parent)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    embedded = f'<script id="embedded-data" type="application/json">{payload}</script>'
    output = template.replace(MARKER, embedded)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"WROTE {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
