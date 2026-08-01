from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QIcon,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..i18n import text
from ..media import format_timecode
from ..repository import Repository


class FrameReviewCanvas(QWidget):
    """Large image canvas with fit, actual-size, zoom, and pan controls."""

    zoom_changed = Signal(int)

    def __init__(self, language: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.language = language
        self.image = QImage()
        self.zoom = 1.0
        self.pan = QPointF()
        self._dragging = False
        self._drag_origin = QPointF()
        self._pan_origin = QPointF()
        self.setMinimumSize(320, 240)
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:
        return QSize(1280, 760)

    def set_image(self, path: Path | None) -> None:
        self.image = QImage(str(path)) if path is not None else QImage()
        self.reset_fit()

    def _fit_scale(self) -> float:
        if self.image.isNull():
            return 1.0
        return max(
            0.0001,
            min(
                self.width() / max(self.image.width(), 1),
                self.height() / max(self.image.height(), 1),
            ),
        )

    def _scale(self) -> float:
        return self._fit_scale() * self.zoom

    def _image_rect(self) -> QRectF:
        if self.image.isNull():
            return QRectF()
        scale = self._scale()
        width = self.image.width() * scale
        height = self.image.height() * scale
        return QRectF(
            (self.width() - width) / 2.0 + self.pan.x(),
            (self.height() - height) / 2.0 + self.pan.y(),
            width,
            height,
        )

    def _maximum_zoom(self) -> float:
        return min(48.0, max(1.0, 8.0 / self._fit_scale()))

    def _minimum_zoom(self) -> float:
        return min(1.0, 1.0 / self._fit_scale())

    def _can_pan(self) -> bool:
        rect = self._image_rect()
        return (
            rect.width() > self.width() + 1.0
            or rect.height() > self.height() + 1.0
        )

    def _clamp_pan(self) -> None:
        rect = self._image_rect()
        max_x = max(0.0, (rect.width() - self.width()) / 2.0)
        max_y = max(0.0, (rect.height() - self.height()) / 2.0)
        self.pan = QPointF(
            min(max(self.pan.x(), -max_x), max_x),
            min(max(self.pan.y(), -max_y), max_y),
        )

    def _emit_zoom(self) -> None:
        self.zoom_changed.emit(round(self._scale() * 100.0))

    def reset_fit(self) -> None:
        self.zoom = 1.0
        self.pan = QPointF()
        self.unsetCursor()
        self._emit_zoom()
        self.update()

    def show_actual_size(self) -> None:
        self.zoom = min(
            self._maximum_zoom(),
            max(self._minimum_zoom(), 1.0 / self._fit_scale()),
        )
        self.pan = QPointF()
        self._update_pan_cursor()
        self._emit_zoom()
        self.update()

    def _update_pan_cursor(self) -> None:
        if self._can_pan():
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.unsetCursor()

    def _set_zoom_at(self, value: float, position: QPointF) -> None:
        if self.image.isNull():
            return
        old_rect = self._image_rect()
        old_scale = self._scale()
        image_x = (position.x() - old_rect.left()) / max(old_scale, 0.0001)
        image_y = (position.y() - old_rect.top()) / max(old_scale, 0.0001)
        self.zoom = min(
            self._maximum_zoom(),
            max(self._minimum_zoom(), value),
        )
        new_scale = self._scale()
        new_width = self.image.width() * new_scale
        new_height = self.image.height() * new_scale
        base_left = (self.width() - new_width) / 2.0
        base_top = (self.height() - new_height) / 2.0
        self.pan = QPointF(
            position.x() - image_x * new_scale - base_left,
            position.y() - image_y * new_scale - base_top,
        )
        self._clamp_pan()
        self._update_pan_cursor()
        self._emit_zoom()
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        application = QApplication.instance()
        theme = (
            str(application.property("shotlab_theme") or "dark")
            if application is not None
            else "dark"
        )
        painter.fillRect(
            self.rect(),
            QColor("#EDF0ED" if theme == "light" else "#050708"),
        )
        if self.image.isNull():
            painter.setPen(QColor("#89918F"))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                text(self.language, "review_image_unavailable"),
            )
            return
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawImage(self._image_rect(), self.image)

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.18 if event.angleDelta().y() > 0 else 1.0 / 1.18
        self._set_zoom_at(self.zoom * factor, event.position())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._can_pan():
            self._dragging = True
            self._drag_origin = event.position()
            self._pan_origin = QPointF(self.pan)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            delta = event.position() - self._drag_origin
            self.pan = self._pan_origin + delta
            self._clamp_pan()
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._update_pan_cursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if abs(self.zoom - 1.0) < 0.01:
            self.show_actual_size()
        else:
            self.reset_fit()
        event.accept()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._clamp_pan()
        self._emit_zoom()


class FrameReviewDialog(QDialog):
    def __init__(
        self,
        repository: Repository,
        language: str,
        capture_ids: list[str] | None = None,
        initial_capture_id: str | None = None,
        fps: float = 24.0,
        standalone_image_path: Path | None = None,
        standalone_title: str = "",
        standalone_timecode: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.repository = repository
        self.language = language
        self.fps = max(0.001, float(fps))
        self.capture_ids = list(dict.fromkeys(capture_ids or []))
        self.standalone_image_path = standalone_image_path
        self.standalone_title = standalone_title
        self.standalone_timecode = standalone_timecode
        self.current_index = (
            self.capture_ids.index(initial_capture_id)
            if initial_capture_id in self.capture_ids
            else 0
        )
        self.show_annotations = True
        self._info_visible = True

        self.setObjectName("FrameReviewDialog")
        self.setWindowTitle(text(language, "frame_review_viewer"))
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setModal(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.resize(1400, 900)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        panel = QFrame()
        panel.setObjectName("FrameReviewPanel")
        root.addWidget(panel)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 6, 10, 6)
        panel_layout.setSpacing(2)

        self.header = QFrame()
        self.header.setObjectName("FrameReviewBar")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(4, 2, 2, 2)
        header_layout.setSpacing(10)
        self.title_label = QLabel()
        self.title_label.setObjectName("FrameReviewTitle")
        self.meta_label = QLabel()
        self.meta_label.setObjectName("FrameReviewMeta")
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.meta_label)
        header_layout.addStretch()
        self.variant_button = QPushButton()
        self.variant_button.setObjectName("FrameReviewAction")
        self.variant_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.variant_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.variant_button.clicked.connect(self._toggle_annotations)
        header_layout.addWidget(self.variant_button)
        close_button = QPushButton("×")
        close_button.setObjectName("FrameReviewClose")
        close_button.setToolTip(text(language, "close"))
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(close_button)
        panel_layout.addWidget(self.header)

        image_row = QHBoxLayout()
        image_row.setContentsMargins(0, 0, 0, 0)
        image_row.setSpacing(5)
        assets = Path(__file__).resolve().parents[2] / "assets" / "final_ui"
        self.previous_button = QPushButton()
        self.previous_button.setObjectName("FrameReviewNav")
        self.previous_button.setIcon(QIcon(str(assets / "previous-frame.svg")))
        self.previous_button.setIconSize(QSize(26, 26))
        self.previous_button.setToolTip(text(language, "previous_frame"))
        self.previous_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.previous_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.previous_button.clicked.connect(self.previous_frame)
        self.canvas = FrameReviewCanvas(language)
        self.next_button = QPushButton()
        self.next_button.setObjectName("FrameReviewNav")
        self.next_button.setIcon(QIcon(str(assets / "next-frame.svg")))
        self.next_button.setIconSize(QSize(26, 26))
        self.next_button.setToolTip(text(language, "next_frame"))
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.next_button.clicked.connect(self.next_frame)
        image_row.addWidget(
            self.previous_button,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        image_row.addWidget(self.canvas, 1)
        image_row.addWidget(
            self.next_button,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        panel_layout.addLayout(image_row, 1)

        self.footer = QFrame()
        self.footer.setObjectName("FrameReviewBar")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(4, 3, 4, 2)
        self.zoom_label = QLabel("100%")
        self.zoom_label.setObjectName("FrameReviewZoom")
        self.canvas.zoom_changed.connect(
            lambda value: self.zoom_label.setText(f"{value}%")
        )
        hint = QLabel(text(language, "frame_review_hint"))
        hint.setObjectName("FrameReviewHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.zoom_label)
        footer_layout.addStretch()
        footer_layout.addWidget(hint)
        footer_layout.addStretch()
        panel_layout.addWidget(self.footer)

        self._show_current()
        self.setFocus()

    def _original_path(self, capture) -> Path:
        return self.repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )

    def _show_current(self) -> None:
        if self.standalone_image_path is not None:
            self.title_label.setText(
                self.standalone_title or text(self.language, "frame_review_viewer")
            )
            self.meta_label.setText(self.standalone_timecode)
            self.variant_button.hide()
            self.previous_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.canvas.set_image(self.standalone_image_path)
            return
        if not self.capture_ids:
            self.canvas.set_image(None)
            self.previous_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.variant_button.hide()
            return
        capture = self.repository.get_capture(
            self.capture_ids[self.current_index]
        )
        if capture is None:
            self.canvas.set_image(None)
            return
        title = capture.editorial.get("title") or (
            f"Capture {capture.capture_number}"
        )
        timecode = (
            text(self.language, "imported_image")
            if capture.source_pts is None
            else format_timecode(capture.source_time_ms, self.fps)
        )
        self.title_label.setText(str(title))
        self.meta_label.setText(
            f"{timecode}  ·  {self.current_index + 1} / {len(self.capture_ids)}"
        )
        annotated = self.repository.annotated_image_path(capture)
        has_annotations = bool(capture.annotations and annotated.is_file())
        self.variant_button.setVisible(has_annotations)
        if has_annotations:
            self.variant_button.setText(
                text(
                    self.language,
                    "review_show_original"
                    if self.show_annotations
                    else "review_show_annotations",
                )
            )
        path = (
            annotated
            if has_annotations and self.show_annotations
            else self._original_path(capture)
        )
        self.canvas.set_image(path)
        self.previous_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(
            self.current_index < len(self.capture_ids) - 1
        )

    def previous_frame(self) -> None:
        if self.current_index <= 0:
            return
        self.current_index -= 1
        self.show_annotations = True
        self._show_current()

    def next_frame(self) -> None:
        if self.current_index >= len(self.capture_ids) - 1:
            return
        self.current_index += 1
        self.show_annotations = True
        self._show_current()

    def _toggle_annotations(self) -> None:
        self.show_annotations = not self.show_annotations
        self._show_current()

    def _toggle_info(self) -> None:
        self._info_visible = not self._info_visible
        self.header.setVisible(self._info_visible)
        self.footer.setVisible(self._info_visible)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        if event.key() == Qt.Key.Key_Left:
            self.previous_frame()
            return
        if event.key() == Qt.Key.Key_Right:
            self.next_frame()
            return
        if event.key() == Qt.Key.Key_A and self.variant_button.isVisible():
            self._toggle_annotations()
            return
        if event.key() == Qt.Key.Key_I:
            self._toggle_info()
            return
        if event.key() == Qt.Key.Key_F:
            self.canvas.reset_fit()
            return
        if event.key() == Qt.Key.Key_1:
            self.canvas.show_actual_size()
            return
        super().keyPressEvent(event)
