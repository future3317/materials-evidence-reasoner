#!/usr/bin/env python3
"""Inspect, query, export, diff, index, and apply approved mechanism graph updates.

The tool is deliberately conservative: it never infers semantic equivalence, never
merges similarly worded nodes, and never upgrades an evidence status without an
explicit approved mechanism_update object.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_output.py"


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("ERROR top-level JSON must be an object")
    return data


def validate(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        message = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
        raise SystemExit(f"ERROR input failed validation:\n{message}")


def array(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def text_tokens(value: Any) -> set[str]:
    text = stable_json(value).lower()
    latin = re.findall(r"[a-z0-9][a-z0-9_.+/-]*", text)
    cjk_runs = re.findall(r"[\u3400-\u9fff]+", text)
    cjk: list[str] = []
    for run in cjk_runs:
        cjk.append(run)
        if len(run) > 1:
            cjk.extend(run[i : i + 2] for i in range(len(run) - 1))
    return set(latin + cjk)


def indexes(document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    graphs = {item["id"]: item for item in array(document.get("mechanism_graphs")) if isinstance(item, dict) and item.get("id")}
    nodes = {item["id"]: item for item in array(document.get("mechanism_nodes")) if isinstance(item, dict) and item.get("id")}
    edges = {item["id"]: item for item in array(document.get("mechanism_edges")) if isinstance(item, dict) and item.get("id")}
    updates = {item["id"]: item for item in array(document.get("mechanism_updates")) if isinstance(item, dict) and item.get("id")}
    return graphs, nodes, edges, updates


def graph_summary(document: dict[str, Any]) -> dict[str, Any]:
    graphs, nodes, edges, updates = indexes(document)
    status_counts = Counter(edge.get("validation_status", "unknown") for edge in edges.values())
    type_counts = Counter(node.get("node_type", "unknown") for node in nodes.values())
    graph_rows = []
    for graph_id, graph in sorted(graphs.items()):
        graph_edges = [edges[eid] for eid in graph.get("edge_ids", []) if eid in edges]
        graph_nodes = [nodes[nid] for nid in graph.get("node_ids", []) if nid in nodes]
        graph_rows.append(
            {
                "id": graph_id,
                "title": graph.get("title"),
                "material_system": graph.get("material_system"),
                "version": graph.get("version"),
                "status": graph.get("status"),
                "node_count": len(graph_nodes),
                "edge_count": len(graph_edges),
                "evidence_count": len(set(graph.get("evidence_ids", []))),
                "edge_statuses": dict(Counter(item.get("validation_status", "unknown") for item in graph_edges)),
                "boundary_count": len(graph.get("boundary_conditions", [])),
                "pending_update_count": sum(1 for uid in graph.get("update_ids", []) if updates.get(uid, {}).get("status") != "applied"),
            }
        )
    return {
        "schema_version": document.get("schema_version"),
        "run_id": document.get("run_id"),
        "graph_count": len(graphs),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "update_count": len(updates),
        "edge_status_counts": dict(status_counts),
        "node_type_counts": dict(type_counts),
        "graphs": graph_rows,
    }


def print_summary(summary: dict[str, Any]) -> None:
    print(f"Run: {summary.get('run_id')} | Schema: {summary.get('schema_version')}")
    print(
        f"Graphs: {summary['graph_count']} | Nodes: {summary['node_count']} | "
        f"Edges: {summary['edge_count']} | Updates: {summary['update_count']}"
    )
    print("Edge status:", ", ".join(f"{k}={v}" for k, v in sorted(summary["edge_status_counts"].items())) or "none")
    for graph in summary["graphs"]:
        print(
            f"- {graph['id']} v{graph.get('version')}: {graph.get('title')} "
            f"[{graph.get('status')}] {graph['node_count']} nodes / {graph['edge_count']} edges / "
            f"{graph['pending_update_count']} pending updates"
        )


def cmd_summary(args: argparse.Namespace) -> int:
    if not args.skip_validation:
        validate(args.input)
    summary = graph_summary(load_json(args.input))
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_summary(summary)
    return 0


def query_matches(item: dict[str, Any], terms: set[str]) -> bool:
    return not terms or terms <= text_tokens(item) or bool(terms & text_tokens(item))


def cmd_query(args: argparse.Namespace) -> int:
    if not args.skip_validation:
        validate(args.input)
    document = load_json(args.input)
    graphs, nodes, edges, _ = indexes(document)
    terms = text_tokens(args.text) if args.text else set()
    graph_ids = {
        gid
        for gid, graph in graphs.items()
        if (not args.material_system or args.material_system.lower() in str(graph.get("material_system", "")).lower())
        and query_matches(graph, terms)
    }
    matched_nodes = []
    for item in nodes.values():
        if graph_ids and not (set(item.get("graph_ids", [])) & graph_ids):
            continue
        if args.node_type and item.get("node_type") != args.node_type:
            continue
        if args.status and item.get("status") != args.status:
            continue
        if query_matches(item, terms):
            matched_nodes.append(item)
    matched_edges = []
    for item in edges.values():
        if graph_ids and item.get("graph_id") not in graph_ids:
            continue
        if args.status and item.get("validation_status") != args.status:
            continue
        if query_matches(item, terms):
            matched_edges.append(item)
    result = {
        "query": {
            "text": args.text,
            "material_system": args.material_system,
            "node_type": args.node_type,
            "status": args.status,
        },
        "graphs": [graphs[gid] for gid in sorted(graph_ids)],
        "nodes": sorted(matched_nodes, key=lambda x: x.get("id", "")),
        "edges": sorted(matched_edges, key=lambda x: x.get("id", "")),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Matched {len(result['graphs'])} graphs, {len(result['nodes'])} nodes, {len(result['edges'])} edges")
        for edge in result["edges"]:
            print(
                f"- {edge['id']} [{edge.get('validation_status')}] "
                f"{edge.get('from_node_id')} -> {edge.get('to_node_id')}: {edge.get('mechanism_description')}"
            )
    return 0


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            flat = {}
            for field in fields:
                value = row.get(field)
                flat[field] = stable_json(value) if isinstance(value, (dict, list)) else value
            writer.writerow(flat)


def dot_escape(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def build_dot(document: dict[str, Any], graph_filter: set[str] | None = None) -> str:
    graphs, nodes, edges, _ = indexes(document)
    lines = ["digraph MechanismGraph {", "  rankdir=LR;", '  graph [fontname="Helvetica", bgcolor="transparent"];', '  node [shape=box, style="rounded,filled", fontname="Helvetica", fillcolor="#f5f5f7", color="#c7c7cc"];', '  edge [fontname="Helvetica", color="#6e6e73"];']
    for graph_id, graph in sorted(graphs.items()):
        if graph_filter and graph_id not in graph_filter:
            continue
        lines.append(f'  subgraph "cluster_{dot_escape(graph_id)}" {{')
        lines.append(f'    label="{dot_escape(graph.get("title", graph_id))}";')
        for node_id in graph.get("node_ids", []):
            node = nodes.get(node_id)
            if not node:
                continue
            label = f"{node_id}\\n{node.get('canonical_term') or node.get('statement')}\\n[{node.get('status')}]"
            lines.append(f'    "{dot_escape(node_id)}" [label="{dot_escape(label)}"];')
        for edge_id in graph.get("edge_ids", []):
            edge = edges.get(edge_id)
            if not edge:
                continue
            label = f"{edge_id}: {edge.get('relation_type')} [{edge.get('validation_status')}]"
            style = "dashed" if edge.get("validation_status") == "hypothesis" else "solid"
            lines.append(
                f'    "{dot_escape(edge.get("from_node_id"))}" -> "{dot_escape(edge.get("to_node_id"))}" '
                f'[label="{dot_escape(label)}", style="{style}"];'
            )
        lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def cmd_export(args: argparse.Namespace) -> int:
    if not args.skip_validation:
        validate(args.input)
    document = load_json(args.input)
    graphs, nodes, edges, updates = indexes(document)
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    graph_filter = set(args.graph_id or []) or None
    selected_graphs = [g for gid, g in sorted(graphs.items()) if not graph_filter or gid in graph_filter]
    selected_node_ids = {nid for graph in selected_graphs for nid in graph.get("node_ids", [])}
    selected_edge_ids = {eid for graph in selected_graphs for eid in graph.get("edge_ids", [])}
    selected_nodes = [nodes[nid] for nid in sorted(selected_node_ids) if nid in nodes]
    selected_edges = [edges[eid] for eid in sorted(selected_edge_ids) if eid in edges]
    selected_update_ids = {uid for graph in selected_graphs for uid in graph.get("update_ids", [])}
    selected_updates = [updates[uid] for uid in sorted(selected_update_ids) if uid in updates]
    bundle = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_run_id": document.get("run_id"),
        "source_sha256": sha256_json(document),
        "mechanism_graphs": selected_graphs,
        "mechanism_nodes": selected_nodes,
        "mechanism_edges": selected_edges,
        "mechanism_updates": selected_updates,
    }
    (output / "mechanism-graph.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(output / "mechanism-nodes.csv", selected_nodes, ["id", "graph_ids", "node_type", "canonical_term", "statement", "status", "entity_ids", "condition_ids", "evidence_ids", "boundary_conditions", "limitations"])
    write_csv(output / "mechanism-edges.csv", selected_edges, ["id", "graph_id", "from_node_id", "to_node_id", "relation_type", "mechanism_description", "validation_status", "source_kind", "support_evidence_ids", "conflict_evidence_ids", "validation_evidence_ids", "condition_ids", "boundary_conditions", "transferability", "version", "limitations"])
    (output / "mechanism-graph.dot").write_text(build_dot(document, graph_filter), encoding="utf-8")
    print(f"WROTE {output} ({len(selected_graphs)} graphs, {len(selected_nodes)} nodes, {len(selected_edges)} edges)")
    return 0


def keyed(items: list[Any]) -> dict[str, Any]:
    return {item["id"]: item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)}


def diff_collection(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = []
    for item_id in sorted(set(old) & set(new)):
        if stable_json(old[item_id]) != stable_json(new[item_id]):
            changed.append(
                {
                    "id": item_id,
                    "before_sha256": sha256_json(old[item_id]),
                    "after_sha256": sha256_json(new[item_id]),
                    "before": old[item_id],
                    "after": new[item_id],
                }
            )
    return {"added": added, "removed": removed, "changed": changed}


def cmd_diff(args: argparse.Namespace) -> int:
    if not args.skip_validation:
        validate(args.old)
        validate(args.new)
    old = load_json(args.old)
    new = load_json(args.new)
    result = {
        "old_run_id": old.get("run_id"),
        "new_run_id": new.get("run_id"),
        "graphs": diff_collection(keyed(array(old.get("mechanism_graphs"))), keyed(array(new.get("mechanism_graphs")))),
        "nodes": diff_collection(keyed(array(old.get("mechanism_nodes"))), keyed(array(new.get("mechanism_nodes")))),
        "edges": diff_collection(keyed(array(old.get("mechanism_edges"))), keyed(array(new.get("mechanism_edges")))),
        "updates": diff_collection(keyed(array(old.get("mechanism_updates"))), keyed(array(new.get("mechanism_updates")))),
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"WROTE {args.output}")
    else:
        print(text, end="")
    return 0


def append_unique(target: list[Any], values: Iterable[Any]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def apply_update(document: dict[str, Any], update: dict[str, Any]) -> None:
    graphs, nodes, edges, _ = indexes(document)
    graph = graphs[update["target_graph_id"]]
    operation = update["operation"]
    if operation == "append-node":
        append_unique(graph["node_ids"], update.get("new_node_ids", []))
    elif operation == "append-edge":
        append_unique(graph["edge_ids"], update.get("new_edge_ids", []))
    elif operation in {"support-edge", "add-conflict", "revise-boundary", "supersede-edge", "deprecate-edge"}:
        edge = edges[update["target_edge_id"]]
        if operation == "support-edge":
            append_unique(edge["support_evidence_ids"], update.get("proposed_support_evidence_ids", []))
            if update.get("proposed_validation_status"):
                edge["validation_status"] = update["proposed_validation_status"]
        elif operation == "add-conflict":
            append_unique(edge["conflict_evidence_ids"], update.get("proposed_conflict_evidence_ids", []))
            edge["validation_status"] = update.get("proposed_validation_status") or "conflicting"
        elif operation == "revise-boundary":
            edge["boundary_conditions"] = list(update.get("proposed_boundary_conditions", []))
        elif operation == "supersede-edge":
            edge["validation_status"] = "deprecated"
            append_unique(edge["conflict_evidence_ids"], update.get("proposed_conflict_evidence_ids", []))
        elif operation == "deprecate-edge":
            edge["validation_status"] = "deprecated"
            append_unique(edge["conflict_evidence_ids"], update.get("proposed_conflict_evidence_ids", []))
    elif operation in {"split-graph", "merge-proposal"}:
        raise ValueError(f"operation '{operation}' requires human graph restructuring and is not auto-applied")
    elif operation == "no-change":
        pass
    else:
        raise ValueError(f"unsupported operation '{operation}'")
    update["status"] = "applied"
    update["persistence_status"] = "artifact-written"


def cmd_apply(args: argparse.Namespace) -> int:
    if not args.skip_validation:
        validate(args.input)
    document = copy.deepcopy(load_json(args.input))
    selected = set(args.update_id or [])
    applied: list[str] = []
    skipped: list[str] = []
    for update in array(document.get("mechanism_updates")):
        if not isinstance(update, dict) or not update.get("id"):
            continue
        if selected and update["id"] not in selected:
            continue
        if update.get("status") != "approved":
            skipped.append(f"{update['id']}: status={update.get('status')}")
            continue
        try:
            apply_update(document, update)
        except (KeyError, ValueError) as exc:
            raise SystemExit(f"ERROR cannot apply {update['id']}: {exc}") from exc
        applied.append(update["id"])
    if not applied:
        raise SystemExit("ERROR no approved updates were applied; review statuses or --update-id")
    quality = document.setdefault("quality", {})
    quality["mechanism_graph_consistency"] = "pass"
    quality.setdefault("notes", []).append(f"Applied mechanism updates to artifact: {', '.join(applied)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.skip_validation:
        try:
            validate(args.output)
        except SystemExit:
            args.output.unlink(missing_ok=True)
            raise
    print(f"WROTE {args.output}; applied={applied}; skipped={skipped}")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    if not args.skip_validation:
        validate(args.input)
    document = load_json(args.input)
    graphs, nodes, edges, _ = indexes(document)
    postings: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"graphs": set(), "nodes": set(), "edges": set()})
    for collection_name, collection in (("graphs", graphs), ("nodes", nodes), ("edges", edges)):
        for item_id, item in collection.items():
            for token in text_tokens(item):
                postings[token][collection_name].add(item_id)
    payload = {
        "index_schema_version": "1.0",
        "source_run_id": document.get("run_id"),
        "source_sha256": sha256_json(document),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": graph_summary(document),
        "postings": {
            token: {name: sorted(ids) for name, ids in groups.items() if ids}
            for token, groups in sorted(postings.items())
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {args.output} ({len(payload['postings'])} terms)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("summary", help="Summarize mechanism graph coverage and status")
    p.add_argument("input", type=Path)
    p.add_argument("--json", action="store_true")
    p.add_argument("--skip-validation", action="store_true")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("query", help="Search graph, node, and edge text")
    p.add_argument("input", type=Path)
    p.add_argument("--text", default="")
    p.add_argument("--material-system")
    p.add_argument("--node-type")
    p.add_argument("--status")
    p.add_argument("--json", action="store_true")
    p.add_argument("--skip-validation", action="store_true")
    p.set_defaults(func=cmd_query)

    p = sub.add_parser("export", help="Export graph JSON, CSV, and Graphviz DOT")
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("mechanism-export"))
    p.add_argument("--graph-id", action="append")
    p.add_argument("--skip-validation", action="store_true")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("diff", help="Compare mechanism graph layers from two results")
    p.add_argument("old", type=Path)
    p.add_argument("new", type=Path)
    p.add_argument("-o", "--output", type=Path)
    p.add_argument("--skip-validation", action="store_true")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("apply", help="Apply approved deterministic graph updates to a new artifact")
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--update-id", action="append")
    p.add_argument("--skip-validation", action="store_true")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("index", help="Build a deterministic local retrieval index")
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("mechanism-index.json"))
    p.add_argument("--skip-validation", action="store_true")
    p.set_defaults(func=cmd_index)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
