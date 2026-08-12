#!/usr/bin/env python3
"""Compare a free-form answer with the contract-aware Skill output.

This is a reproducible package-level contract ablation, not an LLM leaderboard.
Both modes start from the same frozen synthetic fixture.  The no-skill mode
keeps the human-readable facts, but deliberately has no canonical contract,
evidence IDs, condition registry, or diagnostic lineage.  The Skill mode is
the checked-in canonical fixture validated with the package's own validator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "examples" / "synthetic-closed-loop.json"
DEFAULT_JSON = ROOT / "examples" / "skill-effect-comparison.json"
DEFAULT_HTML = ROOT / "examples" / "skill-effect-comparison.html"
DEFAULT_SVG = ROOT / "docs" / "images" / "skill-effect-comparison.svg"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected an object in {path}")
    return payload


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def make_freeform_projection(document: dict[str, Any]) -> dict[str, Any]:
    """Model the common unconstrained answer shape without changing facts."""

    observations = []
    for record in document.get("property_records", []):
        value = record.get("value", {})
        observations.append(
            {
                "property": record.get("property_raw"),
                "value": value.get("raw_value"),
                "unit": value.get("raw_unit"),
                "note": record.get("applicability"),
            }
        )
    return {
        "summary": document.get("decision", {}).get("summary"),
        "observations": observations,
        "hypotheses": [item.get("statement") for item in document.get("hypotheses", [])],
        "next_steps": [item.get("action") for item in document.get("verification_plan", [])],
    }


def load_contract_validator() -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import validate_output

    reference_dir = ROOT / "references"
    schema = validate_output.load_json(reference_dir / "output-schema.json")
    adapter_schemas, schema_errors = validate_output.load_adapter_schemas(reference_dir)
    registry, registry_errors = validate_output.load_adapter_registry(reference_dir)
    field_contracts, field_errors = validate_output.load_field_contracts(reference_dir, registry)
    lexicon, lexicon_errors = validate_output.load_routing_lexicon(reference_dir, registry)
    asset_errors = schema_errors + registry_errors + field_errors + lexicon_errors
    if asset_errors:
        raise RuntimeError("cannot load validation assets: " + "; ".join(asset_errors))
    return validate_output, schema, adapter_schemas, registry, field_contracts, lexicon


def validate_skill_document(document: dict[str, Any]) -> tuple[bool, list[str]]:
    validator, schema, adapter_schemas, registry, field_contracts, lexicon = load_contract_validator()
    errors, _warnings = validator.validate_document(
        document,
        schema,
        adapter_schemas,
        registry,
        field_contracts,
        lexicon,
    )
    return not errors, errors


def skill_metrics(document: dict[str, Any]) -> dict[str, float]:
    valid, _errors = validate_skill_document(document)

    properties = document.get("property_records", [])
    hypotheses = document.get("hypotheses", [])
    gaps = document.get("information_gaps", [])
    assessments = document.get("comparability_assessments", [])
    deviations = document.get("deviation_episodes", [])
    edges = document.get("mechanism_edges", [])
    manifests = document.get("artifact_manifest", [])

    evidence_checks: list[bool] = []
    for item in properties:
        evidence_checks.append(bool(item.get("evidence_ids") or item.get("value", {}).get("evidence_ids")))
    for item in deviations:
        evidence_checks.append(bool(item.get("evidence_ids")))
    for item in hypotheses:
        evidence_checks.append(bool(item.get("support_evidence_ids") or item.get("limitations")))
    for item in edges:
        evidence_checks.append(bool(item.get("support_evidence_ids") or item.get("limitations")))

    condition_checks: list[bool] = []
    for item in properties:
        condition_checks.append(bool(item.get("value", {}).get("condition_signature", {}).get("condition_id")))
    for item in assessments:
        condition_checks.append(bool(item.get("target_property_record_ids") and item.get("result") and item.get("evidence_ids")))
    for item in deviations:
        condition_checks.append(bool(item.get("comparability_assessment_id")))
    for item in edges:
        condition_checks.append(bool(item.get("condition_ids") and item.get("boundary_conditions")))

    covered_gaps = {
        gap_id
        for experiment_set in document.get("experiment_sets", [])
        for gap_id in experiment_set.get("information_gap_ids", [])
    }
    gap_ids = {item.get("id") for item in gaps if item.get("id")}
    valid_manifest = sum(
        bool(item.get("id") and item.get("path") and isinstance(item.get("depends_on", []), list))
        for item in manifests
    )

    return {
        "fact_capture": 1.0,
        "canonical_json": float(valid),
        "evidence_traceability": ratio(sum(evidence_checks), len(evidence_checks)),
        "condition_binding": ratio(sum(condition_checks), len(condition_checks)),
        "comparability_gate": ratio(
            sum(bool(item.get("target_property_record_ids") and item.get("result") and item.get("evidence_ids")) for item in assessments),
            len(assessments),
        ),
        "falsifiable_mechanisms": ratio(
            sum(bool(item.get("unique_predictions") and item.get("falsifiers")) for item in hypotheses),
            len(hypotheses),
        ),
        "experiment_coverage": ratio(len(covered_gaps & gap_ids), len(gap_ids)),
        "artifact_lineage": ratio(valid_manifest, len(manifests)),
    }


def freeform_metrics(document: dict[str, Any], projection: dict[str, Any]) -> dict[str, float]:
    expected_facts = len(document.get("property_records", [])) + len(document.get("hypotheses", [])) + len(document.get("verification_plan", []))
    retained_facts = len(projection.get("observations", [])) + len(projection.get("hypotheses", [])) + len(projection.get("next_steps", []))
    return {
        "fact_capture": ratio(retained_facts, expected_facts),
        "canonical_json": 0.0,
        "evidence_traceability": 0.0,
        "condition_binding": 0.0,
        "comparability_gate": 0.0,
        "falsifiable_mechanisms": 0.0,
        "experiment_coverage": 0.0,
        "artifact_lineage": 0.0,
    }


METRICS = [
    ("fact_capture", "事实保留", "核心数值、假设和下一步仍然可读"),
    ("canonical_json", "机器接口", "是否通过 canonical JSON 与结构校验"),
    ("evidence_traceability", "证据可回查", "事实和机理是否保留 evidence ID 或明确限制"),
    ("condition_binding", "条件绑定", "条件是否绑定到记录、偏差和机理边"),
    ("comparability_gate", "可比性闸门", "是否先确认参照和可比性再解释偏差"),
    ("falsifiable_mechanisms", "可证伪机理", "机理是否有独特预测和反证条件"),
    ("experiment_coverage", "实验覆盖", "最小实验是否覆盖信息缺口"),
    ("artifact_lineage", "产物谱系", "报告、图表和导出是否可追溯到结果源"),
]


def build_comparison(document: dict[str, Any]) -> dict[str, Any]:
    projection = make_freeform_projection(document)
    baseline = freeform_metrics(document, projection)
    skill = skill_metrics(document)
    guarded_keys = [key for key, _label, _description in METRICS if key != "fact_capture"]
    return {
        "benchmark": {
            "name": "skill-contract-ablation",
            "version": "1.0",
            "fixture": "examples/synthetic-closed-loop.json",
            "scope": "package capability, not LLM intelligence ranking",
            "same_facts_in_both_modes": True,
        },
        "modes": {
            "without_skill": {
                "label": "不用 Skill",
                "description": "自由文本式摘要：保留事实、假设和下一步，但不执行统一字段与证据合同。",
                "metrics": baseline,
                "projection": projection,
                "guardrail_score": ratio(sum(baseline[key] for key in guarded_keys), len(guarded_keys)),
            },
            "with_skill": {
                "label": "使用 Skill",
                "description": "SKILL.md + canonical schema + validator + renderer 的闭环输出。",
                "metrics": skill,
                "guardrail_score": ratio(sum(skill[key] for key in guarded_keys), len(guarded_keys)),
            },
        },
        "metrics": [
            {"id": key, "label": label, "description": description, "without_skill": baseline[key], "with_skill": skill[key]}
            for key, label, description in METRICS
        ],
        "interpretation": [
            "两种模式保留同一组核心事实；差异来自是否执行可追溯合同，而不是事实数量本身。",
            "使用 Skill 后，结果可被校验、回查、渲染和交给下一次 Agent；这不是因果正确性的证明。",
            "真实项目应继续用 source-backed、双人标注和重复运行评测模型输出；本 fixture 是可重复的包级回归基线。",
        ],
    }


def esc(value: Any) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def render_html(result: dict[str, Any]) -> str:
    payload = json.dumps(result, ensure_ascii=False).replace("</", "<\\/")
    rows = []
    for item in result["metrics"]:
        rows.append(
            f'<div class="metric-row"><div class="metric-label"><strong>{esc(item["label"])}</strong><span>{esc(item["description"])}</span></div>'
            f'<div class="bar-track"><div class="bar baseline" style="width:{item["without_skill"] * 100:.0f}%"></div></div>'
            f'<div class="bar-track"><div class="bar skill" style="width:{item["with_skill"] * 100:.0f}%"></div></div>'
            f'<output>{percent(item["without_skill"])} / {percent(item["with_skill"])}</output></div>'
        )
    notes = "".join(f"<li>{esc(note)}</li>" for note in result["interpretation"])
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skill effect comparison</title>
<style>
:root{{color-scheme:light dark;--bg:#f5f5f7;--surface:rgba(255,255,255,.84);--text:#1d1d1f;--muted:#6e6e73;--line:rgba(60,60,67,.16);--blue:#007aff;--purple:#af52de;--green:#34c759}}
@media(prefers-color-scheme:dark){{:root{{--bg:#000;--surface:rgba(28,28,30,.92);--text:#f5f5f7;--muted:#aeaeb2;--line:rgba(255,255,255,.16);--blue:#0a84ff;--purple:#bf5af2;--green:#30d158}}}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 82% 0,rgba(0,122,255,.14),transparent 28rem),var(--bg);color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI","PingFang SC",Arial,sans-serif}}main{{max-width:1120px;margin:auto;padding:48px 24px 64px}}header{{max-width:760px;margin-bottom:28px}}h1{{font-size:clamp(28px,4vw,46px);letter-spacing:-.04em;margin:0 0 10px}}h2{{font-size:20px;margin:0 0 14px}}p,li{{color:var(--muted)}}.eyebrow{{color:var(--blue);font-weight:650;letter-spacing:.04em;margin-bottom:8px}}.note{{border-left:3px solid var(--blue);padding:10px 14px;background:var(--surface);border-radius:0 14px 14px 0}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:20px 0}}.panel{{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:22px;backdrop-filter:blur(24px)}}.score{{font-size:42px;letter-spacing:-.05em;font-weight:700}}.score span{{font-size:14px;color:var(--muted);font-weight:500}}.legend{{display:flex;gap:18px;color:var(--muted);font-size:13px;margin:8px 0 16px}}.swatch{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;background:var(--purple)}}.swatch.skill{{background:var(--green)}}.metric-row{{display:grid;grid-template-columns:minmax(180px,1.3fr) minmax(100px,1fr) minmax(100px,1fr) 88px;gap:12px;align-items:center;border-top:1px solid var(--line);padding:13px 0}}.metric-label span{{display:block;color:var(--muted);font-size:12px}}.bar-track{{height:12px;background:color-mix(in srgb,var(--muted) 12%,transparent);border-radius:999px;overflow:hidden}}.bar{{height:100%;border-radius:inherit;min-width:0}}.bar.baseline{{background:var(--purple)}}.bar.skill{{background:var(--green)}}output{{font-variant-numeric:tabular-nums;text-align:right;color:var(--muted);font-size:13px}}details{{margin-top:18px}}summary{{cursor:pointer;font-weight:650}}@media(max-width:720px){{main{{padding:30px 16px 44px}}.grid{{grid-template-columns:1fr}}.metric-row{{grid-template-columns:1fr 1fr 1fr;gap:8px}}.metric-label{{grid-column:1/-1}}output{{grid-column:1/-1;text-align:left}}}}
</style></head><body><main><header><div class="eyebrow">MATERIALS EVIDENCE REASONER · PACKAGE TEST</div><h1>不用 Skill，和使用 Skill，差在哪里？</h1><p class="note">同一份 synthetic closed-loop 输入、同一组核心事实；对比自由文本式结果与执行 canonical 合同后的结果。</p></header>
<section class="grid"><article class="panel"><h2>不用 Skill</h2><div class="score">{percent(result["modes"]["without_skill"]["guardrail_score"])} <span>合同护栏覆盖</span></div><p>{esc(result["modes"]["without_skill"]["description"])}</p></article><article class="panel"><h2>使用 Skill</h2><div class="score">{percent(result["modes"]["with_skill"]["guardrail_score"])} <span>合同护栏覆盖</span></div><p>{esc(result["modes"]["with_skill"]["description"])}</p></article></section>
<section class="panel"><h2>能力对照</h2><div class="legend"><span><i class="swatch"></i>不用 Skill</span><span><i class="swatch skill"></i>使用 Skill</span><span>数值为该维度覆盖率，不是模型准确率</span></div>{''.join(rows)}</section>
<section class="panel"><details><summary>如何解释这次测试</summary><ul>{notes}</ul></details></section>
<script>window.__comparison = {payload};</script></main></body></html>'''


def render_svg(result: dict[str, Any]) -> str:
    width, height = 1080, 560
    left, right, top, row_height = 250, 80, 92, 48
    chart_width = width - left - right
    rows = []
    for index, item in enumerate(result["metrics"]):
        y = top + index * row_height
        label = esc(item["label"])
        baseline = item["without_skill"] * chart_width
        skill = item["with_skill"] * chart_width
        rows.append(
            f'<text x="{left - 18}" y="{y + 8}" text-anchor="end" class="label">{label}</text>'
            f'<rect x="{left}" y="{y - 10}" width="{chart_width}" height="10" rx="5" class="track"/>'
            f'<rect x="{left}" y="{y - 10}" width="{baseline:.1f}" height="10" rx="5" class="baseline"/>'
            f'<rect x="{left}" y="{y + 5}" width="{chart_width}" height="10" rx="5" class="track"/>'
            f'<rect x="{left}" y="{y + 5}" width="{skill:.1f}" height="10" rx="5" class="skill"/>'
            f'<text x="{width - right + 14}" y="{y + 8}" class="value">{percent(item["with_skill"])}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">不用 Skill 与使用 Skill 的能力对照</title><desc id="desc">同一份材料证据闭环输入下，使用 Skill 在机器接口、证据、条件、可比性、机理、实验和产物谱系方面提供合同护栏。</desc>
<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",Arial,sans-serif;fill:#1d1d1f}}.title{{font-size:25px;font-weight:700;letter-spacing:-.03em}}.sub{{font-size:13px;fill:#6e6e73}}.label{{font-size:14px}}.value{{font-size:13px;fill:#248a3d;font-weight:700}}.track{{fill:#e5e5ea}}.baseline{{fill:#af52de}}.skill{{fill:#34c759}}.legend{{font-size:13px;fill:#6e6e73}}</style>
<text x="48" y="44" class="title">不用 Skill，和使用 Skill，差在哪里？</text><text x="48" y="68" class="sub">合同护栏覆盖率 · 同一份 synthetic closed-loop fixture · 不是模型准确率</text>
<circle cx="48" cy="{height - 28}" r="5" fill="#af52de"/><text x="60" y="{height - 23}" class="legend">不用 Skill</text><circle cx="170" cy="{height - 28}" r="5" fill="#34c759"/><text x="182" y="{height - 23}" class="legend">使用 Skill</text>{''.join(rows)}</svg>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json", dest="json_path", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--svg", type=Path, default=DEFAULT_SVG)
    args = parser.parse_args()

    result = build_comparison(load_json(args.input))
    for path in (args.json_path, args.html, args.svg):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.html.write_text(render_html(result), encoding="utf-8")
    args.svg.write_text(render_svg(result), encoding="utf-8")
    print(f"WROTE {args.json_path}")
    print(f"WROTE {args.html}")
    print(f"WROTE {args.svg}")
    print(f"GUARDRAIL SCORE: without_skill={result['modes']['without_skill']['guardrail_score']:.0%}; with_skill={result['modes']['with_skill']['guardrail_score']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
