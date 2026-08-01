(() => {
  "use strict";

  if (window.__shotlabYouTubeCaptureInstalled) {
    return;
  }
  window.__shotlabYouTubeCaptureInstalled = true;

  const BUTTON_ID = "shotlab-youtube-capture";
  const TOAST_ID = "shotlab-youtube-toast";
  const CLEAN_CAPTURE_CLASS = "shotlab-clean-frame-capture";
  const WATCH_PATH = "/watch";
  let captureInProgress = false;
  let ensureScheduled = false;
  let resetTimer = 0;
  let toastTimer = 0;

  const GOLD_MARK = `
    <svg viewBox="0 0 90 90" aria-hidden="true" focusable="false">
      <path fill="currentColor" d="M81.18 44.52l-5.48-1.6c-6.49-1.89-10.95-7.84-10.95-14.59v-14.8c0-5.91-4.05-11.12-9.82-12.42C51.5.34 47.91-.05 44.23 0 20.03.43.33 20.2 0 44.39-.34 69.53 19.94 90.01 45 90.01c20.57 0 37.91-13.8 43.28-32.64 1.57-5.51-1.61-11.25-7.1-12.85ZM45 7.37c3.27 0 5.79 2.86 5.4 6.1l-1.17 9.55A4.27 4.27 0 0 1 45 26.68a4.27 4.27 0 0 1-4.23-3.66l-1.17-9.55c-.4-3.24 2.13-6.1 5.4-6.1ZM7.36 45.01c0-3.27 2.86-5.79 6.1-5.4l9.55 1.17a4.27 4.27 0 0 1 3.66 4.23 4.27 4.27 0 0 1-3.66 4.23l-9.55 1.17c-3.24.4-6.1-2.13-6.1-5.4Zm25.02 18.6-5.93 7.58c-2.01 2.57-5.82 2.81-8.13.5-2.31-2.31-2.08-6.12.5-8.13l7.58-5.93c1.7-1.27 4.07-1.1 5.58.4 1.5 1.5 1.67 3.87.4 5.58Zm-.4-31.62c-1.5 1.5-3.87 1.67-5.58.4l-7.58-5.93c-2.57-2.01-2.81-5.82-.5-8.13 2.31-2.31 6.12-2.08 8.13.5l5.93 7.58c1.27 1.7 1.1 4.07-.4 5.58ZM45 82.66c-3.27 0-5.79-2.86-5.4-6.1l1.17-9.55A4.27 4.27 0 0 1 45 63.35a4.27 4.27 0 0 1 4.23 3.66l1.17 9.55c.4 3.24-2.13 6.1-5.4 6.1Zm27.17-15.68a9.31 9.31 0 1 1 0-18.62 9.31 9.31 0 0 1 0 18.62Z"/>
    </svg>
  `;

  function isPersian() {
    const language = (
      document.documentElement.lang ||
      navigator.language ||
      ""
    ).toLowerCase();
    return language.startsWith("fa");
  }

  function copy(en, fa) {
    return isPersian() ? fa : en;
  }

  function createButton() {
    const button = document.createElement("button");
    button.id = BUTTON_ID;
    button.type = "button";
    button.dataset.state = "idle";
    button.title = copy(
      "Capture the current YouTube frame in ShotLab",
      "ارسال فریم فعلی یوتیوب به ShotLab"
    );
    button.setAttribute("aria-label", button.title);
    button.innerHTML = `
      <span class="shotlab-youtube-icon">${GOLD_MARK}</span>
      <span class="shotlab-youtube-label">ShotLab</span>
    `;
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      captureCurrentFrame(button);
    });
    return button;
  }

  function findActionContainer() {
    return (
      document.querySelector(
        "ytd-watch-metadata #top-level-buttons-computed"
      ) ||
      document.querySelector(
        "#above-the-fold #actions #top-level-buttons-computed"
      ) ||
      document.querySelector(
        "ytd-menu-renderer #top-level-buttons-computed"
      )
    );
  }

  function ensureButton() {
    ensureScheduled = false;
    const existing = document.getElementById(BUTTON_ID);
    if (location.pathname !== WATCH_PATH) {
      existing?.remove();
      return;
    }
    const container = findActionContainer();
    if (!container) {
      return;
    }
    if (existing?.parentElement === container) {
      return;
    }
    existing?.remove();
    container.appendChild(createButton());
  }

  function scheduleEnsureButton() {
    if (ensureScheduled) {
      return;
    }
    ensureScheduled = true;
    window.requestAnimationFrame(ensureButton);
  }

  function findVideo() {
    return (
      document.querySelector("video.html5-main-video") ||
      document.querySelector("#movie_player video") ||
      document.querySelector("video")
    );
  }

  function displayedVideoRect(video) {
    const box = video.getBoundingClientRect();
    const intrinsicWidth = Number(video.videoWidth);
    const intrinsicHeight = Number(video.videoHeight);
    if (
      box.width <= 0 ||
      box.height <= 0 ||
      intrinsicWidth <= 0 ||
      intrinsicHeight <= 0
    ) {
      return null;
    }

    const style = window.getComputedStyle(video);
    if (style.objectFit === "fill" || style.objectFit === "cover") {
      return {
        left: box.left,
        top: box.top,
        width: box.width,
        height: box.height
      };
    }

    const videoAspect = intrinsicWidth / intrinsicHeight;
    const boxAspect = box.width / box.height;
    let width = box.width;
    let height = box.height;
    let left = box.left;
    let top = box.top;
    if (boxAspect > videoAspect) {
      width = box.height * videoAspect;
      left += (box.width - width) / 2;
    } else if (boxAspect < videoAspect) {
      height = box.width / videoAspect;
      top += (box.height - height) / 2;
    }
    return { left, top, width, height };
  }

  function rectIsFullyVisible(rect) {
    const tolerance = 2;
    return (
      rect.left >= -tolerance &&
      rect.top >= -tolerance &&
      rect.left + rect.width <= window.innerWidth + tolerance &&
      rect.top + rect.height <= window.innerHeight + tolerance
    );
  }

  function hideExistingToast() {
    clearTimeout(toastTimer);
    const toast = document.getElementById(TOAST_ID);
    if (toast) {
      toast.dataset.visible = "false";
    }
  }

  function hidePlayerChrome(video) {
    const player =
      video.closest(".html5-video-player") ||
      document.querySelector("#movie_player");
    if (!player) {
      return () => {};
    }
    const wasAlreadyHidden = player.classList.contains(
      CLEAN_CAPTURE_CLASS
    );
    player.classList.add(CLEAN_CAPTURE_CLASS);
    return () => {
      if (!wasAlreadyHidden) {
        player.classList.remove(CLEAN_CAPTURE_CLASS);
      }
    };
  }

  function currentVideoTitle() {
    const heading = document.querySelector(
      "ytd-watch-metadata h1 yt-formatted-string"
    );
    const title = heading?.textContent?.trim();
    if (title) {
      return title;
    }
    return document.title.replace(/\s*-\s*YouTube\s*$/i, "").trim();
  }

  function nextPaint() {
    return new Promise((resolve) => {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(resolve);
      });
    });
  }

  function shortDelay(milliseconds) {
    return new Promise((resolve) => {
      window.setTimeout(resolve, milliseconds);
    });
  }

  function fixedTopInset() {
    const masthead = document.querySelector("ytd-masthead");
    if (!masthead) {
      return 8;
    }
    const rect = masthead.getBoundingClientRect();
    if (
      rect.top <= 1 &&
      rect.bottom > 0 &&
      rect.bottom < window.innerHeight / 3
    ) {
      return Math.ceil(rect.bottom + 8);
    }
    return 8;
  }

  async function bringVideoFullyIntoView(video) {
    let rect = displayedVideoRect(video);
    if (!rect || rectIsFullyVisible(rect)) {
      return rect;
    }

    for (let attempt = 0; attempt < 3; attempt += 1) {
      const topInset = fixedTopInset();
      const bottomInset = 8;
      const availableHeight =
        window.innerHeight - topInset - bottomInset;
      const desiredTop =
        rect.height <= availableHeight
          ? topInset + (availableHeight - rect.height) / 2
          : Math.max(8, (window.innerHeight - rect.height) / 2);
      const targetScrollTop = Math.max(
        0,
        window.scrollY + rect.top - desiredTop
      );

      window.scrollTo(window.scrollX, targetScrollTop);
      await nextPaint();
      await shortDelay(80);

      rect = displayedVideoRect(video);
      if (!rect || rectIsFullyVisible(rect)) {
        return rect;
      }
    }
    return rect;
  }

  async function captureCurrentFrame(button) {
    if (captureInProgress) {
      return;
    }
    const video = findVideo();
    if (!video || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
      showError(button, "VIDEO_NOT_READY");
      return;
    }

    captureInProgress = true;
    clearTimeout(resetTimer);
    setButtonState(
      button,
      "sending",
      copy("Sending…", "در حال ارسال…")
    );
    hideExistingToast();
    video.pause();
    await nextPaint();

    const rect = await bringVideoFullyIntoView(video);
    if (!rect || rect.width < 32 || rect.height < 32) {
      captureInProgress = false;
      showError(button, "VIDEO_NOT_READY");
      return;
    }
    if (!rectIsFullyVisible(rect)) {
      captureInProgress = false;
      showError(button, "VIDEO_NOT_FULLY_VISIBLE");
      return;
    }

    let response;
    const restorePlayerChrome = hidePlayerChrome(video);
    try {
      await nextPaint();
      await shortDelay(60);
      response = await chrome.runtime.sendMessage({
        type: "SHOTLAB_CAPTURE_REQUEST",
        payload: {
          rect,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight
          },
          sourceTitle: currentVideoTitle(),
          sourceUrl: location.href,
          sourceTimeSeconds: Number(video.currentTime) || 0,
          videoWidth: Number(video.videoWidth) || 0,
          videoHeight: Number(video.videoHeight) || 0
        }
      });
    } catch (error) {
      response = {
        ok: false,
        code: "EXTENSION_ERROR",
        message: String(error?.message || error || "")
      };
    } finally {
      restorePlayerChrome();
    }
    captureInProgress = false;

    if (response?.ok) {
      setButtonState(
        button,
        "success",
        copy("Sent!", "ارسال شد!")
      );
      const libraryName = String(response.libraryName || "").trim();
      showToast(
        libraryName
          ? copy(
              `Frame sent to “${libraryName}”.`,
              `فریم به کتابخانهٔ «${libraryName}» فرستاده شد.`
            )
          : copy(
              "Frame sent to ShotLab.",
              "فریم به ShotLab فرستاده شد."
            ),
        "success"
      );
      scheduleButtonReset(button, 2200);
      return;
    }
    showError(button, response?.code, response?.message);
  }

  function showError(button, code, fallbackMessage = "") {
    const messages = {
      VIDEO_NOT_READY: copy(
        "The YouTube video is not ready yet.",
        "ویدیوی یوتیوب هنوز آماده نیست."
      ),
      VIDEO_NOT_FULLY_VISIBLE: copy(
        "Make the complete video visible, then try again.",
        "ابتدا تمام کادر ویدیو را در صفحه قابل‌مشاهده کنید."
      ),
      SHOTLAB_NOT_RUNNING: copy(
        "Open ShotLab, then try again.",
        "ابتدا ShotLab را باز کنید و دوباره تلاش کنید."
      ),
      NO_ACTIVE_LIBRARY: copy(
        "Open a library in ShotLab first.",
        "ابتدا یک کتابخانه را در ShotLab باز کنید."
      ),
      SHOTLAB_BUSY: copy(
        "Confirm or discard the current ShotLab frame first.",
        "ابتدا فریم در حال ویرایش ShotLab را تأیید یا حذف کنید."
      ),
      SHOTLAB_TIMEOUT: copy(
        "ShotLab took too long to prepare the frame.",
        "آماده‌سازی فریم در ShotLab بیش از حد طول کشید."
      ),
      PROTOCOL_MISMATCH: copy(
        "Update ShotLab and the extension to matching versions.",
        "نسخهٔ ShotLab و افزونه باید با یکدیگر هماهنگ باشند."
      )
    };
    const message =
      messages[code] ||
      fallbackMessage ||
      copy(
        "The frame could not be sent to ShotLab.",
        "ارسال فریم به ShotLab ممکن نشد."
      );
    setButtonState(
      button,
      "error",
      copy("Try again", "تلاش دوباره")
    );
    showToast(message, "error");
    scheduleButtonReset(button, 3600);
  }

  function setButtonState(button, state, label) {
    if (!button?.isConnected) {
      return;
    }
    button.dataset.state = state;
    button.disabled = state === "sending";
    const labelElement = button.querySelector(".shotlab-youtube-label");
    if (labelElement) {
      labelElement.textContent = label;
    }
  }

  function scheduleButtonReset(button, delay) {
    clearTimeout(resetTimer);
    resetTimer = window.setTimeout(() => {
      setButtonState(button, "idle", "ShotLab");
    }, delay);
  }

  function showToast(message, kind) {
    let toast = document.getElementById(TOAST_ID);
    if (!toast) {
      toast = document.createElement("div");
      toast.id = TOAST_ID;
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.documentElement.appendChild(toast);
    }
    toast.dir = isPersian() ? "rtl" : "ltr";
    toast.dataset.kind = kind;
    toast.textContent = message;
    toast.dataset.visible = "true";
    clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => {
      toast.dataset.visible = "false";
    }, kind === "error" ? 5200 : 3200);
  }

  chrome.runtime.onMessage.addListener((message) => {
    if (message?.type !== "SHOTLAB_CAPTURE_FROM_ACTION") {
      return;
    }
    const button =
      document.getElementById(BUTTON_ID) ||
      createButton();
    captureCurrentFrame(button);
  });

  const observer = new MutationObserver(scheduleEnsureButton);
  if (document.body) {
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
  document.addEventListener("yt-navigate-finish", scheduleEnsureButton);
  window.addEventListener("popstate", scheduleEnsureButton);
  scheduleEnsureButton();
})();
