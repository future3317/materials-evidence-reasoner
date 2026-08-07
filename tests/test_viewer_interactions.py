from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIEWER = (ROOT / "viewer" / "index.html").read_text(encoding="utf-8")


def test_viewer_exposes_detail_entry_points_for_property_cards() -> None:
    assert "showPropertyDetails" in VIEWER
    assert "查看记录详情" in VIEWER
    assert "card.dataset.detailBound" in VIEWER
    assert 'setAttribute("role","button")' in VIEWER


def test_viewer_handles_page_level_file_drop() -> None:
    assert "function droppedFile" in VIEWER
    assert "function processDrop" in VIEWER
    assert 'window.addEventListener("dragover"' in VIEWER
    assert 'window.addEventListener("drop"' in VIEWER
    assert "dropEffect=\"copy\"" in VIEWER
