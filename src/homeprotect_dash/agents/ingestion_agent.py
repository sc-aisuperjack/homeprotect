from __future__ import annotations

from pathlib import Path

from homeprotect_dash.config import CONFIG
from homeprotect_dash.tools.csv_tool import load_reviews_csv
from homeprotect_dash.tools.insight_builder_tool import build_structured_insights, write_structured_insights
from homeprotect_dash.tools.instruction_tool import load_instruction

try:  # pragma: no cover - optional in tests
    from google.adk.agents import Agent
except Exception:  # pragma: no cover
    Agent = None  # type: ignore[assignment]


INGESTION_INSTRUCTION_PATH = CONFIG.agent_instructions_dir / "ingestion_agent_instructions.md"


def ingest_reviews_file(file_path: Path, output_path: Path) -> Path:
    dataframe = load_reviews_csv(file_path)
    insights = build_structured_insights(dataframe)
    write_structured_insights(insights, output_path)
    return output_path


if Agent is not None:  # pragma: no branch
    root_agent = Agent(
        model=CONFIG.google_genai_model,
        name="ingestion_agent",
        description="Reads a Homeprotect review CSV and produces structured insights JSON.",
        instruction=load_instruction(INGESTION_INSTRUCTION_PATH),
        tools=[ingest_reviews_file],
    )
else:  # pragma: no cover
    root_agent = None
