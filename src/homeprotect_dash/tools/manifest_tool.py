from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ManifestEntry:
    filename: str
    sha256: str
    processed_at: str
    output_file: str
    status: str


@dataclass(frozen=True, slots=True)
class Manifest:
    files: list[ManifestEntry]

    def to_dict(self) -> dict[str, list[dict[str, str]]]:
        return {"files": [asdict(entry) for entry in self.files]}

    def get(self, filename: str) -> ManifestEntry | None:
        for entry in self.files:
            if entry.filename == filename:
                return entry
        return None


EMPTY_MANIFEST = Manifest(files=[])


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> Manifest:
    if not path.exists():
        return EMPTY_MANIFEST
    payload = json.loads(path.read_text(encoding="utf-8"))
    files = [ManifestEntry(**item) for item in payload.get("files", [])]
    return Manifest(files=files)


def save_manifest(path: Path, manifest: Manifest) -> None:
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")


def needs_processing(file_path: Path, manifest: Manifest) -> bool:
    current_hash = compute_sha256(file_path)
    existing = manifest.get(file_path.name)
    return existing is None or existing.sha256 != current_hash


def upsert_entry(manifest: Manifest, *, file_path: Path, output_file: Path, status: str) -> Manifest:
    current_hash = compute_sha256(file_path)
    now = datetime.now(UTC).isoformat()
    new_entry = ManifestEntry(
        filename=file_path.name,
        sha256=current_hash,
        processed_at=now,
        output_file=output_file.name,
        status=status,
    )
    retained = [entry for entry in manifest.files if entry.filename != file_path.name]
    retained.append(new_entry)
    retained.sort(key=lambda item: item.filename)
    return Manifest(files=retained)
