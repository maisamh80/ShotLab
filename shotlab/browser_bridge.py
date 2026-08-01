from __future__ import annotations

import base64
import binascii
import json
import math
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.parse import urlparse


BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 47831
BRIDGE_PROTOCOL_VERSION = 1
MAX_REQUEST_BYTES = 36 * 1024 * 1024
MAX_IMAGE_BYTES = 24 * 1024 * 1024
RESPONSE_TIMEOUT_SECONDS = 30.0

_ALLOWED_YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    }
)


@dataclass(slots=True)
class BrowserCaptureRequest:
    """A validated frame waiting to be accepted by ShotLab's UI thread."""

    image_bytes: bytes
    image_format: str
    source_title: str
    source_url: str
    source_time_seconds: float
    video_width: int
    video_height: int
    _completed: threading.Event = field(
        default_factory=threading.Event,
        init=False,
        repr=False,
    )
    _completion_lock: threading.Lock = field(
        default_factory=threading.Lock,
        init=False,
        repr=False,
    )
    _http_status: int = field(default=202, init=False, repr=False)
    _response: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def accept(self, **details: Any) -> None:
        self._complete(
            200,
            {
                "ok": True,
                "code": "CAPTURE_ACCEPTED",
                **details,
            },
        )

    def reject(
        self,
        code: str,
        message: str,
        *,
        http_status: int = 409,
    ) -> None:
        self._complete(
            http_status,
            {
                "ok": False,
                "code": code,
                "message": message,
            },
        )

    def wait_for_completion(
        self,
        timeout: float = RESPONSE_TIMEOUT_SECONDS,
    ) -> tuple[int, dict[str, Any]] | None:
        if not self._completed.wait(timeout):
            return None
        with self._completion_lock:
            return self._http_status, dict(self._response)

    def _complete(self, status: int, response: dict[str, Any]) -> None:
        with self._completion_lock:
            if self._completed.is_set():
                return
            self._http_status = int(status)
            self._response = dict(response)
            self._completed.set()


CaptureCallback = Callable[[BrowserCaptureRequest], None]


class _BridgeHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        capture_callback: CaptureCallback,
    ) -> None:
        self.capture_callback = capture_callback
        super().__init__(server_address, _BridgeRequestHandler)


class _BridgeRequestHandler(BaseHTTPRequestHandler):
    server: _BridgeHTTPServer
    server_version = "ShotLabCaptureBridge/1"
    sys_version = ""

    def log_message(self, _format: str, *args: object) -> None:
        # Browser health checks should not open a console or produce noisy logs.
        return

    def do_OPTIONS(self) -> None:
        if not self._origin_is_allowed():
            self._send_error(
                403,
                "ORIGIN_NOT_ALLOWED",
                "Only a Chrome extension may contact this local endpoint.",
            )
            return
        self.send_response(204)
        self._send_common_headers()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path != "/status":
            self._send_error(404, "NOT_FOUND", "Unknown ShotLab bridge endpoint.")
            return
        if not self._origin_is_allowed():
            self._send_error(
                403,
                "ORIGIN_NOT_ALLOWED",
                "Only a Chrome extension may contact this local endpoint.",
            )
            return
        self._send_json(
            200,
            {
                "ok": True,
                "service": "ShotLab Capture Bridge",
                "protocol": BRIDGE_PROTOCOL_VERSION,
            },
        )

    def do_POST(self) -> None:
        if self.path != "/capture":
            self._send_error(404, "NOT_FOUND", "Unknown ShotLab bridge endpoint.")
            return
        if not self._origin_is_allowed():
            self._send_error(
                403,
                "ORIGIN_NOT_ALLOWED",
                "Only a Chrome extension may contact this local endpoint.",
            )
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
        if content_type.strip().lower() != "application/json":
            self._send_error(
                415,
                "UNSUPPORTED_MEDIA_TYPE",
                "The capture request must use application/json.",
            )
            return

        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            content_length = -1
        if content_length <= 0:
            self._send_error(
                411,
                "CONTENT_LENGTH_REQUIRED",
                "The capture request has no valid content length.",
            )
            return
        if content_length > MAX_REQUEST_BYTES:
            self._send_error(
                413,
                "REQUEST_TOO_LARGE",
                "The captured frame is too large for the local bridge.",
            )
            return

        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_error(
                400,
                "INVALID_JSON",
                "The capture request is not valid JSON.",
            )
            return
        if not isinstance(payload, dict):
            self._send_error(
                400,
                "INVALID_PAYLOAD",
                "The capture request must be a JSON object.",
            )
            return

        try:
            request = self._parse_capture(payload)
        except _PayloadError as exc:
            self._send_error(exc.http_status, exc.code, exc.message)
            return

        try:
            self.server.capture_callback(request)
        except Exception:
            self._send_error(
                500,
                "SHOTLAB_BRIDGE_ERROR",
                "ShotLab could not receive the captured frame.",
            )
            return

        completion = request.wait_for_completion()
        if completion is None:
            self._send_error(
                504,
                "SHOTLAB_TIMEOUT",
                "ShotLab did not finish preparing the frame in time.",
            )
            return
        status, response = completion
        self._send_json(status, response)

    def _parse_capture(self, payload: dict[str, Any]) -> BrowserCaptureRequest:
        if payload.get("client") != "shotlab-chrome-extension":
            raise _PayloadError(
                400,
                "INVALID_CLIENT",
                "The request did not identify the ShotLab Chrome extension.",
            )
        if payload.get("protocol") != BRIDGE_PROTOCOL_VERSION:
            raise _PayloadError(
                409,
                "PROTOCOL_MISMATCH",
                "The extension and ShotLab use different bridge versions.",
            )

        source_url = str(payload.get("sourceUrl", "")).strip()
        parsed_url = urlparse(source_url)
        hostname = (parsed_url.hostname or "").lower()
        if parsed_url.scheme != "https" or hostname not in _ALLOWED_YOUTUBE_HOSTS:
            raise _PayloadError(
                400,
                "INVALID_SOURCE",
                "Only frames from a YouTube page are accepted.",
            )

        image_data_url = payload.get("imageDataUrl")
        if not isinstance(image_data_url, str) or "," not in image_data_url:
            raise _PayloadError(
                400,
                "INVALID_IMAGE",
                "The request does not contain a captured image.",
            )
        prefix, encoded_image = image_data_url.split(",", 1)
        image_formats = {
            "data:image/jpeg;base64": ("jpeg", b"\xff\xd8\xff"),
            "data:image/png;base64": ("png", b"\x89PNG\r\n\x1a\n"),
        }
        if prefix not in image_formats:
            raise _PayloadError(
                415,
                "INVALID_IMAGE_TYPE",
                "Only JPEG and PNG captures are supported.",
            )
        image_format, signature = image_formats[prefix]
        try:
            image_bytes = base64.b64decode(encoded_image, validate=True)
        except (binascii.Error, ValueError):
            raise _PayloadError(
                400,
                "INVALID_IMAGE",
                "The captured image data is malformed.",
            ) from None
        if not image_bytes.startswith(signature):
            raise _PayloadError(
                400,
                "INVALID_IMAGE",
                "The captured image signature is invalid.",
            )
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise _PayloadError(
                413,
                "IMAGE_TOO_LARGE",
                "The captured frame exceeds the local bridge size limit.",
            )

        try:
            source_time_seconds = float(payload.get("sourceTimeSeconds", 0.0))
        except (TypeError, ValueError):
            source_time_seconds = 0.0
        if not math.isfinite(source_time_seconds):
            source_time_seconds = 0.0
        source_time_seconds = max(0.0, min(source_time_seconds, 31_536_000.0))

        return BrowserCaptureRequest(
            image_bytes=image_bytes,
            image_format=image_format,
            source_title=str(payload.get("sourceTitle", "")).strip()[:500],
            source_url=source_url[:4096],
            source_time_seconds=source_time_seconds,
            video_width=_safe_dimension(payload.get("videoWidth")),
            video_height=_safe_dimension(payload.get("videoHeight")),
        )

    def _origin_is_allowed(self) -> bool:
        origin = self.headers.get("Origin", "").strip()
        return not origin or origin.startswith("chrome-extension://")

    def _send_error(self, status: int, code: str, message: str) -> None:
        self._send_json(
            status,
            {
                "ok": False,
                "code": code,
                "message": message,
            },
        )

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_common_headers(self) -> None:
        origin = self.headers.get("Origin", "").strip()
        if origin.startswith("chrome-extension://"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")


@dataclass(slots=True)
class _PayloadError(Exception):
    http_status: int
    code: str
    message: str


def _safe_dimension(value: object) -> int:
    try:
        dimension = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(dimension, 32768))


class BrowserBridgeServer:
    """Small loopback-only HTTP bridge used by the Chrome extension."""

    def __init__(
        self,
        capture_callback: CaptureCallback,
        *,
        host: str = BRIDGE_HOST,
        port: int = BRIDGE_PORT,
    ) -> None:
        if host != BRIDGE_HOST:
            raise ValueError("ShotLab's browser bridge must stay on 127.0.0.1.")
        self.capture_callback = capture_callback
        self.host = host
        self.requested_port = int(port)
        self._server: _BridgeHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._lifecycle_lock = threading.Lock()

    @property
    def port(self) -> int:
        server = self._server
        return int(server.server_address[1]) if server else self.requested_port

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> int:
        with self._lifecycle_lock:
            if self._server is not None:
                return self.port
            server = _BridgeHTTPServer(
                (self.host, self.requested_port),
                self.capture_callback,
            )
            thread = threading.Thread(
                target=server.serve_forever,
                kwargs={"poll_interval": 0.2},
                name="ShotLabBrowserBridge",
                daemon=True,
            )
            self._server = server
            self._thread = thread
            thread.start()
            return int(server.server_address[1])

    def stop(self) -> None:
        with self._lifecycle_lock:
            server = self._server
            thread = self._thread
            self._server = None
            self._thread = None
        if server is None:
            return
        server.shutdown()
        server.server_close()
        if thread and thread is not threading.current_thread():
            thread.join(timeout=2.0)
