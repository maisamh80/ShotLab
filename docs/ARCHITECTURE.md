# ShotLab Desktop Architecture

## Separation of concerns

- `repository.py`: SQLite, project folders, manifests, confirmed captures
- `session.py`: volatile source-video ownership and draft orchestration
- `media.py`: FFprobe, fingerprinting, and FFmpeg frame extraction
- `analysis.py`: five-color palette extraction and thumbnail generation
- `backup.py`: validated `.shotlab` export/import and local recovery copies
- `ui/`: PySide6 desktop interface

## Privacy boundary

`CaptureSession.video.path` is the only object that owns the source path. It is
never passed to `Repository`. `Repository` accepts a non-reversible fingerprint,
capture timestamps, extracted images, and metadata only.

## Data durability

SQLite is the working index. Each project also owns a versioned `project.json`
manifest so essential records can be reconstructed if the global database is
lost or migrated.

Library exports contain the database, manifests, full captured frames, and
thumbnails. Source videos, session cache, and draft files are excluded.

## Product boundary

ShotLab 1.0.0 deliberately does not use AI or automatic descriptive analysis.
Only the objective color palette is extracted. Shot size, camera angle,
location, time, lighting, mood, tags, and notes are entered and corrected by
the user. Search uses these confirmed values.

## Possible future modules

- Advanced structured filters
- Color Script
- Reference Boards
