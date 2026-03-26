from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from homeprotect_dash.config import CONFIG
from homeprotect_dash.data.contracts import StructuredInsights


class InvalidInsightsError(ValueError):
    """Raised when a structured insights payload cannot be parsed."""


def latest_insights_path() -> Path:
    if CONFIG.insights_path.exists():
        return CONFIG.insights_path
    sample_path = Path(__file__).resolve().parents[3] / "data" / "sample_structured_insights.json"
    return sample_path


def load_insights(path: Path | None = None) -> StructuredInsights:
    target = path or latest_insights_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InvalidInsightsError(f"Insights file not found: {target}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidInsightsError(f"Invalid JSON in insights file: {target}") from exc

    return validate_payload(payload)


def parse_upload(contents: str) -> StructuredInsights:
    try:
        _, encoded = contents.split(",", 1)
        decoded = base64.b64decode(encoded).decode("utf-8")
        payload = json.loads(decoded)
    except Exception as exc:  # pragma: no cover
        raise InvalidInsightsError("Uploaded file could not be decoded as JSON.") from exc

    return validate_payload(payload)


def validate_payload(payload: dict[str, Any]) -> StructuredInsights:
    try:
        return StructuredInsights.model_validate(payload)
    except Exception as exc:
        raise InvalidInsightsError(f"Structured insights payload is invalid: {exc}") from exc
