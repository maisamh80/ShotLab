from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from .models import VideoMetadata


class MediaError(RuntimeError):
    pass


def format_timecode(milliseconds: int, fps: float) -> str:
    """Format milliseconds as an HH:MM:SS:FF video timecode."""
    safe_ms = max(0, int(milliseconds))
    total_seconds, remainder_ms = divmod(safe_ms, 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    safe_fps = fps if fps > 0 else 24.0
    frames = min(
        round((remainder_ms / 1000) * safe_fps),
        max(0, round(safe_fps) - 1),
    )
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


def require_ffmpeg() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise MediaError("FFmpeg and FFprobe are required.")


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError as exc:
        raise MediaError("FFmpeg was not found.") from exc


def _sample_hash(path: Path, chunk_size: int = 65536) -> str:
    size = path.stat().st_size
    offsets = sorted({0, max(0, size // 2 - chunk_size // 2), max(0, size - chunk_size)})
    digest = hashlib.sha256()
    digest.update(str(size).encode("ascii"))
    with path.open("rb") as stream:
        for offset in offsets:
            stream.seek(offset)
            digest.update(stream.read(chunk_size))
    return digest.hexdigest()


def probe_video(path: Path) -> VideoMetadata:
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise MediaError("The selected video does not exist.")
    require_ffmpeg()

    completed = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
    )
    if completed.returncode != 0:
        raise MediaError("The selected file could not be read as a video.")
    try:
        payload = json.loads(completed.stdout)
        stream = next(
            item for item in payload["streams"] if item.get("codec_type") == "video"
        )
        duration = float(
            stream.get("duration") or payload["format"].get("duration")
        )
        rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate", "0/1")
        numerator, denominator = rate.split("/", 1)
        fps = float(numerator) / float(denominator)
    except (KeyError, StopIteration, TypeError, ValueError, ZeroDivisionError) as exc:
        raise MediaError("The video metadata is incomplete.") from exc

    return VideoMetadata(
        duration_ms=round(duration * 1000),
        width=int(stream.get("width", 0)),
        height=int(stream.get("height", 0)),
        fps=fps,
        codec=str(stream.get("codec_name", "")),
        file_size=path.stat().st_size,
        fingerprint=_sample_hash(path),
    )


def fingerprints_match(
    expected: dict,
    actual: VideoMetadata,
) -> bool:
    return expected == actual.fingerprint_payload()


def resolve_frame_pts(source_path: Path, time_ms: int) -> float:
    """Return the closest real presentation timestamp near the requested time."""
    target = max(0, int(time_ms)) / 1000.0
    # Start far enough before the target to survive keyframe-aligned seeking.
    interval_start = max(0.0, target - 2.0)
    completed = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-read_intervals",
            f"{interval_start:.6f}%+4.2",
            "-show_entries",
            "frame=best_effort_timestamp_time,pts_time,pkt_pts_time",
            "-of",
            "json",
            str(source_path),
        ]
    )
    if completed.returncode != 0:
        return target
    try:
        frames = json.loads(completed.stdout).get("frames", [])
    except (json.JSONDecodeError, AttributeError):
        return target

    timestamps: list[float] = []
    for frame in frames:
        for key in (
            "best_effort_timestamp_time",
            "pts_time",
            "pkt_pts_time",
        ):
            value = frame.get(key)
            if value not in (None, "N/A"):
                try:
                    timestamps.append(float(value))
                except (TypeError, ValueError):
                    pass
                break
    return min(timestamps, key=lambda value: abs(value - target)) if timestamps else target


def extract_frame(
    source_path: Path,
    time_ms: int,
    destination: Path,
    max_width: int | None = 1280,
) -> None:
    source_path = Path(source_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    seconds = max(0, time_ms) / 1000.0
    coarse_seek = max(seconds - 2.0, 0.0)
    fine_seek = seconds - coarse_seek
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-ss",
        f"{coarse_seek:.6f}",
        "-i",
        str(source_path),
        "-ss",
        f"{fine_seek:.6f}",
        "-frames:v",
        "1",
    ]
    if max_width is not None:
        command.extend(
            [
                "-vf",
                rf"scale=w=min({max(1, int(max_width))}\,iw):h=-2",
            ]
        )
    command.extend(
        [
            "-q:v",
            "2",
            "-y",
            str(destination),
        ]
    )
    completed = _run(command)
    if completed.returncode != 0 or not destination.is_file():
        raise MediaError("Frame extraction failed.")
