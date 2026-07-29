# ShotLab Final UI Reference Map

This file records the implementation contract extracted from the approved
55-page `ShotLab.pdf` design.

| Reference pages | Implemented surface |
| --- | --- |
| 1–20 | Sidebar navigation, selected/hover states, data actions, storage, language, and theme controls |
| 21–25 | Actual-size, Delete Library, Delete Frame, and Rename Library dialogs |
| 26 | Localized PDF export dialog with 1/2/3-column and scope choices |
| 27–30 | Dark/light and English/Persian Libraries workspace |
| 31–34 | Complete filter taxonomy, similar-color picker, and brightness control |
| 35–36 | Library card hover and ellipsis action menu |
| 37–38 | New Library and required-name validation dialogs |
| 39–42 | Search results and thumbnail Zoom controls |
| 43–48 | A4 PDF output in Persian/English and 1/2/3-column layouts |
| 49–52 | Empty Capture workspace in dark/light and Persian/English |
| 53–55 | Loaded Capture workspace, timeline, confirmed frames, and Shot Information inspector |

## Global rules

- The target application viewport is 1920×1009.
- The Sidebar remains on the left in both Persian and English.
- Persian content uses RTL flow inside the fixed left-Sidebar composition.
- Inter is used for English and Vazirmatn for Persian; both are bundled.
- The primary accent is `#D8B365`.
- Source video bytes are never stored in SQLite or Library exports.
- All descriptive shot information is entered manually; only the color palette
  is extracted automatically.
