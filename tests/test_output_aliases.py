from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalize_output import normalize_viewer_data  # noqa: E402


def test_legacy_result_is_readable_without_inventing_ids() -> None:
    source = json.loads((ROOT / "result(3).json").read_text(encoding="utf-8-sig"))
    normalized = normalize_viewer_data(source)

    hypothesis = normalized["hypotheses"][0]
    assert hypothesis["id"] == "hyp_crack_defects"
    assert hypothesis["statement"] == hypothesis["title"]
    assert hypothesis["legacy_supporting_evidence"]
    assert hypothesis["support_evidence_ids"] == []
    assert hypothesis["falsifiers"] == [hypothesis["falsifier"]]

    plan = normalized["verification_plan"][0]
    assert plan["id"] == "ver_exp_A_optimize_coating"
    assert plan["action"] == plan["title"]
    assert plan["hypothesis_ids"] == plan["target_hypotheses"]
    assert any("if_hyp_crack_defects_true" in value for value in plan["expected_outcomes"])
    assert plan["decision_rule"]
    assert normalized["_compatibility"]["mode"] == "explicit-field-aliases"


def test_canonical_shape_is_not_marked_legacy() -> None:
    source = {
        "schema_version": "4.6",
        "hypotheses": [{"id": "H1", "statement": "test", "mechanism_chain": [], "support_evidence_ids": [], "counterevidence_ids": [], "unique_predictions": [], "falsifiers": [], "status": "speculative"}],
        "verification_plan": [],
    }
    normalized = normalize_viewer_data(source)
    assert normalized["hypotheses"][0]["statement"] == "test"
    assert normalized["_compatibility"]["mode"] == "canonical"
