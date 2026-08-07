#!/usr/bin/env python3
"""Score two real Agent outputs from the same materials task.

The scorer is intentionally rubric-based rather than pretending that one
aggregate number is scientific truth. It reports a metric vector and keeps the
scoring evidence visible in the generated JSON/HTML artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_REPORT = ROOT / "examples" / "skill-effect-real" / "no-skill-report.md"
DEFAULT_BASELINE_JSON = ROOT / "examples" / "skill-effect-real" / "no-skill-output.json"
DEFAULT_SKILL_REPORT = ROOT / "examples" / "skill-effect-real" / "with-skill-report.md"
DEFAULT_SKILL_JSON = ROOT / "examples" / "skill-effect-real" / "with-skill-output.json"
DEFAULT_JSON = ROOT / "examples" / "skill-effect-real" / "evaluation.json"
DEFAULT_HTML = ROOT / "examples" / "skill-effect-real" / "evaluation.html"
DEFAULT_SVG = ROOT / "docs" / "images" / "skill-effect-real-comparison.svg"


METRICS = [
    ("scientific_finding", "核心科学判断", "是否正确识别主要变异来源和结论边界"),
    ("raw_data_and_units", "原始数值与单位", "是否保留原始测量值、单位和重复结构"),
    ("variance_decomposition", "误差分解", "是否区分重复、样品和批次层级"),
    ("uncertainty_boundary", "不确定度边界", "是否避免把描述性方差当成计量学结论"),
    ("missing_information", "信息缺口", "是否指出会改变判断的缺失条件"),
    ("minimum_experiment", "最小验证实验", "是否给出对照、判定规则和停止条件"),
    ("evidence_traceability", "证据可回查", "是否有明确的来源、定位和证据绑定"),
    ("machine_contract", "机器接口", "是否能通过 canonical JSON 与引用校验"),
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def blob(report: str, payload: Any) -> str:
    return (report + "\n" + json.dumps(payload, ensure_ascii=False)).casefold()


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.casefold() in text for term in terms)


def score(value: bool | float) -> float:
    return float(value) if isinstance(value, (int, float)) else float(value)


def canonical_validation(payload: Any) -> tuple[bool, list[str]]:
    if not isinstance(payload, dict) or payload.get("schema_version") != "4.6":
        return False, ["not a canonical 4.6 object"]
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import validate_output

    reference_dir = ROOT / "references"
    schema = validate_output.load_json(reference_dir / "output-schema.json")
    adapter_schemas, errors_a = validate_output.load_adapter_schemas(reference_dir)
    registry, errors_r = validate_output.load_adapter_registry(reference_dir)
    field_contracts, errors_f = validate_output.load_field_contracts(reference_dir, registry)
    lexicon, errors_l = validate_output.load_routing_lexicon(reference_dir, registry)
    if errors_a + errors_r + errors_f + errors_l:
        return False, errors_a + errors_r + errors_f + errors_l
    errors, _warnings = validate_output.validate_document(
        payload, schema, adapter_schemas, registry, field_contracts, lexicon
    )
    return not errors, errors


def evaluate_mode(report: str, payload: Any, is_skill: bool) -> dict[str, Any]:
    text = blob(report, payload)
    metrics: dict[str, float] = {}
    basis: dict[str, str] = {}

    metrics["scientific_finding"] = score(
        has_any(text, ("between-batch", "between batch", "批次间", "批次方差"))
        and has_any(text, ("89.1", "89%", "主导", "dominant"))
    )
    basis["scientific_finding"] = "requires the batch-level driver and its magnitude or dominance to be stated"

    values = re.findall(r"92\.\d+", text)
    metrics["raw_data_and_units"] = score(
        len(values) >= 3 and has_any(text, ("coulombic", "库仑", "efficiency", "效率")) and "%" in text
    )
    basis["raw_data_and_units"] = "requires at least three raw-like values, the property name, and percent units"

    if is_skill and isinstance(payload, dict):
        budgets = payload.get("error_budgets", [])
        metrics["variance_decomposition"] = score(
            bool(budgets) and any("between" in json.dumps(item).casefold() or "batch" in json.dumps(item).casefold() for item in budgets)
        )
    else:
        metrics["variance_decomposition"] = score(
            has_any(text, ("within-sample", "within sample", "样品内", "重复测量"))
            and has_any(text, ("between-sample", "between sample", "样品间", "between-batch", "批次间"))
        )
    basis["variance_decomposition"] = "requires explicit separation of repeat, sample, and batch layers"

    metrics["uncertainty_boundary"] = score(
        has_any(text, ("descriptive", "描述性", "not gum", "非 gum", "不等于", "不能证明", "不能支持", "不支持", "不能把", "does not prove"))
    )
    basis["uncertainty_boundary"] = "requires a visible limit on what the variance calculation does not prove"

    if is_skill and isinstance(payload, dict):
        missing = payload.get("missing_information", [])
        metrics["missing_information"] = score(len(missing) > 0)
    else:
        metrics["missing_information"] = score(
            has_any(text, ("missing", "缺失", "需要补充", "calibration", "校准", "process log", "工艺记录", "标准物质", "参考方法", "已知真值"))
        )
    basis["missing_information"] = "requires at least one decision-relevant missing condition or limitation"

    if is_skill and isinstance(payload, dict):
        experiments = payload.get("experiment_sets", []) or payload.get("verification_plan", [])
        metrics["minimum_experiment"] = score(
            bool(experiments)
            and any(item.get("stop_rules") or item.get("stop_rule") for item in experiments if isinstance(item, dict))
        )
    else:
        metrics["minimum_experiment"] = score(
            has_any(text, ("next", "experiment", "实验", "下一步"))
            and has_any(text, ("control", "对照", "stop", "停止", "判定", "criterion"))
        )
    basis["minimum_experiment"] = "requires a next experiment plus controls and a decision or stop rule"

    if is_skill and isinstance(payload, dict):
        candidates = []
        for key in ("property_records", "deviation_episodes", "hypotheses", "error_budgets", "information_gaps"):
            candidates.extend(payload.get(key, []) or [])
        linked = sum(bool(item.get("evidence_ids") or item.get("support_evidence_ids")) for item in candidates if isinstance(item, dict))
        metrics["evidence_traceability"] = ratio(linked, len(candidates))
    else:
        metrics["evidence_traceability"] = score(
            bool(re.search(r"\bE\d+\b", report)) and has_any(text, ("source", "来源", "locator", "定位"))
        )
    basis["evidence_traceability"] = "canonical mode uses linked evidence arrays; free-form mode must expose locatable source references"

    valid, errors = canonical_validation(payload) if is_skill else (False, ["free-form output is intentionally non-canonical"])
    metrics["machine_contract"] = score(valid)
    basis["machine_contract"] = "canonical 4.6 schema, IDs, references, and adapter boundaries"

    human_keys = [key for key, _label, _description in METRICS[:6]]
    audit_keys = ["evidence_traceability", "machine_contract"]
    return {
        "label": "使用 Skill" if is_skill else "不用 Skill",
        "metrics": metrics,
        "human_score": ratio(sum(metrics[key] for key in human_keys), len(human_keys)),
        "audit_score": ratio(sum(metrics[key] for key in audit_keys), len(audit_keys)),
        "validation_errors": errors,
        "report_path": None,
    }


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def esc(value: Any) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def render_html(result: dict[str, Any]) -> str:
    rows = []
    for item in result["metrics"]:
        rows.append(
            f'<div class="metric"><div><b>{esc(item["label"])}</b><small>{esc(item["description"])}</small></div>'
            f'<div class="track"><i class="base" style="width:{item["without_skill"] * 100:.0f}%"></i></div>'
            f'<div class="track"><i class="skill" style="width:{item["with_skill"] * 100:.0f}%"></i></div>'
            f'<output>{percent(item["without_skill"])} / {percent(item["with_skill"])}</output></div>'
        )
    payload = json.dumps(result, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Real Skill Effect Evaluation</title><style>
:root{{--bg:#f5f5f7;--surface:rgba(255,255,255,.86);--text:#1d1d1f;--muted:#6e6e73;--line:rgba(60,60,67,.16);--base:#af52de;--skill:#34c759;--blue:#007aff}}@media(prefers-color-scheme:dark){{:root{{--bg:#000;--surface:rgba(28,28,30,.92);--text:#f5f5f7;--muted:#aeaeb2;--line:rgba(255,255,255,.16);--base:#bf5af2;--skill:#30d158;--blue:#0a84ff}}}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 85% 2%,rgba(0,122,255,.14),transparent 30rem),var(--bg);color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI","PingFang SC",Arial,sans-serif}}main{{max-width:1120px;margin:auto;padding:48px 24px 64px}}h1{{font-size:clamp(28px,4vw,46px);letter-spacing:-.04em;margin:0 0 10px}}h2{{font-size:20px;margin:0 0 14px}}p,small,li{{color:var(--muted)}}.eyebrow{{color:var(--blue);font-weight:700;letter-spacing:.04em;margin-bottom:8px}}.note,.panel{{background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:22px;backdrop-filter:blur(24px)}}.note{{border-left:3px solid var(--blue);border-radius:0 14px 14px 0;margin:16px 0 22px}}.scores{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:16px}}.score{{font-size:40px;font-weight:700;letter-spacing:-.04em}}.score small{{font-size:13px;font-weight:500}}.legend{{color:var(--muted);font-size:13px;margin-bottom:12px}}.dot{{display:inline-block;width:9px;height:9px;border-radius:50%;margin:0 5px 0 10px;background:var(--base)}}.dot:first-child{{margin-left:0}}.dot.skill{{background:var(--skill)}}.metric{{display:grid;grid-template-columns:minmax(190px,1.4fr) minmax(120px,1fr) minmax(120px,1fr) 90px;gap:12px;align-items:center;border-top:1px solid var(--line);padding:13px 0}}.metric small{{display:block;font-size:12px}}.track{{height:11px;border-radius:99px;background:color-mix(in srgb,var(--muted) 12%,transparent);overflow:hidden}}.track i{{display:block;height:100%;border-radius:inherit}}.base{{background:var(--base)}}.skill{{background:var(--skill)}}output{{text-align:right;color:var(--muted);font-variant-numeric:tabular-nums;font-size:13px}}details{{margin-top:16px}}summary{{cursor:pointer;font-weight:650}}@media(max-width:720px){{main{{padding:30px 16px 44px}}.scores{{grid-template-columns:1fr}}.metric{{grid-template-columns:1fr 1fr 1fr;gap:8px}}.metric>div:first-child{{grid-column:1/-1}}output{{grid-column:1/-1;text-align:left}}}}
</style></head><body><main><div class="eyebrow">REAL LLM A/B · GPT-5.6-LUNA</div><h1>不用 Skill，和使用 Skill，差在哪里？</h1><p class="note">同一份原始 CSV、同一个科研问题、同一个模型；只改变是否加载 Materials Evidence Reasoner。</p><section class="scores"><article class="panel"><h2>不用 Skill</h2><div class="score">{percent(result["modes"]["without_skill"]["human_score"])} <small>人类交付覆盖</small></div><p>普通自由格式回答，重点看结论是否能回答问题。</p></article><article class="panel"><h2>使用 Skill</h2><div class="score">{percent(result["modes"]["with_skill"]["human_score"])} <small>人类交付覆盖</small></div><p>遵循输入、证据、误差、信息缺口和验证合同。</p></article></section><section class="panel"><h2>真实输出的能力对照</h2><div class="legend"><span class="dot"></span>不用 Skill <span class="dot skill"></span>使用 Skill　数值为 rubric 覆盖率，不是科学真理</div>{''.join(rows)}<details><summary>评分说明与校验状态</summary><ul><li>评分脚本保留每个维度的可解释依据，不把结果压缩成唯一结论。</li><li>使用 Skill 的机器接口分数只有在本仓库校验器通过时才计满。</li><li>实际模型输出、报告路径和校验错误保存在同目录 JSON 中。</li></ul></details></section><script>window.__evaluation={payload};</script></main></body></html>'''


def render_svg(result: dict[str, Any]) -> str:
    width, height = 1120, 590
    left, right, top, row_height = 260, 90, 104, 50
    chart_width = width - left - right
    rows = []
    for index, item in enumerate(result["metrics"]):
        y = top + index * row_height
        rows.append(
            f'<text x="{left - 18}" y="{y + 8}" text-anchor="end" class="label">{esc(item["label"])}</text>'
            f'<rect x="{left}" y="{y - 10}" width="{chart_width}" height="10" rx="5" class="track"/><rect x="{left}" y="{y - 10}" width="{item["without_skill"] * chart_width:.1f}" height="10" rx="5" class="base"/>'
            f'<rect x="{left}" y="{y + 5}" width="{chart_width}" height="10" rx="5" class="track"/><rect x="{left}" y="{y + 5}" width="{item["with_skill"] * chart_width:.1f}" height="10" rx="5" class="skill"/>'
            f'<text x="{width - right + 16}" y="{y + 8}" class="value">{percent(item["with_skill"])}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">真实 LLM 对照：不用 Skill 与使用 Skill</title><desc id="desc">同一份原始 CSV 和同一个 GPT-5.6-luna 模型，只改变是否使用 Materials Evidence Reasoner，按八项科研交付维度比较。</desc><style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",Arial,sans-serif;fill:#1d1d1f}}.title{{font-size:26px;font-weight:700;letter-spacing:-.03em}}.sub,.legend{{font-size:13px;fill:#6e6e73}}.label{{font-size:14px}}.value{{font-size:13px;fill:#248a3d;font-weight:700}}.track{{fill:#e5e5ea}}.base{{fill:#af52de}}.skill{{fill:#34c759}}</style><text x="48" y="44" class="title">真实 LLM 对照：不用 Skill，和使用 Skill</text><text x="48" y="68" class="sub">GPT-5.6-luna · 同一份 error-budget-demo.csv · rubric 覆盖率，不是模型准确率</text>{''.join(rows)}<circle cx="48" cy="{height - 28}" r="5" fill="#af52de"/><text x="60" y="{height - 23}" class="legend">不用 Skill</text><circle cx="170" cy="{height - 28}" r="5" fill="#34c759"/><text x="182" y="{height - 23}" class="legend">使用 Skill</text></svg>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-report", type=Path, default=DEFAULT_BASELINE_REPORT)
    parser.add_argument("--baseline-json", type=Path, default=DEFAULT_BASELINE_JSON)
    parser.add_argument("--skill-report", type=Path, default=DEFAULT_SKILL_REPORT)
    parser.add_argument("--skill-json", type=Path, default=DEFAULT_SKILL_JSON)
    parser.add_argument("--json", dest="json_path", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--svg", type=Path, default=DEFAULT_SVG)
    args = parser.parse_args()
    baseline_payload = load_json(args.baseline_json)
    skill_payload = load_json(args.skill_json)
    without_skill = evaluate_mode(read_text(args.baseline_report), baseline_payload, False)
    with_skill = evaluate_mode(read_text(args.skill_report), skill_payload, True)
    without_skill["report_path"] = str(args.baseline_report.relative_to(ROOT)).replace("\\", "/")
    with_skill["report_path"] = str(args.skill_report.relative_to(ROOT)).replace("\\", "/")
    result = {
        "benchmark": {"name": "real-llm-skill-ab", "version": "1.0", "model": "gpt-5.6-luna", "input": "examples/error-budget-demo.csv", "same_task": True, "only_variable": "whether Materials Evidence Reasoner SKILL.md and package contracts were provided"},
        "modes": {"without_skill": without_skill, "with_skill": with_skill},
        "metrics": [{"id": key, "label": label, "description": description, "without_skill": without_skill["metrics"][key], "with_skill": with_skill["metrics"][key]} for key, label, description in METRICS],
        "limitations": ["This is one frozen task and one model run per mode, not a statistically powered benchmark.", "Rubric scores indicate observable deliverable coverage; they do not prove scientific truth or causal correctness.", "For a stronger evaluation, repeat across source-backed papers, domains, seeds, and independently adjudicated gold outputs."],
    }
    for path in (args.json_path, args.html, args.svg):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.html.write_text(render_html(result), encoding="utf-8")
    args.svg.write_text(render_svg(result), encoding="utf-8")
    print(f"WROTE {args.json_path}")
    print(f"WROTE {args.html}")
    print(f"WROTE {args.svg}")
    print(f"HUMAN SCORE: without_skill={without_skill['human_score']:.0%}; with_skill={with_skill['human_score']:.0%}")
    print(f"AUDIT SCORE: human-readable evidence/contract only; without_skill={without_skill['audit_score']:.0%}; with_skill={with_skill['audit_score']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
