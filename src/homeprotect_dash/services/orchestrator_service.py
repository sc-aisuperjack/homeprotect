from __future__ import annotations

from pathlib import Path

from homeprotect_dash.config import CONFIG
from homeprotect_dash.tools.csv_tool import list_csv_files
from homeprotect_dash.tools.manifest_tool import (
    load_manifest,
    needs_processing,
    save_manifest,
    upsert_entry,
)
from homeprotect_dash.agents.ingestion_agent import ingest_reviews_file


def orchestrate_pending_files() -> list[Path]:
    manifest = load_manifest(CONFIG.manifest_path)
    processed_outputs: list[Path] = []
    csv_files = list_csv_files(CONFIG.uploads_dir)
    for file_path in csv_files:
        if not needs_processing(file_path, manifest):
            continue
        output_path = CONFIG.outputs_dir / CONFIG.default_output_json
        ingest_reviews_file(file_path=file_path, output_path=output_path)
        manifest = upsert_entry(
            manifest,
            file_path=file_path,
            output_file=output_path,
            status="processed",
        )
        processed_outputs.append(output_path)
    save_manifest(CONFIG.manifest_path, manifest)
    return processed_outputs
