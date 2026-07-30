from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QImage,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..i18n import text


def _point(payload: list[float], target: QRectF) -> QPointF:
    return QPointF(
        target.left() + float(payload[0]) * target.width(),
        target.top() + float(payload[1]) * target.height(),
    )


def draw_annotations(
    painter: QPainter,
    annotations: list[dict[str, Any]],
    target: QRectF,
) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    for item in annotations:
        color = QColor(str(item.get("color") or "#D8B365"))
        width = max(1.0, float(item.get("width") or 4.0))
        pen = QPen(
            color,
            width * max(target.width(), target.height()) / 1200.0,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        kind = str(item.get("type") or "")
        points = item.get("points") or []
        if kind == "pen" and len(points) > 1:
            path = QPainterPath(_point(points[0], target))
            for raw in points[1:]:
                path.lineTo(_point(raw, target))
            painter.drawPath(path)
        elif kind in {"line", "arrow"} and len(points) >= 2:
            start = _point(points[0], target)
            end = _point(points[-1], target)
            painter.drawLine(start, end)
            if kind == "arrow":
                angle = math.atan2(
                    start.y() - end.y(),
                    start.x() - end.x(),
                )
                length = max(10.0, pen.widthF() * 4.0)
                left = end + QPointF(
                    math.cos(angle + math.pi / 6) * length,
                    math.sin(angle + math.pi / 6) * length,
                )
                right = end + QPointF(
                    math.cos(angle - math.pi / 6) * length,
                    math.sin(angle - math.pi / 6) * length,
                )
                painter.drawLine(end, left)
                painter.drawLine(end, right)
        elif kind in {"rectangle", "ellipse"} and len(points) >= 2:
            bounds = QRectF(
                _point(points[0], target),
                _point(points[-1], target),
            ).normalized()
            if kind == "rectangle":
                painter.drawRect(bounds)
            else:
                painter.drawEllipse(bounds)
        elif kind == "text" and points:
            position = _point(points[0], target)
            font = QFont()
            font.setBold(True)
            font.setPixelSize(
                max(
                    12,
                    int(
                        float(item.get("size") or 28)
                        * target.height()
                        / 1080.0
                    ),
                )
            )
            painter.setFont(font)
            painter.drawText(position, str(item.get("text") or ""))
    painter.restore()


class AnnotationCanvas(QWidget):
    changed = Signal()

    def __init__(
        self,
        image_path: Path,
        annotations: list[dict[str, Any]],
        language: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.language = language
        self.image = QImage(str(image_path))
        self.annotations = [dict(item) for item in annotations]
        self.redo_stack: list[dict[str, Any]] = []
        self.tool = "pen"
        self.color = "#D8B365"
        self.stroke_width = 5
        self.drawing: dict[str, Any] | None = None
        self.image_rect = QRectF()
        self.setMinimumSize(720, 450)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def sizeHint(self) -> QSize:
        return QSize(1100, 680)

    def _fitted_rect(self) -> QRectF:
        if self.image.isNull():
            return QRectF(self.rect())
        fitted = self.image.size().scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        left = (self.width() - fitted.width()) / 2.0
        top = (self.height() - fitted.height()) / 2.0
        return QRectF(left, top, fitted.width(), fitted.height())

    def _normalized(self, position: QPointF) -> list[float]:
        rect = self.image_rect
        return [
            min(1.0, max(0.0, (position.x() - rect.left()) / rect.width())),
            min(1.0, max(0.0, (position.y() - rect.top()) / rect.height())),
        ]

    def set_tool(self, tool: str) -> None:
        self.tool = tool

    def set_color(self, color: str) -> None:
        self.color = color

    def set_stroke_width(self, width: int) -> None:
        self.stroke_width = width

    def undo(self) -> None:
        if not self.annotations:
            return
        self.redo_stack.append(self.annotations.pop())
        self.changed.emit()
        self.update()

    def redo(self) -> None:
        if not self.redo_stack:
            return
        self.annotations.append(self.redo_stack.pop())
        self.changed.emit()
        self.update()

    def clear_annotations(self) -> None:
        if not self.annotations:
            return
        self.redo_stack.extend(reversed(self.annotations))
        self.annotations.clear()
        self.changed.emit()
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#080A0B"))
        self.image_rect = self._fitted_rect()
        if not self.image.isNull():
            painter.drawImage(self.image_rect, self.image)
        items = list(self.annotations)
        if self.drawing:
            items.append(self.drawing)
        draw_annotations(painter, items, self.image_rect)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (
            event.button() != Qt.MouseButton.LeftButton
            or not self.image_rect.contains(event.position())
        ):
            return
        point = self._normalized(event.position())
        if self.tool == "text":
            value, accepted = QInputDialog.getText(
                self,
                text(self.language, "annotation_text"),
                text(self.language, "annotation_text_prompt"),
            )
            if accepted and value.strip():
                self.annotations.append(
                    {
                        "type": "text",
                        "points": [point],
                        "text": value.strip(),
                        "color": self.color,
                        "size": 34,
                    }
                )
                self.redo_stack.clear()
                self.changed.emit()
                self.update()
            return
        self.drawing = {
            "type": self.tool,
            "points": [point, point] if self.tool != "pen" else [point],
            "color": self.color,
            "width": self.stroke_width,
        }
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.drawing:
            return
        point = self._normalized(event.position())
        if self.tool == "pen":
            self.drawing["points"].append(point)
        else:
            self.drawing["points"][-1] = point
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or not self.drawing:
            return
        if len(self.drawing.get("points") or []) > 1:
            self.annotations.append(self.drawing)
            self.redo_stack.clear()
            self.changed.emit()
        self.drawing = None
        self.update()

    def render_annotated(self, full_path: Path, thumb_path: Path) -> None:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.annotations:
            full_path.unlink(missing_ok=True)
            thumb_path.unlink(missing_ok=True)
            return
        output = QImage(self.image)
        painter = QPainter(output)
        draw_annotations(
            painter,
            self.annotations,
            QRectF(0, 0, output.width(), output.height()),
        )
        painter.end()
        if not output.save(str(full_path), "PNG"):
            raise OSError(f"Could not save annotation preview: {full_path}")
        thumb = output.scaled(
            640,
            640,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        if not thumb.save(str(thumb_path), "PNG"):
            raise OSError(f"Could not save annotation thumbnail: {thumb_path}")


class AnnotationBoardDialog(QDialog):
    def __init__(
        self,
        image_path: Path,
        annotations: list[dict[str, Any]],
        language: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.language = language
        self.setObjectName("AnnotationBoardDialog")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1240, 820)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        panel = QFrame()
        panel.setObjectName("AnnotationBoard")
        root.addWidget(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel(text(language, "annotation_board"))
        title.setObjectName("AnnotationTitle")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        toolbar = QHBoxLayout()
        self.tool_buttons: dict[str, QPushButton] = {}
        assets_root = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
        )
        tool_names = (
            ("pen", "annotation-pen.svg"),
            ("line", "annotation-line.svg"),
            ("arrow", "annotation-arrow.svg"),
            ("rectangle", "annotation-rectangle.svg"),
            ("ellipse", "annotation-ellipse.svg"),
            ("text", "annotation-text.svg"),
        )
        for tool, icon_name in tool_names:
            button = QPushButton()
            button.setObjectName("AnnotationTool")
            button.setCheckable(True)
            button.setIcon(QIcon(str(assets_root / icon_name)))
            button.setIconSize(QSize(27, 27))
            button.setFixedSize(42, 38)
            button.setToolTip(text(language, f"annotation_{tool}"))
            button.clicked.connect(
                lambda _checked=False, selected=tool: self._select_tool(selected)
            )
            toolbar.addWidget(button)
            self.tool_buttons[tool] = button
        self.tool_buttons["pen"].setChecked(True)

        self.color_button = QPushButton()
        self.color_button.setObjectName("AnnotationColor")
        self.color_button.setToolTip(text(language, "annotation_color"))
        self.color_button.clicked.connect(self._choose_color)
        toolbar.addSpacing(10)
        toolbar.addWidget(self.color_button)

        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(2, 18)
        self.width_slider.setValue(5)
        self.width_slider.setFixedWidth(110)
        self.width_slider.setToolTip(text(language, "annotation_width"))
        toolbar.addWidget(self.width_slider)

        undo = QPushButton()
        undo.setIcon(QIcon(str(assets_root / "annotation-undo.svg")))
        undo.setIconSize(QSize(27, 27))
        undo.setFixedSize(42, 38)
        redo = QPushButton()
        redo.setIcon(QIcon(str(assets_root / "annotation-redo.svg")))
        redo.setIconSize(QSize(27, 27))
        redo.setFixedSize(42, 38)
        clear = QPushButton(text(language, "annotation_clear"))
        for button, tooltip in (
            (undo, text(language, "annotation_undo")),
            (redo, text(language, "annotation_redo")),
            (clear, text(language, "annotation_clear")),
        ):
            button.setObjectName("AnnotationTool")
            button.setToolTip(tooltip)
            toolbar.addWidget(button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.canvas = AnnotationCanvas(
            image_path,
            annotations,
            language,
        )
        self.width_slider.valueChanged.connect(
            self.canvas.set_stroke_width
        )
        undo.clicked.connect(self.canvas.undo)
        redo.clicked.connect(self.canvas.redo)
        clear.clicked.connect(self.canvas.clear_annotations)
        layout.addWidget(self.canvas, 1)

        footer = QHBoxLayout()
        cancel = QPushButton(text(language, "cancel"))
        cancel.setObjectName("Secondary")
        cancel.clicked.connect(self.reject)
        save = QPushButton(text(language, "annotation_save"))
        save.setObjectName("Primary")
        save.clicked.connect(self.accept)
        footer.addStretch()
        footer.addWidget(cancel)
        footer.addWidget(save)
        layout.addLayout(footer)
        self._update_color_button()

    @property
    def annotations(self) -> list[dict[str, Any]]:
        return self.canvas.annotations

    def _select_tool(self, tool: str) -> None:
        for name, button in self.tool_buttons.items():
            button.setChecked(name == tool)
        self.canvas.set_tool(tool)

    def _choose_color(self) -> None:
        selected = QColorDialog.getColor(
            QColor(self.canvas.color),
            self,
            text(self.language, "annotation_color"),
        )
        if selected.isValid():
            self.canvas.set_color(selected.name().upper())
            self._update_color_button()

    def _update_color_button(self) -> None:
        self.color_button.setStyleSheet(
            "background: "
            f"{self.canvas.color}; border: 2px solid #E5E7E4; "
            "border-radius: 14px; min-width: 28px; max-width: 28px; "
            "min-height: 28px; max-height: 28px;"
        )
