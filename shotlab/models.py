from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Project:
    id: str
    name: str
    optional: dict[str, Any] = field(default_factory=dict)
    source_fingerprint: dict[str, Any] | None = None
    created_at: str = ""
    updated_at: str = ""
    capture_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Capture:
    id: str
    project_id: str
    capture_number: int
    source_time_ms: int
    source_pts: float | None
    image_rel_path: str
    thumbnail_rel_path: str
    analysis: dict[str, Any]
    editorial: dict[str, Any]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class VideoMetadata:
    duration_ms: int
    width: int
    height: int
    fps: float
    codec: str
    file_size: int
    fingerprint: str

    def fingerprint_payload(self) -> dict[str, Any]:
        return {
            "duration_ms": self.duration_ms,
            "width": self.width,
            "height": self.height,
            "fps": round(self.fps, 6),
            "file_size": self.file_size,
            "sample_hash": self.fingerprint,
        }


@dataclass(slots=True)
class CaptureDraft:
    id: str
    project_id: str
    source_time_ms: int
    source_pts: float | None
    image_path: str
    thumbnail_path: str
    analysis: dict[str, Any]
    editorial: dict[str, Any]

