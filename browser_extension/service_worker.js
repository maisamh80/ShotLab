"use strict";

const BRIDGE_URL = "http://127.0.0.1:47831/capture";
const BRIDGE_PROTOCOL = 1;
const REQUEST_TIMEOUT_MS = 35000;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "SHOTLAB_CAPTURE_REQUEST") {
    return false;
  }
  captureAndSend(message.payload, sender)
    .then(sendResponse)
    .catch((error) => {
      sendResponse({
        ok: false,
        code: "EXTENSION_ERROR",
        message: String(error?.message || error || "")
      });
    });
  return true;
});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab.id || !String(tab.url || "").startsWith("https://www.youtube.com/")) {
    return;
  }
  try {
    await chrome.tabs.sendMessage(tab.id, {
      type: "SHOTLAB_CAPTURE_FROM_ACTION"
    });
  } catch (_error) {
    // The in-page button is the primary UI. A toolbar click on an unsupported
    // YouTube surface intentionally does nothing.
  }
});

async function captureAndSend(payload, sender) {
  if (!sender.tab || !sender.tab.active) {
    return {
      ok: false,
      code: "TAB_NOT_ACTIVE",
      message: "The YouTube tab must be active."
    };
  }
  const rect = validRect(payload?.rect);
  const viewport = validViewport(payload?.viewport);
  if (!rect || !viewport) {
    return {
      ok: false,
      code: "INVALID_CAPTURE_AREA",
      message: "The visible video area could not be measured."
    };
  }

  let screenshotDataUrl;
  try {
    screenshotDataUrl = await chrome.tabs.captureVisibleTab(
      sender.tab.windowId,
      {
        format: "png"
      }
    );
  } catch (error) {
    return {
      ok: false,
      code: "SCREENSHOT_FAILED",
      message: String(error?.message || error || "")
    };
  }

  let imageDataUrl;
  try {
    imageDataUrl = await cropScreenshot(
      screenshotDataUrl,
      rect,
      viewport
    );
  } catch (error) {
    return {
      ok: false,
      code: "SCREENSHOT_CROP_FAILED",
      message: String(error?.message || error || "")
    };
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(BRIDGE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        client: "shotlab-chrome-extension",
        protocol: BRIDGE_PROTOCOL,
        imageDataUrl,
        sourceTitle: String(payload.sourceTitle || ""),
        sourceUrl: String(payload.sourceUrl || ""),
        sourceTimeSeconds: Number(payload.sourceTimeSeconds) || 0,
        videoWidth: Number(payload.videoWidth) || 0,
        videoHeight: Number(payload.videoHeight) || 0
      }),
      cache: "no-store",
      signal: controller.signal
    });
    const result = await response.json().catch(() => null);
    if (result && typeof result === "object") {
      return result;
    }
    return {
      ok: false,
      code: "INVALID_SHOTLAB_RESPONSE",
      message: `ShotLab returned HTTP ${response.status}.`
    };
  } catch (error) {
    if (error?.name === "AbortError") {
      return {
        ok: false,
        code: "SHOTLAB_TIMEOUT",
        message: "ShotLab did not respond in time."
      };
    }
    return {
      ok: false,
      code: "SHOTLAB_NOT_RUNNING",
      message: "The local ShotLab capture bridge is not available."
    };
  } finally {
    clearTimeout(timeout);
  }
}

function validRect(value) {
  if (!value || typeof value !== "object") {
    return null;
  }
  const rect = {
    left: Number(value.left),
    top: Number(value.top),
    width: Number(value.width),
    height: Number(value.height)
  };
  if (
    !Object.values(rect).every(Number.isFinite) ||
    rect.width < 16 ||
    rect.height < 16
  ) {
    return null;
  }
  return rect;
}

function validViewport(value) {
  if (!value || typeof value !== "object") {
    return null;
  }
  const viewport = {
    width: Number(value.width),
    height: Number(value.height)
  };
  if (
    !Object.values(viewport).every(Number.isFinite) ||
    viewport.width < 100 ||
    viewport.height < 100
  ) {
    return null;
  }
  return viewport;
}

async function cropScreenshot(dataUrl, rect, viewport) {
  const screenshotBlob = await (await fetch(dataUrl)).blob();
  const screenshot = await createImageBitmap(screenshotBlob);
  try {
    const scaleX = screenshot.width / viewport.width;
    const scaleY = screenshot.height / viewport.height;
    const sourceX = clamp(
      Math.round(rect.left * scaleX),
      0,
      screenshot.width - 1
    );
    const sourceY = clamp(
      Math.round(rect.top * scaleY),
      0,
      screenshot.height - 1
    );
    const sourceWidth = clamp(
      Math.round(rect.width * scaleX),
      1,
      screenshot.width - sourceX
    );
    const sourceHeight = clamp(
      Math.round(rect.height * scaleY),
      1,
      screenshot.height - sourceY
    );
    if (
      sourceWidth < 16 ||
      sourceHeight < 16 ||
      sourceWidth > 16384 ||
      sourceHeight > 16384
    ) {
      throw new Error("The measured video frame has an invalid size.");
    }

    const canvas = new OffscreenCanvas(sourceWidth, sourceHeight);
    const context = canvas.getContext("2d", {
      alpha: false,
      desynchronized: true
    });
    if (!context) {
      throw new Error("Chrome could not create the capture canvas.");
    }
    context.drawImage(
      screenshot,
      sourceX,
      sourceY,
      sourceWidth,
      sourceHeight,
      0,
      0,
      sourceWidth,
      sourceHeight
    );
    const frameBlob = await canvas.convertToBlob({
      type: "image/jpeg",
      quality: 0.96
    });
    return blobToDataUrl(frameBlob);
  } finally {
    screenshot.close();
  }
}

async function blobToDataUrl(blob) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  const chunkSize = 0x8000;
  let binary = "";
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    binary += String.fromCharCode(
      ...bytes.subarray(offset, offset + chunkSize)
    );
  }
  return `data:${blob.type};base64,${btoa(binary)}`;
}

function clamp(value, minimum, maximum) {
  return Math.min(Math.max(value, minimum), maximum);
}
