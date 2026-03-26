from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from homeprotect_dash.config import CONFIG

try:  # pragma: no cover - import presence depends on environment
    from google import genai
except Exception:  # pragma: no cover
    genai = None


@dataclass(slots=True)
class GenAIService:
    api_key: str
    model: str

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key and genai is not None)

    def generate_json(self, prompt: str) -> dict[str, Any]:
        if not self.is_enabled:
            raise RuntimeError("Gemini is not configured. Set GOOGLE_API_KEY to enable live ADK/LLM calls.")
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model, contents=prompt)
        return json.loads(str(response.text))


GENAI_SERVICE = GenAIService(api_key=CONFIG.google_api_key, model=CONFIG.google_genai_model)
