# راهنمای انتشار ShotLab برای Windows

## چرا Windows پیام Unknown Publisher نشان می‌دهد؟

این پیام پیش از اجرای ShotLab یا فایل BAT توسط Windows نمایش داده می‌شود و
معمولاً دو علت دارد:

1. فایل از اینترنت دانلود شده و دارای Mark of the Web است.
2. فایل امضای دیجیتال Authenticode از یک ناشر معتبر ندارد.

هیچ کدی داخل `run_windows.bat` نمی‌تواند این پیام را برای خودش خاموش کند، چون
Windows پیش از اجرای کد تصمیم می‌گیرد.

برای تست شخصی، روی ZIP دانلودشده راست‌کلیک کنید، وارد `Properties` شوید،
گزینهٔ `Unblock` را فعال کنید و سپس ZIP را Extract کنید. دستور PowerShell زیر
هم یک فایل مشخص را روی سیستم خودتان Unblock می‌کند:

```powershell
Unblock-File .\run_windows.bat
```

راه حرفه‌ای برای انتشار عمومی، امضای `ShotLab.exe` و Installer با گواهی
Code Signing و Timestamp معتبر است. بدون Certificate، ساخت EXE به‌تنهایی نام
`Unknown Publisher` را تضمینی حذف نمی‌کند و SmartScreen ممکن است تا زمان
ایجاد Reputation هشدار بدهد.

## Dependencyها و اینترنت

`setup_windows.bat` محیط توسعه را فقط یک بار می‌سازد. اجرای روزمره با
`run_windows.bat` هیچ نصب یا اتصال اینترنتی انجام نمی‌دهد.

برای آماده‌کردن Dependencyهای آفلاین، یک بار در Windows آنلاین اجرا کنید:

```bat
cache_windows_dependencies.bat
```

فایل‌های Wheel در `vendor\wheels` ذخیره می‌شوند. این پوشه بزرگ و وابسته به
نسخهٔ Python و معماری سیستم است؛ بنابراین بهتر است Cache خصوصی Build باشد،
نه بخشی از مخزن عمومی.

در نسخهٔ قابل انتشار، PyInstaller تمام Runtimeهای Python، PySide6 و Pillow را
داخل پوشهٔ برنامه قرار می‌دهد. کاربر نهایی هیچ Dependency دانلود نمی‌کند.

## ساخت ShotLab.exe

دو فایل Static ویندوز را در مسیر زیر قرار دهید:

```text
vendor/
└── ffmpeg/
    ├── ffmpeg.exe
    └── ffprobe.exe
```

سپس:

```bat
build_windows.bat
```

خروجی:

```text
dist\ShotLab\ShotLab.exe
```

این خروجی One-folder است. این روش برای Qt Multimedia پایدارتر، سریع‌تر و
کم‌خطاتر از One-file است. کاربر می‌تواند مستقیماً `ShotLab.exe` را اجرا کند و
به Python، FFmpeg یا اینترنت نیاز ندارد.

## ساخت Portable ZIP و Installer

برای Installer، نسخهٔ ۶۴ بیتی Inno Setup 7 را نصب کنید و سپس اجرا کنید:

```bat
publish_windows.bat
```

خروجی‌ها:

```text
release/
├── ShotLab_Portable_v<version>.zip
└── ShotLab_Setup_v<version>.exe
```

اسکریپت ابتدا Inno Setup 7 را در مسیرهای معمول نصب جست‌وجو می‌کند و برای
سازگاری، نسخهٔ 6 را نیز پشتیبانی می‌کند. اگر هیچ‌کدام نصب نباشند، Portable
ZIP ساخته می‌شود و فقط مرحلهٔ Installer رد می‌شود.

## امضای دیجیتال

پس از تهیهٔ Certificate، فایل اصلی و Installer را با Windows SDK SignTool و
SHA-256 امضا کنید. نمونهٔ عمومی:

```bat
signtool sign /a /fd SHA256 /tr <timestamp-url> /td SHA256 dist\ShotLab\ShotLab.exe
signtool sign /a /fd SHA256 /tr <timestamp-url> /td SHA256 release\ShotLab_Setup_v<version>.exe
```

Certificate خصوصی، Password یا Token امضا را هرگز داخل پروژه یا Git قرار
ندهید.

## پوشهٔ Quality Assurance

کدهای بررسی داخلی در `quality_assurance` نگهداری می‌شوند و در Build نهایی یا
Installer حضور ندارند. وجود این بررسی‌ها برای سورس حرفه‌ای ضروری است، اما
کاربر نهایی آن‌ها را نمی‌بیند.
