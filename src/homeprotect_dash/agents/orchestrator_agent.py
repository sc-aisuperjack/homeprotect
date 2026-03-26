from __future__ import annotations

from homeprotect_dash.config import CONFIG
from homeprotect_dash.services.orchestrator_service import orchestrate_pending_files
from homeprotect_dash.tools.instruction_tool import load_instruction

try:  # pragma: no cover - optional in tests
    from google.adk.agents import Agent
except Exception:  # pragma: no cover
    Agent = None  # type: ignore[assignment]


ORCHESTRATOR_INSTRUCTION_PATH = CONFIG.agent_instructions_dir / "orchestrator_agent_instructions.md"


if Agent is not None:  # pragma: no branch
    root_agent = Agent(
        model=CONFIG.google_genai_model,
        name="orchestrator_agent",
        description="Checks raw uploads, compares them to the manifest, and triggers ingestion when needed.",
        instruction=load_instruction(ORCHESTRATOR_INSTRUCTION_PATH),
        tools=[orchestrate_pending_files],
    )
else:  # pragma: no cover
    root_agent = None
