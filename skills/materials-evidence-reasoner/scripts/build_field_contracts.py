#!/usr/bin/env python3
"""Build semantic, machine-readable field contracts from adapter references."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "references"
OUTPUT_PATH = REFERENCE_DIR / "adapter-field-contracts.json"
EXCLUDED_FILES = {"adapter-interface.md", "adapter-superconductivity.md"}
ADAPTER_RE = re.compile(r"适配器：`([^`]+)`")
RULESET_RE = re.compile(r"规则版本：`([^`]+)`")
HEADING_RE = re.compile(r"^### `([^`]+)`\s*$")
INLINE_RECORD_RE = re.compile(r"^`([^`]+)`\s+字段：(.+)$")
TOKEN_RE = re.compile(r"`([a-z][a-z0-9_-]*)`")


RECORD_DESCRIPTIONS = {
    "identity": "目标材料或组件的领域身份与分类快照。",
    "state": "与目标实体和证据时点绑定的领域状态快照。",
    "protocol": "实际执行的方法、条件、序列与判据。",
    "assessment": "由可定位证据支持的领域判定、结果集合或一致性审计。",
    "performance": "按领域口径组织、但仍引用核心 property record 的性能集合。",
    "process": "引用核心 process run 的领域工艺语义和过程谱系。",
    "measurement": "引用核心 measurement run 和 data artifact 的领域测量语义。",
    "simulation": "引用核心 simulation job 的领域模型、输入、执行和输出语义。",
}


def field_tokens(text: str) -> list[str]:
    """Return only field-position tokens, never enum values after a colon."""
    return TOKEN_RE.findall(text)


def field_line_tokens(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("字段："):
        return field_tokens(stripped.split("：", 1)[1])
    if not stripped.startswith("- "):
        return []
    candidate = stripped[2:]
    separators = [pos for pos in (candidate.find("："), candidate.find(":")) if pos >= 0]
    if separators:
        candidate = candidate[: min(separators)]
    return field_tokens(candidate)


def parse_reference(path: Path) -> dict[str, dict[str, Any]]:
    adapters: dict[str, dict[str, Any]] = {}
    current_adapter: str | None = None
    current_record: str | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        adapter_match = ADAPTER_RE.search(line)
        if adapter_match:
            current_adapter = adapter_match.group(1)
            ruleset_match = RULESET_RE.search(line)
            adapters.setdefault(
                current_adapter,
                {"ruleset_version": ruleset_match.group(1) if ruleset_match else "unknown", "records": {}},
            )
            current_record = None
            continue

        inline_match = INLINE_RECORD_RE.match(line)
        if inline_match and current_adapter:
            record_type, field_text = inline_match.groups()
            adapters[current_adapter]["records"].setdefault(record_type, set()).update(
                field_tokens(field_text)
            )
            current_record = None
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match and current_adapter:
            current_record = heading_match.group(1)
            adapters[current_adapter]["records"].setdefault(current_record, set())
            continue

        if line.startswith("## ") or line.startswith("### "):
            current_record = None
            continue

        if current_adapter and current_record:
            adapters[current_adapter]["records"][current_record].update(field_line_tokens(line))

    return adapters


def reference_target(field_name: str) -> str | None:
    singular = {
        "entity_id": "core entity",
        "property_id": "property_records[]",
        "measurement_run_id": "measurement_runs[]",
        "process_run_id": "process_runs[]",
        "simulation_job_id": "simulation_jobs[]",
        "artifact_id": "data_artifacts[]",
        "evidence_id": "evidence[]",
        "record_id": "domain_records[]",
    }
    plural = {
        "entity_ids": "core entities",
        "property_ids": "property_records[]",
        "measurement_run_ids": "measurement_runs[]",
        "process_run_ids": "process_runs[]",
        "simulation_job_ids": "simulation_jobs[]",
        "artifact_ids": "data_artifacts[]",
        "evidence_ids": "evidence[]",
        "record_ids": "domain_records[]",
    }
    for suffix, target in plural.items():
        if field_name.endswith(suffix):
            return target
    for suffix, target in singular.items():
        if field_name.endswith(suffix):
            return target
    return None


def semantic_role(field_name: str) -> str:
    target = reference_target(field_name)
    if target:
        return f"reference to {target}"
    if field_name.endswith("_evidence") or "evidence" in field_name:
        return "structured evidence summary with evidence_ids"
    if field_name.endswith("_status") or field_name.endswith("_state"):
        return "evidence-bound categorical state"
    if field_name.endswith("_basis") or field_name.endswith("_definition"):
        return "normalization, calculation, or decision basis"
    if "condition" in field_name or field_name in {"temperature", "pressure", "geometry", "orientation"}:
        return "reported experimental or process condition"
    if field_name.endswith("_raw"):
        return "verbatim source term"
    if field_name.endswith("_canonical"):
        return "normalized term linked to the raw term"
    return "domain value or structured description"


def expected_shape(field_name: str) -> dict[str, Any]:
    if field_name.endswith("_ids"):
        return {"json_types": ["array"], "items": "stable ID string", "reference_target": reference_target(field_name)}
    if field_name.endswith("_id"):
        return {"json_types": ["string"], "reference_target": reference_target(field_name)}
    if field_name.endswith("_evidence") or "evidence" in field_name:
        return {
            "json_types": ["object", "array"],
            "minimum_content": ["claim_or_observation", "evidence_ids"],
        }
    return {
        "json_types": ["string", "number", "boolean", "object", "array"],
        "note": "Preserve the reported representation; use core property_records[] for measured numeric properties.",
    }


def describe_record(record_type: str) -> str:
    for token, description in RECORD_DESCRIPTIONS.items():
        if token in record_type:
            return description
    return "仅在本记录类型的目标实体、来源证据和领域含义均已解析时创建。"


def build_field_contract(field_name: str) -> dict[str, Any]:
    target = reference_target(field_name)
    if target:
        evidence_rule = (
            "Referenced IDs must exist in the core output and be supported by the same source or an explicit derivation chain."
        )
    else:
        evidence_rule = (
            "Populate only from a directly reported value, a labeled figure/table estimate, or an explicit derivation; attach field-level evidence."
        )
    return {
        "semantic_role": semantic_role(field_name),
        "expected_shape": expected_shape(field_name),
        "requiredness": "conditional",
        "evidence_rule": evidence_rule,
        "missing_policy": "Omit the field and add missing_information when decision-relevant; never insert a typical or default value.",
        "forbidden_inference": [
            "Do not infer an executed condition from instrument capability, a cited method, or a recommended standard.",
            "Do not transfer a value between samples, process states, measurement runs, model variants, or hierarchy levels.",
        ],
    }


def main() -> int:
    merged: dict[str, dict[str, Any]] = {}
    source_files: list[str] = []
    for path in sorted(REFERENCE_DIR.glob("adapter-*.md")):
        if path.name in EXCLUDED_FILES:
            continue
        parsed = parse_reference(path)
        if not parsed:
            continue
        source_files.append(path.name)
        for adapter_id, payload in parsed.items():
            if adapter_id in merged:
                raise ValueError(f"duplicate adapter definition: {adapter_id}")
            merged[adapter_id] = payload

    empty_records = [
        f"{adapter_id}/{record_type}"
        for adapter_id, payload in merged.items()
        for record_type, fields in payload["records"].items()
        if not fields
    ]
    if empty_records:
        raise ValueError(f"record type has no machine-readable fields: {empty_records}")

    output = {
        "$schema": "adapter-field-contracts.schema.json",
        "contract_version": "2.0.0",
        "generated_from": source_files,
        "field_conventions": {
            "id_references": "Fields ending in _id or _ids reference stable objects; they never embed copied core records.",
            "measured_values": "Measured numeric properties belong in property_records[]; adapters reference them with *_property_id(s).",
            "conditions": "Report actual source-bound conditions. Unreported temperature, pressure, atmosphere, rate, geometry, and software settings remain missing.",
            "field_evidence": "Every populated payload field must be covered by domain_record.field_evidence or by an explicitly referenced core record.",
            "unknowns": "Unknown, not-reported, not-measured, inaccessible, conflicting, and not-applicable are distinct states.",
        },
        "adapters": {
            adapter_id: {
                "ruleset_version": "2.0.0",
                "record_types": {
                    record_type: {
                        "description": describe_record(record_type),
                        "create_when": [
                            "the adapter decision for this source is load",
                            "the record is bound to at least one target entity",
                            "at least one allowed payload field is directly supported",
                        ],
                        "do_not_create_when": [
                            "the adapter decision is candidate or skip",
                            "the only support is a citation, apparatus mention, generic background, or inferred typical value",
                            "the record would duplicate a core entity, process, measurement, property, artifact, or simulation object",
                        ],
                        "required_fields": [],
                        "required_any_of": [sorted(fields)],
                        "allowed_fields": sorted(fields),
                        "field_count": len(fields),
                        "fields": {
                            field_name: build_field_contract(field_name)
                            for field_name in sorted(fields)
                        },
                    }
                    for record_type, fields in sorted(payload["records"].items())
                },
            }
            for adapter_id, payload in sorted(merged.items())
        },
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"WROTE {OUTPUT_PATH.name}: {len(merged)} adapters, "
        f"{sum(len(payload['records']) for payload in merged.values())} record types, "
        f"{sum(len(fields) for payload in merged.values() for fields in payload['records'].values())} fields"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
