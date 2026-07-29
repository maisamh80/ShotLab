# ShotLab

<p align="center">
  <img src="assets/final_ui/logo.svg" alt="ShotLab" width="320">
</p>

<p align="center">
  A local visual-reference library for building your own visual memory.
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#فارسی">فارسی</a>
</p>

<a id="english"></a>

## 🎬 About ShotLab

ShotLab is a tool I originally built for myself through vibe coding with
ChatGPT. I am sharing it freely so filmmakers, cinematographers, lighting
artists, colorists, animators, and visual storytellers can build their own
visual memory.

Instead of automatically describing or interpreting images with AI, ShotLab
keeps the creative decisions in your hands. It extracts an objective color
palette from each frame, while titles, shot information, mood, tags, and notes
remain fully editable by you.

ShotLab works locally. Your source videos remain on your computer and are never
copied into the database or included in a library export.

## ✨ Features

- Create independent visual libraries for films, projects, or research topics.
- Load and play local videos with a frame-accurate timeline.
- Capture the exact frame currently displayed in the player.
- Move forward or backward one frame at a time.
- Import still images manually in addition to capturing video frames.
- Extract a five-color palette with real image-coverage percentages.
- Copy HEX values directly from palette colors.
- Add and edit shot size, camera angle, location, lens type, time of day,
  lighting style, key quality, mood, tags, title, and notes.
- Search across all manually entered information.
- Filter frames by category, HEX code, or perceptually similar colors.
- Browse selected frames in a dedicated Gallery Workspace.
- Resize thumbnails independently in Capture and Gallery workspaces.
- Download stored frames in small, medium, or original resolution.
- Export and restore complete ShotLab libraries without the source video.
- Export frame collections as one-, two-, or three-column PDF reference sheets.
- Use English or Persian with bundled Inter and Vazirmatn fonts.
- Switch between dark and light themes.
- Work entirely offline after the initial development setup.

## 🧩 Technical Overview

ShotLab is a Windows desktop application built with:

| Component | Technology |
| --- | --- |
| Language | Python 3.11+ |
| Desktop UI | PySide6 / Qt 6 |
| Database | SQLite |
| Image processing | Pillow |
| Video metadata and frame extraction | FFmpeg / FFprobe |
| PDF export | Qt PDF painting |
| Windows packaging | PyInstaller |
| Installer | Inno Setup 7 |
| Interface languages | English and Persian |
| Bundled fonts | Inter and Vazirmatn |

The application is divided into focused modules:

- `repository.py` manages SQLite records, manifests, captures, and project
  folders.
- `session.py` manages the active source video and capture drafts.
- `media.py` handles FFmpeg, FFprobe, fingerprints, timecodes, and extraction.
- `analysis.py` creates thumbnails and calculates dominant color palettes.
- `backup.py` exports, validates, restores, and recovers ShotLab libraries.
- `pdf_export.py` generates printable visual-reference sheets.
- `ui/` contains the PySide6 interface, themes, dialogs, and custom widgets.
- `i18n.py` contains the English and Persian interface text and taxonomy.

## 💾 Data and Privacy

By default, ShotLab stores its working data in:

```text
%LOCALAPPDATA%\ShotLab
```

Each library has its own folder:

```text
projects/
└── <project-id>/
    ├── project.json
    ├── captures/
    │   ├── full/
    │   └── thumbnails/
    └── .drafts/
```

SQLite acts as the main searchable index, while each library also keeps a
`project.json` manifest and its extracted frames. The original video itself is
not stored in SQLite, copied into the project, or included in `.shotlab`
exports. Only its local location is remembered in the application settings so
it can be reopened later if the file still exists.

## 🛠️ Running from Source

Requirements:

- Windows 10 or Windows 11, 64-bit
- Python 3.11 or newer
- A trusted 64-bit static build of `ffmpeg.exe` and `ffprobe.exe`

Place the FFmpeg tools here:

```text
vendor/
└── ffmpeg/
    ├── ffmpeg.exe
    └── ffprobe.exe
```

Prepare the development environment once:

```bat
setup_windows.bat
```

After setup, launch ShotLab without reinstalling dependencies:

```bat
run_windows.bat
```

To prepare an optional offline cache of the Python dependencies:

```bat
cache_windows_dependencies.bat
```

## 📦 Building the Portable and Installer Releases

Install the 64-bit version of Inno Setup 7, then run:

```bat
publish_windows.bat
```

The script runs the quality-assurance suite, builds the application with
PyInstaller, creates the portable archive, and generates the Windows installer.

The final files are created in:

```text
release/
├── ShotLab_Portable_v1.0.0.zip
└── ShotLab_Setup_v1.0.0.exe
```

To build only the direct PyInstaller application folder:

```bat
build_windows.bat
```

Its executable is created at:

```text
dist\ShotLab\ShotLab.exe
```

The executable depends on the files beside it, so distribute the complete
`dist\ShotLab` folder or use the generated portable ZIP.

## ⬇️ Downloads

Users who do not want to compile ShotLab can download the latest Windows
installer and portable package from the
[GitHub Releases page](https://github.com/maisamh80/ShotLab/releases).

## 📄 License

ShotLab is free software released under the
[GNU General Public License v3.0](LICENSE).

## 🌱 StoryEco

ShotLab was created by **Maisam Hosaini** within the **StoryEco — Storytellers
Ecosystem**, an initiative focused on tools, workflows, and infrastructure for
visual storytelling.

---

<a id="فارسی"></a>

## 🎬 دربارهٔ ShotLab

ShotLab ابزاری است که در ابتدا برای استفادهٔ شخصی خودم و با روش Vibe Coding
در ChatGPT ساختم. اکنون آن را به‌رایگان در اختیار دیگران قرار می‌دهم تا
فیلم‌سازان، فیلم‌برداران، هنرمندان نورپردازی، کالریست‌ها، انیماتورها و
روایتگران تصویری بتوانند Visual Memory شخصی خودشان را بسازند.

ShotLab به‌جای آنکه تصاویر را با هوش مصنوعی توصیف یا تفسیر کند، تصمیم‌های
خلاقانه را در اختیار خود شما نگه می‌دارد. نرم‌افزار فقط پالت رنگی عینی هر
فریم را استخراج می‌کند و عنوان، اطلاعات نما، مود، تگ‌ها و یادداشت‌ها کاملاً
توسط شما وارد و ویرایش می‌شوند.

ShotLab به‌صورت لوکال کار می‌کند. ویدئوهای اصلی روی کامپیوتر شما باقی
می‌مانند و هرگز داخل دیتابیس کپی یا همراه خروجی کتابخانه ذخیره نمی‌شوند.

## ✨ امکانات

- ساخت کتابخانه‌های تصویری مستقل برای فیلم‌ها، پروژه‌ها یا موضوعات پژوهشی
- پخش ویدئوی لوکال با تایملاین دقیق
- کپچر دقیق همان فریمی که در Player نمایش داده می‌شود
- پیمایش فریم‌به‌فریم به جلو و عقب
- ورود دستی تصاویر ثابت در کنار کپچر از ویدئو
- استخراج پالت پنج‌رنگ همراه درصد واقعی پوشش هر رنگ در تصویر
- کپی مستقیم کد HEX رنگ‌های پالت
- ثبت و ویرایش اندازهٔ نما، زاویهٔ دوربین، محیط، نوع لنز، زمان، سبک
  نورپردازی، کیفیت نور Key، مود، تگ‌ها، عنوان و یادداشت
- جست‌وجو در تمام اطلاعاتی که کاربر وارد کرده است
- فیلتر براساس دسته‌بندی‌ها، کد HEX یا رنگ‌های نزدیک از نظر ادراکی
- مرور فریم‌ها در فضای کاری اختصاصی Gallery
- تغییر مستقل اندازهٔ Thumbnailها در Capture و Gallery
- دانلود فریم‌ها با اندازهٔ کوچک، متوسط یا رزولوشن اصلی
- خروجی و بازیابی کامل کتابخانه‌های ShotLab بدون ویدئوی منبع
- ساخت PDF رفرنس با چیدمان یک، دو یا سه ستون
- رابط فارسی و انگلیسی با فونت‌های داخلی Inter و Vazirmatn
- پوستهٔ روشن و تیره
- کارکرد کاملاً آفلاین پس از آماده‌سازی اولیهٔ محیط توسعه

## 🧩 مشخصات فنی

ShotLab یک نرم‌افزار دسکتاپ ویندوز است که با فناوری‌های زیر ساخته شده:

| بخش | فناوری |
| --- | --- |
| زبان برنامه‌نویسی | Python 3.11+ |
| رابط دسکتاپ | PySide6 / Qt 6 |
| دیتابیس | SQLite |
| پردازش تصویر | Pillow |
| اطلاعات و استخراج فریم ویدئو | FFmpeg / FFprobe |
| خروجی PDF | سیستم ترسیم PDF در Qt |
| بسته‌بندی ویندوز | PyInstaller |
| ساخت Installer | Inno Setup 7 |
| زبان‌های رابط | فارسی و انگلیسی |
| فونت‌های داخلی | Inter و Vazirmatn |

ساختار برنامه به ماژول‌های مستقل تقسیم شده است:

- `repository.py` مدیریت رکوردهای SQLite، Manifestها، فریم‌ها و پوشه‌های
  کتابخانه را انجام می‌دهد.
- `session.py` ویدئوی فعال و Draftهای کپچر را مدیریت می‌کند.
- `media.py` مسئول FFmpeg، FFprobe، Fingerprint، Timecode و استخراج فریم است.
- `analysis.py` Thumbnail و پالت رنگی غالب را تولید می‌کند.
- `backup.py` خروجی، اعتبارسنجی، بازیابی و Recovery کتابخانه‌ها را انجام
  می‌دهد.
- `pdf_export.py` شیت‌های PDF رفرنس را می‌سازد.
- پوشهٔ `ui/` شامل رابط PySide6، پوسته‌ها، Dialogها و Widgetهای اختصاصی است.
- `i18n.py` متن‌های فارسی و انگلیسی و Taxonomy نرم‌افزار را نگهداری می‌کند.

## 💾 ساختار داده و حریم خصوصی

ShotLab به‌صورت پیش‌فرض داده‌های کاری را در این مسیر ذخیره می‌کند:

```text
%LOCALAPPDATA%\ShotLab
```

هر کتابخانه پوشهٔ مستقل خودش را دارد:

```text
projects/
└── <project-id>/
    ├── project.json
    ├── captures/
    │   ├── full/
    │   └── thumbnails/
    └── .drafts/
```

SQLite ایندکس اصلی و قابل جست‌وجوی برنامه است. هر کتابخانه علاوه‌بر آن یک
Manifest با نام `project.json` و فریم‌های استخراج‌شدهٔ خودش را نگهداری
می‌کند. ویدئوی اصلی در SQLite ذخیره نمی‌شود، داخل پروژه کپی نمی‌شود و در
خروجی‌های `.shotlab` قرار نمی‌گیرد. فقط آدرس لوکال آن در تنظیمات برنامه به
خاطر سپرده می‌شود تا در صورت موجودبودن فایل، در مراجعهٔ بعدی دوباره باز شود.

## 🛠️ اجرای سورس

پیش‌نیازها:

- ویندوز ۱۰ یا ۱۱ نسخهٔ ۶۴ بیتی
- Python 3.11 یا جدیدتر
- نسخهٔ Static و ۶۴ بیتی معتبر `ffmpeg.exe` و `ffprobe.exe`

فایل‌های FFmpeg را در این مسیر قرار دهید:

```text
vendor/
└── ffmpeg/
    ├── ffmpeg.exe
    └── ffprobe.exe
```

محیط توسعه را فقط یک بار آماده کنید:

```bat
setup_windows.bat
```

پس از آن ShotLab را بدون نصب دوبارهٔ Dependencyها اجرا کنید:

```bat
run_windows.bat
```

برای ساخت Cache آفلاین اختیاری از Dependencyهای Python:

```bat
cache_windows_dependencies.bat
```

## 📦 ساخت نسخهٔ پرتابل و نصبی

ابتدا نسخهٔ ۶۴ بیتی Inno Setup 7 را نصب و سپس اجرا کنید:

```bat
publish_windows.bat
```

این اسکریپت آزمون‌های کنترل کیفیت را اجرا می‌کند، نرم‌افزار را با PyInstaller
می‌سازد، فایل پرتابل را ایجاد می‌کند و Installer ویندوز را می‌سازد.

فایل‌های نهایی در این مسیر ایجاد می‌شوند:

```text
release/
├── ShotLab_Portable_v1.0.0.zip
└── ShotLab_Setup_v1.0.0.exe
```

برای ساختن فقط پوشهٔ مستقیم برنامه با PyInstaller:

```bat
build_windows.bat
```

فایل اجرایی در این مسیر ساخته می‌شود:

```text
dist\ShotLab\ShotLab.exe
```

فایل اجرایی به فایل‌های کنارش وابسته است؛ بنابراین پوشهٔ کامل
`dist\ShotLab` را منتشر کنید یا از ZIP پرتابل ساخته‌شده استفاده کنید.

## ⬇️ دانلود

کاربرانی که نمی‌خواهند ShotLab را کامپایل کنند می‌توانند آخرین نسخهٔ نصبی و
پرتابل ویندوز را از
[بخش Releases گیت‌هاب](https://github.com/maisamh80/ShotLab/releases)
دانلود کنند.

## 📄 مجوز

ShotLab یک نرم‌افزار آزاد است و تحت
[GNU General Public License v3.0](LICENSE)
منتشر می‌شود.

## 🌱 StoryEco

ShotLab توسط **میثم حسنی** در **StoryEco — Storytellers Ecosystem** ساخته شده
است؛ اکوسیستمی برای ابزارها، گردش‌های کاری و زیرساخت روایتگری تصویری.
