from __future__ import annotations

from contextlib import closing
import json
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .config import SCHEMA_VERSION
from .repository import Repository


class BackupError(RuntimeError):
    pass


def export_library(repository: Repository, destination: Path) -> Path:
    destination = Path(destination)
    if destination.suffix.lower() != ".shotlab":
        destination = destination.with_suffix(".shotlab")
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="shotlab-export-") as temporary:
        staging = Path(temporary)
        database_copy = staging / "database.sqlite"
        with (
            closing(sqlite3.connect(repository.database_path)) as source,
            closing(sqlite3.connect(database_copy)) as target,
        ):
            source.backup(target)
            target.commit()

        manifest = {
            "format": "shotlab-library",
            "format_version": 1,
            "schema_version": SCHEMA_VERSION,
            "shotlab_version": __version__,
            "exported_at": datetime.now(UTC).isoformat(),
            "includes_source_video": False,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        temporary_archive = destination.with_suffix(".shotlab.tmp")
        with zipfile.ZipFile(
            temporary_archive,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            archive.write(staging / "manifest.json", "manifest.json")
            archive.write(database_copy, "database.sqlite")
            projects_root = repository.data_root / "projects"
            if projects_root.is_dir():
                for path in projects_root.rglob("*"):
                    if not path.is_file():
                        continue
                    relative = path.relative_to(projects_root)
                    if ".drafts" in relative.parts or "cache" in relative.parts:
                        continue
                    archive.write(path, (Path("projects") / relative).as_posix())
        temporary_archive.replace(destination)
    return destination


def restore_library(repository: Repository, archive_path: Path) -> Path:
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise BackupError("Backup file not found.")

    with tempfile.TemporaryDirectory(prefix="shotlab-import-") as temporary:
        staging = Path(temporary)
        with zipfile.ZipFile(archive_path, "r") as archive:
            for info in archive.infolist():
                target = (staging / info.filename).resolve()
                try:
                    target.relative_to(staging.resolve())
                except ValueError as exc:
                    raise BackupError("Unsafe path found in backup.") from exc
            archive.extractall(staging)

        manifest_path = staging / "manifest.json"
        database_path = staging / "database.sqlite"
        if not manifest_path.is_file() or not database_path.is_file():
            raise BackupError("This is not a complete ShotLab backup.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("format") != "shotlab-library":
            raise BackupError("Unsupported backup format.")
        if int(manifest.get("schema_version", -1)) > SCHEMA_VERSION:
            raise BackupError("Backup schema is newer than this ShotLab version.")

        with closing(sqlite3.connect(database_path)) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise BackupError("Backup database integrity check failed.")

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        recovery = repository.data_root / "recovery" / timestamp
        recovery.mkdir(parents=True, exist_ok=False)
        current_projects = repository.data_root / "projects"
        imported_projects = staging / "projects"

        if repository.database_path.is_file():
            shutil.copy2(repository.database_path, recovery / "shotlab.db")
        if current_projects.is_dir():
            shutil.copytree(
                current_projects,
                recovery / "projects",
                dirs_exist_ok=True,
            )

        try:
            shutil.copy2(database_path, repository.database_path)
            if current_projects.exists():
                shutil.rmtree(current_projects)
            if imported_projects.is_dir():
                shutil.copytree(imported_projects, current_projects)
            else:
                current_projects.mkdir(parents=True)
        except Exception:
            recovery_database = recovery / "shotlab.db"
            recovery_projects = recovery / "projects"
            if recovery_database.is_file():
                shutil.copy2(recovery_database, repository.database_path)
            if current_projects.exists():
                shutil.rmtree(current_projects)
            if recovery_projects.is_dir():
                shutil.copytree(recovery_projects, current_projects)
            raise

        repository._initialize()
        return recovery
