#!/usr/bin/env python3
"""Run a local browser smoke test for the offline materials dashboard.

The script never starts a server and never performs network requests. It loads the
HTML string directly into a headless Chromium page, checks the guided overview,
scientific comparison views, Mechanism Graph interaction, narrow layout and theme
control, and optionally writes screenshots plus a machine-readable report.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def find_chromium(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dashboard", type=Path)
    parser.add_argument("--chromium", help="Path to a Chromium-compatible executable")
    parser.add_argument("--report", type=Path, default=Path("viewer-smoke.json"))
    parser.add_argument("--screenshots", type=Path, help="Optional directory for light/dark screenshots")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR playwright is not installed; run: python -m pip install playwright", file=sys.stderr)
        return 2

    if not args.dashboard.is_file():
        print(f"ERROR dashboard not found: {args.dashboard}", file=sys.stderr)
        return 2
    chromium = find_chromium(args.chromium)
    if not chromium:
        print("ERROR no Chromium executable found; provide --chromium", file=sys.stderr)
        return 2

    html = args.dashboard.read_text(encoding="utf-8")
    console_errors: list[str] = []
    checks: dict[str, Any] = {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=chromium,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = browser.new_page(viewport={"width": 1440, "height": 1050})
            page.on(
                "console",
                lambda message: console_errors.append(f"{message.type}: {message.text}")
                if message.type == "error"
                else None,
            )
            page.on("pageerror", lambda error: console_errors.append(f"pageerror: {error}"))
            page.set_content(html, wait_until="load")
            page.wait_for_timeout(400)

            checks["title"] = page.title()
            checks["status"] = page.locator("#status").inner_text()
            checks["nav_count"] = page.locator(".nav-button").count()
            checks["overview_heading"] = page.locator("#content h2").first.inner_text()
            checks["guide_steps"] = page.locator(".guide-step").count()
            checks["comparison_charts"] = page.locator(".chart-card svg").count()

            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshots / "overview-light.png"), full_page=True)

            page.get_by_role("button", name="机理图谱").click()
            page.wait_for_timeout(250)
            checks["mechanism_heading"] = page.locator("#content h2").first.inner_text()
            checks["mechanism_nodes"] = page.locator(".graph-node").count()
            checks["mechanism_edges"] = page.locator(".graph-edge-hit").count()
            checks["graph_controls"] = page.locator(".graph-controls select").count()
            if checks["mechanism_edges"]:
                page.locator(".graph-edge-hit").first.dispatch_event("click")
                page.wait_for_timeout(80)
                checks["inspector_heading"] = page.locator(".inspector h3").inner_text()
                checks["transferability_level"] = page.locator(
                    ".inspector .transfer-box .badge"
                ).first.inner_text()
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "mechanism-light.png"), full_page=True)

            page.get_by_role("button", name="偏差与误差").click()
            page.wait_for_timeout(100)
            checks["error_charts"] = page.locator(".chart-card .effect-mark").count()
            page.get_by_role("button", name="异常传播链").click()
            page.wait_for_timeout(100)
            checks["chain_edge_details"] = page.locator(".edge-details").count()
            page.get_by_role("button", name="信息缺口与实验").click()
            page.wait_for_timeout(100)
            checks["coverage_matrix"] = page.locator(".coverage-table").count()
            checks["coverage_hits"] = page.locator(".coverage-hit").count()
            page.get_by_role("button", name="PSPP 与经验").click()
            page.wait_for_timeout(100)
            checks["pspp_graphs"] = page.locator(".pspp-canvas svg").count()

            page.locator("#theme-button").click()
            page.locator("#theme-button").click()
            page.wait_for_timeout(80)
            checks["theme"] = page.locator("html").get_attribute("data-theme")
            page.set_viewport_size({"width": 360, "height": 900})
            page.wait_for_timeout(100)
            checks["narrow_horizontal_overflow"] = page.evaluate(
                "document.documentElement.scrollWidth - window.innerWidth"
            )
            checks["narrow_table_scrollable"] = page.locator("#content .table-wrap").evaluate_all(
                "els => els.some(el => el.scrollWidth > el.clientWidth + 4)"
            )
            checks["narrow_table_min_width"] = page.locator(
                "#content .table-wrap table"
            ).first.evaluate("el => Math.round(el.getBoundingClientRect().width)")
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "mechanism-dark.png"), full_page=True)
            browser.close()
    except Exception as exc:  # Playwright raises several generated exception types.
        checks["exception"] = f"{type(exc).__name__}: {exc}"

    expected = {
        "title": checks.get("title") == "Materials Evidence Viewer",
        "status_loaded": "已加载" in str(checks.get("status", "")),
        "navigation": int(checks.get("nav_count", 0)) >= 10,
        "overview": checks.get("overview_heading") == "概览",
        "guided_overview": int(checks.get("guide_steps", 0)) == 4,
        "comparison_chart": int(checks.get("comparison_charts", 0)) > 0,
        "mechanism_view": checks.get("mechanism_heading") == "证据约束机理图谱",
        "mechanism_nodes": int(checks.get("mechanism_nodes", 0)) > 0,
        "mechanism_edges": int(checks.get("mechanism_edges", 0)) > 0,
        "inspector": bool(checks.get("inspector_heading")),
        "error_chart": int(checks.get("error_charts", 0)) > 0,
        "chain_audit": int(checks.get("chain_edge_details", 0)) > 0,
        "coverage_matrix": int(checks.get("coverage_matrix", 0)) == 1
        and int(checks.get("coverage_hits", 0)) > 0,
        "pspp_graph": int(checks.get("pspp_graphs", 0)) > 0,
        "dark_theme": checks.get("theme") == "dark",
        "narrow_layout": int(checks.get("narrow_horizontal_overflow", 0)) <= 2,
        "narrow_tables_readable": bool(checks.get("narrow_table_scrollable"))
        and int(checks.get("narrow_table_min_width", 0)) >= 600,
        "console_clean": not console_errors,
        "no_exception": "exception" not in checks,
    }
    payload = {
        "test": "offline-materials-viewer-smoke",
        "dashboard": str(args.dashboard),
        "chromium": chromium,
        "checks": checks,
        "assertions": expected,
        "console_errors": console_errors,
        "pass": all(expected.values()),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
