#!/usr/bin/env python3
"""Audit mechanism graph structure, traceability, boundaries, and update governance.

Coverage percentages describe contract completeness only. They are not scientific
confidence scores and must not be used to rank mechanisms by truth.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_output.py"


def load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR cannot read JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("ERROR top-level JSON must be an object")
    return data


def validate(path: Path) -> None:
    result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit((result.stdout + "\n" + result.stderr).strip())


def arr(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def audit(document: dict[str, Any]) -> dict[str, Any]:
    graphs = {item.get("id"): item for item in arr(document.get("mechanism_graphs")) if isinstance(item, dict)}
    nodes = {item.get("id"): item for item in arr(document.get("mechanism_nodes")) if isinstance(item, dict)}
    edges = {item.get("id"): item for item in arr(document.get("mechanism_edges")) if isinstance(item, dict)}
    updates = {item.get("id"): item for item in arr(document.get("mechanism_updates")) if isinstance(item, dict)}
    hypotheses = arr(document.get("hypotheses"))
    evidence = {item.get("id"): item for item in arr(document.get("evidence")) if isinstance(item, dict)}

    linked_node_ids = {nid for graph in graphs.values() for nid in arr(graph.get("node_ids"))}
    edge_endpoint_ids = {nid for edge in edges.values() for nid in (edge.get("from_node_id"), edge.get("to_node_id")) if nid}
    orphan_nodes = sorted(set(nodes) - edge_endpoint_ids)
    nodes_not_in_graph = sorted(set(nodes) - linked_node_ids)
    edges_not_in_graph = sorted(set(edges) - {eid for graph in graphs.values() for eid in arr(graph.get("edge_ids"))})

    traceable = sum(bool(edge.get("support_evidence_ids")) for edge in edges.values())
    bounded = sum(bool(edge.get("boundary_conditions")) for edge in edges.values())
    falsifiable = sum(bool(edge.get("falsifiers")) for edge in edges.values())
    transfer_assessed = sum((edge.get("transferability") or {}).get("level") not in {None, "not-assessed"} for edge in edges.values())
    validated_with_evidence = sum(
        edge.get("validation_status") != "locally-validated" or bool(edge.get("validation_evidence_ids"))
        for edge in edges.values()
    )
    conflict_disclosed = sum(
        edge.get("validation_status") not in {"contradicted", "deprecated", "conflicting"}
        or bool(edge.get("conflict_evidence_ids") or edge.get("supersedes_edge_id"))
        for edge in edges.values()
    )
    unknown_evidence = sorted(
        {
            eid
            for edge in edges.values()
            for key in ("support_evidence_ids", "conflict_evidence_ids", "validation_evidence_ids")
            for eid in arr(edge.get(key))
            if eid not in evidence
        }
    )
    unlinked_hypotheses = sorted(
        item.get("id")
        for item in hypotheses
        if isinstance(item, dict)
        and item.get("mechanism_match_status") not in {None, "no-match"}
        and not item.get("linked_mechanism_edge_ids")
    )
    approved_not_applied = sorted(
        uid for uid, item in updates.items() if item.get("status") == "approved" and item.get("persistence_status") == "proposed-not-written"
    )
    applied_without_confirmed_write = sorted(
        uid
        for uid, item in updates.items()
        if item.get("status") == "applied"
        and item.get("persistence_status") not in {"artifact-written", "external-written-confirmed"}
    )

    findings: list[dict[str, Any]] = []
    def add(severity: str, code: str, message: str, ids: list[str] | None = None) -> None:
        findings.append({"severity": severity, "code": code, "message": message, "ids": ids or []})

    if nodes_not_in_graph:
        add("error", "MG-ORPHAN-GRAPH", "Mechanism nodes are not listed by any graph.", nodes_not_in_graph)
    if edges_not_in_graph:
        add("error", "MG-ORPHAN-EDGE", "Mechanism edges are not listed by any graph.", edges_not_in_graph)
    if unknown_evidence:
        add("error", "MG-EVIDENCE-BROKEN", "Mechanism edges reference unknown evidence IDs.", unknown_evidence)
    if unlinked_hypotheses:
        add("error", "MG-HYPOTHESIS-DISCONNECT", "Hypotheses claim a graph match without linked edges.", unlinked_hypotheses)
    if applied_without_confirmed_write:
        add("error", "MG-UPDATE-WRITE", "Applied updates lack confirmed artifact/external persistence.", applied_without_confirmed_write)
    if orphan_nodes:
        add("warning", "MG-ISOLATED-NODE", "Nodes are present but unused by any edge; confirm whether they are staged or obsolete.", orphan_nodes)
    if approved_not_applied:
        add("warning", "MG-UPDATE-PENDING", "Approved updates have not been applied to an artifact.", approved_not_applied)
    cross_transfer = sorted(
        edge_id
        for edge_id, edge in edges.items()
        if (edge.get("transferability") or {}).get("level") == "cross-material-proposed"
    )
    if cross_transfer:
        add("warning", "MG-CROSS-MATERIAL", "Cross-material analogies require explicit matching before reuse.", cross_transfer)

    return {
        "audit_type": "mechanism-graph-contract-audit",
        "source_run_id": document.get("run_id"),
        "schema_version": document.get("schema_version"),
        "counts": {
            "graphs": len(graphs),
            "nodes": len(nodes),
            "edges": len(edges),
            "updates": len(updates),
        },
        "structural_coverage": {
            "traceable_edge_fraction": ratio(traceable, len(edges)),
            "boundary_fraction": ratio(bounded, len(edges)),
            "falsifier_fraction": ratio(falsifiable, len(edges)),
            "transferability_assessed_fraction": ratio(transfer_assessed, len(edges)),
            "validation_evidence_consistency_fraction": ratio(validated_with_evidence, len(edges)),
            "conflict_disclosure_fraction": ratio(conflict_disclosed, len(edges)),
            "note": "These are contract-completeness metrics, not scientific confidence scores.",
        },
        "edge_status_counts": dict(Counter(edge.get("validation_status", "unknown") for edge in edges.values())),
        "source_kind_counts": dict(Counter(edge.get("source_kind", "unknown") for edge in edges.values())),
        "transferability_counts": dict(Counter((edge.get("transferability") or {}).get("level", "unknown") for edge in edges.values())),
        "findings": findings,
        "pass": not any(item["severity"] == "error" for item in findings),
    }


def render_markdown(result: dict[str, Any]) -> str:
    counts = result["counts"]
    coverage = result["structural_coverage"]
    lines = [
        "# Mechanism Graph Audit",
        "",
        f"- Run: `{result.get('source_run_id')}`",
        f"- Schema: `{result.get('schema_version')}`",
        f"- Result: **{'PASS' if result.get('pass') else 'FAIL'}**",
        f"- Graphs / nodes / edges / updates: {counts['graphs']} / {counts['nodes']} / {counts['edges']} / {counts['updates']}",
        "",
        "## Contract completeness",
        "",
        "| Metric | Coverage |",
        "|---|---:|",
    ]
    for key, label in (
        ("traceable_edge_fraction", "Edges with supporting evidence"),
        ("boundary_fraction", "Edges with explicit boundaries"),
        ("falsifier_fraction", "Edges with falsifiers"),
        ("transferability_assessed_fraction", "Edges with transfer assessment"),
        ("validation_evidence_consistency_fraction", "Validation status consistent with evidence"),
        ("conflict_disclosure_fraction", "Contradiction/deprecation disclosed"),
    ):
        value = coverage.get(key)
        text = "n/a" if value is None else f"{value:.1%}"
        lines.append(f"| {label} | {text} |")
    lines.extend(["", f"> {coverage['note']}", "", "## Findings", ""])
    if not result["findings"]:
        lines.append("No structural findings.")
    for item in result["findings"]:
        ids = f" ({', '.join(item['ids'])})" if item.get("ids") else ""
        lines.append(f"- **{item['severity'].upper()} `{item['code']}`**: {item['message']}{ids}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("mechanism-audit.json"))
    parser.add_argument("--report", type=Path)
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()
    if not args.skip_validation:
        validate(args.input)
    result = audit(load(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_markdown(result), encoding="utf-8")
    print(f"WROTE {args.output}; pass={result['pass']}; findings={len(result['findings'])}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
