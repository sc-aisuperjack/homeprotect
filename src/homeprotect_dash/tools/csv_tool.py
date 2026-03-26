from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"Title", "Content", "Stars"}


class InvalidReviewCsvError(ValueError):
    """Raised when the review CSV cannot be parsed."""


def list_csv_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.csv") if path.is_file())


def load_reviews_csv(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover
        raise InvalidReviewCsvError(f"Unable to read CSV file: {path}") from exc

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise InvalidReviewCsvError(f"CSV is missing required columns: {sorted(missing)}")

    normalized = df.copy()
    normalized["Title"] = normalized["Title"].fillna("").astype(str)
    normalized["Content"] = normalized["Content"].fillna("").astype(str)
    normalized["review_text"] = (
        normalized["Title"].str.strip() + " " + normalized["Content"].str.strip()
    ).str.strip()
    normalized["Stars"] = pd.to_numeric(normalized["Stars"], errors="coerce").fillna(3).clip(1, 5).astype(int)
    normalized = normalized.reset_index(drop=True)
    normalized["review_id"] = normalized.index + 1
    return normalized[["review_id", "Title", "Content", "review_text", "Stars"]]
