from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_skill_modes import build_comparison, load_json, render_html, render_svg  # noqa: E402


def test_skill_effect_comparison_keeps_facts_but_adds_contract_guards() -> None:
    result = build_comparison(load_json(ROOT / "examples" / "synthetic-closed-loop.json"))
    without_skill = result["modes"]["without_skill"]
    with_skill = result["modes"]["with_skill"]

    assert without_skill["metrics"]["fact_capture"] == 1.0
    assert with_skill["metrics"]["fact_capture"] == 1.0
    assert without_skill["guardrail_score"] == 0.0
    assert with_skill["guardrail_score"] == 1.0
    assert with_skill["metrics"]["canonical_json"] == 1.0
    assert with_skill["metrics"]["experiment_coverage"] == 1.0


def test_comparison_renderers_are_available_without_checked_in_build_outputs() -> None:
    result = build_comparison(load_json(ROOT / "examples" / "synthetic-closed-loop.json"))
    html = render_html(result)
    svg = render_svg(result)
    assert "Skill effect comparison" in html
    assert "能力对照" in html
    assert "<svg" in svg
    assert "合同护栏覆盖率" in svg
