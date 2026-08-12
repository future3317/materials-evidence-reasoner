#!/usr/bin/env python3
"""Render an action-first Markdown report from validated Materials Evidence JSON 4.6."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def array(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def safe(value: Any, fallback: str = "未提供") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return html.escape(str(value), quote=False)


def joined(value: Any, sep: str = "；", fallback: str = "无") -> str:
    items = [safe(item, "") for item in array(value) if item not in (None, "")]
    return sep.join(items) if items else fallback


def bullet(lines: list[str], text: str, indent: int = 0) -> None:
    lines.append(f"{'  ' * indent}- {text}")


def value_summary(value: Any) -> str:
    if not isinstance(value, dict):
        return safe(value)
    normalized = value.get("normalized_value", value.get("raw_value"))
    unit = value.get("normalized_unit", value.get("raw_unit", ""))
    return f"{safe(normalized)} {safe(unit, '')}".strip()


def render(document: dict[str, Any], json_name: str) -> str:
    lines: list[str] = ["# 材料实验推理报告", ""]
    decision = document.get("decision") or {}
    deviations = array(document.get("deviation_episodes"))
    first_deviation = deviations[0] if deviations else {}

    lines.extend([
        "## 一句话结论",
        "",
        safe(decision.get("summary"), "当前证据不足以形成结论。"),
        "",
        f"- 决策状态：`{safe(decision.get('status', '未评估'))}`",
        f"- 证据强度：`{safe(decision.get('evidence_strength', '未评估'))}`",
        f"- 可比性/偏差状态：`{safe(first_deviation.get('classification', '未形成偏差事件'))}`",
        "",
        "## 现在该做什么",
        "",
    ])

    plans = array(document.get("verification_plan"))[:3]
    if not plans:
        lines.append("当前没有可执行的验证项；先补充阻塞信息或完成数据质量/误差审查。")
    else:
        for index, item in enumerate(plans, start=1):
            action = item.get("action") or item.get("minimal_change") or item.get("id")
            lines.append(f"{index}. **{safe(action)}**")
            bullet(lines, f"优先级：`{safe(item.get('priority_tier', '未评估'))}`；理由：{safe(item.get('priority_rationale'))}", 1)
            bullet(lines, f"关闭信息缺口：{joined(item.get('information_gap_ids'), ', ')}", 1)
            gain = item.get("information_gain") or {}
            if gain:
                bullet(lines, f"预期决策变化：{safe(gain.get('decision_change'))}", 1)
            bullet(lines, f"判定规则：{safe(item.get('decision_rule'))}", 1)
            bullet(lines, f"停止规则：{safe(item.get('stop_rule'))}", 1)
            if item.get("safety"):
                bullet(lines, f"安全：{safe(item['safety'])}", 1)

    lines.extend(["", "## 输入完整度与缺失信息", ""])
    assessment = document.get("input_assessment") or {}
    lines.append(f"输入状态：`{safe(assessment.get('readiness', '未评估'))}`；已规范化对象数：{safe(assessment.get('normalized_item_count', 0))}。")
    for key, title in (("blockers", "必须补充"), ("analysis_limitations", "会限制结论"), ("optional_enrichment", "可选增强")):
        lines.extend(["", f"### {title}", ""])
        items = array(assessment.get(key))
        if not items:
            lines.append("无。")
        for item in items:
            bullet(lines, f"**{safe(item.get('field', '字段'))}**：{safe(item.get('reason'))} 影响：{safe(item.get('impact'))} 最小补充：{safe(item.get('suggested_input'))}")

    conditions = array(document.get("condition_registry"))
    lines.extend(["", "## 条件对照表", ""])
    if not conditions:
        lines.append("未建立条件别名。")
    else:
        lines.extend(["| 条件 | 说明 | 完整签名 | 缺失条件 |", "|---|---|---|---|"])
        for item in conditions:
            signature = safe(json.dumps(item.get("condition_signature", {}), ensure_ascii=False, sort_keys=True)).replace("|", "\\|")
            missing = joined(item.get("missing_conditions"))
            lines.append(f"| [{safe(item.get('alias', item.get('id')))}] | {safe(item.get('label', ''))} | `{signature}` | {missing} |")

    lines.extend(["", "## 基准、可比性与偏差", ""])
    baselines = array(document.get("baseline_packages"))
    if not baselines:
        lines.append("未建立基准包。")
    for item in baselines:
        bullet(lines, f"`{safe(item.get('baseline_kind'))}` / `{safe(item.get('status'))}`：{safe(item.get('property_canonical'))}；适用范围：{safe(item.get('applicability'))}；统计/趋势：{safe(item.get('statistics'))}；限制：{joined(item.get('limitations'))}")
    for item in array(document.get("comparability_assessments")):
        issue_text = "；".join(safe(issue.get("description", "")) for issue in array(item.get("issues"))) or "未登记差异项"
        bullet(lines, f"可比性 `{safe(item.get('result'))}`：{issue_text}")
    for item in deviations:
        residual_text = "因不可比而不计算" if item.get("classification") == "not-comparable" else value_summary(item.get("residual"))
        bullet(lines, f"偏差 `{safe(item.get('classification'))}`；方法：{safe(item.get('method'))}；残差：{residual_text}；工程意义：{safe(item.get('engineering_meaning'))}")

    lines.extend(["", "## 误差预算", ""])
    budgets = array(document.get("error_budgets"))
    if not budgets:
        lines.append("未建立误差预算；这通常意味着重复结构或误差来源不足以审计。")
    for budget in budgets:
        lines.append(f"### {safe(budget.get('id'))}：{safe(budget.get('method'))}")
        lines.append("")
        bullet(lines, f"结论：{safe(budget.get('conclusion'))}")
        comparison = budget.get("effect_comparison") or {}
        bullet(lines, f"效应与不确定度：`{safe(comparison.get('relation'))}`；{safe(comparison.get('rationale'))}")
        bullet(lines, f"主导来源：{joined(budget.get('dominant_component_ids'), ', ')}")
        components = array(budget.get("components"))
        if components:
            lines.extend(["", "| 分量 | 类别 | 估计状态 | 贡献基础 | 贡献比例 | 限制 |", "|---|---|---|---|---:|---|"])
            for comp in components:
                fraction = comp.get("fraction_of_total")
                fraction_text = f"{fraction:.1%}" if isinstance(fraction, (int, float)) else "未量化"
                lines.append(f"| {safe(comp.get('label'))} | `{safe(comp.get('category'))}` | `{safe(comp.get('estimate_status'))}` | `{safe(comp.get('contribution_basis'))}` | {fraction_text} | {joined(comp.get('limitations'))} |")
        if budget.get("limitations"):
            bullet(lines, f"局限：{joined(budget.get('limitations'))}")
        lines.append("")

    lines.extend(["## 异常传播链", ""])
    chains = array(document.get("anomaly_propagation_chains"))
    if not chains:
        lines.append("没有建立材料异常传播链。")
    for index, chain in enumerate(chains, start=1):
        lines.append(f"### {index}. {safe(chain.get('title', chain.get('id')))}")
        lines.append("")
        node_by_id = {node.get("node_id"): node for node in array(chain.get("nodes")) if isinstance(node, dict)}
        ordered_nodes: list[str] = []
        edges = array(chain.get("edges"))
        if edges:
            ordered_nodes.append(edges[0].get("from_node_id"))
            ordered_nodes.extend(edge.get("to_node_id") for edge in edges)
        if ordered_nodes:
            chain_text = " → ".join(
                f"{safe(node_by_id.get(node_id, {}).get('statement', node_id))} [{safe(node_by_id.get(node_id, {}).get('status', ''))}]"
                for node_id in ordered_nodes
            )
            bullet(lines, f"传播路径：{chain_text}")
        bullet(lines, f"状态：`{safe(chain.get('status'))}`；排序理由：{safe((chain.get('ranking_basis') or {}).get('rationale'))}")
        bullet(lines, f"未解决节点：{joined(chain.get('unresolved_node_ids'), ', ')}")
        bullet(lines, f"证据缺口：{joined(chain.get('chain_evidence_gaps'))}")
        for edge in edges:
            bullet(lines, f"{safe(edge.get('from_node_id'))} → {safe(edge.get('to_node_id'))}：{safe(edge.get('mechanism'))}（证据 `{safe(edge.get('evidence_strength'))}`；falsifier：{joined(edge.get('falsifiers'))}）")
        lines.append("")

    lines.extend(["## 证据约束机理图谱", ""])
    mechanism_graphs = array(document.get("mechanism_graphs"))
    mechanism_nodes = {
        item.get("id"): item
        for item in array(document.get("mechanism_nodes"))
        if isinstance(item, dict)
    }
    mechanism_edges = {
        item.get("id"): item
        for item in array(document.get("mechanism_edges"))
        if isinstance(item, dict)
    }
    if not mechanism_graphs:
        lines.append("没有建立跨实验可复用的证据约束机理图谱；当前机理仅限本次运行。")
    for graph in mechanism_graphs:
        lines.append(f"### {safe(graph.get('id'))}：{safe(graph.get('title'))}")
        lines.append("")
        bullet(lines, f"材料体系：{safe(graph.get('material_system'))}；版本：`{safe(graph.get('version'))}`；状态：`{safe(graph.get('status'))}`")
        bullet(lines, f"适用条件：{joined(graph.get('condition_ids'), ', ')}；边界：{joined(graph.get('boundary_conditions'))}")
        bullet(lines, f"来源类型：{joined(graph.get('source_kinds'), ', ')}；更新提案：{joined(graph.get('update_ids'), ', ')}")
        for edge_id in array(graph.get("edge_ids")):
            edge = mechanism_edges.get(edge_id, {})
            source = mechanism_nodes.get(edge.get("from_node_id"), {})
            target = mechanism_nodes.get(edge.get("to_node_id"), {})
            transfer = edge.get("transferability") or {}
            bullet(
                lines,
                f"{safe(source.get('canonical_term', edge.get('from_node_id')))} → "
                f"{safe(target.get('canonical_term', edge.get('to_node_id')))}："
                f"{safe(edge.get('mechanism_description'))} "
                f"（`{safe(edge.get('validation_status'))}`；证据 {joined(edge.get('support_evidence_ids'), ', ')}；"
                f"迁移 `{safe(transfer.get('level'))}`；falsifier：{joined(edge.get('falsifiers'))}）",
            )
        if graph.get("limitations"):
            bullet(lines, f"局限：{joined(graph.get('limitations'))}")
        lines.append("")

    lines.extend(["## 机理假设排序", ""])
    hypotheses = array(document.get("hypotheses"))
    if not hypotheses:
        lines.append("没有形成可证伪的机理假设。")
    for index, item in enumerate(hypotheses, start=1):
        lines.append(f"### {index}. {safe(item.get('statement', item.get('id', '假设')))}")
        lines.append("")
        bullet(lines, f"状态：`{safe(item.get('status', '未评估'))}`")
        bullet(lines, f"传播链：{joined(item.get('anomaly_propagation_chain_ids'), ', ')}")
        bullet(lines, f"机理图谱匹配：`{safe(item.get('mechanism_match_status', '未检索'))}`；边：{joined(item.get('linked_mechanism_edge_ids'), ', ')}")
        bullet(lines, f"迁移边界：{safe(item.get('mechanism_transferability'))}；检索说明：{joined(item.get('graph_retrieval_notes'))}")
        bullet(lines, f"支持证据：{joined(item.get('support_evidence_ids'), ', ', '无直接证据')}")
        bullet(lines, f"反证：{joined(item.get('counterevidence_ids'), ', ', '未提供')}")
        bullet(lines, f"独有预测：{joined(item.get('unique_predictions'))}")
        bullet(lines, f"反证条件：{joined(item.get('falsifiers'))}")
        bullet(lines, f"适用边界：{safe(item.get('applicability'))}")
        lines.append("")

    lines.extend(["## 信息缺口", ""])
    gaps = array(document.get("information_gaps"))
    if not gaps:
        lines.append("没有登记信息缺口；这不等于当前证据已经充分。")
    else:
        lines.extend(["| ID | 未知量 | 层级 | 影响 | 当前状态 | 最小测量 | 决策用途 | 处置 |", "|---|---|---|---|---|---|---|---|"])
        for gap in gaps:
            measurement = gap.get("minimal_measurement") or {}
            lines.append(f"| {safe(gap.get('id'))} | {safe(gap.get('unknown_variable'))} | `{safe(gap.get('stage'))}` | `{safe(gap.get('impact'))}` | `{safe(gap.get('current_state'))}` | {safe(measurement.get('candidate_method'))} | {safe(measurement.get('decision_use'))} | `{safe(gap.get('disposition'))}` |")

    lines.extend(["", "## 最小实验集与验证方案", ""])
    for exp_set in array(document.get("experiment_sets")):
        lines.append(f"### {safe(exp_set.get('id'))}：{safe(exp_set.get('objective'))}")
        lines.append("")
        bullet(lines, f"选择理由：{safe(exp_set.get('selection_rationale'))}")
        bullet(lines, f"覆盖 gap：{joined(exp_set.get('information_gap_ids'), ', ')}；实验：{joined(exp_set.get('verification_item_ids'), ', ')}")
        bullet(lines, f"资源：{safe(exp_set.get('resource_summary'))}")
        bullet(lines, f"停止规则：{joined(exp_set.get('stop_rules'))}")
        lines.append("")
    if not plans:
        lines.append("无验证方案。")
    for item in array(document.get("verification_plan")):
        lines.append(f"### {safe(item.get('id', '验证项'))}：{safe(item.get('action'))}")
        lines.append("")
        bullet(lines, f"区分假设：{joined(item.get('hypothesis_ids'), ', ')}；关闭 gap：{joined(item.get('information_gap_ids'), ', ')}")
        bullet(lines, f"最小变化：{safe(item.get('minimal_change'))}")
        bullet(lines, f"对照：{joined(item.get('controls'))}")
        bullet(lines, f"重复数：{safe(item.get('repeats'))}")
        bullet(lines, f"预期：{joined(item.get('expected_outcomes'))}")
        bullet(lines, f"判定规则：{safe(item.get('decision_rule'))}")
        bullet(lines, f"停止规则：{safe(item.get('stop_rule'))}")
        bullet(lines, f"可执行性：`{safe(item.get('feasibility'))}`；成本档：`{safe(item.get('cost_band'))}`；样品消耗：{safe(item.get('sample_consumption'))}")
        bullet(lines, f"风险：{safe(item.get('risk'))}；安全：{safe(item.get('safety'))}")
        lines.append("")

    lines.extend(["## PSPP 经验图与更新", ""])
    maps = array(document.get("pspp_maps"))
    if not maps:
        lines.append("没有形成可复用 PSPP 图。")
    for pspp in maps:
        lines.append(f"### {safe(pspp.get('id'))}：{safe(pspp.get('title'))}")
        lines.append("")
        nodes = {node.get("node_id"): node for node in array(pspp.get("nodes")) if isinstance(node, dict)}
        bullet(lines, f"状态：`{safe(pspp.get('status'))}`；覆盖：{safe(pspp.get('coverage'))}")
        for rel in array(pspp.get("relationships")):
            source = nodes.get(rel.get("from_node_id"), {})
            target = nodes.get(rel.get("to_node_id"), {})
            bullet(lines, f"{safe(source.get('stage', rel.get('from_node_id')))} → {safe(target.get('stage', rel.get('to_node_id')))}：{safe(rel.get('statement'))}（`{safe(rel.get('relation_status'))}`；falsifier：{joined(rel.get('falsifiers'))}）")
        bullet(lines, f"缺失层：{joined(pspp.get('missing_stages'))}；局限：{joined(pspp.get('limitations'))}")
        lines.append("")

    updates = array(document.get("experience_updates"))
    if not updates:
        lines.append("没有经验更新提案。")
    for item in updates:
        bullet(lines, f"`{safe(item.get('persistence_status'))}`：{joined(item.get('facts'))}；PSPP：{joined(item.get('pspp_map_ids'), ', ')}；机理图谱更新：{joined(item.get('mechanism_update_ids'), ', ')}；边界：{safe(item.get('applicability'))}；复核触发：{safe(item.get('review_trigger'))}")
        if item.get("graph_operation_summary"):
            bullet(lines, f"图谱操作说明：{safe(item.get('graph_operation_summary'))}", 1)
    for item in array(decision.get("limitations")):
        bullet(lines, safe(item))

    lines.extend(["", "## 交付与审计", "", f"- 机器记录：`{safe(json_name)}`", f"- Schema：`{safe(document.get('schema_version', '未知'))}`", f"- JSON 验证：`{safe((document.get('quality') or {}).get('json_valid', '未提供'))}`"])
    for item in array(document.get("artifact_manifest")):
        bullet(lines, f"{safe(item.get('artifact_type'))}: `{safe(item.get('path'))}`（{safe(item.get('validation_status'))}）")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("materials-report.md"))
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR cannot read JSON: {exc}", file=sys.stderr)
        return 2
    if not args.skip_validation:
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_output.py"), str(args.input)], cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(document, args.input.name), encoding="utf-8")
    print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
