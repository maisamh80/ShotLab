from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "ShotLab"
SCHEMA_VERSION = 1


def default_data_root() -> Path:
    override = os.environ.get("SHOTLAB_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / APP_NAME


def ensure_data_tree(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "projects").mkdir(exist_ok=True)
    (root / "cache").mkdir(exist_ok=True)


def configure_bundled_tools() -> None:
    """Expose bundled FFmpeg binaries to subprocesses in packaged builds."""
    candidates: list[Path] = []
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.append(Path(bundle_root) / "tools" / "ffmpeg")
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "tools" / "ffmpeg")

    for directory in candidates:
        if directory.is_dir():
            current = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{directory}{os.pathsep}{current}"
            break
