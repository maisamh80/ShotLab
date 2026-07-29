from __future__ import annotations

import uuid
import shutil
from dataclasses import dataclass
from pathlib import Path

from .analysis import analyze_image, make_thumbnail, prepare_imported_image
from .media import extract_frame, fingerprints_match, probe_video, resolve_frame_pts
from .models import CaptureDraft, Project, VideoMetadata
from .repository import Repository


@dataclass(slots=True)
class SessionVideo:
    path: Path
    metadata: VideoMetadata


class CaptureSession:
    """Keeps source bytes out of storage and opens a local path per session."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.project_id: str | None = None
        self.video: SessionVideo | None = None

    def open_project(self, project_id: str) -> Project:
        project = self.repository.get_project(project_id)
        if project is None:
            raise KeyError(project_id)
        self.close_video()
        self.project_id = project_id
        return project

    def attach_video(self, source_path: Path, allow_mismatch: bool = False) -> VideoMetadata:
        if self.project_id is None:
            raise RuntimeError("Open a library before attaching a video.")
        metadata = probe_video(source_path)
        project = self.repository.get_project(self.project_id)
        if project is None:
            raise KeyError(self.project_id)

        if project.source_fingerprint:
            if not fingerprints_match(project.source_fingerprint, metadata):
                if not allow_mismatch:
                    raise ValueError("SOURCE_FINGERPRINT_MISMATCH")
                self.repository.set_source_fingerprint(
                    self.project_id,
                    metadata.fingerprint_payload(),
                )
        else:
            self.repository.set_source_fingerprint(
                self.project_id,
                metadata.fingerprint_payload(),
            )

        # The active path lives here; the UI may remember it in local settings.
        self.video = SessionVideo(Path(source_path).resolve(), metadata)
        return metadata

    def close_video(self) -> None:
        self.video = None

    def close_project(self) -> None:
        self.close_video()
        self.project_id = None

    def create_draft(
        self,
        time_ms: int,
        storage_mode: str = "medium",
    ) -> CaptureDraft:
        if self.project_id is None or self.video is None:
            raise RuntimeError("No video is attached to the current library.")
        if storage_mode not in {"actual", "medium", "small"}:
            raise ValueError(f"Unsupported frame storage mode: {storage_mode}")

        requested_time = max(0, min(int(time_ms), self.video.metadata.duration_ms))
        source_pts = resolve_frame_pts(self.video.path, requested_time)
        safe_time = max(
            0,
            min(round(source_pts * 1000), self.video.metadata.duration_ms),
        )
        draft_id = uuid.uuid4().hex
        folder = self.repository.project_folder(self.project_id) / ".drafts"
        image_path = folder / f"{draft_id}.jpg"
        thumbnail_path = folder / f"{draft_id}_thumb.jpg"
        max_width = {
            "actual": None,
            "medium": 1280,
            "small": 720,
        }[storage_mode]
        extract_frame(
            self.video.path,
            safe_time,
            image_path,
            max_width=max_width,
        )
        return self._build_draft(
            draft_id,
            safe_time,
            source_pts,
            image_path,
            thumbnail_path,
        )

    def create_draft_from_displayed_frame(
        self,
        time_ms: int,
        displayed_image_path: Path,
    ) -> CaptureDraft:
        """Create a draft from the exact pixels currently shown by Qt."""
        if self.project_id is None or self.video is None:
            raise RuntimeError("No video is attached to the current library.")
        displayed_image_path = Path(displayed_image_path)
        if not displayed_image_path.is_file():
            raise FileNotFoundError("The displayed video frame is unavailable.")

        safe_time = max(0, min(int(time_ms), self.video.metadata.duration_ms))
        draft_id = uuid.uuid4().hex
        folder = self.repository.project_folder(self.project_id) / ".drafts"
        image_path = folder / f"{draft_id}.jpg"
        thumbnail_path = folder / f"{draft_id}_thumb.jpg"
        shutil.copy2(displayed_image_path, image_path)
        displayed_image_path.unlink(missing_ok=True)
        return self._build_draft(
            draft_id,
            safe_time,
            safe_time / 1000.0,
            image_path,
            thumbnail_path,
        )

    def create_draft_from_source_frame(
        self,
        time_ms: int,
        displayed_image_path: Path,
        storage_mode: str,
    ) -> CaptureDraft:
        """Extract the displayed frame time from the source at the chosen size."""
        if self.project_id is None or self.video is None:
            raise RuntimeError("No video is attached to the current library.")
        displayed_image_path = Path(displayed_image_path)
        if not displayed_image_path.is_file():
            raise FileNotFoundError("The displayed video frame is unavailable.")
        if storage_mode not in {"actual", "medium", "small"}:
            raise ValueError(f"Unsupported frame storage mode: {storage_mode}")

        safe_time = max(0, min(int(time_ms), self.video.metadata.duration_ms))
        draft_id = uuid.uuid4().hex
        folder = self.repository.project_folder(self.project_id) / ".drafts"
        image_path = folder / f"{draft_id}.jpg"
        thumbnail_path = folder / f"{draft_id}_thumb.jpg"
        max_width = {
            "actual": None,
            "medium": 1280,
            "small": 720,
        }[storage_mode]
        try:
            extract_frame(
                self.video.path,
                safe_time,
                image_path,
                max_width=max_width,
            )
        finally:
            displayed_image_path.unlink(missing_ok=True)
        return self._build_draft(
            draft_id,
            safe_time,
            safe_time / 1000.0,
            image_path,
            thumbnail_path,
        )

    def create_draft_from_image(
        self,
        source_path: Path,
        storage_mode: str,
    ) -> CaptureDraft:
        """Create an editable draft from a still image selected by the user."""
        if self.project_id is None:
            raise RuntimeError("Open a library before importing an image.")
        source_path = Path(source_path)
        if not source_path.is_file():
            raise FileNotFoundError("The selected image is unavailable.")
        if storage_mode not in {"actual", "medium", "small"}:
            raise ValueError(f"Unsupported frame storage mode: {storage_mode}")

        draft_id = uuid.uuid4().hex
        folder = self.repository.project_folder(self.project_id) / ".drafts"
        image_path = folder / f"{draft_id}.jpg"
        thumbnail_path = folder / f"{draft_id}_thumb.jpg"
        max_width = {
            "actual": None,
            "medium": 1280,
            "small": 720,
        }[storage_mode]
        try:
            prepare_imported_image(
                source_path,
                image_path,
                max_width=max_width,
            )
            draft = self._build_draft(
                draft_id,
                0,
                None,
                image_path,
                thumbnail_path,
            )
        except Exception:
            image_path.unlink(missing_ok=True)
            thumbnail_path.unlink(missing_ok=True)
            raise
        return draft

    def _build_draft(
        self,
        draft_id: str,
        safe_time: int,
        source_pts: float | None,
        image_path: Path,
        thumbnail_path: Path,
    ) -> CaptureDraft:
        if self.project_id is None:
            raise RuntimeError("No library is open.")
        make_thumbnail(image_path, thumbnail_path)
        analysis = analyze_image(image_path)
        editorial = {
            "title": "",
            "shot_size": "",
            "camera_angle": "",
            "location_type": "",
            "lens_type": "",
            "time_of_day": "",
            "lighting_style": "",
            "key_direction": "",
            "key_quality": "",
            "mood": [],
            "tags": [],
            "notes": "",
        }
        return CaptureDraft(
            id=draft_id,
            project_id=self.project_id,
            source_time_ms=safe_time,
            source_pts=source_pts,
            image_path=str(image_path),
            thumbnail_path=str(thumbnail_path),
            analysis=analysis,
            editorial=editorial,
        )
