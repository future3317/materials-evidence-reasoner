#!/usr/bin/env python3
"""Validate editable external knowledge assets used by the skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


def load(name: str) -> Any:
    return json.loads((REFERENCES / name).read_text(encoding="utf-8"))


def absolute_reference(value: Any) -> bool:
    text = str(value or "")
    return (
        Path(text).is_absolute()
        or bool(re.match(r"^[A-Za-z]:", text))
        or text.startswith("\\\\")
        or bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", text))
    )


def validate() -> list[str]:
    errors: list[str] = []
    try:
        lexicon = load("adapter-routing-lexicon.json")
        schema = load("adapter-routing-lexicon.schema.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read routing assets: {exc}"]

    try:
        import jsonschema

        validator = jsonschema.validators.validator_for(schema)(schema)
        errors.extend(error.message for error in validator.iter_errors(lexicon))
    except ImportError:
        if not isinstance(lexicon.get("adapters"), dict):
            errors.append("routing lexicon must contain adapters")

    adapters = lexicon.get("adapters", {}) if isinstance(lexicon, dict) else {}
    signal_ids: dict[str, str] = {}
    for adapter_id, adapter in adapters.items():
        if not isinstance(adapter, dict):
            continue
        strengths = {signal.get("strength") for signal in adapter.get("signals", []) if isinstance(signal, dict)}
        if strengths != {"strong", "supporting", "weak", "exclusion"}:
            errors.append(f"{adapter_id}: signal strengths must cover strong/supporting/weak/exclusion")
        for signal in adapter.get("signals", []):
            if not isinstance(signal, dict):
                continue
            signal_id = signal.get("signal_id")
            if signal_id in signal_ids:
                errors.append(f"duplicate signal_id {signal_id}: {signal_ids[signal_id]} and {adapter_id}")
            else:
                signal_ids[signal_id] = adapter_id
            all_terms = signal.get("terms_en", []) + signal.get("terms_zh", []) + signal.get("abbreviations", []) + signal.get("symbols", [])
            if len(all_terms) != len({str(term).casefold() for term in all_terms}):
                errors.append(f"{adapter_id}/{signal_id}: duplicate surface term")

    policy = lexicon.get("matching_policy", {}) if isinstance(lexicon, dict) else {}
    maintenance = policy.get("maintenance_contract")
    if not maintenance or absolute_reference(maintenance) or not (REFERENCES / maintenance).is_file():
        errors.append("matching_policy.maintenance_contract must be an existing relative reference")

    try:
        registry = load("adapter-registry.json")
        registry_ids = {item.get("adapter_id") for item in registry.get("adapters", []) if isinstance(item, dict)}
        lexicon_ids = set(adapters)
        if registry_ids != lexicon_ids:
            errors.append(f"registry/lexicon adapter mismatch: registry-only={sorted(registry_ids - lexicon_ids)}, lexicon-only={sorted(lexicon_ids - registry_ids)}")
        for key in ("execution_standard", "routing_lexicon", "routing_lexicon_schema", "field_contract_catalog", "field_contract_schema", "registry_schema", "source_backed_catalog", "standards_and_sources"):
            value = registry.get(key)
            if not isinstance(value, str) or absolute_reference(value) or not (REFERENCES / value).is_file():
                errors.append(f"registry.{key} must point to an existing relative reference")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read adapter registry: {exc}")

    try:
        # Reuse the field-alias collision check instead of maintaining a second
        # alias parser here.
        sys.path.insert(0, str(ROOT / "scripts"))
        from prepare_intake import load_aliases

        load_aliases()
    except Exception as exc:
        errors.append(f"intake aliases invalid: {type(exc).__name__}: {exc}")

    try:
        intent_lexicon = load("task-intent-lexicon.json")
        intent_schema = load("task-intent-lexicon.schema.json")
        try:
            import jsonschema

            intent_validator = jsonschema.validators.validator_for(intent_schema)(intent_schema)
            errors.extend(f"task intent schema: {error.message}" for error in intent_validator.iter_errors(intent_lexicon))
        except ImportError:
            pass
        intents = intent_lexicon.get("intents", {})
        policy = intent_lexicon.get("matching_policy", {})
        if not policy.get("semantic_match_required") or not policy.get("surface_terms_are_recall_only"):
            errors.append("task intent lexicon must mark surface terms as recall-only and require semantic matching")
        for intent_id, intent in intents.items():
            if not isinstance(intent, dict) or not intent.get("concept"):
                errors.append(f"task intent is missing concept: {intent_id}")
            elif not (intent.get("terms_zh") or intent.get("terms_en")):
                errors.append(f"task intent has no recall terms: {intent_id}")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read task intent lexicon: {exc}")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print(f"KNOWLEDGE ASSETS INVALID: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("KNOWLEDGE ASSETS VALID: routing lexicon, registry references, and intake aliases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
