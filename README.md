# Homeprotect Review Intelligence

A Submission for the Homeprotect AI take-home task.

This project ingests a Trustpilot review CSV, runs an agentic orchestration flow shaped around Google ADK patterns, creates a structured insights JSON file, and renders a Plotly Dash dashboard for the three required business segments: Claims, Pricing, and Customer Service.

## What this project does

The repository covers the full workflow, not just the dashboard.

It can:

- ingest Trustpilot review CSV files from `data/raw/`
- track uploaded files with a manifest to avoid unnecessary reprocessing
- process new or changed review files through an orchestration layer
- generate a structured JSON output with segment-level insights
- render a Plotly Dash dashboard from the generated insights
- support extension toward live Gemini-backed agent behaviour
- run unit tests for loaders, figures, tools, and orchestration logic

## Core flow

The application follows this contract:

```text
CSV -> orchestration -> structured_insights.json -> dashboard
```

At runtime, the system:

1. ensures required folders exist
2. checks the raw upload manifest
3. detects whether the input CSV is new or has changed
4. runs the ingestion pipeline
5. writes `data/processed/structured_insights.json`
6. launches the Dash dashboard using the latest structured insights

## Business outputs

The structured insights layer is designed to support:

- review profiling and segmentation into exactly three areas:
  - Claims
  - Pricing
  - Customer Servicing

- sentiment extraction per segment
- NPS-style inference per segment
- positive and negative theme extraction per segment
- interesting outlier insights outside the three required categories

## Project structure

```text
homeprotect/
├── .env
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── data/
│   ├── processed/
│   │   └── structured_insights.json
│   ├── raw/
│   │   ├── homeprotect_reviews.csv
│   │   └── upload_manifest.json
│   └── sample_structured_insights.json
├── src/
│   └── homeprotect_dash/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── config.py
│       ├── main.py
│       ├── agent_instructions/
│       │   ├── ingestion_agent_instructions.md
│       │   └── orchestrator_agent_instructions.md
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── ingestion_agent.py
│       │   └── orchestrator_agent.py
│       ├── assets/
│       │   └── style.css
│       ├── components/
│       │   ├── __init__.py
│       │   ├── cards.py
│       │   └── tables.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── contracts.py
│       │   ├── figures.py
│       │   └── loaders.py
│       ├── pages/
│       │   ├── __init__.py
│       │   └── dashboard.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── genai_service.py
│       │   └── orchestrator_service.py
│       └── tools/
│           ├── __init__.py
│           ├── csv_tool.py
│           ├── insight_builder_tool.py
│           ├── instruction_tool.py
│           └── manifest_tool.py
└── tests/
    ├── test_figures.py
    ├── test_loaders.py
    └── test_tools_and_orchestration.py
```

## Python version

This project targets Python 3.13.

## Environment configuration

Create a local `.env` file by copying `.env.example`.

### macOS or Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

The current example environment file is:

```dotenv
GOOGLE_API_KEY=
GOOGLE_GENAI_MODEL=gemini-3-flash-preview
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8050
APP_DEBUG=true
UPLOADS_DIR=data/raw
OUTPUTS_DIR=data/processed
AGENT_INSTRUCTIONS_DIR=src/homeprotect_dash/agent_instructions
AGENT_DIR=src/homeprotect_dash/agents
TOOLS_DIR=src/homeprotect_dash/tools
UPLOAD_MANIFEST_NAME=upload_manifest.json
DEFAULT_INPUT_CSV=homeprotect_reviews.csv
DEFAULT_OUTPUT_JSON=structured_insights.json
HOMEPROTECT_INSIGHTS_PATH="D:\pythondev\homeprotect\data\processed\structured_insights.json"
```

## Environment variables explained

`GOOGLE_API_KEY`
Optional. Required only if you want to enable live Gemini-backed behaviour.

`GOOGLE_GENAI_MODEL`
The Gemini model name used by the GenAI service when live model integration is enabled.

`APP_ENV`
Application environment name, `development`.

`APP_HOST`
Host address used by the Dash server.

`APP_PORT`
Port used by the Dash server.

`APP_DEBUG`
Enables Dash debug mode during development.

`UPLOADS_DIR`
Folder containing raw uploaded CSV files.

`OUTPUTS_DIR`
Folder where processed outputs are written.

`AGENT_INSTRUCTIONS_DIR`
Directory containing markdown instruction files for the agents.

`AGENT_DIR`
Directory containing the agent modules.

`TOOLS_DIR`
Directory containing tool modules used by orchestration.

`UPLOAD_MANIFEST_NAME`
Manifest filename used to track processed uploads and file hashes.

`DEFAULT_INPUT_CSV`
Default raw input filename expected in `data/raw/`.

`DEFAULT_OUTPUT_JSON`
Default processed output filename written to `data/processed/`.

`HOMEPROTECT_INSIGHTS_PATH`
Optional absolute path override pointing directly to the structured insights JSON file. This is useful on Windows when running the dashboard against a known output location.

## Installation

Create and activate a virtual environment.

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS or Linux

```bash
source .venv/bin/activate
```

Upgrade pip and install the project.

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Running the application

Run the full application with:

```bash
python -m homeprotect_dash
```

This will:

- ensure runtime folders exist
- process new or changed CSV files in `data/raw/`
- generate or refresh `data/processed/structured_insights.json`
- launch the Plotly Dash application

Open the local URL printed in the terminal, typically:

```text
http://127.0.0.1:8050
```

## Input data

Place the review CSV in:

```text
data/raw/homeprotect_reviews.csv
```

The orchestrator uses the upload manifest to detect whether the file is new or has changed. If the SHA256 hash differs from the recorded value, the pipeline rebuilds the structured insights output and updates the manifest.

## Output data

The main processed output is:

```text
data/processed/structured_insights.json
```

A sample reference file is also included:

```text
data/sample_structured_insights.json
```

The dashboard reads the structured output rather than parsing the CSV directly. That keeps the UI layer cleaner and stops it turning into spaghetti with charts.

## Agentic architecture

The project is organised around ADK-style separation of concerns:

### Agents

- `agents/orchestrator_agent.py`
- `agents/ingestion_agent.py`

These define the high-level responsibilities for workflow coordination and review ingestion.

### Tools

- `tools/csv_tool.py`
- `tools/insight_builder_tool.py`
- `tools/instruction_tool.py`
- `tools/manifest_tool.py`

These provide reusable units for reading source data, building structured insight outputs, loading agent instructions, and maintaining the upload manifest.

### Services

- `services/orchestrator_service.py`
- `services/genai_service.py`

These contain the operational logic used to coordinate orchestration and optional model-backed behaviour.

### Agent instructions

- `agent_instructions/ingestion_agent_instructions.md`
- `agent_instructions/orchestrator_agent_instructions.md`

These store the instruction prompts and behavioural guidance for the agent layer.

## Deterministic processing and model-backed extension

The local pipeline is intentionally deterministic so the application can run cleanly without requiring live LLM calls.

That means:

- the app can process the CSV and build dashboard data locally
- tests can run without network dependence

If `GOOGLE_API_KEY` is configured, the project is also structured so Gemini-backed behaviour can be introduced through the existing services and agent modules.

## Running tests

Run the full test suite with:

```bash
pytest
```

The tests currently cover:

- figure generation
- data loading
- tools
- orchestration flow

## Linting and type checking

Run linting with:

```bash
ruff check .
```

Run type checking with:

```bash
mypy src
```

## Development notes

A few important implementation details:

- the dashboard does not directly parse the raw CSV
- the manifest prevents unnecessary reprocessing
- the JSON output acts as the contract between the agentic pipeline and the dashboard
- the structure is intentionally modular so the solution can be extended with richer agents, improved classification, or more advanced insight generation later

## Typical local workflow

1. copy `.env.example` to `.env`
2. add a Gemini API key if required
3. place the latest Trustpilot CSV in `data/raw/`
4. run `python -m homeprotect_dash`
5. inspect the dashboard in the browser
6. rerun after CSV changes to regenerate insights

## Submission summary

This repository provides:

- a Python 3.13 codebase
- a Dash front end suitable for stakeholder review
- ADK agents, tools, and orchestration modules
- structured business insight generation from review data
- automated change detection via manifest hashing
- test coverage for the core data and orchestration paths
