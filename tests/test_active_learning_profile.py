from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_prepare_intake_ignores_macos_metadata_and_reads_python(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "labeled.csv").write_text("x,y,z\n0.1,0.2,3\n", encoding="utf-8")
    (input_dir / "._labeled.csv").write_bytes(b"metadata")
    (input_dir / ".DS_Store").write_bytes(b"metadata")
    macosx = input_dir / "__MACOSX"
    macosx.mkdir()
    (macosx / "._extra.csv").write_bytes(b"metadata")
    (input_dir / "run.py").write_text("from pathlib import Path\nprint('safe static input')\n", encoding="utf-8")
    output = tmp_path / "intake"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "prepare_intake.py"), str(input_dir), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    packet = json.loads((output / "intake-packet.json").read_text(encoding="utf-8"))
    names = {item["name"] for item in packet["received_inputs"]}
    assert names == {"labeled.csv", "run.py"}
    assert any(item["input_id"] == "IN-0002" for item in packet["text_items"])


def test_profile_separates_recommendations_from_observations(tmp_path: Path) -> None:
    input_dir = tmp_path / "active"
    input_dir.mkdir()
    (input_dir / "labeled.csv").write_text("x,y,z\n0.1,0.2,3\n", encoding="utf-8")
    (input_dir / "init_unlabeled.csv").write_text("x,y\n0.1,0.2\n0.4,0.5\n", encoding="utf-8")
    (input_dir / "recommended_1.csv").write_text("x,y,acquisition_value\n0.4,0.5,0.9\n", encoding="utf-8")
    (input_dir / "model.py").write_text("from missing_local import value\n", encoding="utf-8")
    output = tmp_path / "profile"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "profile_active_learning.py"), str(input_dir), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    profile = json.loads((output / "active-learning-profile.json").read_text(encoding="utf-8"))
    assert profile["summary"]["observed_rows"] == 1
    assert profile["recommendations"][0]["status"] == "proposed-for-experiment-not-validated"
    assert profile["recommendations"][0]["new_candidate_count"] == 1
    assert "missing_local" in profile["warnings"][1]
    assert (output / "active-learning-dashboard.html").is_file()
