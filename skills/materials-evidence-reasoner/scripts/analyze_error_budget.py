#!/usr/bin/env python3
"""Estimate a conservative descriptive error budget from repeat-level CSV data.

This helper separates nested measurement repeatability, sample-within-batch,
batch-between, and unallocated variance using a simple method-of-moments
approximation. It is intended for workflow triage, not accreditation or a
universal metrology statement. Preserve the original CSV and review design
assumptions before integrating the emitted fragment into materials-result.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def sample_variance(values: list[float]) -> float:
    return statistics.variance(values) if len(values) >= 2 else 0.0


def weighted_mean(items: Iterable[tuple[float, int]]) -> float:
    pairs = [(value, weight) for value, weight in items if weight > 0]
    total_weight = sum(weight for _, weight in pairs)
    return sum(value * weight for value, weight in pairs) / total_weight if total_weight else 0.0


def value_record(value: float, unit: str, operation: str, formula: str) -> dict[str, Any]:
    return {
        "raw_value": value,
        "raw_unit": unit,
        "normalized_value": value,
        "normalized_unit": unit,
        "value_status": "derived",
        "extraction_method": "analyze_error_budget.py",
        "derivation": {
            "input_evidence_ids": [],
            "operation": operation,
            "formula": formula,
        },
        "evidence_ids": [],
        "confidence": {
            "level": "low",
            "basis": ["descriptive-method-of-moments", "requires-design-review"],
        },
        "notes": [
            "Generated from repeat-level CSV by a deterministic descriptive helper.",
            "Review balance, nesting, independence, covariance, and units before scientific use.",
        ],
    }


def parse_rows(path: Path, value_col: str, batch_col: str, sample_col: str, repeat_col: str | None) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        required = {value_col, batch_col, sample_col}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        rows: list[dict[str, Any]] = []
        for line_no, row in enumerate(reader, start=2):
            raw = (row.get(value_col) or "").strip()
            if raw == "":
                continue
            try:
                value = float(raw)
            except ValueError as exc:
                raise ValueError(f"line {line_no}: {value_col}={raw!r} is not numeric") from exc
            batch = (row.get(batch_col) or "").strip()
            sample = (row.get(sample_col) or "").strip()
            repeat = (row.get(repeat_col) or "").strip() if repeat_col else str(line_no)
            if not batch or not sample:
                raise ValueError(f"line {line_no}: batch and sample IDs are required")
            rows.append({"batch": batch, "sample": sample, "repeat": repeat, "value": value, "line": line_no})
    if len(rows) < 3:
        raise ValueError("at least three numeric rows are required")
    return rows


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = [row["value"] for row in rows]
    total_variance = sample_variance(values)

    sample_groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    batch_groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        sample_groups[(row["batch"], row["sample"])].append(row["value"])
        batch_groups[row["batch"]].append(row["value"])

    # Pooled within-sample repeatability variance.
    within_terms: list[tuple[float, int]] = []
    for group in sample_groups.values():
        if len(group) >= 2:
            within_terms.append((sample_variance(group), len(group) - 1))
    repeatability_var = weighted_mean(within_terms)

    # Between-sample variance within each batch, adjusted for repeatability of sample means.
    sample_component_terms: list[tuple[float, int]] = []
    for batch in batch_groups:
        batch_sample_groups = [vals for (batch_id, _), vals in sample_groups.items() if batch_id == batch]
        means = [statistics.fmean(vals) for vals in batch_sample_groups]
        if len(means) < 2:
            continue
        mean_repeats = statistics.fmean(len(vals) for vals in batch_sample_groups)
        adjusted = max(sample_variance(means) - repeatability_var / max(mean_repeats, 1.0), 0.0)
        sample_component_terms.append((adjusted, len(means) - 1))
    sample_var = weighted_mean(sample_component_terms)

    # Between-batch variance of batch means, adjusted approximately for lower-level components.
    batch_means = [statistics.fmean(vals) for vals in batch_groups.values()]
    if len(batch_means) >= 2:
        mean_samples_per_batch = statistics.fmean(
            sum(1 for batch_id, _ in sample_groups if batch_id == batch) for batch in batch_groups
        )
        mean_repeats_per_sample = statistics.fmean(len(vals) for vals in sample_groups.values())
        lower_level_on_mean = sample_var / max(mean_samples_per_batch, 1.0) + repeatability_var / max(mean_samples_per_batch * mean_repeats_per_sample, 1.0)
        batch_var = max(sample_variance(batch_means) - lower_level_on_mean, 0.0)
    else:
        batch_var = 0.0

    identified = repeatability_var + sample_var + batch_var
    unallocated_var = max(total_variance - identified, 0.0)
    components = {
        "measurement-repeatability": repeatability_var,
        "sample-within-batch": sample_var,
        "batch-between": batch_var,
        "unallocated": unallocated_var,
    }
    denominator = sum(components.values())
    fractions = {key: (value / denominator if denominator > 0 else 0.0) for key, value in components.items()}

    return {
        "n_rows": len(rows),
        "n_batches": len(batch_groups),
        "n_samples": len(sample_groups),
        "min_repeats_per_sample": min(len(vals) for vals in sample_groups.values()),
        "max_repeats_per_sample": max(len(vals) for vals in sample_groups.values()),
        "mean": statistics.fmean(values),
        "total_variance": total_variance,
        "components": components,
        "fractions": fractions,
        "balanced": len({len(vals) for vals in sample_groups.values()}) == 1
        and len({sum(1 for batch_id, _ in sample_groups if batch_id == batch) for batch in batch_groups}) == 1,
    }


def build_budget(result: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    variance_unit = f"{args.unit}^2" if args.unit else "value-unit^2"
    components: list[dict[str, Any]] = []
    labels = {
        "measurement-repeatability": "Pooled within-sample repeatability",
        "sample-within-batch": "Between-sample variance within batch",
        "batch-between": "Between-batch variance",
        "unallocated": "Unallocated/designer-unidentified variance",
    }
    limitations = {
        "measurement-repeatability": [],
        "sample-within-batch": ["Method-of-moments adjustment assumes nested samples and comparable repeat counts."],
        "batch-between": ["Requires at least two batches; estimate is approximate for unbalanced designs."],
        "unallocated": ["May contain covariance, condition drift, data processing, operator, instrument, or model effects."],
    }
    for index, (category, estimate) in enumerate(result["components"].items(), start=1):
        components.append({
            "id": f"EC-DRAFT-{index}",
            "category": category,
            "label": labels[category],
            "contribution_basis": "variance",
            "estimate_status": "quantified" if category != "unallocated" else "bounded",
            "estimate": value_record(estimate, variance_unit, "nested descriptive variance component", "see analyze_error_budget.py"),
            "fraction_of_total": result["fractions"][category],
            "source_entity_ids": [],
            "measurement_run_ids": [],
            "model_ids": [],
            "correlation_notes": "Covariance is not identified by this helper.",
            "limitations": limitations[category],
            "evidence_ids": [],
        })
    dominant = sorted(components, key=lambda item: item["fraction_of_total"], reverse=True)
    dominant_ids = [item["id"] for item in dominant if item["fraction_of_total"] >= dominant[0]["fraction_of_total"] - 1e-12][:2]
    spread = math.sqrt(max(result["total_variance"], 0.0))
    expanded = args.coverage_factor * spread
    effect_comparison: dict[str, Any] = {
        "relation": "unknown",
        "uncertainty_value": value_record(expanded, args.unit, "coverage-factor times observed standard deviation", f"{args.coverage_factor} * sqrt(total variance)"),
        "rationale": "No effect value was provided; compare the expanded descriptive spread with the decision-relevant effect before classifying a deviation.",
    }
    if args.effect is not None:
        effect_abs = abs(args.effect)
        if effect_abs > expanded:
            relation = "uncertainty-smaller"
        elif expanded >= 2 * effect_abs and effect_abs > 0:
            relation = "uncertainty-dominates"
        else:
            relation = "comparable"
        effect_comparison = {
            "relation": relation,
            "effect_value": value_record(effect_abs, args.effect_unit or args.unit, "absolute user-supplied effect", "abs(effect)"),
            "uncertainty_value": value_record(expanded, args.unit, "coverage-factor times observed standard deviation", f"{args.coverage_factor} * sqrt(total variance)"),
            "rationale": (
                f"Descriptive comparison only: |effect|={effect_abs:g} and k·SD={expanded:g} with k={args.coverage_factor:g}. "
                "This is not a significance test or accredited uncertainty statement."
            ),
        }
    return {
        "id": args.id,
        "target_property_record_ids": args.target_property_record_id,
        **({"deviation_episode_id": args.deviation_episode_id} if args.deviation_episode_id else {}),
        "method": "variance-components",
        "replicate_structure": {
            "n_rows": result["n_rows"],
            "n_batches": result["n_batches"],
            "n_samples": result["n_samples"],
            "min_repeats_per_sample": result["min_repeats_per_sample"],
            "max_repeats_per_sample": result["max_repeats_per_sample"],
            "balanced": result["balanced"],
            "nesting": "measurement repeats nested in samples nested in batches",
        },
        "assumptions": [
            "Rows are independent conditional on the declared nested IDs.",
            "Samples are nested in batches; crossed instrument/operator effects are not separated.",
            "Component estimates are descriptive method-of-moments approximations.",
            "Covariance and process-condition effects are included in unallocated variance unless modeled separately.",
        ],
        "components": components,
        "combined_uncertainty": value_record(expanded, args.unit, "coverage-factor times total observed standard deviation", f"{args.coverage_factor} * sqrt(total variance)"),
        "dominant_component_ids": dominant_ids,
        "quantitative_fraction_complete": True,
        "effect_comparison": effect_comparison,
        "conclusion": (
            "This draft separates repeatability, within-batch sample, between-batch, and unallocated variance. "
            "Review the experimental design and add calibration, processing, environment, analysis, and model components before final use."
        ),
        "limitations": [
            "Not a GUM-compliant or accreditation-grade uncertainty budget.",
            "Unbalanced or crossed designs require a more appropriate statistical model.",
            "No automatic causal attribution is made from variance components.",
        ],
        "evidence_ids": [],
    }


def markdown_summary(result: dict[str, Any], budget: dict[str, Any], source: Path) -> str:
    lines = [
        "# Descriptive Error Budget Draft",
        "",
        f"Source: `{source.name}`",
        "",
        f"Rows: {result['n_rows']}; batches: {result['n_batches']}; samples: {result['n_samples']}; balanced: `{result['balanced']}`.",
        "",
        "| Component | Variance | Fraction |",
        "|---|---:|---:|",
    ]
    for component in budget["components"]:
        estimate = component["estimate"]["normalized_value"]
        lines.append(f"| {component['label']} | {estimate:.6g} | {component['fraction_of_total']:.1%} |")
    lines.extend([
        "",
        f"Effect vs uncertainty: `{budget['effect_comparison']['relation']}`.",
        "",
        "> This is a deterministic descriptive helper output, not a GUM-compliant or accreditation-grade uncertainty statement. It does not prove a material mechanism and must be reviewed against the repeat design, calibration, covariance, process logs and model assumptions.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--value", required=True, help="Numeric measurement column")
    parser.add_argument("--batch", default="batch_id")
    parser.add_argument("--sample", default="sample_id")
    parser.add_argument("--repeat", default="measurement_repeat_id")
    parser.add_argument("--unit", default="")
    parser.add_argument("--effect", type=float, default=None, help="Optional decision-relevant effect magnitude")
    parser.add_argument("--effect-unit", default=None)
    parser.add_argument("--coverage-factor", type=float, default=2.0)
    parser.add_argument("--id", default="EB-DRAFT-1")
    parser.add_argument("--target-property-record-id", action="append", default=[])
    parser.add_argument("--deviation-episode-id", default=None)
    parser.add_argument("-o", "--output", type=Path, default=Path("error-budget-fragment.json"))
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    if args.coverage_factor <= 0:
        parser.error("--coverage-factor must be positive")
    try:
        rows = parse_rows(args.input, args.value, args.batch, args.sample, args.repeat)
        result = analyze(rows)
        budget = build_budget(result, args)
    except (OSError, ValueError, statistics.StatisticsError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(budget, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(markdown_summary(result, budget, args.input), encoding="utf-8")
    print(f"WROTE {args.output}")
    if args.report:
        print(f"WROTE {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
