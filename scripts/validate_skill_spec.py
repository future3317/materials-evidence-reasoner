#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the public Agent Skills specification."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

ALLOWED_FIELDS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed with ---")
    payload = text[4:end]
    parsed = yaml.safe_load(payload)
    if not isinstance(parsed, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return parsed


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    path = path.resolve()
    skill_file = path / "SKILL.md" if path.is_dir() else path
    skill_dir = skill_file.parent.resolve()
    try:
        metadata = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return [str(exc)]

    extra = set(metadata) - ALLOWED_FIELDS
    if extra:
        errors.append(f"unexpected frontmatter fields: {sorted(extra)}")

    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name must be a non-empty string")
    else:
        normalized = unicodedata.normalize("NFKC", name)
        if len(normalized) > 64:
            errors.append("name exceeds 64 characters")
        if normalized != normalized.lower():
            errors.append("name must be lowercase")
        if normalized.startswith("-") or normalized.endswith("-") or "--" in normalized:
            errors.append("name cannot start/end with a hyphen or contain consecutive hyphens")
        if not re.fullmatch(r"[a-z0-9-]+", normalized):
            errors.append("name must contain only lowercase ASCII letters, numbers, and hyphens")
        if skill_dir.name != normalized:
            errors.append(f"parent directory '{skill_dir.name}' must match name '{normalized}'")

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description must be a non-empty string")
    elif len(description) > 1024:
        errors.append(f"description exceeds 1024 characters ({len(description)})")

    compatibility = metadata.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            errors.append("compatibility must be a string")
        elif not 1 <= len(compatibility) <= 500:
            errors.append(f"compatibility must be 1-500 characters ({len(compatibility)})")

    arbitrary = metadata.get("metadata")
    if arbitrary is not None:
        if not isinstance(arbitrary, dict):
            errors.append("metadata must be a mapping")
        else:
            for key, value in arbitrary.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append("metadata keys and values must be strings")

    allowed_tools = metadata.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append("allowed-tools must be a space-separated string")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.path)
    if errors:
        print(f"AGENT SKILL SPEC INVALID: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("AGENT SKILL SPEC VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
