#!/usr/bin/env python3
"""Evaluate adapter routing predictions against synthetic or source-backed cases."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "references" / "adapter-benchmark-cases.json"
SOURCE_CATALOG = ROOT / "references" / "source-backed-routing-cases.json"
STATUSES = ("load", "candidate", "skip")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def flatten_expected(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for case in catalog.get("cases", []):
        if "decisions" in case:
            for decision in case["decisions"]:
                flattened.append(
                    {
                        "case_id": case["case_id"],
                        "adapter_id": decision["adapter_id"],
                        "status": decision["expected_status"],
                        "signal_ids": decision.get("expected_signal_ids", []),
                        "reason_codes": decision.get("expected_reason_codes", []),
                    }
                )
        else:
            flattened.append(
                {
                    "case_id": case["case_id"],
                    "adapter_id": case["adapter_id"],
                    "status": case["expected_status"],
                    "signal_ids": case.get("expected_signal_ids", []),
                    "reason_codes": case.get("expected_reason_codes", []),
                }
            )
    return flattened


def normalize_predictions(payload: Any) -> list[dict[str, Any]]:
    predictions = payload.get("predictions") if isinstance(payload, dict) else payload
    if not isinstance(predictions, list):
        raise ValueError("predictions must be an array or an object containing predictions[]")
    return predictions


def safe_div(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def evaluate(expected: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    prediction_index: dict[tuple[str, str], dict[str, Any]] = {}
    duplicate_keys: list[str] = []
    for prediction in predictions:
        key = (prediction.get("case_id"), prediction.get("adapter_id"))
        if key in prediction_index:
            duplicate_keys.append(f"{key[0]}/{key[1]}")
        prediction_index[key] = prediction

    confusion = {expected_status: Counter() for expected_status in STATUSES}
    errors: list[dict[str, Any]] = []
    signal_tp = signal_fp = signal_fn = 0
    reason_exact = 0
    evaluated = 0
    for item in expected:
        key = (item["case_id"], item["adapter_id"])
        prediction = prediction_index.get(key)
        if prediction is None:
            confusion[item["status"]]["missing"] += 1
            errors.append({"case_id": key[0], "adapter_id": key[1], "error": "missing-prediction"})
            continue
        evaluated += 1
        predicted_status = prediction.get("status")
        confusion[item["status"]][predicted_status] += 1
        if predicted_status != item["status"]:
            errors.append(
                {
                    "case_id": key[0],
                    "adapter_id": key[1],
                    "error": "status-mismatch",
                    "expected": item["status"],
                    "predicted": predicted_status,
                }
            )
        expected_signals = set(item["signal_ids"])
        predicted_signals = set(prediction.get("matched_signal_ids", []))
        signal_tp += len(expected_signals & predicted_signals)
        signal_fp += len(predicted_signals - expected_signals)
        signal_fn += len(expected_signals - predicted_signals)
        if set(prediction.get("reason_codes", [])) == set(item["reason_codes"]):
            reason_exact += 1

    expected_keys = {(item["case_id"], item["adapter_id"]) for item in expected}
    extra_keys = [
        f"{case_id}/{adapter_id}"
        for case_id, adapter_id in prediction_index
        if (case_id, adapter_id) not in expected_keys
    ]
    total = len(expected)
    status_correct = sum(confusion[status][status] for status in STATUSES)
    per_status: dict[str, Any] = {}
    f1_values = []
    for status in STATUSES:
        tp = confusion[status][status]
        fn = sum(confusion[status].values()) - tp
        fp = sum(confusion[other][status] for other in STATUSES if other != status)
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * tp, 2 * tp + fp + fn)
        per_status[status] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(confusion[status].values())}
        f1_values.append(f1)

    return {
        "expected_count": total,
        "evaluated_count": evaluated,
        "status_accuracy": safe_div(status_correct, total),
        "status_macro_f1": sum(f1_values) / len(f1_values),
        "per_status": per_status,
        "signal_precision": safe_div(signal_tp, signal_tp + signal_fp),
        "signal_recall": safe_div(signal_tp, signal_tp + signal_fn),
        "reason_code_exact_rate": safe_div(reason_exact, evaluated),
        "duplicate_predictions": sorted(duplicate_keys),
        "extra_predictions": sorted(extra_keys),
        "errors": errors,
    }


def perfect_predictions(expected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": item["case_id"],
            "adapter_id": item["adapter_id"],
            "status": item["status"],
            "matched_signal_ids": item["signal_ids"],
            "reason_codes": item["reason_codes"],
        }
        for item in expected
    ]


def run_self_test() -> int:
    for catalog_path in (DEFAULT_CATALOG, SOURCE_CATALOG):
        expected = flatten_expected(load_json(catalog_path))
        perfect = evaluate(expected, perfect_predictions(expected))
        if perfect["status_accuracy"] != 1.0 or perfect["signal_recall"] != 1.0:
            print(f"SELF-TEST FAILED: perfect fixture failed for {catalog_path.name}")
            return 1
        degraded_predictions = perfect_predictions(expected)
        degraded_predictions[0]["status"] = "skip" if expected[0]["status"] != "skip" else "load"
        degraded = evaluate(expected, degraded_predictions)
        if degraded["status_accuracy"] >= 1.0 or not degraded["errors"]:
            print(f"SELF-TEST FAILED: degraded fixture passed for {catalog_path.name}")
            return 1
    print("ROUTING EVALUATOR SELF-TEST PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", nargs="?", type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--source-backed", action="store_true", help="Use the bundled source-backed non-gold catalog")
    parser.add_argument("--write-template", type=Path, help="Write a prediction template and exit")
    parser.add_argument("--strict", action="store_true", help="Return nonzero for any missing, duplicate, extra, or status error")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    catalog_path = SOURCE_CATALOG if args.source_backed else args.catalog
    expected = flatten_expected(load_json(catalog_path))
    if args.write_template:
        template = {
            "catalog": catalog_path.name,
            "predictions": [
                {
                    "case_id": item["case_id"],
                    "adapter_id": item["adapter_id"],
                    "status": None,
                    "matched_signal_ids": [],
                    "reason_codes": [],
                }
                for item in expected
            ],
        }
        args.write_template.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE {args.write_template}")
        return 0
    if args.predictions is None:
        parser.error("predictions is required unless --self-test or --write-template is used")
    result = evaluate(expected, normalize_predictions(load_json(args.predictions)))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.strict and (result["errors"] or result["duplicate_predictions"] or result["extra_predictions"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
