#!/usr/bin/env python3
"""Validate Materials Evidence Reasoner JSON output."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


REQUIRED_TOP_LEVEL = (
    "schema_version",
    "run_id",
    "loop_state",
    "decision_profile",
    "decision",
    "input_assessment",
    "condition_registry",
    "sources",
    "evidence",
    "entities",
    "process_runs",
    "data_artifacts",
    "analysis_steps",
    "measurement_runs",
    "simulation_jobs",
    "property_records",
    "baseline_packages",
    "comparability_assessments",
    "deviation_episodes",
    "error_budgets",
    "anomaly_propagation_chains",
    "mechanism_graphs",
    "mechanism_nodes",
    "mechanism_edges",
    "mechanism_updates",
    "models",
    "hypotheses",
    "information_gaps",
    "verification_plan",
    "experiment_sets",
    "adapter_decisions",
    "domain_records",
    "experience_updates",
    "pspp_maps",
    "missing_information",
    "artifact_manifest",
    "quality",
)

ID_COLLECTIONS = {
    "condition_registry": "condition",
    "sources": "source",
    "evidence": "evidence",
    "entities": "entity",
    "process_runs": "process_run",
    "data_artifacts": "data_artifact",
    "analysis_steps": "analysis_step",
    "measurement_runs": "measurement_run",
    "simulation_jobs": "simulation_job",
    "property_records": "property_record",
    "baseline_packages": "baseline_package",
    "comparability_assessments": "comparability_assessment",
    "deviation_episodes": "deviation_episode",
    "error_budgets": "error_budget",
    "anomaly_propagation_chains": "anomaly_chain",
    "mechanism_graphs": "mechanism_graph",
    "mechanism_nodes": "mechanism_node",
    "mechanism_edges": "mechanism_edge",
    "mechanism_updates": "mechanism_update",
    "models": "model",
    "hypotheses": "hypothesis",
    "information_gaps": "information_gap",
    "verification_plan": "verification_item",
    "experiment_sets": "experiment_set",
    "domain_records": "domain_record",
    "experience_updates": "experience_update",
    "pspp_maps": "pspp_map",
    "artifact_manifest": "artifact",
}

REFERENCE_TARGETS = {
    "condition_id": "condition",
    "condition_ids": "condition",
    "source_id": "source",
    "source_ids": "source",
    "evidence_id": "evidence",
    "evidence_ids": "evidence",
    "input_evidence_ids": "evidence",
    "support_evidence_ids": "evidence",
    "counterevidence_ids": "evidence",
    "figure_or_table_evidence_ids": "evidence",
    "figure_evidence_ids": "evidence",
    "validation_evidence_ids": "evidence",
    "entity_id": "entity",
    "entity_ids": "entity",
    "parent_ids": "entity",
    "input_entity_ids": "entity",
    "output_entity_ids": "entity",
    "primary_entity_id": "entity",
    "process_run_id": "process_run",
    "process_run_ids": "process_run",
    "measurement_run_id": "measurement_run",
    "measurement_run_ids": "measurement_run",
    "simulation_job_id": "simulation_job",
    "simulation_job_ids": "simulation_job",
    "parent_job_ids": "simulation_job",
    "data_artifact_id": "data_artifact",
    "data_artifact_ids": "data_artifact",
    "input_artifact_ids": "data_artifact",
    "output_artifact_ids": "data_artifact",
    "parent_artifact_ids": "data_artifact",
    "analysis_step_id": "analysis_step",
    "analysis_step_ids": "analysis_step",
    "generated_by_analysis_step_id": "analysis_step",
    "property_record_id": "property_record",
    "property_record_ids": "property_record",
    "target_property_record_ids": "property_record",
    "transition_width_property_id": "property_record",
    "input_property_record_ids": "property_record",
    "baseline_package_id": "baseline_package",
    "comparability_assessment_id": "comparability_assessment",
    "hypothesis_ids": "hypothesis",
    "affected_hypothesis_ids": "hypothesis",
    "hypotheses_discriminated": "hypothesis",
    "deviation_episode_id": "deviation_episode",
    "deviation_episode_ids": "deviation_episode",
    "affected_deviation_episode_ids": "deviation_episode",
    "error_budget_id": "error_budget",
    "error_budget_ids": "error_budget",
    "anomaly_propagation_chain_id": "anomaly_chain",
    "anomaly_propagation_chain_ids": "anomaly_chain",
    "information_gap_id": "information_gap",
    "information_gap_ids": "information_gap",
    "verification_item_id": "verification_item",
    "verification_item_ids": "verification_item",
    "experiment_set_id": "experiment_set",
    "experiment_set_ids": "experiment_set",
    "pspp_map_id": "pspp_map",
    "pspp_map_ids": "pspp_map",
    "mechanism_graph_id": "mechanism_graph",
    "mechanism_graph_ids": "mechanism_graph",
    "graph_id": "mechanism_graph",
    "graph_ids": "mechanism_graph",
    "target_graph_id": "mechanism_graph",
    "supersedes_graph_id": "mechanism_graph",
    "mechanism_node_id": "mechanism_node",
    "mechanism_node_ids": "mechanism_node",
    "target_node_id": "mechanism_node",
    "new_node_ids": "mechanism_node",
    "mechanism_edge_id": "mechanism_edge",
    "mechanism_edge_ids": "mechanism_edge",
    "linked_mechanism_edge_ids": "mechanism_edge",
    "target_edge_id": "mechanism_edge",
    "new_edge_ids": "mechanism_edge",
    "supersedes_edge_id": "mechanism_edge",
    "mechanism_update_id": "mechanism_update",
    "mechanism_update_ids": "mechanism_update",
    "update_ids": "mechanism_update",
    "created_from_experience_update_ids": "experience_update",
    "linked_hypothesis_ids": "hypothesis",
    "proposed_support_evidence_ids": "evidence",
    "proposed_conflict_evidence_ids": "evidence",
    "model_id": "model",
    "model_ids": "model",
    "resolution_evidence_ids": "evidence",
    "same_transition_as": "domain_record",
    "microstructure_record_ids": "domain_record",
    "competing_order_ids": "domain_record",
    "depends_on": "artifact",
}

VALID_ADAPTER_STATUSES = {"implemented", "specified", "planned"}
VALID_VERIFICATION_STATUSES = {"provisional", "source-backed", "human-adjudicated"}
VALID_SIGNAL_STRENGTHS = {"strong", "supporting", "weak", "exclusion"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(document: Any, schema: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        import jsonschema
    except ImportError:
        warnings.append(
            "The optional 'jsonschema' package is unavailable; ran structural and reference checks only."
        )
        return errors, warnings

    try:
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.absolute_path) or "$"
            errors.append(f"schema {location}: {error.message}")
    except Exception as exc:  # pragma: no cover - protects CLI diagnostics
        errors.append(f"schema validator failure: {exc}")
    return errors, warnings


def load_adapter_schemas(reference_dir: Path) -> tuple[dict[str, Any], list[str]]:
    schemas: dict[str, Any] = {}
    errors: list[str] = []
    for path in sorted(reference_dir.glob("adapter-*.schema.json")):
        try:
            schema = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load adapter schema {path.name}: {exc}")
            continue
        adapter_id = schema.get("x-adapter-id") if isinstance(schema, dict) else None
        if not isinstance(adapter_id, str) or not adapter_id:
            # Catalog/registry schemas share the adapter-*.schema.json naming family.
            continue
        if adapter_id in schemas:
            errors.append(f"duplicate adapter schema for '{adapter_id}'")
            continue
        schemas[adapter_id] = schema
    return schemas, errors


def load_adapter_registry(reference_dir: Path) -> tuple[dict[str, Any], list[str]]:
    path = reference_dir / "adapter-registry.json"
    errors: list[str] = []
    try:
        registry = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot load adapter registry: {exc}"]
    if not isinstance(registry, dict):
        return {}, ["adapter registry must be a JSON object"]

    registry_schema_path = reference_dir / "adapter-registry.schema.json"
    if registry_schema_path.is_file():
        try:
            registry_schema = load_json(registry_schema_path)
            schema_validation_errors, _ = schema_errors(registry, registry_schema)
            errors.extend(f"adapter registry {error}" for error in schema_validation_errors)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load adapter registry schema: {exc}")

    adapters = registry.get("adapters")
    if not isinstance(adapters, list):
        return registry, ["adapter registry 'adapters' must be an array"]
    for asset_key in (
        "execution_standard",
        "routing_lexicon",
        "routing_lexicon_schema",
        "field_contract_catalog",
        "field_contract_schema",
        "registry_schema",
        "benchmark_catalog",
        "source_backed_catalog",
        "standards_and_sources",
    ):
        asset_name = registry.get(asset_key)
        if not isinstance(asset_name, str) or not (reference_dir / asset_name).is_file():
            errors.append(f"adapter registry asset '{asset_key}' is missing")
    seen: set[str] = set()
    for index, adapter in enumerate(adapters):
        if not isinstance(adapter, dict):
            errors.append(f"adapter registry adapters[{index}] must be an object")
            continue
        adapter_id = adapter.get("adapter_id")
        if not isinstance(adapter_id, str) or not adapter_id:
            errors.append(f"adapter registry adapters[{index}] has no adapter_id")
            continue
        if adapter_id in seen:
            errors.append(f"adapter registry contains duplicate '{adapter_id}'")
        seen.add(adapter_id)
        if adapter.get("status") not in VALID_ADAPTER_STATUSES:
            errors.append(f"adapter registry '{adapter_id}' has invalid status")
        if adapter.get("verification_status") not in VALID_VERIFICATION_STATUSES:
            errors.append(f"adapter registry '{adapter_id}' has invalid verification_status")
        if not isinstance(adapter.get("ruleset_version"), str):
            errors.append(f"adapter registry '{adapter_id}' has no ruleset_version")
        reference = adapter.get("reference")
        if not isinstance(reference, str) or not (reference_dir / reference).is_file():
            errors.append(f"adapter registry '{adapter_id}' has a missing reference")
        payload_schema = adapter.get("payload_schema")
        if payload_schema is not None and (
            not isinstance(payload_schema, str)
            or not (reference_dir / payload_schema).is_file()
        ):
            errors.append(f"adapter registry '{adapter_id}' has a missing payload schema")
    return registry, errors


def load_field_contracts(
    reference_dir: Path, registry: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    catalog_name = registry.get("field_contract_catalog")
    if not isinstance(catalog_name, str) or not catalog_name:
        return {}, ["adapter registry has no field_contract_catalog"]
    try:
        catalog = load_json(reference_dir / catalog_name)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot load adapter field contracts: {exc}"]
    adapters = catalog.get("adapters") if isinstance(catalog, dict) else None
    if not isinstance(adapters, dict):
        return {}, ["adapter field contracts 'adapters' must be an object"]
    errors: list[str] = []
    schema_name = registry.get("field_contract_schema")
    if isinstance(schema_name, str) and schema_name:
        try:
            contract_schema = load_json(reference_dir / schema_name)
            contract_schema_errors, _ = schema_errors(catalog, contract_schema)
            errors.extend(f"adapter field contracts {error}" for error in contract_schema_errors)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load adapter field-contract schema: {exc}")
    for adapter_id, contract in adapters.items():
        records = contract.get("record_types") if isinstance(contract, dict) else None
        if not isinstance(records, dict) or not records:
            errors.append(f"field contract '{adapter_id}' has no record types")
            continue
        for record_type, record_contract in records.items():
            fields = (
                record_contract.get("allowed_fields")
                if isinstance(record_contract, dict)
                else None
            )
            if not isinstance(fields, list) or not fields or not all(
                isinstance(field, str) and field for field in fields
            ):
                errors.append(
                    f"field contract '{adapter_id}/{record_type}' has invalid allowed_fields"
                )
                continue
            field_definitions = record_contract.get("fields")
            if not isinstance(field_definitions, dict) or set(field_definitions) != set(fields):
                errors.append(
                    f"field contract '{adapter_id}/{record_type}' field definitions do not match allowed_fields"
                )
    return catalog, errors


def load_routing_lexicon(
    reference_dir: Path, registry: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    catalog_name = registry.get("routing_lexicon")
    if not isinstance(catalog_name, str) or not catalog_name:
        return {}, ["adapter registry has no routing_lexicon"]
    try:
        lexicon = load_json(reference_dir / catalog_name)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot load adapter routing lexicon: {exc}"]
    errors: list[str] = []
    schema_name = registry.get("routing_lexicon_schema")
    if isinstance(schema_name, str) and schema_name:
        try:
            lexicon_schema = load_json(reference_dir / schema_name)
            lexicon_schema_errors, _ = schema_errors(lexicon, lexicon_schema)
            errors.extend(f"adapter routing lexicon {error}" for error in lexicon_schema_errors)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load adapter routing-lexicon schema: {exc}")
    if not isinstance(lexicon.get("adapters"), dict):
        errors.append("adapter routing lexicon 'adapters' must be an object")
    return lexicon, errors


def load_benchmark_catalog(
    reference_dir: Path, registry: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    catalog_name = registry.get("benchmark_catalog")
    if not isinstance(catalog_name, str) or not catalog_name:
        return {}, ["adapter registry has no benchmark_catalog"]
    try:
        catalog = load_json(reference_dir / catalog_name)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot load adapter benchmark catalog: {exc}"]
    cases = catalog.get("cases") if isinstance(catalog, dict) else None
    if not isinstance(cases, list):
        return {}, ["adapter benchmark catalog 'cases' must be an array"]
    return catalog, []


def load_source_backed_catalog(
    reference_dir: Path, registry: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    catalog_name = registry.get("source_backed_catalog")
    if not isinstance(catalog_name, str) or not catalog_name:
        return {}, ["adapter registry has no source_backed_catalog"]
    try:
        catalog = load_json(reference_dir / catalog_name)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot load source-backed routing catalog: {exc}"]
    if not isinstance(catalog.get("cases"), list):
        return catalog, ["source-backed routing catalog 'cases' must be an array"]
    if catalog.get("gold_status") != "not-gold":
        return catalog, ["source-backed routing catalog must not claim gold status"]
    return catalog, []


def validate_adapter_assets(
    registry: dict[str, Any],
    field_contracts: dict[str, Any],
    routing_lexicon: dict[str, Any],
    benchmark_catalog: dict[str, Any],
    source_backed_catalog: dict[str, Any],
    adapter_schemas: dict[str, Any],
    reference_dir: Path,
) -> list[str]:
    errors: list[str] = []
    adapters = registry_index(registry)
    contracts = field_contracts.get("adapters", {})
    routing_adapters = routing_lexicon.get("adapters", {})
    cases = benchmark_catalog.get("cases", [])
    source_cases = source_backed_catalog.get("cases", [])
    seen_case_ids: set[str] = set()
    counts = {
        adapter_id: {"positive": 0, "negative": 0, "ambiguous": 0}
        for adapter_id in adapters
    }
    expected_by_kind = {
        "positive": "load",
        "negative": "skip",
        "ambiguous": "candidate",
    }

    schema_record_types: dict[str, set[str]] = {}
    for adapter_id, schema in adapter_schemas.items():
        record_schema = schema.get("properties", {}).get("record_type", {})
        schema_record_types[adapter_id] = set(record_schema.get("enum", []))

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"benchmark cases[{index}] must be an object")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"benchmark cases[{index}] has no case_id")
        elif case_id in seen_case_ids:
            errors.append(f"benchmark catalog contains duplicate case_id '{case_id}'")
        else:
            seen_case_ids.add(case_id)
        adapter_id = case.get("adapter_id")
        if adapter_id not in adapters:
            errors.append(f"benchmark case '{case_id}' has unknown adapter_id '{adapter_id}'")
            continue
        case_kind = case.get("case_kind")
        if case_kind not in expected_by_kind:
            errors.append(f"benchmark case '{case_id}' has invalid case_kind")
            continue
        counts[adapter_id][case_kind] += 1
        if case.get("expected_status") != expected_by_kind[case_kind]:
            errors.append(f"benchmark case '{case_id}' has inconsistent expected_status")
        if case.get("review_status") not in {"provisional", "source-backed", "adjudicated"}:
            errors.append(f"benchmark case '{case_id}' has invalid review_status")
        expected_signal_ids = case.get("expected_signal_ids")
        if not isinstance(expected_signal_ids, list) or not expected_signal_ids:
            errors.append(f"benchmark case '{case_id}' has no expected_signal_ids")
        else:
            known_signal_ids = {
                signal.get("signal_id")
                for signal in routing_adapters.get(adapter_id, {}).get("signals", [])
                if isinstance(signal, dict)
            }
            unknown_signal_ids = sorted(set(expected_signal_ids) - known_signal_ids)
            if unknown_signal_ids:
                errors.append(
                    f"benchmark case '{case_id}' has unknown expected signal(s) {unknown_signal_ids}"
                )
        record_types = case.get("expected_record_types")
        if not isinstance(record_types, list):
            errors.append(f"benchmark case '{case_id}' expected_record_types must be an array")
            continue
        if case_kind != "positive" and record_types:
            errors.append(f"benchmark case '{case_id}' must not emit domain records")
        known_record_types = schema_record_types.get(adapter_id, set())
        contract = contracts.get(adapter_id, {}) if isinstance(contracts, dict) else {}
        contract_records = contract.get("record_types", {}) if isinstance(contract, dict) else {}
        known_record_types.update(contract_records)
        unknown = sorted(set(record_types) - known_record_types)
        if unknown:
            errors.append(
                f"benchmark case '{case_id}' has unknown expected record type(s) {unknown}"
            )

    for adapter_id, adapter in adapters.items():
        for case_kind, count in counts[adapter_id].items():
            if count < 2:
                errors.append(
                    f"adapter '{adapter_id}' has only {count} {case_kind} benchmark case(s)"
                )
        contract = contracts.get(adapter_id) if isinstance(contracts, dict) else None
        if isinstance(contract, dict) and (
            contract.get("ruleset_version") != adapter.get("ruleset_version")
        ):
            errors.append(
                f"adapter '{adapter_id}' field-contract version does not match registry"
            )
        if adapter.get("status") == "implemented" and (
            adapter_id not in adapter_schemas
            and (not isinstance(contracts, dict) or adapter_id not in contracts)
        ):
            errors.append(
                f"implemented adapter '{adapter_id}' has no payload schema or field contract"
            )
        routing_spec = routing_adapters.get(adapter_id) if isinstance(routing_adapters, dict) else None
        if not isinstance(routing_spec, dict):
            errors.append(f"adapter '{adapter_id}' has no routing lexicon entry")
            continue
        if routing_spec.get("ruleset_version") != adapter.get("ruleset_version"):
            errors.append(f"adapter '{adapter_id}' routing version does not match registry")
        signals = routing_spec.get("signals")
        if not isinstance(signals, list) or not signals:
            errors.append(f"adapter '{adapter_id}' has no routing signals")
            continue
        signal_ids = [signal.get("signal_id") for signal in signals if isinstance(signal, dict)]
        if len(signal_ids) != len(set(signal_ids)):
            errors.append(f"adapter '{adapter_id}' has duplicate routing signal IDs")
        strengths = {
            signal.get("strength") for signal in signals if isinstance(signal, dict)
        }
        missing_strengths = VALID_SIGNAL_STRENGTHS - strengths
        if missing_strengths:
            errors.append(
                f"adapter '{adapter_id}' lacks signal strength(s) {sorted(missing_strengths)}"
            )
        reference_name = adapter.get("reference")
        if isinstance(reference_name, str):
            reference_path = reference_dir / reference_name
            if reference_path.is_file():
                reference_text = reference_path.read_text(encoding="utf-8")
                begin = f"<!-- BEGIN GENERATED ROUTING CONTRACT: {adapter_id} -->"
                end = f"<!-- END GENERATED ROUTING CONTRACT: {adapter_id} -->"
                if reference_text.count(begin) != 1 or reference_text.count(end) != 1:
                    errors.append(f"adapter '{adapter_id}' reference routing block is missing or duplicated")

    registry_ids = set(adapters)
    routing_ids = set(routing_adapters) if isinstance(routing_adapters, dict) else set()
    if registry_ids != routing_ids:
        errors.append(
            f"registry/routing adapter sets differ: registry_only={sorted(registry_ids-routing_ids)}, "
            f"routing_only={sorted(routing_ids-registry_ids)}"
        )

    source_covered: set[str] = set()
    seen_source_case_ids: set[str] = set()
    for case_index, case in enumerate(source_cases):
        if not isinstance(case, dict):
            errors.append(f"source-backed cases[{case_index}] must be an object")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"source-backed cases[{case_index}] has no case_id")
        elif case_id in seen_source_case_ids:
            errors.append(f"source-backed catalog contains duplicate case_id '{case_id}'")
        else:
            seen_source_case_ids.add(case_id)
        source = case.get("source")
        if not isinstance(source, dict) or not isinstance(source.get("url"), str):
            errors.append(f"source-backed case '{case_id}' has no source URL")
        if case.get("review_status") != "source-backed":
            errors.append(f"source-backed case '{case_id}' has invalid review_status")
        decisions = case.get("decisions")
        if not isinstance(decisions, list) or not decisions:
            errors.append(f"source-backed case '{case_id}' has no decisions")
            continue
        for decision in decisions:
            if not isinstance(decision, dict):
                errors.append(f"source-backed case '{case_id}' has a non-object decision")
                continue
            adapter_id = decision.get("adapter_id")
            if adapter_id not in adapters:
                errors.append(f"source-backed case '{case_id}' has unknown adapter '{adapter_id}'")
                continue
            source_covered.add(adapter_id)
            spec = routing_adapters.get(adapter_id, {})
            if decision.get("ruleset_version") != spec.get("ruleset_version"):
                errors.append(f"source-backed case '{case_id}/{adapter_id}' has stale ruleset version")
            signal_defs = {
                item.get("signal_id"): item
                for item in spec.get("signals", [])
                if isinstance(item, dict)
            }
            expected_signal_ids = decision.get("expected_signal_ids")
            if not isinstance(expected_signal_ids, list) or not expected_signal_ids:
                errors.append(f"source-backed case '{case_id}/{adapter_id}' has no signal IDs")
                continue
            unknown = set(expected_signal_ids) - set(signal_defs)
            if unknown:
                errors.append(
                    f"source-backed case '{case_id}/{adapter_id}' has unknown signals {sorted(unknown)}"
                )
            status = decision.get("expected_status")
            strengths = {
                signal_defs[signal_id].get("strength")
                for signal_id in expected_signal_ids
                if signal_id in signal_defs
            }
            if status == "load" and "strong" not in strengths:
                errors.append(f"source-backed load '{case_id}/{adapter_id}' lacks a strong signal")
            if status == "skip" and strengths != {"exclusion"}:
                errors.append(f"source-backed skip '{case_id}/{adapter_id}' is not exclusion-only")
            if status not in {"load", "candidate", "skip"}:
                errors.append(f"source-backed case '{case_id}/{adapter_id}' has invalid status")
    if source_covered != registry_ids:
        errors.append(
            f"source-backed coverage differs from registry: missing={sorted(registry_ids-source_covered)}, "
            f"extra={sorted(source_covered-registry_ids)}"
        )
    return errors


def registry_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        adapter["adapter_id"]: adapter
        for adapter in registry.get("adapters", [])
        if isinstance(adapter, dict) and isinstance(adapter.get("adapter_id"), str)
    }


def adapter_schema_errors(
    document: dict[str, Any], adapter_schemas: dict[str, Any]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not adapter_schemas:
        return errors, warnings
    try:
        import jsonschema
    except ImportError:
        warnings.append(
            "Adapter payload schemas were not applied because 'jsonschema' is unavailable."
        )
        return errors, warnings

    validators: dict[str, Any] = {}
    for adapter_id, schema in adapter_schemas.items():
        try:
            validator_cls = jsonschema.validators.validator_for(schema)
            validator_cls.check_schema(schema)
            validators[adapter_id] = validator_cls(schema)
        except Exception as exc:  # pragma: no cover - protects CLI diagnostics
            errors.append(f"adapter schema '{adapter_id}' is invalid: {exc}")

    for index, record in enumerate(document.get("domain_records", [])):
        if not isinstance(record, dict):
            continue
        adapter_id = record.get("adapter_id")
        validator = validators.get(adapter_id)
        if validator is None:
            continue
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.absolute_path)
            suffix = f".{location}" if location else ""
            errors.append(
                f"adapter[{adapter_id}] domain_records[{index}]{suffix}: {error.message}"
            )
    return errors, warnings


def adapter_field_contract_errors(
    document: dict[str, Any], field_contracts: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    contracts = field_contracts.get("adapters", {})
    if not isinstance(contracts, dict):
        return errors
    for index, record in enumerate(document.get("domain_records", [])):
        if not isinstance(record, dict):
            continue
        adapter_id = record.get("adapter_id")
        contract = contracts.get(adapter_id)
        if not isinstance(contract, dict):
            continue
        record_types = contract.get("record_types", {})
        record_type = record.get("record_type")
        record_contract = record_types.get(record_type) if isinstance(record_types, dict) else None
        if not isinstance(record_contract, dict):
            errors.append(
                f"domain_records[{index}]: unknown record_type '{record_type}' "
                f"for adapter '{adapter_id}'"
            )
            continue
        allowed_fields = set(record_contract.get("allowed_fields", []))
        fields = record.get("fields")
        if not isinstance(fields, dict):
            continue
        unknown_fields = sorted(set(fields) - allowed_fields)
        if unknown_fields:
            errors.append(
                f"domain_records[{index}]: field(s) {unknown_fields} are not declared "
                f"for '{adapter_id}/{record_type}'"
            )
        for group in record_contract.get("required_any_of", []):
            if isinstance(group, list) and group and not (set(group) & set(fields)):
                errors.append(
                    f"domain_records[{index}]: at least one declared field is required "
                    f"for '{adapter_id}/{record_type}'"
                )
        field_evidence = record.get("field_evidence")
        if not isinstance(field_evidence, dict):
            errors.append(f"domain_records[{index}]: field_evidence must be an object")
            continue
        if set(field_evidence) != set(fields):
            errors.append(
                f"domain_records[{index}]: field_evidence keys must exactly match populated fields"
            )
        record_evidence = set(record.get("evidence_ids", []))
        for field_name, evidence_ids in field_evidence.items():
            if not isinstance(evidence_ids, list) or not evidence_ids:
                errors.append(
                    f"domain_records[{index}].field_evidence.{field_name}: requires at least one evidence ID"
                )
                continue
            uncovered = set(evidence_ids) - record_evidence
            if uncovered:
                errors.append(
                    f"domain_records[{index}].field_evidence.{field_name}: evidence {sorted(uncovered)} "
                    "is not included in the domain record evidence_ids"
                )
    return errors



def validate_condition_registry(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    alias_to_signature: dict[str, str] = {}
    for index, record in enumerate(document.get("condition_registry", [])):
        if not isinstance(record, dict):
            continue
        alias = record.get("alias")
        signature = record.get("condition_signature")
        if not isinstance(alias, str) or not isinstance(signature, dict):
            continue
        canonical = json.dumps(signature, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        previous = alias_to_signature.get(alias)
        if previous is not None and previous != canonical:
            errors.append(
                f"condition_registry[{index}].alias: '{alias}' maps to multiple condition signatures"
            )
        alias_to_signature[alias] = canonical
    return errors


def validate_comparison_presentation(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    comparisons = {
        item.get("id"): item
        for item in document.get("comparability_assessments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for index, episode in enumerate(document.get("deviation_episodes", [])):
        if not isinstance(episode, dict):
            continue
        classification = episode.get("classification")
        assessment = comparisons.get(episode.get("comparability_assessment_id"), {})
        result = assessment.get("result") if isinstance(assessment, dict) else None
        if result == "not-comparable" and classification != "not-comparable":
            errors.append(
                f"deviation_episodes[{index}]: a not-comparable assessment cannot be presented as '{classification}'"
            )
        if classification == "not-comparable" and episode.get("residual") is not None:
            errors.append(
                f"deviation_episodes[{index}].residual: residual must be omitted for not-comparable data"
            )
    return errors


def validate_error_budget_logic(document: dict[str, Any]) -> list[str]:
    """Check that error attribution uses a common basis and cannot silently overrule uncertainty."""
    errors: list[str] = []
    deviations = {
        item.get("id"): item
        for item in document.get("deviation_episodes", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for index, budget in enumerate(document.get("error_budgets", [])):
        if not isinstance(budget, dict):
            continue
        components = [item for item in budget.get("components", []) if isinstance(item, dict)]
        component_ids = [item.get("id") for item in components if isinstance(item.get("id"), str)]
        if len(component_ids) != len(set(component_ids)):
            errors.append(f"error_budgets[{index}].components: duplicate component IDs")
        unknown_dominant = set(budget.get("dominant_component_ids", [])) - set(component_ids)
        if unknown_dominant:
            errors.append(
                f"error_budgets[{index}].dominant_component_ids: unknown local component IDs {sorted(unknown_dominant)}"
            )
        fractions = [item.get("fraction_of_total") for item in components]
        provided = [value for value in fractions if isinstance(value, (int, float))]
        if budget.get("quantitative_fraction_complete"):
            if len(provided) != len(components):
                errors.append(
                    f"error_budgets[{index}]: quantitative_fraction_complete requires a fraction for every component"
                )
            bases = {item.get("contribution_basis") for item in components}
            if len(bases) != 1 or bases & {"qualitative", None}:
                errors.append(
                    f"error_budgets[{index}]: complete fractions require one common quantitative contribution basis"
                )
            if provided and not 0.98 <= sum(provided) <= 1.02:
                errors.append(
                    f"error_budgets[{index}]: complete component fractions must sum to approximately 1.0, got {sum(provided):.4f}"
                )
        elif provided and len({item.get("contribution_basis") for item in components if item.get("fraction_of_total") is not None}) > 1:
            errors.append(
                f"error_budgets[{index}]: fraction_of_total values cannot mix contribution bases"
            )
        comparison = budget.get("effect_comparison") or {}
        relation = comparison.get("relation") if isinstance(comparison, dict) else None
        deviation = deviations.get(budget.get("deviation_episode_id"), {})
        classification = deviation.get("classification") if isinstance(deviation, dict) else None
        if relation in {"comparable", "uncertainty-dominates"} and classification in {
            "material-process-deviation", "promising-outlier"
        } and not comparison.get("override_justification"):
            errors.append(
                f"error_budgets[{index}].effect_comparison: '{relation}' cannot support '{classification}' without an explicit override_justification"
            )
        if budget.get("method") == "insufficient-data" and budget.get("combined_uncertainty") is not None:
            errors.append(
                f"error_budgets[{index}]: insufficient-data method cannot claim a combined quantitative uncertainty"
            )
    return errors


def validate_anomaly_chain_logic(document: dict[str, Any]) -> list[str]:
    """Validate local graph integrity and prevent unsupported anomaly-chain upgrades."""
    errors: list[str] = []
    deviations = {
        item.get("id"): item
        for item in document.get("deviation_episodes", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for index, chain in enumerate(document.get("anomaly_propagation_chains", [])):
        if not isinstance(chain, dict):
            continue
        nodes = [item for item in chain.get("nodes", []) if isinstance(item, dict)]
        node_ids = [item.get("node_id") for item in nodes if isinstance(item.get("node_id"), str)]
        if len(node_ids) != len(set(node_ids)):
            errors.append(f"anomaly_propagation_chains[{index}].nodes: duplicate node IDs")
        node_set = set(node_ids)
        edge_ids: set[str] = set()
        direct_edges = 0
        for edge_index, edge in enumerate(chain.get("edges", [])):
            if not isinstance(edge, dict):
                continue
            edge_id = edge.get("edge_id")
            if edge_id in edge_ids:
                errors.append(
                    f"anomaly_propagation_chains[{index}].edges[{edge_index}]: duplicate edge ID '{edge_id}'"
                )
            if isinstance(edge_id, str):
                edge_ids.add(edge_id)
            source, target = edge.get("from_node_id"), edge.get("to_node_id")
            if source not in node_set or target not in node_set:
                errors.append(
                    f"anomaly_propagation_chains[{index}].edges[{edge_index}]: endpoints must name local nodes"
                )
            if source == target:
                errors.append(
                    f"anomaly_propagation_chains[{index}].edges[{edge_index}]: self-loop is not a propagation step"
                )
            strength = edge.get("evidence_strength")
            if strength in {"direct", "indirect"} and not edge.get("evidence_ids"):
                errors.append(
                    f"anomaly_propagation_chains[{index}].edges[{edge_index}]: {strength} evidence strength requires evidence IDs"
                )
            if strength == "direct":
                direct_edges += 1
        unresolved = set(chain.get("unresolved_node_ids", []))
        if unresolved - node_set:
            errors.append(
                f"anomaly_propagation_chains[{index}].unresolved_node_ids: unknown local node IDs {sorted(unresolved - node_set)}"
            )
        deviation = deviations.get(chain.get("deviation_episode_id"), {})
        classification = deviation.get("classification") if isinstance(deviation, dict) else None
        if classification in {"aligned", "expected-variation", "not-comparable"}:
            errors.append(
                f"anomaly_propagation_chains[{index}]: classification '{classification}' does not justify a material anomaly chain"
            )
        if chain.get("status") in {"supported", "locally-validated"} and direct_edges == 0:
            errors.append(
                f"anomaly_propagation_chains[{index}]: supported chains require at least one directly evidenced edge"
            )
        if chain.get("status") == "locally-validated" and unresolved:
            errors.append(
                f"anomaly_propagation_chains[{index}]: locally-validated chains cannot retain unresolved nodes"
            )
    return errors



def validate_mechanism_graph_logic(document: dict[str, Any]) -> list[str]:
    """Validate the reusable evidence-grounded mechanism layer.

    Run-scoped anomaly chains and PSPP maps may point into this layer, but they do
    not silently create reusable mechanism facts. Every graph edge must preserve
    evidence, conditions, falsifiers, boundaries, versioning, and transfer limits.
    """
    errors: list[str] = []
    graphs = {
        item.get("id"): item
        for item in document.get("mechanism_graphs", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    nodes = {
        item.get("id"): item
        for item in document.get("mechanism_nodes", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    edges = {
        item.get("id"): item
        for item in document.get("mechanism_edges", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    updates = {
        item.get("id"): item
        for item in document.get("mechanism_updates", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    for graph_id, graph in graphs.items():
        graph_nodes = set(graph.get("node_ids", []))
        graph_edges = set(graph.get("edge_ids", []))
        unknown_nodes = graph_nodes - set(nodes)
        unknown_edges = graph_edges - set(edges)
        if unknown_nodes:
            errors.append(f"mechanism_graphs[{graph_id}].node_ids: unknown nodes {sorted(unknown_nodes)}")
        if unknown_edges:
            errors.append(f"mechanism_graphs[{graph_id}].edge_ids: unknown edges {sorted(unknown_edges)}")
        for node_id in graph_nodes & set(nodes):
            if graph_id not in nodes[node_id].get("graph_ids", []):
                errors.append(
                    f"mechanism_graphs[{graph_id}].node_ids: node '{node_id}' does not link back to the graph"
                )
        for edge_id in graph_edges & set(edges):
            edge = edges[edge_id]
            if edge.get("graph_id") != graph_id:
                errors.append(
                    f"mechanism_graphs[{graph_id}].edge_ids: edge '{edge_id}' belongs to '{edge.get('graph_id')}'"
                )
            if edge.get("from_node_id") not in graph_nodes or edge.get("to_node_id") not in graph_nodes:
                errors.append(
                    f"mechanism_edges[{edge_id}]: endpoints must both be listed in graph '{graph_id}'"
                )
        unknown_updates = set(graph.get("update_ids", [])) - set(updates)
        if unknown_updates:
            errors.append(
                f"mechanism_graphs[{graph_id}].update_ids: unknown updates {sorted(unknown_updates)}"
            )
        if graph.get("status") == "locally-validated":
            statuses = {edges[e].get("validation_status") for e in graph_edges if e in edges}
            if "locally-validated" not in statuses:
                errors.append(
                    f"mechanism_graphs[{graph_id}]: locally-validated graph requires at least one locally-validated edge"
                )

    for node_id, node in nodes.items():
        for graph_id in node.get("graph_ids", []):
            graph = graphs.get(graph_id)
            if graph is not None and node_id not in graph.get("node_ids", []):
                errors.append(
                    f"mechanism_nodes[{node_id}].graph_ids: graph '{graph_id}' does not list the node"
                )
        if node.get("status") in {"supported", "locally-validated"} and not node.get("evidence_ids"):
            errors.append(
                f"mechanism_nodes[{node_id}]: status '{node.get('status')}' requires evidence"
            )

    for edge_id, edge in edges.items():
        graph_id = edge.get("graph_id")
        if graph_id not in graphs:
            continue
        source = edge.get("from_node_id")
        target = edge.get("to_node_id")
        if source == target:
            errors.append(f"mechanism_edges[{edge_id}]: self-loop requires an explicit intermediate node")
        if source not in nodes or target not in nodes:
            errors.append(f"mechanism_edges[{edge_id}]: endpoints must name mechanism_nodes")
        status = edge.get("validation_status")
        source_kind = edge.get("source_kind")
        if source_kind == "domain-inference" and status != "hypothesis":
            errors.append(
                f"mechanism_edges[{edge_id}]: domain-inference edges must remain hypotheses"
            )
        if status == "locally-validated" and not edge.get("validation_evidence_ids"):
            errors.append(
                f"mechanism_edges[{edge_id}]: locally-validated status requires validation_evidence_ids"
            )
        if status in {"contradicted", "deprecated", "conflicting"} and not (
            edge.get("conflict_evidence_ids") or edge.get("supersedes_edge_id")
        ):
            errors.append(
                f"mechanism_edges[{edge_id}]: status '{status}' requires conflict evidence or an explicit supersession"
            )
        transfer = edge.get("transferability") or {}
        level = transfer.get("level") if isinstance(transfer, dict) else None
        if level == "cross-material-proposed" and status in {"supported", "locally-validated"}:
            errors.append(
                f"mechanism_edges[{edge_id}]: cross-material transfer proposals cannot be marked '{status}'"
            )
        if level == "cross-material-proposed" and not transfer.get("required_matches"):
            errors.append(
                f"mechanism_edges[{edge_id}].transferability: cross-material proposal requires explicit matching conditions"
            )

    edge_ops = {"support-edge", "add-conflict", "revise-boundary", "supersede-edge", "deprecate-edge"}
    for update_id, update in updates.items():
        operation = update.get("operation")
        graph_id = update.get("target_graph_id")
        if graph_id in graphs and update_id not in graphs[graph_id].get("update_ids", []):
            errors.append(
                f"mechanism_updates[{update_id}]: target graph '{graph_id}' does not list the update"
            )
        if operation in edge_ops and not update.get("target_edge_id"):
            errors.append(f"mechanism_updates[{update_id}]: operation '{operation}' requires target_edge_id")
        if operation == "append-node" and not update.get("new_node_ids"):
            errors.append(f"mechanism_updates[{update_id}]: append-node requires new_node_ids")
        if operation == "append-edge" and not update.get("new_edge_ids"):
            errors.append(f"mechanism_updates[{update_id}]: append-edge requires new_edge_ids")
        if operation == "support-edge" and not update.get("proposed_support_evidence_ids"):
            errors.append(
                f"mechanism_updates[{update_id}]: support-edge requires proposed_support_evidence_ids"
            )
        if operation == "add-conflict" and not update.get("proposed_conflict_evidence_ids"):
            errors.append(
                f"mechanism_updates[{update_id}]: add-conflict requires proposed_conflict_evidence_ids"
            )
        if operation == "revise-boundary" and not update.get("proposed_boundary_conditions"):
            errors.append(
                f"mechanism_updates[{update_id}]: revise-boundary requires proposed_boundary_conditions"
            )
        if update.get("status") == "applied" and update.get("persistence_status") not in {
            "artifact-written", "external-written-confirmed"
        }:
            errors.append(
                f"mechanism_updates[{update_id}]: applied update requires a confirmed artifact or external write"
            )
        if update.get("status") in {"proposed", "reviewed", "approved"} and update.get("persistence_status") in {
            "artifact-written", "external-written-confirmed"
        }:
            errors.append(
                f"mechanism_updates[{update_id}]: unapplied update cannot claim confirmed persistence"
            )

    for index, hypothesis in enumerate(document.get("hypotheses", [])):
        if not isinstance(hypothesis, dict):
            continue
        linked = hypothesis.get("linked_mechanism_edge_ids", [])
        match = hypothesis.get("mechanism_match_status")
        if match in {"exact-condition-match", "partial-condition-match", "analogy-only", "conflicting"} and not linked:
            errors.append(
                f"hypotheses[{index}]: mechanism_match_status '{match}' requires linked_mechanism_edge_ids"
            )
        if match == "no-match" and linked:
            errors.append(
                f"hypotheses[{index}]: no-match cannot retain linked mechanism edges"
            )
        if match == "analogy-only":
            transfer = hypothesis.get("mechanism_transferability") or {}
            if transfer.get("level") not in {"same-material-family", "cross-material-proposed"}:
                errors.append(
                    f"hypotheses[{index}]: analogy-only match requires an explicit transferability assessment"
                )

    return errors

def validate_information_gap_logic(document: dict[str, Any]) -> list[str]:
    """Ensure proposed experiments resolve declared unknowns and high-value gaps are not orphaned."""
    errors: list[str] = []
    gaps = {
        item.get("id"): item
        for item in document.get("information_gaps", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    linked_by_plan: set[str] = set()
    plans = {
        item.get("id"): item
        for item in document.get("verification_plan", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for index, item in enumerate(document.get("verification_plan", [])):
        if not isinstance(item, dict):
            continue
        gap_ids = set(item.get("information_gap_ids", []))
        linked_by_plan.update(gap_ids)
        if item.get("status") in {"proposed", "approved"} and not gap_ids:
            errors.append(f"verification_plan[{index}]: proposed work must resolve at least one information gap")
        gain = item.get("information_gain") or {}
        discriminated = set(gain.get("hypotheses_discriminated", [])) if isinstance(gain, dict) else set()
        hypothesis_ids = set(item.get("hypothesis_ids", []))
        if discriminated - hypothesis_ids:
            errors.append(
                f"verification_plan[{index}].information_gain: discriminated hypotheses must be included in hypothesis_ids"
            )
    for gap_id, gap in gaps.items():
        if gap.get("current_state") == "resolved" and not gap.get("resolution_evidence_ids"):
            errors.append(f"information_gaps[{gap_id}]: resolved gaps require resolution_evidence_ids")
        if gap.get("impact") in {"blocker", "high"} and gap.get("disposition") == "plan-measurement" and gap_id not in linked_by_plan:
            errors.append(
                f"information_gaps[{gap_id}]: high-impact planned measurement is not linked to a verification item"
            )
    for set_index, exp_set in enumerate(document.get("experiment_sets", [])):
        if not isinstance(exp_set, dict):
            continue
        set_plan_ids = set(exp_set.get("verification_item_ids", []))
        set_gap_ids = set(exp_set.get("information_gap_ids", []))
        matrix_gap_ids: set[str] = set()
        for row_index, row in enumerate(exp_set.get("coverage_matrix", [])):
            if not isinstance(row, dict):
                continue
            if row.get("verification_item_id") not in set_plan_ids:
                errors.append(
                    f"experiment_sets[{set_index}].coverage_matrix[{row_index}]: verification item is not declared in the set"
                )
            row_gaps = set(row.get("information_gap_ids", []))
            matrix_gap_ids.update(row_gaps)
            if row_gaps - set_gap_ids:
                errors.append(
                    f"experiment_sets[{set_index}].coverage_matrix[{row_index}]: coverage contains undeclared information gaps"
                )
        if set_gap_ids - matrix_gap_ids:
            errors.append(
                f"experiment_sets[{set_index}]: information gaps {sorted(set_gap_ids - matrix_gap_ids)} are not covered by the matrix"
            )
        for plan_id in set_plan_ids:
            plan = plans.get(plan_id)
            if isinstance(plan, dict) and plan.get("experiment_set_id") not in {None, exp_set.get("id")}:
                errors.append(
                    f"experiment_sets[{set_index}]: verification item '{plan_id}' points to another experiment set"
                )
    return errors


def validate_pspp_logic(document: dict[str, Any]) -> list[str]:
    """Validate PSPP graph coverage and evidence binding for reusable experience updates."""
    errors: list[str] = []
    maps = {
        item.get("id"): item
        for item in document.get("pspp_maps", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    canonical = {"processing", "structure", "properties", "performance"}
    for index, item in enumerate(document.get("pspp_maps", [])):
        if not isinstance(item, dict):
            continue
        nodes = [node for node in item.get("nodes", []) if isinstance(node, dict)]
        node_ids = [node.get("node_id") for node in nodes if isinstance(node.get("node_id"), str)]
        if len(node_ids) != len(set(node_ids)):
            errors.append(f"pspp_maps[{index}].nodes: duplicate node IDs")
        node_set = set(node_ids)
        present_stages = {node.get("stage") for node in nodes if node.get("status") not in {"unknown", "not-applicable"}}
        coverage = item.get("coverage") or {}
        for stage in canonical:
            declared = coverage.get(stage) if isinstance(coverage, dict) else None
            actual = stage in present_stages
            if declared == "present" and not actual:
                errors.append(f"pspp_maps[{index}].coverage.{stage}: declared present but no supported node exists")
            if declared == "missing" and actual:
                errors.append(f"pspp_maps[{index}].coverage.{stage}: declared missing but a supported node exists")
        if item.get("status") != "insufficient-evidence" and len(present_stages & canonical) < 3:
            errors.append(
                f"pspp_maps[{index}]: reusable PSPP maps require at least three of processing/structure/properties/performance"
            )
        validated_relations = 0
        for rel_index, rel in enumerate(item.get("relationships", [])):
            if not isinstance(rel, dict):
                continue
            if rel.get("from_node_id") not in node_set or rel.get("to_node_id") not in node_set:
                errors.append(f"pspp_maps[{index}].relationships[{rel_index}]: endpoints must name local PSPP nodes")
            if rel.get("from_node_id") == rel.get("to_node_id"):
                errors.append(f"pspp_maps[{index}].relationships[{rel_index}]: self-relation is invalid")
            if rel.get("relation_status") in {"observation", "derived", "locally-validated"} and not rel.get("evidence_ids"):
                errors.append(
                    f"pspp_maps[{index}].relationships[{rel_index}]: asserted relation status requires evidence IDs"
                )
            if rel.get("relation_status") == "locally-validated":
                validated_relations += 1
        if item.get("status") == "locally-validated" and validated_relations == 0:
            errors.append(f"pspp_maps[{index}]: locally-validated map requires a locally-validated relationship")
    for index, update in enumerate(document.get("experience_updates", [])):
        if not isinstance(update, dict):
            continue
        map_ids = set(update.get("pspp_map_ids", []))
        if update.get("action") in {"add", "revise", "supersede"} and not map_ids and not update.get("pspp_exception_reason"):
            errors.append(
                f"experience_updates[{index}]: reusable updates require pspp_map_ids or a documented pspp_exception_reason"
            )
        if map_ids - set(maps):
            errors.append(f"experience_updates[{index}]: unknown PSPP map IDs {sorted(map_ids - set(maps))}")
    return errors


def require_core_shape(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["$: output must be a JSON object"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in document:
            errors.append(f"$: missing required top-level key '{key}'")

    if document.get("schema_version") != "4.6":
        errors.append("schema_version: expected '4.6'")

    for key in REQUIRED_TOP_LEVEL:
        if key in {"schema_version", "run_id", "loop_state", "decision_profile", "decision", "input_assessment", "quality"}:
            continue
        if key in document and not isinstance(document[key], list):
            errors.append(f"{key}: expected an array")
    return errors


def validate_relative_artifact_paths(document: dict[str, Any]) -> list[str]:
    """Reject absolute paths in the portable artifact manifest and input list."""
    errors: list[str] = []

    def absolute(value: Any) -> bool:
        text = str(value or "")
        return (
            Path(text).is_absolute()
            or bool(re.match(r"^[A-Za-z]:", text))
            or text.startswith("\\\\")
            or bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", text))
        )

    for index, item in enumerate(document.get("artifact_manifest", [])):
        if isinstance(item, dict) and absolute(item.get("path")):
            errors.append(f"artifact_manifest[{index}].path: must be relative to the artifact root")
    assessment = document.get("input_assessment", {})
    for index, item in enumerate(assessment.get("received_inputs", []) if isinstance(assessment, dict) else []):
        if isinstance(item, dict) and item.get("path") is not None and absolute(item.get("path")):
            errors.append(f"input_assessment.received_inputs[{index}].path: must be relative to the artifact root")
    return errors


def collect_ids(document: dict[str, Any]) -> tuple[dict[str, set[str]], list[str]]:
    errors: list[str] = []
    ids_by_kind = {kind: set() for kind in ID_COLLECTIONS.values()}
    globally_seen: dict[str, str] = {}

    for collection, kind in ID_COLLECTIONS.items():
        records = document.get(collection, [])
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"{collection}[{index}]: expected an object")
                continue
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id:
                errors.append(f"{collection}[{index}].id: missing or invalid")
                continue
            previous = globally_seen.get(record_id)
            if previous is not None:
                errors.append(
                    f"{collection}[{index}].id: duplicate ID '{record_id}' already used by {previous}"
                )
            else:
                globally_seen[record_id] = f"{collection}[{index}]"
            ids_by_kind[kind].add(record_id)

    for run_index, run in enumerate(document.get("process_runs", [])):
        if not isinstance(run, dict):
            continue
        for step_index, step in enumerate(run.get("steps", [])):
            if not isinstance(step, dict):
                continue
            step_id = step.get("step_id")
            if not isinstance(step_id, str) or not step_id:
                errors.append(
                    f"process_runs[{run_index}].steps[{step_index}].step_id: missing or invalid"
                )
                continue
            previous = globally_seen.get(step_id)
            if previous is not None:
                errors.append(
                    f"process_runs[{run_index}].steps[{step_index}].step_id: duplicate ID "
                    f"'{step_id}' already used by {previous}"
                )
            else:
                globally_seen[step_id] = f"process_runs[{run_index}].steps[{step_index}]"
    return ids_by_kind, errors


def iter_reference_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                yield item


def validate_references(
    node: Any,
    ids_by_kind: dict[str, set[str]],
    path: str = "$",
) -> list[str]:
    errors: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}"
            target_kind = REFERENCE_TARGETS.get(key)
            if target_kind is not None:
                for reference in iter_reference_values(value):
                    if reference not in ids_by_kind.get(target_kind, set()):
                        errors.append(
                            f"{child_path}: unknown {target_kind} reference '{reference}'"
                        )
            errors.extend(validate_references(value, ids_by_kind, child_path))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            errors.extend(validate_references(item, ids_by_kind, f"{path}[{index}]"))
    return errors


def validate_adapter_routing_signals(
    document: dict[str, Any], routing_lexicon: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    routing_adapters = routing_lexicon.get("adapters", {})
    if not isinstance(routing_adapters, dict):
        return ["routing lexicon has no adapter definitions"]

    for decision_index, decision in enumerate(document.get("adapter_decisions", [])):
        if not isinstance(decision, dict):
            continue
        adapter_id = decision.get("adapter_id")
        spec = routing_adapters.get(adapter_id)
        if not isinstance(spec, dict):
            errors.append(
                f"adapter_decisions[{decision_index}]: no routing lexicon for '{adapter_id}'"
            )
            continue
        signal_defs = {
            signal.get("signal_id"): signal
            for signal in spec.get("signals", [])
            if isinstance(signal, dict) and isinstance(signal.get("signal_id"), str)
        }
        target_ids = {
            target.get("entity_id")
            for target in decision.get("target_entities", [])
            if isinstance(target, dict) and isinstance(target.get("entity_id"), str)
        }
        valid_positive: list[dict[str, Any]] = []
        for collection_name, expect_exclusion in (
            ("matched_signals", False),
            ("exclusion_matches", True),
        ):
            for signal_index, matched in enumerate(decision.get(collection_name, [])):
                if not isinstance(matched, dict):
                    continue
                location = f"adapter_decisions[{decision_index}].{collection_name}[{signal_index}]"
                signal_id = matched.get("signal_id")
                signal_def = signal_defs.get(signal_id)
                if not isinstance(signal_def, dict):
                    errors.append(f"{location}: unknown signal_id '{signal_id}'")
                    continue
                expected_strength = signal_def.get("strength")
                if matched.get("strength") != expected_strength:
                    errors.append(
                        f"{location}: strength does not match routing lexicon for '{signal_id}'"
                    )
                if matched.get("independence_group") != signal_def.get("independence_group"):
                    errors.append(
                        f"{location}: independence_group does not match routing lexicon"
                    )
                if expect_exclusion != (expected_strength == "exclusion"):
                    errors.append(
                        f"{location}: exclusion signal placement does not match its lexicon strength"
                    )
                entity_ids = set(matched.get("entity_ids", []))
                if signal_def.get("requires_entity_binding") and not entity_ids:
                    errors.append(f"{location}: signal requires target-entity binding")
                if entity_ids - target_ids:
                    errors.append(
                        f"{location}: entity IDs are not declared decision targets: {sorted(entity_ids-target_ids)}"
                    )
                if matched.get("evidence_id") not in decision.get("evidence_ids", []):
                    errors.append(f"{location}: evidence_id is not included in decision evidence_ids")
                if (
                    not expect_exclusion
                    and matched.get("valid_context") is True
                    and matched.get("polarity") == "affirmed"
                    and expected_strength in {"strong", "supporting"}
                ):
                    valid_positive.append(matched)

        if decision.get("status") == "load":
            strong = [signal for signal in valid_positive if signal.get("strength") == "strong"]
            supporting_groups = {
                signal.get("independence_group")
                for signal in valid_positive
                if signal.get("strength") == "supporting"
            }
            if not strong and len(supporting_groups) < 2:
                errors.append(
                    f"adapter_decisions[{decision_index}]: load requires a valid strong signal "
                    "or two independent supporting groups"
                )
        known_reason_codes = set(spec.get("reason_codes", {}))
        unknown_reason_codes = set(decision.get("reason_codes", [])) - known_reason_codes
        if unknown_reason_codes and decision.get("decision_mode") != "manual":
            errors.append(
                f"adapter_decisions[{decision_index}]: unknown reason code(s) {sorted(unknown_reason_codes)}"
            )
    return errors


def validate_adapter_boundaries(
    document: dict[str, Any], registry: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    decisions: dict[str, list[dict[str, Any]]] = {}
    adapters = registry_index(registry)

    for index, decision in enumerate(document.get("adapter_decisions", [])):
        if not isinstance(decision, dict):
            continue
        adapter_id = decision.get("adapter_id")
        if not isinstance(adapter_id, str) or not adapter_id:
            errors.append(f"adapter_decisions[{index}].adapter_id: missing or invalid")
            continue
        registry_record = adapters.get(adapter_id)
        if registry_record is None:
            errors.append(
                f"adapter_decisions[{index}]: unknown adapter_id '{adapter_id}'"
            )
        elif decision.get("ruleset_version") != registry_record.get("ruleset_version"):
            errors.append(
                f"adapter_decisions[{index}]: ruleset_version does not match registry "
                f"for '{adapter_id}'"
            )
        decisions.setdefault(adapter_id, []).append(decision)

        status = decision.get("status")
        if status == "load" and not decision.get("target_entities"):
            errors.append(
                f"adapter_decisions[{index}]: load requires at least one target entity"
            )
        if status == "load" and not decision.get("evidence_ids"):
            errors.append(
                f"adapter_decisions[{index}]: load requires routing evidence"
            )

    for index, record in enumerate(document.get("domain_records", [])):
        if not isinstance(record, dict):
            continue
        adapter_id = record.get("adapter_id")
        registry_record = adapters.get(adapter_id)
        if registry_record is None:
            errors.append(f"domain_records[{index}]: unknown adapter_id '{adapter_id}'")
        elif registry_record.get("status") != "implemented":
            errors.append(
                f"domain_records[{index}]: adapter '{adapter_id}' is "
                f"{registry_record.get('status')}, not implemented"
            )
        matching = decisions.get(adapter_id, [])
        loaded = [decision for decision in matching if decision.get("status") == "load"]
        if not loaded:
            errors.append(
                f"domain_records[{index}]: adapter '{adapter_id}' has no load decision"
            )
            continue
        loaded_source_ids = {
            source_id
            for decision in loaded
            for source_id in decision.get("source_ids", [])
            if isinstance(source_id, str)
        }
        record_source_ids = {
            source_id
            for source_id in record.get("source_ids", [])
            if isinstance(source_id, str)
        }
        uncovered = record_source_ids - loaded_source_ids
        if uncovered:
            errors.append(
                f"domain_records[{index}]: source(s) {sorted(uncovered)} are not covered by "
                f"a load decision for adapter '{adapter_id}'"
            )
    return errors


def validate_lineage_consistency(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    artifacts = {
        record.get("id"): record
        for record in document.get("data_artifacts", [])
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    analysis_steps = {
        record.get("id"): record
        for record in document.get("analysis_steps", [])
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }

    for step_id, step in analysis_steps.items():
        inputs = set(step.get("input_artifact_ids", []))
        outputs = set(step.get("output_artifact_ids", []))
        overlap = sorted(inputs & outputs)
        if overlap:
            errors.append(
                f"analysis_steps[{step_id}]: artifacts cannot be both input and output: {overlap}"
            )
        for artifact_id in outputs:
            artifact = artifacts.get(artifact_id)
            if artifact is None:
                continue
            generator = artifact.get("generated_by_analysis_step_id")
            if generator != step_id:
                errors.append(
                    f"data_artifacts[{artifact_id}]: output of '{step_id}' must name that "
                    "analysis step as generator"
                )

    for artifact_id, artifact in artifacts.items():
        generator = artifact.get("generated_by_analysis_step_id")
        if not isinstance(generator, str):
            continue
        step = analysis_steps.get(generator)
        if step is not None and artifact_id not in step.get("output_artifact_ids", []):
            errors.append(
                f"data_artifacts[{artifact_id}]: generator '{generator}' does not list "
                "the artifact as an output"
            )
    return errors


def validate_property_consistency(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    compatible_statuses = {
        "reported": {"reported", "secondary"},
        "derived": {"derived"},
        "inferred": {"inferred", "secondary"},
        "predicted": {"predicted"},
        "ambiguous": {"ambiguous"},
        "conflicting": {"conflicting"},
        "negative-result": {"negative-result"},
        "invalid": {"invalid"},
    }
    for index, record in enumerate(document.get("property_records", [])):
        if not isinstance(record, dict):
            continue
        determination = record.get("determination")
        value = record.get("value")
        value_status = value.get("value_status") if isinstance(value, dict) else None
        allowed = compatible_statuses.get(determination)
        if allowed is not None and value_status not in allowed:
            errors.append(
                f"property_records[{index}]: determination '{determination}' is "
                f"incompatible with value_status '{value_status}'"
            )
    return errors


def validate_document(
    document: Any,
    schema: Any,
    adapter_schemas: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
    field_contracts: dict[str, Any] | None = None,
    routing_lexicon: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    errors = require_core_shape(document)
    schema_check, warnings = schema_errors(document, schema)
    errors.extend(schema_check)
    if not isinstance(document, dict):
        return errors, warnings

    ids_by_kind, id_errors = collect_ids(document)
    errors.extend(id_errors)
    errors.extend(validate_references(document, ids_by_kind))
    errors.extend(validate_relative_artifact_paths(document))
    errors.extend(validate_lineage_consistency(document))
    errors.extend(validate_property_consistency(document))
    errors.extend(validate_condition_registry(document))
    errors.extend(validate_comparison_presentation(document))
    errors.extend(validate_error_budget_logic(document))
    errors.extend(validate_anomaly_chain_logic(document))
    errors.extend(validate_mechanism_graph_logic(document))
    errors.extend(validate_information_gap_logic(document))
    errors.extend(validate_pspp_logic(document))
    errors.extend(validate_adapter_boundaries(document, registry or {}))
    if routing_lexicon:
        errors.extend(validate_adapter_routing_signals(document, routing_lexicon))
    errors.extend(adapter_field_contract_errors(document, field_contracts or {}))
    adapter_errors, adapter_warnings = adapter_schema_errors(
        document, adapter_schemas or {}
    )
    errors.extend(adapter_errors)
    warnings.extend(adapter_warnings)
    return sorted(set(errors)), sorted(set(warnings))


def minimal_valid_document() -> dict[str, Any]:
    confidence = {"level": "high", "basis": ["direct-text", "entity-explicit"]}
    return {
        "schema_version": "4.6",
        "run_id": "RUN-SELFTEST",
        "loop_state": "audit-extraction",
        "decision_profile": "benchmark",
        "decision": {
            "question": "Can the adapter route a source to the scoped material?",
            "status": "answerable",
            "summary": "The test source contains target-bound routing evidence.",
            "evidence_strength": "high",
        },
        "input_assessment": {
            "readiness": "ready",
            "received_inputs": [
                {
                    "id": "IN1",
                    "name": "self-test.json",
                    "kind": "json",
                    "path": None,
                    "sha256": None,
                    "access_scope": "full",
                    "parse_status": "parsed",
                    "warnings": []
                }
            ],
            "normalized_item_count": 1,
            "blockers": [],
            "analysis_limitations": [],
            "optional_enrichment": [],
            "recommended_next_inputs": [],
            "notes": []
        },
        "condition_registry": [],
        "sources": [
            {
                "id": "S1",
                "source_type": "primary-experiment",
                "title": "Self-test source",
            }
        ],
        "evidence": [
            {
                "id": "E1",
                "source_id": "S1",
                "entity_ids": ["MAT1"],
                "modality": "text",
                "locator": {"section": "Results"},
                "raw_content": "A domain signal is reported for the target material.",
                "directness": "direct-primary",
                "extraction_method": "text",
                "confidence": confidence,
            }
        ],
        "entities": [
            {
                "id": "MAT1",
                "entity_type": "material",
                "names": [
                    {
                        "raw_term": "Material A",
                        "canonical_term": "Material A",
                        "mapping_status": "exact",
                        "evidence_ids": ["E1"],
                    }
                ],
                "parent_ids": [],
                "scope_status": "resolved",
                "evidence_ids": ["E1"],
            }
        ],
        "process_runs": [],
        "data_artifacts": [],
        "analysis_steps": [],
        "measurement_runs": [],
        "simulation_jobs": [],
        "property_records": [],
        "baseline_packages": [],
        "comparability_assessments": [],
        "deviation_episodes": [],
        "error_budgets": [],
        "anomaly_propagation_chains": [],
        "mechanism_graphs": [],
        "mechanism_nodes": [],
        "mechanism_edges": [],
        "mechanism_updates": [],
        "models": [],
        "hypotheses": [],
        "information_gaps": [],
        "verification_plan": [],
        "experiment_sets": [],
        "adapter_decisions": [
            {
                "adapter_id": "superconductivity",
                "ruleset_version": "2.0.0",
                "status": "load",
                "decision_mode": "benchmark",
                "source_ids": ["S1"],
                "paper_profile": "theoretical-materials",
                "article_centrality": "primary",
                "target_entities": [
                    {
                        "entity_id": "MAT1",
                        "role": "primary-system",
                        "scope_status": "resolved",
                    }
                ],
                "matched_signals": [
                    {
                        "signal_id": "sc-superconducting-claim",
                        "signal_type": "direct-domain-term",
                        "raw_term": "superconducting state",
                        "canonical_concept": "direct superconducting claim",
                        "strength": "strong",
                        "independence_group": "sc-claim",
                        "polarity": "affirmed",
                        "section": "Results",
                        "valid_context": True,
                        "entity_ids": ["MAT1"],
                        "evidence_id": "E1",
                    }
                ],
                "decision_gates": {
                    "target_entity_binding": "pass",
                    "independent_signal_count": 1,
                },
                "exclusion_matches": [],
                "ambiguities": [],
                "reason_codes": ["SC-LOAD-TARGET"],
                "evidence_ids": ["E1"],
                "decision_reason": "Self-test evidence is bound to the target.",
            }
        ],
        "domain_records": [
            {
                "id": "DOMAIN1",
                "adapter_id": "superconductivity",
                "record_type": "superconductivity-assessment",
                "source_ids": ["S1"],
                "entity_ids": ["MAT1"],
                "measurement_run_ids": [],
                "property_record_ids": [],
                "fields": {
                    "classification": "predicted-superconducting",
                    "evidence_channel_count": 1,
                    "evidence_channels": ["theoretical"],
                    "limitations": ["No experimental confirmation."],
                },
                "field_evidence": {
                    "classification": ["E1"],
                    "evidence_channel_count": ["E1"],
                    "evidence_channels": ["E1"],
                    "limitations": ["E1"],
                },
                "evidence_ids": ["E1"],
                "status": "reported",
                "confidence": confidence,
            }
        ],
        "experience_updates": [],
        "pspp_maps": [],
        "missing_information": [],
        "artifact_manifest": [],
        "quality": {
            "traceability": "pass",
            "entity_and_scope": "pass",
            "data_integrity": "pass",
            "comparability": "not-applicable",
            "normalization": "not-applicable",
            "adapter_routing": "pass",
            "counterevidence": "not-applicable",
            "error_attribution": "not-applicable",
            "anomaly_chain": "not-applicable",
            "information_gap_coverage": "not-applicable",
            "pspp_consistency": "not-applicable",
            "mechanism_graph_consistency": "not-applicable",
            "memory_governance": "not-applicable",
            "safety": "not-applicable",
            "json_valid": "tool-validated",
            "notes": [],
        },
    }


def run_self_test(
    schema: Any,
    adapter_schemas: dict[str, Any],
    registry: dict[str, Any],
    field_contracts: dict[str, Any],
    routing_lexicon: dict[str, Any],
) -> int:
    valid = minimal_valid_document()
    valid_errors, warnings = validate_document(
        valid, schema, adapter_schemas, registry, field_contracts, routing_lexicon
    )
    if valid_errors:
        print("SELF-TEST FAILED: valid fixture was rejected", file=sys.stderr)
        for error in valid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    invalid = json.loads(json.dumps(valid))
    invalid["domain_records"][0]["adapter_id"] = "not-loaded"
    invalid_errors, _ = validate_document(
        invalid, schema, adapter_schemas, registry, field_contracts
    )
    if not any("has no load decision" in error for error in invalid_errors):
        print("SELF-TEST FAILED: invalid adapter fixture was accepted", file=sys.stderr)
        return 1

    wrong_source = json.loads(json.dumps(valid))
    wrong_source["sources"].append(
        {
            "id": "S2",
            "source_type": "primary-experiment",
            "title": "Candidate-only source",
        }
    )
    wrong_source["domain_records"][0]["source_ids"] = ["S2"]
    wrong_source_errors, _ = validate_document(
        wrong_source, schema, adapter_schemas, registry, field_contracts
    )
    if not any("not covered by a load decision" in error for error in wrong_source_errors):
        print(
            "SELF-TEST FAILED: cross-source adapter leakage was accepted",
            file=sys.stderr,
        )
        return 1

    metallic_registry = json.loads(json.dumps(registry))
    for adapter in metallic_registry.get("adapters", []):
        if adapter.get("adapter_id") == "metallic-materials":
            adapter["status"] = "implemented"
    metallic = json.loads(json.dumps(valid))
    metallic["adapter_decisions"][0]["adapter_id"] = "metallic-materials"
    metallic["adapter_decisions"][0]["paper_profile"] = "experimental-materials"
    metallic["adapter_decisions"][0]["matched_signals"][0].update(
        {
            "signal_id": "met-alloy-identity",
            "raw_term": "alloy grade",
            "canonical_concept": "metal or alloy identity",
            "independence_group": "met-identity",
        }
    )
    metallic["adapter_decisions"][0]["reason_codes"] = ["MET-LOAD-TARGET"]
    metallic["domain_records"][0].update(
        {
            "adapter_id": "metallic-materials",
            "record_type": "metallic-identity",
            "fields": {"metallic_class": "alloy"},
            "field_evidence": {"metallic_class": ["E1"]},
        }
    )
    metallic_errors, _ = validate_document(
        metallic, schema, adapter_schemas, metallic_registry, field_contracts
    )
    if metallic_errors:
        print("SELF-TEST FAILED: field-contract fixture was rejected", file=sys.stderr)
        for error in metallic_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    invalid_metallic = json.loads(json.dumps(metallic))
    invalid_metallic["domain_records"][0]["fields"]["metallic_clas"] = "alloy"
    invalid_metallic_errors, _ = validate_document(
        invalid_metallic,
        schema,
        adapter_schemas,
        metallic_registry,
        field_contracts,
    )
    if not any("not declared" in error for error in invalid_metallic_errors):
        print("SELF-TEST FAILED: unknown adapter field was accepted", file=sys.stderr)
        return 1

    polluted_contract = field_contracts["adapters"]["metallic-materials"]["record_types"]["metallic-identity"]
    if {"alloy", "intermetallic", "unknown", "pure-metal"} & set(
        polluted_contract.get("allowed_fields", [])
    ):
        print("SELF-TEST FAILED: enum values leaked into adapter field names", file=sys.stderr)
        return 1

    invalid_signal = json.loads(json.dumps(valid))
    invalid_signal["adapter_decisions"][0]["matched_signals"][0]["signal_id"] = "invented-signal"
    invalid_signal_errors = validate_adapter_routing_signals(invalid_signal, routing_lexicon)
    if not any("unknown signal_id" in error for error in invalid_signal_errors):
        print("SELF-TEST FAILED: unknown routing signal was accepted", file=sys.stderr)
        return 1

    lineage = json.loads(json.dumps(valid))
    lineage["data_artifacts"] = [
        {
            "id": "DATA-RAW",
            "artifact_level": "raw",
            "source_ids": ["S1"],
            "access_status": "available",
            "evidence_ids": ["E1"],
        },
        {
            "id": "DATA-FIT",
            "artifact_level": "fitted",
            "source_ids": ["S1"],
            "parent_artifact_ids": ["DATA-RAW"],
            "generated_by_analysis_step_id": "ANALYSIS-1",
            "access_status": "available",
            "evidence_ids": ["E1"],
        },
    ]
    lineage["analysis_steps"] = [
        {
            "id": "ANALYSIS-1",
            "operation": "fit",
            "input_artifact_ids": ["DATA-RAW"],
            "output_artifact_ids": ["DATA-FIT"],
            "parameters": [],
            "evidence_ids": ["E1"],
            "status": "reported",
        }
    ]
    lineage_errors, _ = validate_document(
        lineage, schema, adapter_schemas, registry, field_contracts
    )
    if lineage_errors:
        print("SELF-TEST FAILED: valid artifact lineage was rejected", file=sys.stderr)
        for error in lineage_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    invalid_lineage = json.loads(json.dumps(lineage))
    invalid_lineage["data_artifacts"][1]["generated_by_analysis_step_id"] = "ANALYSIS-X"
    invalid_lineage_errors, _ = validate_document(
        invalid_lineage, schema, adapter_schemas, registry, field_contracts
    )
    if not any(
        "unknown analysis_step reference" in error or "must name" in error
        for error in invalid_lineage_errors
    ):
        print("SELF-TEST FAILED: broken artifact lineage was accepted", file=sys.stderr)
        return 1

    property_fixture = json.loads(json.dumps(valid))
    property_fixture["property_records"] = [
        {
            "id": "PROP-1",
            "entity_id": "MAT1",
            "property_raw": "test property",
            "value": {
                "raw_value": 1.0,
                "value_status": "reported",
                "extraction_method": "text",
                "evidence_ids": ["E1"],
                "confidence": valid["domain_records"][0]["confidence"],
            },
            "determination": "reported",
            "conditions": [],
            "reporting_role": "single-case",
            "evidence_ids": ["E1"],
        }
    ]
    property_errors, _ = validate_document(
        property_fixture, schema, adapter_schemas, registry, field_contracts
    )
    if property_errors:
        print("SELF-TEST FAILED: valid property fixture was rejected", file=sys.stderr)
        for error in property_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    invalid_property = json.loads(json.dumps(property_fixture))
    invalid_property["property_records"][0]["determination"] = "predicted"
    invalid_property_errors, _ = validate_document(
        invalid_property, schema, adapter_schemas, registry, field_contracts
    )
    if not any("incompatible with value_status" in error for error in invalid_property_errors):
        print("SELF-TEST FAILED: inconsistent property status was accepted", file=sys.stderr)
        return 1

    superconductivity = json.loads(json.dumps(valid))
    superconductivity["adapter_decisions"][0]["adapter_id"] = "superconductivity"
    superconductivity["adapter_decisions"][0]["paper_profile"] = "theoretical-materials"
    superconductivity["domain_records"][0].update(
        {
            "adapter_id": "superconductivity",
            "record_type": "superconductivity-assessment",
            "fields": {
                "classification": "predicted-superconducting",
                "evidence_channel_count": 1,
                "evidence_channels": ["theoretical"],
                "limitations": ["No experimental confirmation."],
            },
        }
    )
    superconductivity_errors, _ = validate_document(
        superconductivity, schema, adapter_schemas, registry, field_contracts
    )
    if superconductivity_errors:
        print("SELF-TEST FAILED: superconductivity fixture was rejected", file=sys.stderr)
        for error in superconductivity_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    invalid_superconductivity = json.loads(json.dumps(superconductivity))
    invalid_superconductivity["domain_records"][0]["fields"]["classification"] = (
        "invented-status"
    )
    invalid_superconductivity_errors, _ = validate_document(
        invalid_superconductivity,
        schema,
        adapter_schemas,
        registry,
        field_contracts,
    )
    if not any(
        "adapter[superconductivity]" in error
        for error in invalid_superconductivity_errors
    ):
        print(
            "SELF-TEST FAILED: invalid superconductivity payload was accepted",
            file=sys.stderr,
        )
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}")
    print("SELF-TEST PASSED")
    return 0


def main() -> int:
    default_schema = Path(__file__).resolve().parents[1] / "references" / "output-schema.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="JSON output to validate")
    parser.add_argument("--schema", type=Path, default=default_schema)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        schema = load_json(args.schema)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot load schema: {exc}", file=sys.stderr)
        return 2

    adapter_schemas, adapter_schema_load_errors = load_adapter_schemas(
        args.schema.resolve().parent
    )
    registry, registry_load_errors = load_adapter_registry(args.schema.resolve().parent)
    field_contracts, field_contract_load_errors = load_field_contracts(
        args.schema.resolve().parent, registry
    )
    routing_lexicon, routing_lexicon_load_errors = load_routing_lexicon(
        args.schema.resolve().parent, registry
    )
    benchmark_catalog, benchmark_load_errors = load_benchmark_catalog(
        args.schema.resolve().parent, registry
    )
    source_backed_catalog, source_backed_load_errors = load_source_backed_catalog(
        args.schema.resolve().parent, registry
    )
    adapter_asset_errors = validate_adapter_assets(
        registry,
        field_contracts,
        routing_lexicon,
        benchmark_catalog,
        source_backed_catalog,
        adapter_schemas,
        args.schema.resolve().parent,
    )
    asset_load_errors = (
        adapter_schema_load_errors
        + registry_load_errors
        + field_contract_load_errors
        + routing_lexicon_load_errors
        + benchmark_load_errors
        + source_backed_load_errors
        + adapter_asset_errors
    )
    if asset_load_errors:
        for error in asset_load_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.self_test:
        return run_self_test(
            schema, adapter_schemas, registry, field_contracts, routing_lexicon
        )
    if args.input is None:
        parser.error("input is required unless --self-test is used")

    try:
        document = load_json(args.input)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot load input JSON: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate_document(
        document,
        schema,
        adapter_schemas,
        registry,
        field_contracts,
        routing_lexicon,
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print(f"INVALID: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("VALID: schema, IDs, references, and adapter boundaries passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
