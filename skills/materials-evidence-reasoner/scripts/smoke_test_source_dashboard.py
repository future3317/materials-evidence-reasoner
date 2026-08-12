#!/usr/bin/env python3
"""Run a local Chromium smoke test for the offline source review dashboard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dashboard", type=Path)
    parser.add_argument("--chromium", required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR playwright is not installed", file=sys.stderr)
        return 2
    errors: list[str] = []
    checks: dict[str, object] = {}
    try:
        html = args.dashboard.read_text(encoding="utf-8")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=args.chromium, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
            page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
            page.set_content(html, wait_until="load")
            page.wait_for_timeout(250)
            source_section = page.locator("h2").filter(has_text="文件清单").locator("xpath=..")
            checks.update({
                "title": page.title(),
                "heading": page.locator("h1").inner_text(),
                "metrics": page.locator(".metric").count(),
                "profile_rows": page.locator("h3").filter(has_text="按任务选择处理 profile").locator("xpath=following-sibling::div[1]//tr").count(),
                "source_rows": max(0, source_section.locator(".table-wrap tr").count() - 1),
                "relative_links": page.locator("a").count(),
                "horizontal_overflow": page.evaluate("document.documentElement.scrollWidth - window.innerWidth"),
            })
            page.set_viewport_size({"width": 360, "height": 900})
            page.wait_for_timeout(100)
            checks["narrow_horizontal_overflow"] = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            browser.close()
    except Exception as exc:
        checks["exception"] = f"{type(exc).__name__}: {exc}"
    result = {
        "test": "offline-source-dashboard-smoke",
        "dashboard": str(args.dashboard),
        "checks": checks,
        "console_errors": errors,
        "pass": checks.get("title") == "Source Extraction Review"
        and checks.get("heading") == "文献提取检查台"
        and int(checks.get("metrics", 0)) >= 4
        and int(checks.get("profile_rows", 0)) >= 2
        and int(checks.get("source_rows", 0)) >= 1
        and int(checks.get("narrow_horizontal_overflow", 0)) <= 2
        and not errors
        and "exception" not in checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
