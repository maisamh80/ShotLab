# ShotLab Quality Assurance

This directory contains the internal regression suite for ShotLab's data,
privacy, capture, search, and backup behavior.

Run it from the source root with:

```bat
.venv\Scripts\python -m unittest discover -s quality_assurance -v
```

These development checks are intentionally excluded from the standalone
application, portable package, and Windows installer.
