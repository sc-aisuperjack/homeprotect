from __future__ import annotations

from pathlib import Path

from homeprotect_dash.data.figures import (
    build_nps_score_figure,
    build_outlier_table,
    build_segment_volume_figure,
    build_sentiment_figure,
)
from homeprotect_dash.data.loaders import load_insights


def test_core_figures_build() -> None:
    insights = load_insights(Path("data/processed/structured_insights.json"))
    volume = build_segment_volume_figure(insights)
    sentiment = build_sentiment_figure(insights)
    nps = build_nps_score_figure(insights)
    outliers = build_outlier_table(insights)

    assert volume.data
    assert sentiment.data
    assert nps.data
    assert len(outliers) >= 1
