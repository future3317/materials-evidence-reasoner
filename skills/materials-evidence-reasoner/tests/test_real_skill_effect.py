from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_real_skill_effect import evaluate_mode, read_text  # noqa: E402


def test_real_skill_output_passes_contract_and_improves_auditability() -> None:
    baseline_dir = ROOT / "examples" / "skill-effect-real"
    baseline = json.loads((baseline_dir / "no-skill-output.json").read_text(encoding="utf-8"))
    skill = json.loads((baseline_dir / "with-skill-output.json").read_text(encoding="utf-8"))
    baseline_result = evaluate_mode(read_text(baseline_dir / "no-skill-report.md"), baseline, False)
    skill_result = evaluate_mode(read_text(baseline_dir / "with-skill-report.md"), skill, True)

    assert baseline_result["human_score"] == 1.0
    assert skill_result["human_score"] == 1.0
    assert baseline_result["audit_score"] == 0.0
    assert skill_result["audit_score"] > 0.9
    assert skill_result["validation_errors"] == []
