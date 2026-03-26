from __future__ import annotations

import json
from pathlib import Path

from homeprotect_dash.tools.csv_tool import load_reviews_csv
from homeprotect_dash.tools.insight_builder_tool import build_structured_insights
from homeprotect_dash.tools.manifest_tool import EMPTY_MANIFEST, needs_processing, upsert_entry


def test_csv_loader_normalizes_review_rows() -> None:
    df = load_reviews_csv(Path("data/raw/homeprotect_reviews.csv"))
    assert {"review_id", "Title", "Content", "review_text", "Stars"}.issubset(df.columns)
    assert len(df) == 1751


def test_insight_builder_creates_required_segments() -> None:
    df = load_reviews_csv(Path("data/raw/homeprotect_reviews.csv")).head(50)
    insights = build_structured_insights(df)
    assert [segment.segment for segment in insights.segments] == [
        "Claims",
        "Customer Service",
        "Pricing",
    ]


def test_manifest_detects_new_and_processed_file(tmp_path: Path) -> None:
    csv_file = tmp_path / "example.csv"
    csv_file.write_text("Title,Content,Stars\nA,B,5\n", encoding="utf-8")
    assert needs_processing(csv_file, EMPTY_MANIFEST) is True

    updated_manifest = upsert_entry(
        EMPTY_MANIFEST,
        file_path=csv_file,
        output_file=tmp_path / "structured.json",
        status="processed",
    )
    assert needs_processing(csv_file, updated_manifest) is False
    payload = updated_manifest.to_dict()
    assert payload["files"][0]["filename"] == "example.csv"
