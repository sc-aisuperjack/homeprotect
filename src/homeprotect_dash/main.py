from __future__ import annotations

from homeprotect_dash.app import build_app
from homeprotect_dash.config import CONFIG, ensure_runtime_directories
from homeprotect_dash.services.orchestrator_service import orchestrate_pending_files


def main() -> None:
    ensure_runtime_directories()
    orchestrate_pending_files()
    app = build_app()
    app.run(host=CONFIG.host, port=CONFIG.port, debug=CONFIG.debug)


if __name__ == "__main__":
    main()
