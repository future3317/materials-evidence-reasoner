#!/usr/bin/env python3
"""Profile active-learning artifacts without upgrading model output to evidence.

The profile is deliberately descriptive: it reads CSV headers/values and statically
inspects Python source, but never executes user code or treats a recommendation as a
measurement.  Semantic hints live in references/active-learning-field-lexicon.json.
"""

from __future__ import annotations

import argparse
import ast
import csv
import html
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEXICON_PATH = ROOT / "references" / "active-learning-field-lexicon.json"
IGNORED_NAMES = {".ds_store", "thumbs.db"}


def ignored(path: Path) -> bool:
    return path.name.startswith("._") or path.name.lower() in IGNORED_NAMES or any(
        part.casefold() == "__macosx" for part in path.parts
    )


def rel(path: Path, base: Path) -> str:
    try:
        return Path(__import__("os").path.relpath(path.resolve(), base.resolve())).as_posix()
    except ValueError:
        return path.name


def numeric(value: Any) -> float | None:
    try:
        value = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def file_role(name: str, rules: list[dict[str, Any]]) -> tuple[str, str | None]:
    for rule in rules:
        if re.search(str(rule["pattern"]), name, flags=re.IGNORECASE):
            return str(rule["role"]), rule.get("caution")
    return "unclassified", None


def column_hints(headers: list[str], lexicon: dict[str, Any]) -> dict[str, dict[str, Any]]:
    hints = lexicon.get("column_hints", {})
    return {header: hints[header] for header in headers if header in hints}


def table_profile(path: Path, output: Path, lexicon: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, float]]]:
    headers, rows = read_csv(path)
    role, caution = file_role(path.name, lexicon.get("file_rules", []))
    stats: dict[str, dict[str, Any]] = {}
    for header in headers:
        values = [value for value in (numeric(row.get(header)) for row in rows) if value is not None]
        stats[header] = {
            "numeric_count": len(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
        }
    coordinates = []
    if {"x", "y"}.issubset(headers):
        for row in rows:
            x, y = numeric(row.get("x")), numeric(row.get("y"))
            if x is not None and y is not None:
                coordinates.append({"x": x, "y": y})
    profile: dict[str, Any] = {
        "path": rel(path, output),
        "name": path.name,
        "role": role,
        "caution": caution,
        "row_count": len(rows),
        "columns": headers,
        "column_hints": column_hints(headers, lexicon),
        "numeric_summary": stats,
        "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
    }
    if role in {"model_recommendation", "qbc_model_recommendation"}:
        profile["preview"] = rows[:10]
    return profile, coordinates


def static_code_profile(path: Path, output: Path, lexicon: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text, filename=str(path))
        syntax_error = None
    except SyntaxError as exc:
        tree = None
        syntax_error = f"SyntaxError: {exc.msg} (line {exc.lineno})"
    imports: list[str] = []
    functions: list[str] = []
    classes: list[str] = []
    constants: list[str] = []
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module.split(".")[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append(target.id)
    references = sorted(set(re.findall(r"(?:read_csv|to_csv|open)\s*\(\s*['\"]([^'\"]+)", text)))
    known_external = set(lexicon.get("code_signals", {}).get("model_libraries", []))
    known_external.update({"numpy", "pandas", "matplotlib", "torch", "warnings", "os", "sys", "datetime"})
    local_missing: list[str] = []
    for module in sorted(set(imports)):
        if module in known_external or module in {"__future__", "pathlib", "typing", "csv", "json", "math", "re"}:
            continue
        local_py = path.parent / f"{module}.py"
        local_pkg = path.parent / module / "__init__.py"
        if ("." not in module and ("from " + module) in text) and not local_py.exists() and not local_pkg.exists():
            local_missing.append(module)
    in_place = any(name in {"labeled.csv", "curr_unlabeled.csv", "qbc_recommended.csv"} for name in references)
    return {
        "path": rel(path, output),
        "name": path.name,
        "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
        "imports": sorted(set(imports)),
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "constants": sorted(set(constants)),
        "referenced_paths": references,
        "missing_local_imports": local_missing,
        "writes_in_place": in_place,
        "syntax_error": syntax_error,
    }


def point_set(points: list[dict[str, float]]) -> set[tuple[float, float]]:
    return {(round(point["x"], 10), round(point["y"], 10)) for point in points}


def recommendation_summary(table: dict[str, Any], coordinates: list[dict[str, float]], observed: set[tuple[float, float]], candidate: set[tuple[float, float]]) -> dict[str, Any]:
    points = point_set(coordinates)
    return {
        "name": table["name"],
        "path": table["path"],
        "role": table["role"],
        "row_count": len(coordinates),
        "already_observed_count": len(points & observed),
        "new_candidate_count": len(points & candidate) - len(points & observed),
        "outside_candidate_count": len(points - candidate) if candidate else None,
        "score_column": "qbc_variance" if table["role"] == "qbc_model_recommendation" else "acquisition_value",
        "status": "proposed-for-experiment-not-validated",
    }


def svg_scatter(points: dict[str, list[dict[str, float]]]) -> str:
    all_points = [point for values in points.values() for point in values]
    if not all_points:
        return '<div class="empty">没有可绘制的 x/y 坐标</div>'
    xmin, xmax = min(p["x"] for p in all_points), max(p["x"] for p in all_points)
    ymin, ymax = min(p["y"] for p in all_points), max(p["y"] for p in all_points)
    dx, dy = max(xmax - xmin, 1e-9), max(ymax - ymin, 1e-9)
    width, height, pad = 860, 360, 38

    def xy(point: dict[str, float]) -> tuple[float, float]:
        return pad + (point["x"] - xmin) / dx * (width - 2 * pad), height - pad - (point["y"] - ymin) / dy * (height - 2 * pad)

    colors = {"candidate": "#d7dce5", "observed": "#1d1d1f", "recommendation": "#007aff"}
    parts = [f'<svg class="scatter" viewBox="0 0 {width} {height}" role="img" aria-label="主动学习候选点与推荐点分布">', '<rect width="100%" height="100%" rx="18" fill="#f7f8fa"/>']
    for tick in range(5):
        gx = pad + tick * (width - 2 * pad) / 4
        gy = height - pad - tick * (height - 2 * pad) / 4
        parts.append(f'<line x1="{gx:.1f}" y1="{pad}" x2="{gx:.1f}" y2="{height-pad}" stroke="#e5e7eb"/>')
        parts.append(f'<line x1="{pad}" y1="{gy:.1f}" x2="{width-pad}" y2="{gy:.1f}" stroke="#e5e7eb"/>')
    step = max(1, len(points.get("candidate", [])) // 700)
    for kind, values in (("candidate", points.get("candidate", [])[::step]), ("observed", points.get("observed", [])), ("recommendation", points.get("recommendation", []))):
        for point in values:
            x, y = xy(point)
            radius = 3.2 if kind == "candidate" else (4.6 if kind == "observed" else 6.2)
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{colors[kind]}" opacity="{0.48 if kind == "candidate" else 0.9}"/>')
    parts.append(f'<text x="{pad}" y="{height-10}" fill="#6e6e73" font-size="11">x: {xmin:.3g}–{xmax:.3g}</text>')
    parts.append(f'<text x="{width-pad}" y="{height-10}" text-anchor="end" fill="#6e6e73" font-size="11">y: {ymin:.3g}–{ymax:.3g}</text>')
    parts.append("</svg>")
    return "".join(parts)


def dashboard(profile: dict[str, Any]) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    summary = profile["summary"]
    cards = [
        ("已标注记录", summary.get("observed_rows", 0), "文件中带有目标列的记录"),
        ("候选点", summary.get("candidate_rows", 0), "尚无独立验证的输入空间"),
        ("推荐方法", summary.get("recommendation_count", 0), "模型输出，不等于实验结果"),
        ("缺失本地依赖", summary.get("missing_local_import_count", 0), "静态检查发现的复现缺口"),
    ]
    card_html = "".join(f'<div class="metric"><div class="muted">{esc(label)}</div><strong>{esc(value)}</strong><div class="small">{esc(note)}</div></div>' for label, value, note in cards)
    rows = "".join(
        f'<tr><td>{esc(item["name"])}</td><td>{esc(item["row_count"])}</td><td>{esc(item["score_column"])}</td><td>{esc(item["already_observed_count"])}</td><td>{esc(item["new_candidate_count"])}</td><td><span class="tag blue">待实验验证</span></td></tr>'
        for item in profile["recommendations"]
    ) or '<tr><td colspan="6">没有识别到推荐表</td></tr>'
    warnings = "".join(f'<li>{esc(item)}</li>' for item in profile["warnings"]) or "<li>未发现额外提醒</li>"
    code = "".join(f'<li><a href="{esc(item["path"])}">{esc(item["name"])}</a>：imports={esc(", ".join(item["imports"]) or "无")}；functions={esc(", ".join(item["functions"]) or "无")}'+ (f'；缺少本地模块 {esc(", ".join(item["missing_local_imports"]))}' if item["missing_local_imports"] else "") + ("；会覆盖输入文件" if item["writes_in_place"] else "") + "</li>" for item in profile["code_files"])
    files = "".join(f'<li><span class="tag">{esc(item["role"])}</span> <a href="{esc(item["path"])}">{esc(item["name"])}</a> · {esc(item["row_count"])} rows</li>' for item in profile["tables"])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Active Learning Evidence Profile</title><style>
:root{{--bg:#f5f5f7;--panel:#fff;--text:#1d1d1f;--muted:#6e6e73;--line:#e5e5ea;--blue:#007aff;--blue-soft:#eaf3ff;--orange:#ff9500;--shadow:0 16px 40px rgba(0,0,0,.06)}}*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(180deg,#fbfbfd 0,#f5f5f7 46%,#eef0f4 100%);font:14px -apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif;color:var(--text)}}main{{max-width:1240px;margin:0 auto;padding:36px 22px 60px}}.hero{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:24px}}h1{{font-size:36px;letter-spacing:-.045em;margin:0 0 8px}}h2{{font-size:21px;letter-spacing:-.025em;margin:0 0 14px}}.lead{{color:var(--muted);line-height:1.6;max-width:760px}}.tag{{display:inline-flex;align-items:center;padding:5px 9px;border-radius:999px;background:#f0f0f2;color:var(--muted);font-size:11px;font-weight:650}}.tag.blue{{background:var(--blue-soft);color:var(--blue)}}.hero-badge{{padding:10px 13px;border-radius:999px;background:#fff4df;color:#9a5b00;font-weight:700;font-size:12px;white-space:nowrap}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0 28px}}.metric,.panel{{background:rgba(255,255,255,.86);border:1px solid rgba(0,0,0,.06);border-radius:22px;box-shadow:var(--shadow)}}.metric{{padding:18px 19px}}.metric strong{{display:block;font-size:31px;letter-spacing:-.04em;margin:8px 0 3px}}.muted,.small{{color:var(--muted)}}.small{{font-size:11px;line-height:1.45}}.panel{{padding:22px;margin:14px 0}}.grid{{display:grid;grid-template-columns:1.25fr .75fr;gap:14px}}.scatter{{width:100%;height:auto;display:block}}table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:11px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{font-size:11px;color:var(--muted);font-weight:650}}ul{{margin:0;padding-left:20px}}li{{margin:9px 0;line-height:1.5}}a{{color:var(--blue);text-decoration:none}}a:hover{{text-decoration:underline}}.callout{{padding:14px 16px;border-radius:16px;background:var(--blue-soft);color:#164f9c;line-height:1.55;margin-top:14px}}@media(max-width:800px){{.metrics{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}.hero{{display:block}}.hero-badge{{display:inline-block;margin-top:12px}}h1{{font-size:30px}}.panel{{overflow:auto}}}}
</style></head><body><main><section class="hero"><div><div class="tag">Materials Evidence Reasoner · active-learning profile</div><h1>主动学习证据画像</h1><p class="lead">这是一份输入盘点和可复现性检查，不是“最优工艺”结论。推荐点仍处于待实验验证状态；请先确认 x/y 的物理含义、z 的来源和单位。</p></div><div class="hero-badge">待实验验证 · evidence boundary visible</div></section><section class="metrics">{card_html}</section><section class="grid"><div class="panel"><h2>输入空间与推荐分布</h2>{svg_scatter(profile["plot_points"])}<div class="small" style="margin-top:10px">灰点：候选空间抽样；黑点：带标签记录；蓝点：推荐点。图形只帮助定位分布，原始 CSV 才是数据源。</div></div><div class="panel"><h2>先看这三件事</h2><ol><li>把 x/y 映射到真实工艺变量并补充单位、范围和约束。</li><li>确认 z 是实验测量、可信模拟，还是示例目标函数。</li><li>推荐点执行后，把每个点的实际条件、测量方法、重复和 z 写回新的记录。</li></ol><div class="callout">`acquisition_value` 和 `qbc_variance` 只用于选择/排序；它们不是性能值，也不是实验不确定度。</div></div></section><section class="panel"><h2>推荐对比</h2><table><thead><tr><th>文件</th><th>点数</th><th>排序量</th><th>已出现于标签</th><th>候选池中新点</th><th>状态</th></tr></thead><tbody>{rows}</tbody></table></section><section class="grid"><div class="panel"><h2>文件角色</h2><ul>{files}</ul></div><div class="panel"><h2>复现与安全提醒</h2><ul>{code}</ul></div></section><section class="panel"><h2>需要人工补充或回查</h2><ul>{warnings}</ul></section><section class="panel"><h2>原始代码与数据</h2><p class="small">画像文件使用相对路径；点击下列路径可回到原始输入。生成时间：{esc(profile["created_at"])}</p></section></main></body></html>'''


def markdown(profile: dict[str, Any]) -> str:
    lines = ["# 主动学习证据画像", "", "> 这是模型/数据资产盘点，不是实验结论。推荐点必须独立验证后才能进入实测记录。", "", f"- 状态：**{profile['summary']['status']}**", f"- 输入目录：`{profile['input_root']}`", "", "## 文件角色", ""]
    for item in profile["tables"]:
        lines.append(f"- `{item['name']}` · `{item['role']}` · {item['row_count']} rows · columns={', '.join(item['columns'])}")
    lines.extend(["", "## 推荐摘要", "", "| 文件 | 排序量 | 点数 | 已在标签 | 候选池新点 | 状态 |", "|---|---|---:|---:|---:|---|"])
    for item in profile["recommendations"]:
        lines.append(f"| `{item['name']}` | `{item['score_column']}` | {item['row_count']} | {item['already_observed_count']} | {item['new_candidate_count']} | {item['status']} |")
    lines.extend(["", "## 代码可复现性", ""])
    for item in profile["code_files"]:
        note = []
        if item["missing_local_imports"]:
            note.append("missing local import: " + ", ".join(item["missing_local_imports"]))
        if item["writes_in_place"]:
            note.append("writes to input-named files")
        lines.append(f"- `{item['name']}` · imports={', '.join(item['imports']) or 'none'}" + (" · " + "; ".join(note) if note else ""))
    lines.extend(["", "## 需要补充", ""])
    lines.extend(f"- {warning}" for warning in profile["warnings"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("active-learning-profile"))
    parser.add_argument("--lexicon", type=Path, default=LEXICON_PATH)
    args = parser.parse_args()
    root = args.input.resolve()
    if not root.exists():
        parser.error(f"input path does not exist: {args.input}")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    lexicon = json.loads(args.lexicon.read_text(encoding="utf-8"))
    files = [p for p in sorted(root.rglob("*")) if p.is_file() and not ignored(p) and output not in p.resolve().parents]
    tables: list[dict[str, Any]] = []
    table_coords: dict[str, list[dict[str, float]]] = {}
    code_files: list[dict[str, Any]] = []
    for path in files:
        if path.suffix.lower() == ".csv":
            try:
                item, coordinates = table_profile(path, output, lexicon)
                tables.append(item)
                table_coords[path.name] = coordinates
            except Exception as exc:
                tables.append({"path": rel(path, output), "name": path.name, "role": "parse-failed", "row_count": 0, "columns": [], "error": f"{type(exc).__name__}: {exc}"})
        elif path.suffix.lower() == ".py":
            code_files.append(static_code_profile(path, output, lexicon))
    observed = point_set(next((coords for name, coords in table_coords.items() if name.lower() == "labeled.csv"), []))
    candidate = point_set(next((coords for name, coords in table_coords.items() if name.lower() == "init_unlabeled.csv"), []))
    recommendations = [recommendation_summary(item, table_coords.get(item["name"], []), observed, candidate) for item in tables if item["role"] in {"model_recommendation", "qbc_model_recommendation"}]
    missing = sorted({module for item in code_files for module in item["missing_local_imports"]})
    warnings: list[str] = []
    if not any(item["role"] == "observed_or_simulated_labels" for item in tables):
        warnings.append("未发现 labeled.csv：无法建立已有标签基线。")
    if any(item["role"] in {"model_recommendation", "qbc_model_recommendation"} for item in tables):
        warnings.append("推荐 CSV 没有独立测量列；请保持“模型推荐/待实验验证”状态。")
    if missing:
        warnings.append("代码引用了未随目录提供的本地模块：" + ", ".join(missing) + "。")
    if any(item["writes_in_place"] for item in code_files):
        warnings.append("至少一个脚本会写入输入命名文件；复现前复制数据目录并记录运行快照。")
    warnings.append("x/y/z 的物理含义、单位、目标来源和目标方向仍需研究者确认。")
    profile = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "path_base": ".",
        "input_root": rel(root, output),
        "lexicon": rel(args.lexicon.resolve(), output),
        "tables": tables,
        "code_files": code_files,
        "recommendations": recommendations,
        "warnings": warnings,
        "plot_points": {
            "candidate": next((coords for name, coords in table_coords.items() if name.lower() == "init_unlabeled.csv"), [])[:1200],
            "observed": next((coords for name, coords in table_coords.items() if name.lower() == "labeled.csv"), []),
            "recommendation": [point for item in recommendations for point in table_coords.get(item["name"], [])],
        },
        "summary": {
            "status": "ready-with-model-caveats" if tables else "no-csv-assets",
            "observed_rows": sum(item["row_count"] for item in tables if item["role"] == "observed_or_simulated_labels"),
            "candidate_rows": sum(item["row_count"] for item in tables if item["role"] in {"candidate_pool", "current_acquisition_pool"}),
            "recommendation_count": len(recommendations),
            "missing_local_import_count": len(missing),
            "code_count": len(code_files),
        },
    }
    (output / "active-learning-profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "active-learning-profile.md").write_text(markdown(profile), encoding="utf-8")
    (output / "active-learning-dashboard.html").write_text(dashboard(profile), encoding="utf-8")
    print(f"WROTE {output / 'active-learning-profile.json'}; tables={len(tables)}, code={len(code_files)}, recommendations={len(recommendations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
