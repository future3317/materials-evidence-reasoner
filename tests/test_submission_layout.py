from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_submission_skill_entry_has_matching_name_and_description() -> None:
    skill_dir = ROOT / "skills" / "materials-evidence-reasoner"
    skill_path = skill_dir / "SKILL.md"

    assert skill_path.is_file()
    text = skill_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "name: materials-evidence-reasoner" in text
    assert "description:" in text
    assert skill_dir.name == "materials-evidence-reasoner"


def test_submission_entry_matches_root_skill() -> None:
    root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    submission_skill = (ROOT / "skills" / "materials-evidence-reasoner" / "SKILL.md").read_text(encoding="utf-8")

    assert submission_skill.rstrip() == root_skill.rstrip()
