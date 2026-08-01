from __future__ import annotations

import base64
import http.client
import json
import unittest
from pathlib import Path

from shotlab.browser_bridge import (
    BRIDGE_HOST,
    BRIDGE_PROTOCOL_VERSION,
    BrowserBridgeServer,
)


ROOT = Path(__file__).resolve().parents[1]
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
    "nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


class BrowserBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.received = []

        def accept_capture(request) -> None:
            self.received.append(request)
            request.accept(libraryName="Test Library", storageMode="small")

        self.bridge = BrowserBridgeServer(
            accept_capture,
            port=0,
        )
        self.port = self.bridge.start()

    def tearDown(self) -> None:
        self.bridge.stop()

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: dict | None = None,
        origin: str | None = None,
    ) -> tuple[int, dict, dict[str, str]]:
        connection = http.client.HTTPConnection(
            BRIDGE_HOST,
            self.port,
            timeout=3,
        )
        headers: dict[str, str] = {}
        body: str | None = None
        if payload is not None:
            body = json.dumps(payload)
            headers["Content-Type"] = "application/json"
        if origin is not None:
            headers["Origin"] = origin
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw_body = response.read()
        response_headers = dict(response.getheaders())
        connection.close()
        decoded = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        return response.status, decoded, response_headers

    def valid_payload(self) -> dict:
        encoded = base64.b64encode(ONE_PIXEL_PNG).decode("ascii")
        return {
            "client": "shotlab-chrome-extension",
            "protocol": BRIDGE_PROTOCOL_VERSION,
            "imageDataUrl": f"data:image/png;base64,{encoded}",
            "sourceTitle": "A YouTube frame",
            "sourceUrl": "https://www.youtube.com/watch?v=shotlab-test",
            "sourceTimeSeconds": 12.345,
            "videoWidth": 1920,
            "videoHeight": 1080,
        }

    def test_status_and_capture_round_trip(self) -> None:
        status, payload, _headers = self.request("GET", "/status")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["protocol"], BRIDGE_PROTOCOL_VERSION)

        status, payload, _headers = self.request(
            "POST",
            "/capture",
            payload=self.valid_payload(),
            origin="chrome-extension://abcdefghijklmnop",
        )
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["libraryName"], "Test Library")
        self.assertEqual(len(self.received), 1)
        capture = self.received[0]
        self.assertEqual(capture.image_bytes, ONE_PIXEL_PNG)
        self.assertEqual(capture.image_format, "png")
        self.assertEqual(capture.source_time_seconds, 12.345)

    def test_rejects_web_page_origin(self) -> None:
        status, payload, _headers = self.request(
            "POST",
            "/capture",
            payload=self.valid_payload(),
            origin="https://www.youtube.com",
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["code"], "ORIGIN_NOT_ALLOWED")
        self.assertFalse(self.received)

    def test_rejects_non_youtube_source(self) -> None:
        capture = self.valid_payload()
        capture["sourceUrl"] = "https://example.com/video"
        status, payload, _headers = self.request(
            "POST",
            "/capture",
            payload=capture,
            origin="chrome-extension://abcdefghijklmnop",
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "INVALID_SOURCE")
        self.assertFalse(self.received)

    def test_extension_preflight_is_allowed(self) -> None:
        status, _payload, headers = self.request(
            "OPTIONS",
            "/capture",
            origin="chrome-extension://abcdefghijklmnop",
        )
        self.assertEqual(status, 204)
        self.assertEqual(
            headers["Access-Control-Allow-Origin"],
            "chrome-extension://abcdefghijklmnop",
        )
        self.assertEqual(
            headers["Access-Control-Allow-Private-Network"],
            "true",
        )


class BrowserExtensionContractTests(unittest.TestCase):
    def test_manifest_has_capture_permission_and_youtube_only_injection(
        self,
    ) -> None:
        manifest = json.loads(
            (ROOT / "browser_extension" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertIn("<all_urls>", manifest["host_permissions"])
        self.assertEqual(
            manifest["content_scripts"][0]["matches"],
            ["https://www.youtube.com/*"],
        )

    def test_extension_uses_visible_tab_and_in_page_button(self) -> None:
        service_worker = (
            ROOT / "browser_extension" / "service_worker.js"
        ).read_text(encoding="utf-8")
        content_script = (
            ROOT / "browser_extension" / "content.js"
        ).read_text(encoding="utf-8")
        content_style = (
            ROOT / "browser_extension" / "content.css"
        ).read_text(encoding="utf-8")
        self.assertIn("chrome.tabs.captureVisibleTab", service_worker)
        self.assertIn("127.0.0.1:47831/capture", service_worker)
        self.assertIn("top-level-buttons-computed", content_script)
        self.assertIn("shotlab-youtube-capture", content_script)
        self.assertIn("video.pause()", content_script)
        self.assertIn("bringVideoFullyIntoView", content_script)
        self.assertIn("window.scrollTo", content_script)
        self.assertIn("hidePlayerChrome", content_script)
        self.assertIn("restorePlayerChrome", content_script)
        self.assertIn("shotlab-clean-frame-capture", content_style)
        self.assertIn(".ytp-chrome-bottom", content_style)
        self.assertIn(".ytp-cards-button", content_style)

    def test_windows_publisher_packages_extension_separately(self) -> None:
        publisher = (ROOT / "publish_windows.bat").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "ShotLab_Chrome_Extension_v%SHOTLAB_EXTENSION_VERSION%.zip",
            publisher,
        )
        self.assertIn("Compress-Archive -Path 'browser_extension\\*'", publisher)


if __name__ == "__main__":
    unittest.main()
