# ShotLab Capture Bridge

The ShotLab Chrome extension adds a native-looking **ShotLab** button to the
action row below standard YouTube videos. Pressing it pauses the video,
captures only the visible video image, and sends that frame to the running
ShotLab desktop application.

ShotLab opens the received image as an editable draft, extracts its color
palette, and waits for you to confirm or discard it. The extension does not
download the YouTube video or send the frame to an internet service.

The standalone extension repository, complete documentation, privacy policy,
and release files are available at
[ShotLab Capture Bridge](https://github.com/maisamh80/ShotLab-Capture-Bridge).

## Install for development

1. Open ShotLab and open the library that should receive the frame.
2. Open `chrome://extensions` in Google Chrome.
3. Enable **Developer mode**.
4. Select **Load unpacked**.
5. Select this `browser_extension` folder.
6. Open or reload a standard YouTube watch page.

The **ShotLab** button will appear in the action row below the video. You can
also pin the extension and press its toolbar icon while a YouTube watch page is
active.

If an older unpacked version is already installed, replace its files, press
**Reload** on its card in `chrome://extensions`, and then reload the YouTube
page.

## Use

1. Open ShotLab and select a library.
2. Open a YouTube video and make sure its complete picture is visible.
3. Stop on the desired frame.
4. Press the **ShotLab** button below the video.
5. Review the received frame, palette, title, and other information in
   ShotLab's Capture Workspace.
6. Confirm or discard the draft before sending the next frame.

If clicking the button has moved part of the player outside the browser
viewport, the extension first scrolls the complete video image back into view
and then captures it.

YouTube's playback controls, gradients, cards, captions, and other player UI
are hidden only for the instant in which the screenshot is taken and restored
immediately afterward. Logos or captions permanently burned into the source
video remain part of the frame.

The captured image resolution is the resolution at which Chrome is currently
displaying the video. Theater mode generally provides a larger frame.

## Local connection and privacy

- The extension talks only to `http://127.0.0.1:47831`.
- ShotLab listens only on the local loopback interface.
- Only JPEG or PNG data from a YouTube URL is accepted.
- A received frame remains a draft until the user confirms it.
- YouTube video files and streams are never downloaded by this extension.
- Chrome requires the `<all_urls>` host permission for
  `captureVisibleTab` when capture starts from the ShotLab button injected into
  the YouTube page. Despite that browser-level permission, ShotLab's content
  script is configured to run only on `https://www.youtube.com/*`, and the
  captured image is sent only to the fixed loopback address above.

To check the local bridge from PowerShell while ShotLab is running, use:

```powershell
Invoke-RestMethod http://127.0.0.1:47831/status
```

To open the same address in your default browser, use:

```powershell
Start-Process "http://127.0.0.1:47831/status"
```

---

<div dir="rtl" align="right">

# پل کپچر ShotLab

افزونهٔ Chrome شات‌لب، دکمه‌ای با عنوان **ShotLab** به ردیف دکمه‌های زیر
ویدیوهای معمولی یوتیوب اضافه می‌کند. با فشردن آن، ویدیو متوقف می‌شود، فقط تصویر
قابل‌مشاهدهٔ ویدیو کپچر می‌شود و همان فریم به نرم‌افزار دسکتاپ ShotLab فرستاده
می‌شود.

ShotLab تصویر دریافت‌شده را به‌شکل Draft قابل‌ویرایش باز می‌کند، پالت رنگ را
استخراج می‌کند و تا زمان تأیید یا حذف آن منتظر می‌ماند. افزونه ویدیوی یوتیوب را
دانلود نمی‌کند و فریم را به هیچ سرویس اینترنتی نمی‌فرستد.

ریپوزیتوری مستقل افزونه، مستندات کامل، بیانیهٔ حریم خصوصی و فایل‌های انتشار
در
<a href="https://github.com/maisamh80/ShotLab-Capture-Bridge"><bdi dir="ltr">ShotLab Capture Bridge</bdi></a>
قرار دارند.

## نصب نسخهٔ آزمایشی

1. ShotLab را باز کنید و کتابخانهٔ مقصد را انتخاب کنید.
2. در Google Chrome آدرس `chrome://extensions` را باز کنید.
3. گزینهٔ **Developer mode** را فعال کنید.
4. روی **Load unpacked** بزنید.
5. همین پوشهٔ `browser_extension` را انتخاب کنید.
6. یک صفحهٔ معمولی نمایش ویدیوی یوتیوب را باز یا دوباره بارگذاری کنید.

دکمهٔ **ShotLab** در ردیف دکمه‌های زیر ویدیو ظاهر می‌شود. همچنین می‌توانید
افزونه را در Toolbar پین کنید و هنگام فعال‌بودن صفحهٔ یوتیوب، روی آیکون آن
بزنید.

اگر نسخهٔ قدیمی افزونه را به‌صورت <bdi dir="ltr">Load unpacked</bdi> نصب
کرده‌اید، فایل‌ها را جایگزین کنید، در صفحهٔ
<bdi dir="ltr"><code>chrome://extensions</code></bdi> روی
<bdi dir="ltr"><b>Reload</b></bdi> کارت افزونه بزنید و سپس صفحهٔ یوتیوب را
دوباره بارگذاری کنید.

## روش استفاده

1. ShotLab را باز کنید و یک کتابخانه را انتخاب کنید.
2. ویدیوی یوتیوب را باز کنید و مطمئن شوید تمام تصویر آن داخل صفحه دیده می‌شود.
3. روی فریم دلخواه توقف کنید.
4. دکمهٔ **ShotLab** را زیر ویدیو بزنید.
5. فریم، پالت و اطلاعات آن را در Capture Workspace بررسی و ویرایش کنید.
6. پیش از ارسال فریم بعدی، Draft فعلی را تأیید یا حذف کنید.

اگر هنگام کلیک روی دکمه بخشی از پلیر از کادر مرورگر خارج شده باشد، افزونه
ابتدا تمام تصویر ویدیو را دوباره داخل صفحه قرار می‌دهد و سپس کپچر می‌کند.

کنترل‌ها، گرادیان‌ها، کارت‌ها، زیرنویس‌ها و دیگر اجزای رابط پلیر یوتیوب فقط
در لحظهٔ گرفتن تصویر مخفی و بلافاصله پس از آن دوباره نمایش داده می‌شوند.
لوگو یا زیرنویسی که به‌صورت دائمی داخل خود ویدیوی منبع ثبت شده باشد، بخشی از
فریم است و باقی می‌ماند.

رزولوشن تصویر کپچر‌شده برابر اندازه‌ای است که ویدیو در Chrome نمایش داده
می‌شود. حالت Theater معمولاً تصویر بزرگ‌تری در اختیار افزونه می‌گذارد.

## اتصال محلی و حریم خصوصی

- افزونه فقط با آدرس `http://127.0.0.1:47831` ارتباط برقرار می‌کند.
- ShotLab فقط روی رابط Loopback همان کامپیوتر گوش می‌دهد.
- فقط تصویر JPEG یا PNG دارای آدرس منبع یوتیوب پذیرفته می‌شود.
- فریم دریافت‌شده تا زمان تأیید کاربر به‌شکل Draft باقی می‌ماند.
- این افزونه فایل یا استریم ویدیوی یوتیوب را دانلود نمی‌کند.
- کروم برای استفاده از <bdi dir="ltr"><code>captureVisibleTab</code></bdi>
  از طریق دکمه‌ای که داخل صفحهٔ یوتیوب قرار گرفته است، مجوز
  <bdi dir="ltr"><code>&lt;all_urls&gt;</code></bdi> را الزامی می‌کند.
  با وجود این مجوز در سطح مرورگر، اسکریپت ShotLab فقط روی
  <bdi dir="ltr"><code>https://www.youtube.com/*</code></bdi> اجرا می‌شود و
  تصویر کپچر‌شده را فقط به آدرس ثابت محلی بالا می‌فرستد.

برای آزمایش پل محلی درحالی‌که ShotLab باز است، این فرمان را در PowerShell
اجرا کنید:

```powershell
Invoke-RestMethod http://127.0.0.1:47831/status
```

برای بازکردن همین آدرس در مرورگر پیش‌فرض:

```powershell
Start-Process "http://127.0.0.1:47831/status"
```

</div>
