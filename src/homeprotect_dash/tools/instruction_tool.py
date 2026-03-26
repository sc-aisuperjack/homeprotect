from __future__ import annotations

from pathlib import Path


class InstructionNotFoundError(FileNotFoundError):
    """Raised when an agent instruction file is missing."""


def load_instruction(path: Path) -> str:
    if not path.exists():
        raise InstructionNotFoundError(f"Instruction file not found: {path}")
    return path.read_text(encoding="utf-8").strip()
