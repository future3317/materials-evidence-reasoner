from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_submission_skill_entry_has_matching_name_and_description() -> None:
    skill_dir = PACKAGE_ROOT
    skill_path = skill_dir / "SKILL.md"

    assert skill_path.is_file()
    text = skill_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "name: materials-evidence-reasoner" in text
    assert "description:" in text
    assert skill_dir.name == "materials-evidence-reasoner"


def test_submission_package_contains_runtime_assets() -> None:
    for directory in ("agents", "references", "scripts", "examples", "templates", "viewer", "tests"):
        assert (PACKAGE_ROOT / directory).is_dir()
