#!/usr/bin/env python3
"""Normalize canonical and explicitly supported legacy result fields for display.

This module is a compatibility adapter, not a relaxed output validator.  Its
output is suitable for the offline viewer or a migration preview.  Run
validate_output.py on the final canonical result separately.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALIASES = ROOT / "references" / "output-field-aliases.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    return value if isinstance(value, list) else [value]


def first_value(item: dict[str, Any], keys: list[str], fallback: Any = None) -> Any:
    for key in keys:
        value = item.get(key)
        if value is not None and value != "":
            return value
    return fallback


def alias(spec: dict[str, Any], group: str, field: str) -> list[str]:
    return list(spec.get(group, {}).get(field, [field]))


def normalize_collection_item(item: Any, collection: str, index: int, spec: dict[str, Any]) -> dict[str, Any]:
    source = dict(item) if isinstance(item, dict) else {"value": item}
    result = dict(source)
    collection_aliases = spec.get("collections", {}).get(collection, {})
    result["id"] = first_value(source, list(collection_aliases.get("id", ["id"])), f"{collection}-{index + 1}")
    if collection == "evidence":
        result["raw_content"] = first_value(source, list(collection_aliases.get("raw_content", ["raw_content"])), "")
    if collection == "property_records":
        result["property_raw"] = first_value(source, list(collection_aliases.get("property_raw", ["property_raw"])), "")
    return result


def normalize_hypothesis(item: Any, index: int, spec: dict[str, Any]) -> dict[str, Any]:
    source = dict(item) if isinstance(item, dict) else {"value": item}
    result = dict(source)
    result["id"] = first_value(source, alias(spec, "hypotheses", "id"), f"H-{index + 1}")
    result["statement"] = first_value(source, alias(spec, "hypotheses", "statement"), "未命名假设")
    result["mechanism_chain"] = as_list(source.get("mechanism_chain"))
    result["support_evidence_ids"] = as_list(source.get("support_evidence_ids"))
    result["counterevidence_ids"] = as_list(source.get("counterevidence_ids"))
    result["missing_evidence"] = as_list(source.get("missing_evidence"))
    result["unique_predictions"] = as_list(source.get("unique_predictions"))
    result["falsifiers"] = as_list(first_value(source, alias(spec, "hypotheses", "falsifiers"), source.get("falsifier")))
    result["status"] = first_value(source, alias(spec, "hypotheses", "status"), "speculative")
    result["evidence_status"] = first_value(source, alias(spec, "hypotheses", "legacy_evidence_status"), "not-assessed")
    result["legacy_supporting_evidence"] = as_list(source.get("supporting_evidence"))
    result["legacy_contradicting_evidence"] = as_list(source.get("contradicting_evidence"))
    result["legacy_falsifier"] = as_list(source.get("falsifier"))
    return result


def outcome_list(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [f"{key}: {item}" for key, item in value.items()]
    return [str(item) for item in as_list(value)]


def normalize_verification_item(item: Any, index: int, spec: dict[str, Any]) -> dict[str, Any]:
    source = dict(item) if isinstance(item, dict) else {"value": item}
    result = dict(source)
    result["id"] = first_value(source, alias(spec, "verification_plan", "id"), f"V-{index + 1}")
    result["action"] = first_value(source, alias(spec, "verification_plan", "action"), "未命名验证项")
    result["description"] = first_value(source, alias(spec, "verification_plan", "description"), "")
    result["hypothesis_ids"] = as_list(first_value(source, alias(spec, "verification_plan", "hypothesis_ids"), []))
    result["minimal_change"] = first_value(source, alias(spec, "verification_plan", "minimal_change"), "")
    result["controls"] = as_list(source.get("controls"))
    result["expected_outcomes"] = outcome_list(source.get("expected_outcomes"))
    result["decision_rule"] = "；".join(str(value) for value in as_list(first_value(source, alias(spec, "verification_plan", "decision_rule"), "")))
    result["cost"] = first_value(source, alias(spec, "verification_plan", "cost"), "")
    result["risk"] = first_value(source, alias(spec, "verification_plan", "risk"), "")
    result["repeats"] = first_value(source, alias(spec, "verification_plan", "repeats"), "")
    result["status"] = first_value(source, ["status"], "proposed")
    result["priority_tier"] = first_value(source, ["priority_tier"], "medium")
    result["information_gap_ids"] = as_list(source.get("information_gap_ids"))
    result["stop_rule"] = first_value(source, alias(spec, "verification_plan", "stop_rule"), "")
    return result


def normalize_viewer_data(document: dict[str, Any], aliases: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a deterministic, display-oriented view without inventing evidence."""

    spec = aliases or load_json(DEFAULT_ALIASES)
    result = dict(document)
    for collection in spec.get("collections", {}):
        if collection in result:
            result[collection] = [normalize_collection_item(item, collection, index, spec) for index, item in enumerate(as_list(result[collection]))]
    result["hypotheses"] = [normalize_hypothesis(item, index, spec) for index, item in enumerate(as_list(document.get("hypotheses")))]
    result["verification_plan"] = [normalize_verification_item(item, index, spec) for index, item in enumerate(as_list(document.get("verification_plan")))]
    legacy = document.get("schema_version") != "4.6" or any(
        key in item
        for item in as_list(document.get("hypotheses"))
        if isinstance(item, dict)
        for key in ("hypothesis_id", "title", "supporting_evidence", "falsifier")
    ) or any(
        key in item
        for item in as_list(document.get("verification_plan"))
        if isinstance(item, dict)
        for key in ("experiment_id", "target_hypotheses", "decision_rules")
    )
    result["_compatibility"] = {
        "mode": "explicit-field-aliases" if legacy else "canonical",
        "canonical_schema": spec["canonical_schema"],
        "canonical_validation": "not-validated",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON result to inspect or normalize")
    parser.add_argument("-o", "--output", type=Path, help="Write normalized viewer JSON")
    parser.add_argument("--check", action="store_true", help="Only report detected compatibility fields")
    args = parser.parse_args()
    document = load_json(args.input)
    if not isinstance(document, dict):
        raise SystemExit("top-level JSON must be an object")
    normalized = normalize_viewer_data(document)
    legacy = document.get("schema_version") != "4.6" or any(key in document for key in ("hypothesis_id", "title", "supporting_evidence"))
    print(f"COMPATIBILITY {'legacy-input' if legacy else 'canonical-or-compatible'}; hypotheses={len(normalized['hypotheses'])}; verification_plan={len(normalized['verification_plan'])}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif not args.check:
        print(json.dumps(normalized, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
