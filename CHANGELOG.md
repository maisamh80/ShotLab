# Changelog

## Unreleased — YouTube Capture Bridge

- Treat six-digit HEX searches with or without a leading `#` identically and
  include perceptually nearby matches in both forms.
- Present frame palettes as five equal-width swatches without coverage labels.
- Add a two-action palette menu for copying a HEX code or replacing a swatch
  by sampling a color directly from the displayed frame with an eyedropper
  cursor; persist edits in drafts and saved captures.
- Render equal-width palette blocks in PDF exports as well.
- Update the Chrome extension to 0.1.3 and include the host permission required
  by `captureVisibleTab` when capture is triggered from the in-page YouTube
  button; keep script injection limited to YouTube and transmission fixed to
  ShotLab's local loopback bridge.
- Automatically return a partially scrolled YouTube player to the visible
  viewport before measuring and capturing subsequent frames.
- Temporarily suppress YouTube playback controls, gradients, cards, captions,
  and other player overlays so captured references contain only video pixels.
- Add an optional Manifest V3 Chrome extension with a native-looking ShotLab
  button in the action row below standard YouTube videos.
- Pause on the current YouTube frame, crop only the visible video image, and
  send it directly to the running ShotLab app without downloading the video.
- Add a loopback-only bridge on `127.0.0.1:47831` with source, origin, protocol,
  image-type, dimension, and payload-size validation.
- Reuse ShotLab's existing manual-import draft workflow so browser frames open
  in Capture Workspace with palette extraction and editable information.
- Add localized browser-capture states and errors plus automated bridge,
  permission, and extension-contract tests.
- Package the optional Chrome extension as a separate ZIP when publishing on
  Windows.

## 1.0.0 — First Stable Release

- Preserve the same left-aligned Sidebar composition in English and Persian;
  only the displayed copy changes with the selected language.
- Always show the Notes section for a selected Gallery frame, including frames
  whose notes are currently empty.
- Promote the application, Sidebar footer, Windows executable metadata, and
  installer to version 1.0.0.

## 0.15.3 — Final Interaction and Export Corrections

- Pause video and audio immediately when leaving Capture Workspace while
  preserving the current playback position.
- Use a pointing-hand cursor across clickable controls and interactive
  surfaces.
- Keep the Sidebar physically on the left in Persian while retaining RTL page
  content.
- Reserve independent PDF header regions for the logo and page text, and place
  palette labels above their color strips in every column layout.
- Remove the Timeline Play button background in every state and keep the
  Capture vertical splitter hidden until a neutral-gray hover.

## 0.15.2 — Focused Typography and Layout Corrections

- Replace the split Vazirmatn subsets with the complete supplied Vazirmatn
  family and enforce it consistently throughout the Persian interface.
- Let Library cards continue across every column that fits the current window
  width before wrapping to the next row.
- Increase the three compact Sidebar controls, show the moon in Dark Mode,
  shrink Timeline transport icons by 20%, and remove their button backgrounds.
- Keep the Capture vertical splitter invisible until hover and use neutral
  headings for Confirmed Frames and Search Results.
- Normalize Gallery metadata-row heights and spacing.
- Prevent PDF palette labels from overlapping their color strips and fill each
  PDF page with multiple rows before creating another page.
- Keep technical taxonomy values in English in the Persian interface, while
  localizing only Location and Time of Day values.

## 0.15.1 — Design-Matched UI Rebuild

- Correct `QFont.setWeight` usage for current PySide6 releases so PDF export
  passes a `QFont.Weight` enum instead of a raw integer.
- Rebuild the main 1920×1009 composition against the final ShotLab PDF,
  keeping the Sidebar on the left in both English and Persian.
- Separate gold workspace names from muted active-Library names in Capture and
  Gallery headers.
- Match the final three-column Library cards, compact four-image mosaics,
  proportional palette strips, and ellipsis action menus.
- Complete the final filter taxonomy with Lens Type, Shoulder/Hip/Knee/Ground
  camera levels, High Noon, and Sunset.
- Add independent thumbnail Zoom controls to Library search results and align
  Capture and Gallery toolbars with the approved compositions.
- Rebuild New Library, Rename Library, validation, warning, color-picker, and
  PDF-export dialogs as localized borderless surfaces.
- Match the Gallery and Capture thumbnail browsers, Shot Information panels,
  action hierarchy, light theme, and dark theme more closely to the approved
  layouts.
- Add source-level regression coverage for the PySide6 PDF font-weight contract
  and final bilingual UI taxonomy.

## 0.15.0 — Final UI and PDF Reference Export

- Fix the application startup import path by sharing timecode formatting through
  the media module used by both the interface and PDF exporter.
- Rebuild the dark and light interfaces from the approved 55-page ShotLab
  design, including compact workspace headers, Library cards, filters,
  inspectors, Timeline controls, and Sidebar navigation.
- Bundle the final SVG icon set and the Inter and Vazirmatn variable fonts so
  the installed application preserves its typography without internet access.
- Add localized A4 PDF reference export with one-, two-, or three-frame page
  layouts.
- Allow PDF export from all Libraries, the last active Library, or the current
  search results.
- Include frame imagery, proportional color palettes, timecodes, and manually
  entered editorial metadata in PDF exports.
- Keep PDF pages presentation-neutral with a white background and ShotLab
  branding in both Persian and English.

## 0.14.0 — Windows Publishing Pipeline

- Separate one-time development setup from the daily launcher so
  `run_windows.bat` never installs packages or accesses the internet.
- Add an optional Windows wheel-cache script for fully offline setup and build.
- Keep runtime and build virtual environments reusable between executions.
- Build a standalone `dist\ShotLab\ShotLab.exe` with bundled Python, Qt,
  application assets, and vendor-supplied FFmpeg tools.
- Add an Inno Setup definition and publishing script for portable ZIP and
  installer EXE outputs.
- Prefer Inno Setup 7 x64 when available while retaining Inno Setup 6
  compatibility.
- Explicitly close the direct SQLite inspection connection in the regression
  suite so Windows can remove its temporary database after testing.
- Add Windows version metadata for StoryEco and ShotLab.
- Rename the internal regression folder from `tests` to
  `quality_assurance`.
- Exclude internal quality checks and development dependencies from end-user
  release output.

## 0.13.2 — Unified Workspace Headers

- Remove the framed Toolbar container from the Capture header.
- Match the open, borderless Gallery Workspace header composition.
- Add a clear 20-pixel separation between Change Video and Gallery Workspace
  so the two independent actions do not read as one control group.

## 0.13.1 — Workspace Header Polish

- Swap the Change Video and Gallery Workspace button positions in the Capture
  toolbar.
- Add a `CAPTURE WORKSPACE` eyebrow above the active Library name.
- Replace `LIBRARY FRAMES ARCHIVE` with the corrected `GALLERY WORKSPACE`
  heading.
- Replace the generic manual-image icon with the supplied import artwork and
  combine it with the concise localized `Import Frame` label.

## 0.13.0 — Remembered Video Paths and Library Mood Palettes

- Remember each Library's source-video path in local application settings while
  keeping the path and video bytes out of SQLite, manifests, and `.shotlab`
  exports.
- Automatically reopen the video when it still exists at its previous path.
- Show the active video path in Capture, show a localized missing-path message
  when unavailable, and hide the message for a new empty Library.
- Add a Gallery Workspace switch beside the video selector in Capture.
- Add an equal-width five-color mood strip to every Library card, calculated by
  coverage-weighted clustering across all saved frame palettes.
- Remove the global eyedropper from the color picker.
- Require a double-click, rather than a single click, to open global search
  results in Gallery Workspace.

## 0.12.0 — Proportional Palettes and Global Color Picking

- Divide each palette bar proportionally by the measured image coverage of its
  dominant colors.
- Rename the user-facing Projects destination to Libraries and Gallery to
  Gallery Workspace across both interface languages.
- Remove the redundant Back to Library button from the Capture header.
- Add a global eyedropper to the color-filter dialog for sampling a visible
  pixel from inside or outside ShotLab.
- Compare similar-color searches against only the two most dominant colors in
  each frame, improving relevance when minor accent colors are present.

## 0.11.0 — Palette Coverage and Frame Deletion

- Measure each dominant color's pixel coverage during palette quantization.
- Display coverage percentages on palette swatches while keeping HEX codes in
  immediate text-only hover tooltips.
- Re-analyze and persist palette percentages for older captures when first
  viewed.
- Add the supplied Delete icon to selected-frame actions in Capture and
  Gallery.
- Permanently remove deleted frame records from SQLite while retaining their
  image and thumbnail files under `Recovery/deleted-frames`.
- Limit project-card image navigation to a double-click on the thumbnail mosaic.

## 0.10.0 — Manual Stills and Perceptual Color Search

- Remove the window-level status bar so the Sidebar and all pages align to the
  full bottom edge.
- Replace status-bar messages with non-layout floating toast notifications.
- Add manual image import beside the Capture thumbnail-size controls.
- Normalize imported JPG, PNG, WebP, BMP, and TIFF images at the active frame
  storage size, extract their palettes, and open them as editable drafts.
- Identify imported stills without creating false Timeline markers.
- Match HEX queries by perceptual CIE76 color distance instead of exact text.
- Add a color-wheel filter with brightness control to Library and Gallery
  filter rows.
- Rank similar-color results from closest to furthest within the similarity
  threshold.

## 0.9.0 — Reliable Library Operations and Developer Easter Egg

- Set Medium frame storage to a maximum width of 1280 px and Small to 720 px.
- Explicitly commit and close every SQLite connection.
- Fix Windows file-lock errors during `.shotlab` export and import.
- Verify project deletion after commit so removed projects stay absent after restart.
- Keep deleted project folders in Recovery while permanently removing their
  database records.
- Show palette HEX values only in tooltips while retaining click-to-copy.
- Reveal a borderless developer-credit dialog after a continuous five-second
  hover over the ShotLab logo.

## 0.8.0 — Project Continuity and Source-Size Capture

- Refresh captured-frame thumbnails whenever Gallery returns to Capture.
- Make Capture and Gallery navigation restore the last valid project after startup.
- Re-render thumbnail pixmaps at each selected size instead of only enlarging
  their grid spacing.
- Reduce the decrease-thumbnail icon size.
- Add a persistent frame-storage selector between Language and Theme.
- Support Actual source size, Medium up to 1920 px wide, and Small up to
  1280 px wide.
- Confirm Actual-size storage with the custom warning dialog.
- Extract the exact displayed frame time from the source video at the selected
  storage resolution.

## 0.7.0 — Compact Gallery and Custom Dialogs

- Use the standalone supplied decrease-size icon without sprite cropping.
- Add the supplied ShotLab window icon to Qt and the Windows executable build.
- Move Gallery thumbnail-size controls inside the thumbnail browser.
- Reduce Gallery detail spacing and place title and timecode on one line.
- Use compact, single-line thumbnail captions.
- Copy palette HEX values on click and choose black or white label text from
  calculated color luminance.
- Increase the sidebar logo size.
- Replace the native project-delete prompt with a custom borderless dialog
  using the supplied warning artwork.

## 0.6.0 — Flexible Thumbnails and Refined Frame Details

- Remove Backlight from shot metadata, filters, new drafts, and gallery details.
- Redesign gallery frame details with larger typography and structured information rows.
- Open a project's gallery by double-clicking its project card.
- Add independent thumbnail size controls to Capture and Gallery views.
- Add a vertical splitter between Video/Timeline and captured-frame thumbnails.
- Increase the library and gallery eyebrow text and rename the gallery line to
  `PROJECT FRAMES ARCHIVE`.

## 0.5.0 — Animated Sidebar and Direct Timeline Seeking

- Use the supplied icon pack for Projects, Capture, Gallery, Export, and Import.
- Replace Stop with a dedicated Pause control that preserves the current position.
- Seek directly by clicking anywhere along the timeline track.
- Increase sidebar navigation, section, and data-action text sizes.
- Add StoryEco developer credit and the current ShotLab version below theme controls.
- Animate sidebar expansion and collapse with eased width transitions.

## 0.4.0 — Custom Icon System and Project Actions

- Use the supplied high-resolution Navigator sprite for previous frame, Stop, Play, and next frame.
- Use the supplied pointer artwork for the timeline slider handle.
- Keep all category filters on one horizontal row.
- Move the sidebar hide control onto the panel boundary and center it vertically.
- Replace large project actions with supplied icon buttons.
- Add project Rename and recoverable Delete actions.
- Move deleted project folders into local Recovery storage.
- Add localized tooltips to every primary application button.

## 0.3.1 — Logo Startup Fix

- Remove the unsupported `QBitmap.boundingRect()` call that prevented startup on Windows.
- Pre-trim the transparent logo asset so no runtime alpha-bound calculation is required.

## 0.3.0 — Filtered Library and Compact Interface

- Use the supplied official ShotLab transparent logo in the sidebar.
- Add a hideable sidebar that leaves only a slim reopen control.
- Remove the redundant Settings destination while keeping language and theme controls.
- Replace search-only inputs with category-aware filter panels.
- Add exact filters for framing, camera, location, time, lighting, key light, and backlight.
- Make project cards compact with square thumbnails and vertically stacked actions.
- Remove opaque label backgrounds from cards, headings, and logo areas.
- Replace timeline text controls with centered transport icons and a dedicated Stop action.
- Keep timecode left-aligned and Capture right-aligned.
- Increase sidebar and general interface text sizes without changing the established palette.

## 0.2.0 — Exact Capture and Professional Library

- Capture the exact frame currently rendered by Qt's video sink.
- Keep AI out of the workflow; extract only a five-color palette.
- Add global and per-project metadata search with Persian/English taxonomy aliases.
- Add a persistent RTL/LTR sidebar with navigation, language, theme, and data tools.
- Replace project rows with four-thumbnail project cards.
- Add separate Timeline and Gallery project entry points.
- Add Gallery details, editing, and original-frame download.
- Add `.shotlab` library export/import without source-video files.
- Increase timeline hit area and handle size.
- Add a light theme, polished empty states, and visual refinements.

## 0.1.0 — Desktop Core

- Added a PySide6 desktop shell.
- Added bilingual Persian and English UI foundations.
- Added project creation with project name as the only required field.
- Added session-only video attachment.
- Added non-reversible source fingerprint validation.
- Added Qt video playback, timeline navigation, and keyboard shortcuts.
- Added real-PTS frame capture through FFmpeg.
- Added deterministic image analysis and five-color palettes.
- Added editable capture drafts and confirmed-capture editing.
- Added SQLite storage and per-project JSON manifests.
- Added timeline markers and a capture gallery.
- Added PyInstaller build configuration for a self-contained Windows build.
- Added privacy and end-to-end core tests.
