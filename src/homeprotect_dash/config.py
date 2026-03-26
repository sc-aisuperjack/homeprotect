from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True, slots=True)
class AppConfig:
    title: str
    host: str
    port: int
    debug: bool
    app_env: str
    google_api_key: str
    google_genai_model: str
    uploads_dir: Path
    outputs_dir: Path
    agent_instructions_dir: Path
    agent_dir: Path
    tools_dir: Path
    upload_manifest_name: str
    default_input_csv: str
    default_output_json: str

    @property
    def assets_dir(self) -> Path:
        return ROOT_DIR / "src" / "homeprotect_dash" / "assets"

    @property
    def default_input_csv_path(self) -> Path:
        return self.uploads_dir / self.default_input_csv

    @property
    def default_output_json_path(self) -> Path:
        return self.outputs_dir / self.default_output_json

    @property
    def manifest_path(self) -> Path:
        return self.uploads_dir / self.upload_manifest_name

    @property
    def insights_path(self) -> Path:
        explicit = os.getenv("HOMEPROTECT_INSIGHTS_PATH")
        if explicit:
            return Path(explicit)
        return self.default_output_json_path


CONFIG = AppConfig(
    title="Homeprotect Review Intelligence",
    host=os.getenv("APP_HOST", "127.0.0.1"),
    port=int(os.getenv("APP_PORT", "8050")),
    debug=os.getenv("APP_DEBUG", "true").lower() == "true",
    app_env=os.getenv("APP_ENV", "development"),
    google_api_key=os.getenv("GOOGLE_API_KEY", ""),
    google_genai_model=os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash"),
    uploads_dir=ROOT_DIR / os.getenv("UPLOADS_DIR", "data/raw"),
    outputs_dir=ROOT_DIR / os.getenv("OUTPUTS_DIR", "data/processed"),
    agent_instructions_dir=ROOT_DIR / os.getenv(
        "AGENT_INSTRUCTIONS_DIR", "src/homeprotect_dash/agent_instructions"
    ),
    agent_dir=ROOT_DIR / os.getenv("AGENT_DIR", "src/homeprotect_dash/agents"),
    tools_dir=ROOT_DIR / os.getenv("TOOLS_DIR", "src/homeprotect_dash/tools"),
    upload_manifest_name=os.getenv("UPLOAD_MANIFEST_NAME", "upload_manifest.json"),
    default_input_csv=os.getenv("DEFAULT_INPUT_CSV", "homeprotect_reviews.csv"),
    default_output_json=os.getenv("DEFAULT_OUTPUT_JSON", "structured_insights.json"),
)


def ensure_runtime_directories() -> None:
    CONFIG.uploads_dir.mkdir(parents=True, exist_ok=True)
    CONFIG.outputs_dir.mkdir(parents=True, exist_ok=True)
    CONFIG.agent_instructions_dir.mkdir(parents=True, exist_ok=True)
    CONFIG.agent_dir.mkdir(parents=True, exist_ok=True)
    CONFIG.tools_dir.mkdir(parents=True, exist_ok=True)
