# ShotLab Product Specification and Development Roadmap

> Version 0.2 note: the current product decision supersedes the AI analysis and
> suggestion sections in this document. The implemented application extracts
> only a five-color palette; users enter all descriptive metadata manually.
> This note takes precedence over older AI sections below.

**Document version:** 1.0  
**Date:** July 24, 2026  
**Status:** Baseline product and development specification

---

## 1. Product Definition

ShotLab is a fully local desktop application for building a personal library of
cinematic frames, metadata, and visual analyses. It is intended for directors,
cinematographers, production designers, lighting artists, look development
artists, colorists, and other visual storytellers.

ShotLab is inspired by the general utility of tools such as ShotDeck, but it
will be an independent product with its own taxonomy, user experience, and data
architecture.

All project data, images, and processing remain on the user's computer. Core
features do not depend on an online service.

## 2. Primary Goal

The user must be able to:

1. Create a named project.
2. Open a local video only for a frame-capture session.
3. Play and navigate the video on a timeline.
4. Capture the current frame at any chosen moment.
5. Review immediate measurements and AI-generated suggestions.
6. Correct or extend the suggested information.
7. Confirm the frame and add it to the project library.
8. Edit, search, compare, and reuse saved frames as visual references.
9. Back up projects and restore them in another ShotLab installation.

## 3. Fundamental Product Principles

### 3.1. A True Desktop Application

The final product must be an installable desktop application, not a browser-
based web app. Users must not be required to install or configure Python,
FFmpeg, AI models, or any other dependency manually.

The installer must deploy and configure every required runtime component.

### 3.2. Local Processing and Privacy

- Image and video analysis is performed locally by default.
- Project information is not sent to an external service without explicit user
  consent.
- The application remains useful without a persistent internet connection.

### 3.3. The Source Video Stays Outside the Database

Because source videos can be extremely large:

- The original video file is never stored in the database.
- The original video is not copied into the project folder or a standard
  backup.
- The video's permanent file path is not stored in the database.
- Its path exists only in volatile session memory while the user is playing the
  video and extracting frames.
- After the capture session ends, ShotLab can still display all confirmed
  frames and metadata. To continue capturing from the same video, the user must
  select the source file again.
- ShotLab may store a non-reversible fingerprint consisting of duration,
  dimensions, frame rate, file size, and a sampled hash. This fingerprint does
  not contain the video or its path.
- When the user selects the source again, ShotLab validates it against the
  stored fingerprint and warns about a mismatch.

Every confirmed capture retains its precise source timecode so that its
original position remains known in future sessions.

### 3.4. The User Has Final Authority

AI provides suggestions. No AI result becomes final metadata without being
visible, editable, and confirmable by the user.

## 4. Top-Level Application Structure

ShotLab contains two main workspaces.

### 4.1. Capture Workspace

The workspace for working with a local video:

- Video player
- Timeline
- Playback and navigation controls
- Frame-by-frame stepping
- Frame capture
- Confirmed-capture markers on the timeline
- Immediate analysis
- AI analysis
- Inspector for reviewing and editing metadata
- Editing of previous captures

### 4.2. Library Workspace

The workspace for using saved information:

- All-projects view
- Global search
- Metadata filters
- Project detail pages
- Color Script visualization
- Frame viewing and comparison
- Standalone image import
- Reference Boards
- Export, backup, and import

## 5. Project Creation

### 5.1. Required Information

The only required field when creating a project is:

- **Project name**

### 5.2. Optional Information

Every other field is optional. The user may enter it during creation, later on
the project page, or never:

- Original title
- Translated title
- Production year
- Country
- Director
- Director of Photography
- Production Designer
- Colorist
- Genre
- Aspect ratio
- Description
- Notes
- Cover image

An empty optional field must never prevent project creation or normal use.

## 6. Capture Workflow

### 6.1. Selecting a Video

Inside a project, the user chooses **Start Capture Session** and selects a video
from the local computer.

ShotLab:

- Reads the technical metadata.
- Compares the video fingerprint with the project.
- Plays the file directly from its local location without copying it or adding
  it to the database.
- With user approval, creates a temporary proxy if the codec cannot be played
  directly.
- Does not include the proxy in the database or project backup; the proxy can
  be cleared safely.

### 6.2. Player and Timeline

The user can:

- Play and pause.
- Seek on the timeline.
- Step forward or backward by one frame.
- Jump forward or backward by several seconds.
- Change playback speed.
- See precise timecode.
- See confirmed captures as timeline markers.
- Click a marker to open and edit an existing capture.

For variable-frame-rate media, timecode must be calculated from presentation
timestamps and the source time base, not merely by multiplying time by an
average FPS.

### 6.3. Capture

The user captures the current frame with a button or keyboard shortcut.

Suggested shortcuts:

| Key | Action |
|---|---|
| `Space` | Play or pause |
| `C` | Capture the current frame |
| `←` and `→` | Step by one frame |
| `J` and `L` | Jump by several seconds |
| `Esc` | Close the current draft |

### 6.4. Inspector Instead of a Blocking Popup

After capture, the frame and its information appear in a persistent Inspector
beside the player. This is preferable to a blocking popup because:

- The video and timeline remain visible.
- Comparing the capture with its source is easier.
- Repeated capture is faster.
- The same Inspector can edit previous captures.

A new capture is a draft and does not enter the main database until confirmed.

### 6.5. Two-Stage Analysis

#### Stage One: Immediate Analysis

This stage should finish almost instantly:

- Frame extraction
- Timecode
- Frame number or PTS
- Color palette
- Brightness
- Contrast
- Saturation
- Sharpness
- Warm, cool, or neutral classification
- Low-key, high-key, or balanced classification

#### Stage Two: AI Analysis

AI suggestions may appear progressively in the Inspector over several seconds:

- Shot size
- Camera angle
- Interior or exterior
- Time of day
- Composition
- Depth of field
- Lighting type and quality
- Probable key-light direction
- Mood
- Subject
- Environment
- Objects and story elements
- Semantic tags
- Estimated lens category

Opening the Inspector must not wait for the AI stage to finish.

### 6.6. Short Temporal Analysis

A single frame cannot reveal motion. When the user captures a frame, ShotLab
may temporarily analyze a short interval, such as one second before and one
second after the capture, without preserving that clip.

This analysis can suggest:

- Pan
- Tilt
- Dolly
- Tracking
- Zoom
- Handheld motion
- Subject movement
- Significant lighting changes

These results are labeled `Temporal Analysis` and remain distinct from static
frame analysis.

### 6.7. Correction and Confirmation

The user can:

- Correct every suggested value.
- Add custom tags.
- Write notes.
- Discard the draft.
- Confirm the frame.

After confirmation:

- The captured image is stored in the project folder.
- A thumbnail is generated.
- Metadata is inserted into the database.
- The independent project JSON is updated.
- A marker appears on the timeline.
- The thumbnail appears among completed captures.

## 7. Metadata Taxonomy

ShotLab's controlled vocabulary must be designed before connecting an AI model.
This prevents inconsistent labels such as `Medium Shot`, `Mid Shot`, and
`Waist Shot`.

Primary categories:

1. Framing
2. Camera
3. Composition
4. Subject
5. Environment
6. Lighting
7. Color
8. Focus
9. Mood
10. Motion
11. Story Elements
12. Technical Estimate
13. Custom Tags

Every standard value has a language-independent identifier:

```json
{
  "id": "lighting.low_key",
  "en": "Low-Key",
  "fa": "نورپردازی کم‌مایه"
}
```

The interface can switch between Persian and English, while the database always
stores the stable identifier.

## 8. Accuracy, Provenance, and Confidence

Information is separated by its nature.

### 8.1. Measured Data

- Timecode
- PTS
- Resolution
- Frame rate
- Aspect ratio
- Color palette
- Brightness
- Contrast
- Saturation

### 8.2. Estimated Data

- Probable focal length
- Lens category
- Light-source direction
- Time of day
- Mood
- Depth of field
- Location type

Every AI suggestion includes:

```json
{
  "value": "camera_left",
  "confidence": 0.78,
  "source": "ai",
  "edited_by_user": false
}
```

After user correction:

```json
{
  "value": "camera_right",
  "confidence": 1.0,
  "source": "user",
  "edited_by_user": true
}
```

Reanalysis must never overwrite a user-corrected value without permission.

## 9. Project Page

A project page may contain:

- Project name
- Optional project information
- Selected cover
- Source duration and technical properties, if recorded
- Capture count
- Creation and last-modified dates
- Five representative project colors
- Color Script
- Capture gallery
- Project-level filters
- Start or continue Capture Session
- Standalone image import
- Backup and export

Only the project name is required. The layout must handle all other fields being
empty without looking incomplete or blocking the workflow.

## 10. Project Card and Five Representative Colors

In the Library view, each project displays:

- Project name
- Selected or automatically chosen cover
- Capture count
- Last-modified date
- Five representative colors

The five colors must not be chosen by simple RGB frequency counting. Colors
from all captures should be clustered in a perceptual color space such as
`CIELAB`. The user may optionally exclude near-black and near-white colors.

## 11. Color Script

The Color Script visualizes how the colors of confirmed captures change over
source time.

Requirements:

- Each capture is positioned according to its source timecode.
- Intervals without captures remain visibly unsampled.
- The application must not imply that a few samples form a complete Color
  Script for the entire film.
- Two display modes are available:
  - `Discrete`: each capture is shown independently.
  - `Continuous`: samples are interpolated, explicitly labeled as an estimate.
- Clicking any segment opens its capture.

## 12. Standalone Image Import

The user can import standalone images with drag and drop or a file picker.

Every record declares its source type:

```text
Video Capture
Imported Image
```

An imported image has no timecode, but may include:

- Source name
- Film or project name
- Photographer or cinematographer
- Year
- Description
- Tags

The image follows the same analysis, correction, and confirmation process as a
video capture.

## 13. Search

### 13.1. Structured Search

Fast and precise search by:

- Project
- Framing
- Camera angle
- Interior or exterior
- Day or night
- Lighting
- Color
- Mood
- Subject
- Tags
- Motion
- Timecode range

This layer can use SQLite with suitable indexes.

### 13.2. Semantic Search

The user can search in natural Persian or English:

> A warm, intimate space with a lonely character beside a window

This layer uses local image and text embeddings with a local vector index.

## 14. Reference Boards

The user can select frames from multiple projects and place them on a Board:

- Manual arrangement
- Per-frame notes
- Board title and description
- Optional color and tag display
- PDF or image export
- Shareable team output

## 15. Language and User Interface

- The interface supports Persian and English.
- Language is selected in Settings.
- Persian UI is RTL; English UI is LTR.
- The visual design is modern, professional, and low in saturation.
- The visual language may take inspiration from applications such as Blender.
- Layouts are optimized for professional monitors and long work sessions.
- Shortcuts remain visible and can become customizable in later releases.

## 16. Storage

Suggested project structure:

```text
projects/
└── <project-id>/
    ├── project.json
    ├── captures/
    │   ├── full/
    │   └── thumbnails/
    ├── imported-images/
    ├── boards/
    └── cache/
```

The main database stores structured information and search indexes.
`project.json` provides an independent, recoverable representation of essential
project data.

The source video and its permanent path are not stored in this structure or in
the database.

## 17. Backup, Export, and Import

Suggested portable format:

```text
MyProject.shotlab
```

This can be an archive containing:

```text
manifest.json
project.json
captures/
imported-images/
boards/
database.sqlite
preview.jpg
```

The source video is not included in a standard backup.

Export options:

- Metadata and thumbnails
- Full captured images and metadata
- Selected Board or collection

Every backup contains:

- Schema version
- ShotLab version
- AI model version
- Export date
- File checksums

Import must:

- Validate version compatibility.
- Apply migration when required.
- Prevent unintended duplicate records.
- Preview the import result before finalization.

## 18. Recommended Technical Architecture

### 18.1. Desktop Interface and Shell

- `PySide6`
- `Qt/QML`

### 18.2. Processing

- Python
- Bundled FFmpeg and FFprobe
- Pillow, NumPy, and OpenCV for baseline analysis
- A local vision-language model for metadata suggestions
- An embedding model for semantic search

### 18.3. Data

- SQLite
- SQLite FTS for textual search
- Local vector index for semantic search
- JSON manifests for recovery and transfer

### 18.4. Packaging

- PyInstaller or an equivalent bundler
- Windows installer
- Automatic installation of all runtimes

## 19. AI Model and Installation Packages

Because AI models can be large, distribution may be split into:

### ShotLab Core

- Application
- Player
- Timeline
- Database
- Color analysis
- Project management
- Structured search

### ShotLab AI Model Pack

- Vision-language model
- Embedding model
- Supporting models

The Model Pack can be installed automatically through the installer or from
inside ShotLab. Users never configure model files or dependencies manually.

For hardware such as an RTX 4060 Laptop GPU with 8 GB VRAM, quantized 3B or 7B
models and capture-by-capture processing are appropriate.

## 20. Performance and User Experience

- Project creation should be nearly immediate.
- Video playback must not require full-video analysis.
- Only selected frames and short surrounding intervals are analyzed.
- Heavy work runs in the background.
- Analysis results are cached.
- The interface remains responsive during AI processing.
- Processing state, errors, and confidence are visible to the user.

## 21. Development Roadmap

### Phase One: Desktop Core

- PySide6 and QML
- Initial installer
- Project Manager
- Player and timeline
- Session-only video source
- Capture
- Inspector
- Saving and editing captures
- Independent project folders

### Phase Two: Information Structure

- Persian and English taxonomy
- Project page
- Optional project details
- Cover
- Gallery
- Standalone image import
- Five project colors
- Color Script

### Phase Three: Library

- All-projects view
- Structured search
- Filters
- Frame comparison
- Reference Boards

### Phase Four: Artificial Intelligence

- Local vision-language model
- Automatic metadata suggestions
- Confidence and provenance tracking
- Short-interval video analysis
- Persian and English semantic search

### Phase Five: Portability and Release

- Backup
- Export and import
- Schema migration
- Final installer
- AI Model Pack
- Testing on systems without Python or FFmpeg
- Large-library and thousands-of-captures testing

## 22. Acceptance Criteria for the First Releasable Version

- The application installs on Windows through an installer.
- A project can be created with only a name.
- Missing optional information never blocks the workflow.
- The source video and its permanent path are not inserted into the database.
- The video is shown from its local location only during a Capture Session.
- Each capture is saved with precise timecode.
- A draft can be corrected or discarded before confirmation.
- A confirmed frame is stored in both the project folder and database.
- Existing captures are editable.
- A project remains viewable and searchable without the source video.
- A backup can be transferred and restored without the source video.
- Both Persian and English interfaces are usable.
- No dependency requires manual installation for normal use.

## 23. Current Product Decisions

1. ShotLab is a local desktop application.
2. Frame selection is intentional and manual in the primary workflow.
3. The project name is the only required field.
4. Every other project field is optional.
5. The source video and its permanent path are not stored in the database.
6. The video is displayed from its local location only during a Capture
   Session.
7. AI suggests; the user makes the final decision.
8. The taxonomy is finalized before AI integration.
9. Capture and Library are separate workspaces.
10. Backup and portability are considered from the beginning of data-architecture
    design.
