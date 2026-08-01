from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import json
import re
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .analysis import aggregate_palette, closest_palette_distance
from .config import SCHEMA_VERSION, ensure_data_tree
from .i18n import OPTIONS
from .models import Capture, CaptureDraft, Project


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    optional_json TEXT NOT NULL DEFAULT '{}',
    source_fingerprint_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS captures (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    capture_number INTEGER NOT NULL,
    source_time_ms INTEGER NOT NULL,
    source_pts REAL,
    image_rel_path TEXT NOT NULL,
    thumbnail_rel_path TEXT NOT NULL,
    analysis_json TEXT NOT NULL,
    editorial_json TEXT NOT NULL,
    annotations_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, capture_number)
);

CREATE INDEX IF NOT EXISTS idx_capture_project ON captures(project_id);
CREATE INDEX IF NOT EXISTS idx_capture_time ON captures(project_id, source_time_ms);
"""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _clean_editorial(editorial: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(editorial)
    cleaned.pop("backlight", None)
    return cleaned


HEX_COLOR_PATTERN = re.compile(
    r"(?<![0-9A-Za-z])#?([0-9a-fA-F]{6})(?![0-9A-Za-z])"
)
COLOR_SIMILARITY_THRESHOLD = 26.0


def _normalize_hex_color(value: str) -> str | None:
    match = HEX_COLOR_PATTERN.fullmatch(str(value).strip())
    return f"#{match.group(1).upper()}" if match else None


class Repository:
    def __init__(self, data_root: Path) -> None:
        self.data_root = Path(data_root).resolve()
        ensure_data_tree(self.data_root)
        self.database_path = self.data_root / "shotlab.db"
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        except Exception:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)
            columns = {
                str(row["name"])
                for row in connection.execute(
                    "PRAGMA table_info(captures)"
                ).fetchall()
            }
            if "annotations_json" not in columns:
                connection.execute(
                    "ALTER TABLE captures ADD COLUMN "
                    "annotations_json TEXT NOT NULL DEFAULT '[]'"
                )
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def project_folder(self, project_id: str) -> Path:
        return self.data_root / "projects" / project_id

    def create_project(
        self,
        name: str,
        optional: dict[str, Any] | None = None,
    ) -> Project:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Library name is required.")

        project_id = uuid.uuid4().hex
        now = _utc_now()
        folder = self.project_folder(project_id)
        try:
            (folder / "captures" / "full").mkdir(parents=True, exist_ok=False)
            (folder / "captures" / "thumbnails").mkdir(parents=True)
            (folder / ".drafts").mkdir(parents=True)
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO projects (
                        id, name, optional_json, source_fingerprint_json,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, NULL, ?, ?)
                    """,
                    (
                        project_id,
                        clean_name,
                        json.dumps(optional or {}, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
        except Exception:
            shutil.rmtree(folder, ignore_errors=True)
            raise

        project = self.get_project(project_id)
        if project is None:
            raise RuntimeError("Library creation failed.")
        self.write_manifest(project_id)
        return project

    def list_projects(self) -> list[Project]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT p.*,
                       (SELECT COUNT(*) FROM captures c WHERE c.project_id = p.id)
                       AS capture_count
                FROM projects p
                ORDER BY p.updated_at DESC
                """
            ).fetchall()
        return [self._project_from_row(row) for row in rows]

    def get_project(self, project_id: str) -> Project | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT p.*,
                       (SELECT COUNT(*) FROM captures c WHERE c.project_id = p.id)
                       AS capture_count
                FROM projects p
                WHERE p.id = ?
                """,
                (project_id,),
            ).fetchone()
        return self._project_from_row(row) if row else None

    def rename_project(self, project_id: str, name: str) -> Project:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Library name is required.")
        with self._connect() as connection:
            connection.execute(
                "UPDATE projects SET name = ?, updated_at = ? WHERE id = ?",
                (clean_name, _utc_now(), project_id),
            )
        self.write_manifest(project_id)
        project = self.get_project(project_id)
        if project is None:
            raise KeyError(project_id)
        return project

    def delete_project(self, project_id: str) -> Path:
        if self.get_project(project_id) is None:
            raise KeyError(project_id)

        folder = self.project_folder(project_id)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        recovery = (
            self.data_root
            / "recovery"
            / "deleted-projects"
            / f"{timestamp}_{project_id}"
        )
        recovery.parent.mkdir(parents=True, exist_ok=True)
        if recovery.exists():
            recovery = recovery.with_name(f"{recovery.name}_{uuid.uuid4().hex[:8]}")

        moved = False
        if folder.exists():
            shutil.move(str(folder), str(recovery))
            moved = True
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    "DELETE FROM projects WHERE id = ?",
                    (project_id,),
                )
                if cursor.rowcount != 1:
                    raise KeyError(project_id)
            if self.get_project(project_id) is not None:
                raise RuntimeError("Library deletion did not persist.")
        except Exception:
            if moved and recovery.exists():
                shutil.move(str(recovery), str(folder))
            raise
        return recovery

    def set_source_fingerprint(
        self,
        project_id: str,
        fingerprint: dict[str, Any],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE projects
                SET source_fingerprint_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    json.dumps(fingerprint, ensure_ascii=False),
                    _utc_now(),
                    project_id,
                ),
            )
        self.write_manifest(project_id)

    def next_capture_number(self, project_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(MAX(capture_number), 0) + 1 AS next_number
                FROM captures WHERE project_id = ?
                """,
                (project_id,),
            ).fetchone()
        return int(row["next_number"])

    def confirm_draft(
        self,
        draft: CaptureDraft,
        editorial: dict[str, Any],
    ) -> Capture:
        if self.get_project(draft.project_id) is None:
            raise KeyError(draft.project_id)

        draft_image = Path(draft.image_path)
        draft_thumb = Path(draft.thumbnail_path)
        if not draft_image.is_file() or not draft_thumb.is_file():
            raise FileNotFoundError("Draft images are missing.")

        capture_id = uuid.uuid4().hex
        number = self.next_capture_number(draft.project_id)
        token = f"{draft.source_time_ms:012d}"
        full_name = f"capture_{number:05d}_{token}.jpg"
        thumb_name = f"capture_{number:05d}_{token}_thumb.jpg"
        folder = self.project_folder(draft.project_id)
        final_image = folder / "captures" / "full" / full_name
        final_thumb = folder / "captures" / "thumbnails" / thumb_name
        image_rel = final_image.relative_to(folder).as_posix()
        thumb_rel = final_thumb.relative_to(folder).as_posix()
        now = _utc_now()

        shutil.move(str(draft_image), str(final_image))
        shutil.move(str(draft_thumb), str(final_thumb))
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO captures (
                        id, project_id, capture_number, source_time_ms,
                        source_pts, image_rel_path, thumbnail_rel_path,
                        analysis_json, editorial_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        capture_id,
                        draft.project_id,
                        number,
                        draft.source_time_ms,
                        draft.source_pts,
                        image_rel,
                        thumb_rel,
                        json.dumps(draft.analysis, ensure_ascii=False),
                        json.dumps(
                            _clean_editorial(editorial),
                            ensure_ascii=False,
                        ),
                        now,
                        now,
                    ),
                )
                connection.execute(
                    "UPDATE projects SET updated_at = ? WHERE id = ?",
                    (now, draft.project_id),
                )
        except Exception:
            shutil.move(str(final_image), str(draft_image))
            shutil.move(str(final_thumb), str(draft_thumb))
            raise

        self.write_manifest(draft.project_id)
        capture = self.get_capture(capture_id)
        if capture is None:
            raise RuntimeError("Capture confirmation failed.")
        return capture

    def update_capture_editorial(
        self,
        capture_id: str,
        editorial: dict[str, Any],
    ) -> Capture:
        now = _utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT project_id FROM captures WHERE id = ?",
                (capture_id,),
            ).fetchone()
            if not row:
                raise KeyError(capture_id)
            project_id = str(row["project_id"])
            connection.execute(
                """
                UPDATE captures
                SET editorial_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    json.dumps(
                        _clean_editorial(editorial),
                        ensure_ascii=False,
                    ),
                    now,
                    capture_id,
                ),
            )
            connection.execute(
                "UPDATE projects SET updated_at = ? WHERE id = ?",
                (now, project_id),
            )
        self.write_manifest(project_id)
        capture = self.get_capture(capture_id)
        if capture is None:
            raise KeyError(capture_id)
        return capture

    def update_capture_analysis(
        self,
        capture_id: str,
        analysis: dict[str, Any],
    ) -> Capture:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT project_id FROM captures WHERE id = ?",
                (capture_id,),
            ).fetchone()
            if not row:
                raise KeyError(capture_id)
            project_id = str(row["project_id"])
            connection.execute(
                """
                UPDATE captures
                SET analysis_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    json.dumps(analysis, ensure_ascii=False),
                    _utc_now(),
                    capture_id,
                ),
            )
        self.write_manifest(project_id)
        capture = self.get_capture(capture_id)
        if capture is None:
            raise KeyError(capture_id)
        return capture

    def update_capture_annotations(
        self,
        capture_id: str,
        annotations: list[dict[str, Any]],
    ) -> Capture:
        now = _utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT project_id FROM captures WHERE id = ?",
                (capture_id,),
            ).fetchone()
            if not row:
                raise KeyError(capture_id)
            project_id = str(row["project_id"])
            connection.execute(
                """
                UPDATE captures
                SET annotations_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    json.dumps(annotations, ensure_ascii=False),
                    now,
                    capture_id,
                ),
            )
            connection.execute(
                "UPDATE projects SET updated_at = ? WHERE id = ?",
                (now, project_id),
            )
        self.write_manifest(project_id)
        capture = self.get_capture(capture_id)
        if capture is None:
            raise KeyError(capture_id)
        return capture

    def delete_capture(self, capture_id: str) -> Path:
        capture = self.get_capture(capture_id)
        if capture is None:
            raise KeyError(capture_id)

        image_path = self.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
        thumbnail_path = self.resolve_project_file(
            capture.project_id,
            capture.thumbnail_rel_path,
        )
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        recovery = (
            self.data_root
            / "recovery"
            / "deleted-frames"
            / f"{timestamp}_{capture.id}"
        )
        recovery.mkdir(parents=True, exist_ok=False)

        moved_files: list[tuple[Path, Path]] = []
        try:
            for source in (
                image_path,
                thumbnail_path,
                self.annotated_image_path(capture),
                self.annotated_thumbnail_path(capture),
            ):
                if not source.is_file():
                    continue
                destination = recovery / source.name
                shutil.move(str(source), str(destination))
                moved_files.append((source, destination))

            with self._connect() as connection:
                cursor = connection.execute(
                    "DELETE FROM captures WHERE id = ?",
                    (capture.id,),
                )
                if cursor.rowcount != 1:
                    raise KeyError(capture.id)
                connection.execute(
                    "UPDATE projects SET updated_at = ? WHERE id = ?",
                    (_utc_now(), capture.project_id),
                )
            if self.get_capture(capture.id) is not None:
                raise RuntimeError("Frame deletion did not persist.")
        except Exception:
            for source, destination in reversed(moved_files):
                if destination.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
            try:
                recovery.rmdir()
            except OSError:
                pass
            raise

        try:
            self.write_manifest(capture.project_id)
        except OSError:
            pass
        return recovery

    def get_capture(self, capture_id: str) -> Capture | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM captures WHERE id = ?",
                (capture_id,),
            ).fetchone()
        return self._capture_from_row(row) if row else None

    def list_captures(self, project_id: str) -> list[Capture]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM captures
                WHERE project_id = ?
                ORDER BY capture_number
                """,
                (project_id,),
            ).fetchall()
        return [self._capture_from_row(row) for row in rows]

    def project_palette(
        self,
        project_id: str,
        count: int = 5,
    ) -> list[str]:
        return aggregate_palette(
            [
                capture.analysis
                for capture in self.list_captures(project_id)
            ],
            count,
        )

    def list_all_captures(self) -> list[Capture]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT c.* FROM captures c
                JOIN projects p ON p.id = c.project_id
                ORDER BY p.updated_at DESC, c.capture_number
                """
            ).fetchall()
        return [self._capture_from_row(row) for row in rows]

    def search_captures(
        self,
        query: str,
        project_id: str | None = None,
    ) -> list[Capture]:
        color_targets = [
            f"#{match.group(1).upper()}"
            for match in HEX_COLOR_PATTERN.finditer(query)
        ]
        text_query = HEX_COLOR_PATTERN.sub(" ", query)
        terms = [
            term.strip()
            for term in text_query.replace("،", " ").split()
            if term.strip()
        ]
        if not terms:
            captures = (
                self.list_captures(project_id)
                if project_id
                else self.list_all_captures()
            )
            return (
                self._similar_color_matches(captures, color_targets)
                if color_targets
                else []
            )

        clauses: list[str] = []
        values: list[Any] = []
        for term in terms:
            variants = {term}
            folded = term.casefold()
            for options in OPTIONS.values():
                for value, fa_label, en_label in options:
                    if not value:
                        continue
                    labels = (value, fa_label, en_label)
                    if any(folded in label.casefold() for label in labels):
                        variants.add(value)
            variant_clauses: list[str] = []
            for variant in sorted(variants):
                pattern = f"%{variant}%"
                variant_clauses.append(
                    """
                    (
                        p.name LIKE ? COLLATE NOCASE OR
                        c.editorial_json LIKE ? COLLATE NOCASE OR
                        c.analysis_json LIKE ? COLLATE NOCASE
                    )
                    """
                )
                values.extend([pattern, pattern, pattern])
            clauses.append(f"({' OR '.join(variant_clauses)})")
        if project_id:
            clauses.append("c.project_id = ?")
            values.append(project_id)

        sql = (
            "SELECT c.* FROM captures c "
            "JOIN projects p ON p.id = c.project_id "
            f"WHERE {' AND '.join(clauses)} "
            "ORDER BY p.updated_at DESC, c.capture_number"
        )
        with self._connect() as connection:
            rows = connection.execute(sql, values).fetchall()
        captures = [self._capture_from_row(row) for row in rows]
        return (
            self._similar_color_matches(captures, color_targets)
            if color_targets
            else captures
        )

    @staticmethod
    def _similar_color_matches(
        captures: list[Capture],
        targets: list[str],
    ) -> list[Capture]:
        if not targets:
            return captures
        scored: list[tuple[float, Capture]] = []
        for capture in captures:
            colors = [
                str(color)
                for color in capture.analysis.get("dominant_colors", [])
            ][:2]
            distances = [
                closest_palette_distance(colors, target)
                for target in targets
            ]
            if all(
                distance <= COLOR_SIMILARITY_THRESHOLD
                for distance in distances
            ):
                scored.append((sum(distances), capture))
        scored.sort(key=lambda item: item[0])
        return [capture for _, capture in scored]

    def filter_captures(
        self,
        query: str = "",
        filters: dict[str, object] | None = None,
        project_id: str | None = None,
        color_hex: str | None = None,
    ) -> list[Capture]:
        captures = (
            self.search_captures(query, project_id)
            if query.strip()
            else self.list_captures(project_id)
            if project_id
            else self.list_all_captures()
        )
        active_filters = filters or {}
        def matches(capture: Capture) -> bool:
            for key, expected in active_filters.items():
                actual = capture.editorial.get(key)
                if str(actual or "") != str(expected):
                    return False
            return True

        if active_filters:
            captures = [
                capture
                for capture in captures
                if matches(capture)
            ]
        if color_hex:
            normalized_color = _normalize_hex_color(color_hex)
            captures = self._similar_color_matches(
                captures,
                [normalized_color or color_hex.upper()],
            )
        return captures

    def project_thumbnails(self, project_id: str, limit: int = 4) -> list[Path]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM captures
                WHERE project_id = ?
                ORDER BY capture_number DESC
                LIMIT ?
                """,
                (project_id, max(1, int(limit))),
            ).fetchall()
        return [
            self.display_thumbnail_path(self._capture_from_row(row))
            for row in reversed(rows)
        ]

    def annotated_image_path(self, capture: Capture) -> Path:
        return (
            self.project_folder(capture.project_id)
            / "captures"
            / "annotated"
            / f"{capture.id}.png"
        )

    def annotated_thumbnail_path(self, capture: Capture) -> Path:
        return (
            self.project_folder(capture.project_id)
            / "captures"
            / "annotated"
            / f"{capture.id}_thumb.png"
        )

    def display_image_path(self, capture: Capture) -> Path:
        annotated = self.annotated_image_path(capture)
        if capture.annotations and annotated.is_file():
            return annotated
        return self.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )

    def display_thumbnail_path(self, capture: Capture) -> Path:
        annotated = self.annotated_thumbnail_path(capture)
        if capture.annotations and annotated.is_file():
            return annotated
        return self.resolve_project_file(
            capture.project_id,
            capture.thumbnail_rel_path,
        )

    def discard_draft(self, draft: CaptureDraft) -> None:
        Path(draft.image_path).unlink(missing_ok=True)
        Path(draft.thumbnail_path).unlink(missing_ok=True)

    def resolve_project_file(self, project_id: str, relative_path: str) -> Path:
        folder = self.project_folder(project_id).resolve()
        candidate = (folder / relative_path).resolve()
        candidate.relative_to(folder)
        return candidate

    def write_manifest(self, project_id: str) -> Path:
        project = self.get_project(project_id)
        if project is None:
            raise KeyError(project_id)
        captures = self.list_captures(project_id)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "project": project.to_dict(),
            "captures": [capture.to_dict() for capture in captures],
            "updated_at": _utc_now(),
        }
        folder = self.project_folder(project_id)
        target = folder / "project.json"
        temporary = folder / "project.json.tmp"
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(target)
        return target

    @staticmethod
    def _project_from_row(row: sqlite3.Row) -> Project:
        return Project(
            id=str(row["id"]),
            name=str(row["name"]),
            optional=json.loads(row["optional_json"] or "{}"),
            source_fingerprint=(
                json.loads(row["source_fingerprint_json"])
                if row["source_fingerprint_json"]
                else None
            ),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
            capture_count=int(row["capture_count"]),
        )

    @staticmethod
    def _capture_from_row(row: sqlite3.Row) -> Capture:
        editorial = _clean_editorial(json.loads(row["editorial_json"]))
        return Capture(
            id=str(row["id"]),
            project_id=str(row["project_id"]),
            capture_number=int(row["capture_number"]),
            source_time_ms=int(row["source_time_ms"]),
            source_pts=(
                float(row["source_pts"]) if row["source_pts"] is not None else None
            ),
            image_rel_path=str(row["image_rel_path"]),
            thumbnail_rel_path=str(row["thumbnail_rel_path"]),
            analysis=json.loads(row["analysis_json"]),
            editorial=editorial,
            annotations=(
                json.loads(row["annotations_json"] or "[]")
                if "annotations_json" in row.keys()
                else []
            ),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )
