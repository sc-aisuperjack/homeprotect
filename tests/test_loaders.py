from __future__ import annotations

from pathlib import Path

import pytest

from homeprotect_dash.data.loaders import InvalidInsightsError, load_insights


def test_load_processed_insights() -> None:
    path = Path("data/processed/structured_insights.json")
    insights = load_insights(path)
    assert insights.summary.total_reviews == 1751
    assert len(insights.segments) == 3


def test_invalid_segment_set_raises(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(
        '{"summary":{"total_reviews":1,"generated_at":"2026-03-22T15:00:00Z"},"segments":[],"outliers":[]}',
        encoding="utf-8",
    )
    with pytest.raises(InvalidInsightsError):
        load_insights(bad_file)
