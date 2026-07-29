# FFmpeg Runtime Files

Before building the Windows release, place the 64-bit Windows executables here:

```text
vendor/
└── ffmpeg/
    ├── ffmpeg.exe
    └── ffprobe.exe
```

Use a trusted static Windows build and review its license before distribution.
The build pipeline bundles these files with ShotLab; they are intentionally not
stored in this source package.
