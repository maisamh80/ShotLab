from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QCursor,
    QIcon,
    QImage,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QComboBox,
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)

from ..i18n import OPTIONS, option_label, text
from ..models import Project


class ColorSwatch(QLabel):
    color_clicked = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._color = ""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(28)
        self.setMinimumWidth(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )
        self.setMouseTracking(True)
        self._hover_label = QLabel(
            "",
            self,
            (
                Qt.WindowType.ToolTip
                | Qt.WindowType.FramelessWindowHint
            ),
        )
        self._hover_label.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self._hover_label.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating
        )
        self._hover_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self._hover_label.hide()
        self.set_color("")

    def set_color(
        self,
        value: str,
        percentage: float | None = None,
    ) -> None:
        color = QColor(value)
        valid = bool(value) and color.isValid()
        self._color = color.name().upper() if valid else ""
        background = self._color if valid else "#15191A"
        # Coverage remains available in analysis data for compatibility, but
        # the editable palette is intentionally presented as equal swatches.
        self.setText("")
        self.setToolTip("")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"background:{background}; border:none;"
        )
        if not valid:
            self._hover_label.hide()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.color_clicked.emit(self._color)
            event.accept()
            return
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        self._show_color_tooltip()
        super().enterEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._show_color_tooltip()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover_label.hide()
        super().leaveEvent(event)

    def _show_color_tooltip(self) -> None:
        if not self._color:
            return
        application = QApplication.instance()
        theme = (
            str(application.property("shotlab_theme") or "dark")
            if application
            else "dark"
        )
        foreground = "#26302E" if theme == "light" else "#F7F5EE"
        self._hover_label.setText(self._color)
        self._hover_label.setStyleSheet(
            f"color:{foreground}; background:transparent;"
            "border:none; padding:0; font-size:10pt; font-weight:650;"
        )
        self._hover_label.adjustSize()
        self._hover_label.move(QCursor.pos() + QPoint(14, 18))
        self._hover_label.show()
        self._hover_label.raise_()


class FrameColorPickerLabel(QLabel):
    """A frame preview that can sample a color from its displayed pixmap."""

    color_picked = Signal(str)
    pick_cancelled = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._color_pick_active = False

    def begin_color_pick(self) -> bool:
        pixmap = self.pixmap()
        if pixmap is None or pixmap.isNull():
            return False
        self._color_pick_active = True
        cursor_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
            / "color-picker.svg"
        )
        cursor_pixmap = QIcon(str(cursor_path)).pixmap(QSize(28, 28))
        if cursor_pixmap.isNull():
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(QCursor(cursor_pixmap, 5, 23))
        return True

    def cancel_color_pick(self) -> None:
        self._color_pick_active = False
        self.unsetCursor()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._color_pick_active:
            super().mousePressEvent(event)
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.cancel_color_pick()
            self.pick_cancelled.emit()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            color = self._color_at(event.position().toPoint())
            if color:
                self.cancel_color_pick()
                self.color_picked.emit(color)
            event.accept()
            return
        super().mousePressEvent(event)

    def _color_at(self, position: QPoint) -> str:
        pixmap = self.pixmap()
        if pixmap is None or pixmap.isNull():
            return ""
        ratio = max(float(pixmap.devicePixelRatio()), 1.0)
        display_width = pixmap.width() / ratio
        display_height = pixmap.height() / ratio
        left = (self.width() - display_width) / 2.0
        top = (self.height() - display_height) / 2.0
        if not (
            left <= position.x() < left + display_width
            and top <= position.y() < top + display_height
        ):
            return ""
        image = pixmap.toImage()
        x = min(
            image.width() - 1,
            max(0, int((position.x() - left) * image.width() / display_width)),
        )
        y = min(
            image.height() - 1,
            max(0, int((position.y() - top) * image.height() / display_height)),
        )
        return image.pixelColor(x, y).name(QColor.NameFormat.HexRgb).upper()


class HoverHoldLabel(QLabel):
    hold_completed = Signal()

    def __init__(self, hold_duration_ms: int = 5000, parent=None) -> None:
        super().__init__(parent)
        self._hold_duration_ms = max(1, int(hold_duration_ms))
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._complete_hold)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event) -> None:
        self._hold_timer.start(self._hold_duration_ms)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hold_timer.stop()
        super().leaveEvent(event)

    def _complete_hold(self) -> None:
        if self.underMouse():
            self.hold_completed.emit()


def sprite_icon(
    path: Path,
    index: int,
    count: int,
    size: QSize,
) -> QIcon:
    sprite = QPixmap(str(path))
    if sprite.isNull() or count < 1:
        return QIcon()
    segment_width = sprite.width() // count
    segment = sprite.copy(
        index * segment_width,
        0,
        segment_width,
        sprite.height(),
    )
    scaled = segment.scaled(
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    return QIcon(scaled)


class TimelineSlider(QSlider):
    marker_clicked = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._markers: list[tuple[int, str]] = []
        handle_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
            / "slider.svg"
        )
        source = QPixmap(str(handle_path))
        self._handle_pixmap = source.scaled(
            QSize(20, 26),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_markers(self, markers: list[tuple[int, str]]) -> None:
        self._markers = markers
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            option,
            QStyle.SubControl.SC_SliderGroove,
            self,
        )
        painter = QPainter(self)
        if self._markers and self.maximum() > self.minimum():
            painter.setPen(QPen(QColor("#f0c979"), 2))
            for value, _ in self._markers:
                x = QStyle.sliderPositionFromValue(
                    self.minimum(),
                    self.maximum(),
                    value,
                    groove.width(),
                )
                x += groove.left()
                painter.drawLine(x, groove.top() - 5, x, groove.bottom() + 5)

        handle = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            option,
            QStyle.SubControl.SC_SliderHandle,
            self,
        )
        if not self._handle_pixmap.isNull():
            painter.drawPixmap(
                handle.center().x() - self._handle_pixmap.width() // 2,
                handle.center().y() - self._handle_pixmap.height() // 2,
                self._handle_pixmap,
            )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            option = QStyleOptionSlider()
            self.initStyleOption(option)
            handle = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider,
                option,
                QStyle.SubControl.SC_SliderHandle,
                self,
            )
            if not handle.contains(event.position().toPoint()):
                span = max(1, self.width() - handle.width())
                pixel_position = round(
                    event.position().x() - handle.width() / 2
                )
                pixel_position = max(0, min(pixel_position, span))
                value = QStyle.sliderValueFromPosition(
                    self.minimum(),
                    self.maximum(),
                    pixel_position,
                    span,
                    option.upsideDown,
                )
                self.setValue(value)
                self.sliderMoved.emit(value)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self._markers and self.maximum() > self.minimum():
            position = event.position().toPoint()
            ratio = max(0.0, min(position.x() / max(self.width(), 1), 1.0))
            time_value = round(self.minimum() + ratio * (self.maximum() - self.minimum()))
            nearest = min(self._markers, key=lambda item: abs(item[0] - time_value))
            threshold = max(500, int((self.maximum() - self.minimum()) * 0.01))
            if abs(nearest[0] - time_value) <= threshold:
                self.marker_clicked.emit(nearest[1])
                return
        super().mouseDoubleClickEvent(event)


class ColorWheelWidget(QWidget):
    color_changed = Signal(object)

    def __init__(self, color: QColor, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Transparent")
        self.setFixedSize(270, 270)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hue = 0.0
        self._saturation = 1.0
        self._value = 1.0
        self._wheel_image = QImage()
        self.set_color(color)

    def set_color(self, color: QColor) -> None:
        hue, saturation, value, _alpha = color.getHsvF()
        self._hue = 0.0 if hue < 0 else hue
        self._saturation = max(0.0, min(saturation, 1.0))
        self._value = max(0.0, min(value, 1.0))
        self.update()

    def set_value(self, value: int) -> None:
        self._value = max(0.0, min(int(value) / 100.0, 1.0))
        self.color_changed.emit(self.color())
        self.update()

    def color(self) -> QColor:
        return QColor.fromHsvF(
            self._hue,
            self._saturation,
            self._value,
        )

    def _geometry(self) -> tuple[float, float, float]:
        radius = max(1.0, min(self.width(), self.height()) / 2.0 - 5.0)
        return self.width() / 2.0, self.height() / 2.0, radius

    def _rebuild_wheel(self) -> None:
        self._wheel_image = QImage(
            self.size(),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        self._wheel_image.fill(Qt.GlobalColor.transparent)
        center_x, center_y, radius = self._geometry()
        for y in range(self.height()):
            for x in range(self.width()):
                delta_x = x - center_x
                delta_y = y - center_y
                distance = math.hypot(delta_x, delta_y)
                if distance > radius:
                    continue
                hue = (
                    math.atan2(-delta_y, delta_x)
                    / (2.0 * math.pi)
                ) % 1.0
                saturation = min(distance / radius, 1.0)
                self._wheel_image.setPixelColor(
                    x,
                    y,
                    QColor.fromHsvF(hue, saturation, 1.0),
                )

    def resizeEvent(self, event) -> None:
        self._rebuild_wheel()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        if self._wheel_image.isNull():
            self._rebuild_wheel()
        center_x, center_y, radius = self._geometry()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawImage(0, 0, self._wheel_image)
        if self._value < 1.0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(
                QColor(0, 0, 0, round((1.0 - self._value) * 255))
            )
            painter.drawEllipse(
                round(center_x - radius),
                round(center_y - radius),
                round(radius * 2),
                round(radius * 2),
            )

        angle = self._hue * 2.0 * math.pi
        marker_x = center_x + math.cos(angle) * radius * self._saturation
        marker_y = center_y - math.sin(angle) * radius * self._saturation
        painter.setBrush(self.color())
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawEllipse(
            round(marker_x - 7),
            round(marker_y - 7),
            14,
            14,
        )
        painter.setPen(QPen(QColor("#202424"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            round(marker_x - 8),
            round(marker_y - 8),
            16,
            16,
        )
        painter.end()

    def _select_position(self, event: QMouseEvent) -> None:
        center_x, center_y, radius = self._geometry()
        delta_x = event.position().x() - center_x
        delta_y = event.position().y() - center_y
        distance = math.hypot(delta_x, delta_y)
        if distance > radius:
            scale = radius / max(distance, 1.0)
            delta_x *= scale
            delta_y *= scale
            distance = radius
        self._hue = (
            math.atan2(-delta_y, delta_x)
            / (2.0 * math.pi)
        ) % 1.0
        self._saturation = min(distance / radius, 1.0)
        self.color_changed.emit(self.color())
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._select_position(event)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._select_position(event)
            event.accept()
            return
        super().mouseMoveEvent(event)


class ColorPickerDialog(QDialog):
    def __init__(
        self,
        language: str,
        initial_color: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ColorPickerDialog")
        self.setModal(True)
        self.setFixedWidth(450)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if language == "fa"
            else Qt.LayoutDirection.LeftToRight
        )
        self.setWindowTitle(text(language, "select_similar_color"))
        initial = QColor(initial_color or "#D5AE62")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        panel = QFrame()
        panel.setObjectName("ColorPickerPanel")
        outer.addWidget(panel)

        root = QVBoxLayout(panel)
        root.setContentsMargins(26, 24, 26, 24)
        root.setSpacing(14)
        title = QLabel(text(language, "select_similar_color"))
        title.setObjectName("ColorPickerTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        self.wheel = ColorWheelWidget(initial)
        root.addWidget(
            self.wheel,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        brightness_row = QHBoxLayout()
        brightness_label = QLabel(text(language, "brightness"))
        brightness_label.setObjectName("Muted")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(5, 100)
        self.brightness_slider.setValue(
            max(5, round(initial.valueF() * 100))
        )
        self.brightness_slider.valueChanged.connect(self.wheel.set_value)
        brightness_row.addWidget(brightness_label)
        brightness_row.addWidget(self.brightness_slider, 1)
        root.addLayout(brightness_row)

        self.preview = QLabel()
        self.preview.setObjectName("ColorPreview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(42)
        root.addWidget(self.preview)
        self.wheel.color_changed.connect(self._update_preview)
        self.wheel.set_value(self.brightness_slider.value())
        self._update_preview(self.wheel.color())

        buttons = QHBoxLayout()
        buttons.setSpacing(14)
        apply_button = QPushButton(text(language, "apply_color"))
        apply_button.setObjectName("Primary")
        cancel_button = QPushButton(text(language, "cancel"))
        cancel_button.setObjectName("WarningCancel")
        cancel_button.setToolTip(text(language, "cancel"))
        apply_button.setToolTip(text(language, "apply_color"))
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.accept)
        buttons.addWidget(apply_button, 1)
        buttons.addWidget(cancel_button, 1)
        root.addLayout(buttons)

    def _update_preview(self, color: QColor) -> None:
        value = color.name().upper()
        foreground = "#111514" if color.lightness() > 150 else "#F7F5EE"
        self.preview.setText(value)
        self.preview.setStyleSheet(
            f"background:{value}; color:{foreground};"
            "border:1px solid #66706E; border-radius:6px;"
            "font-weight:700;"
        )

    def selected_color(self) -> str:
        return self.wheel.color().name().upper()


class CaptureFilterPanel(QFrame):
    changed = Signal()

    FILTER_KEYS = (
        "shot_size",
        "camera_angle",
        "location_type",
        "lens_type",
        "time_of_day",
        "lighting_style",
        "key_quality",
    )

    def __init__(self, language: str, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self._selected_color = ""
        self.setObjectName("FilterPanel")

        root = QVBoxLayout(self)
        root.setContentsMargins(15, 14, 15, 14)
        root.setSpacing(12)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("Search")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setMinimumHeight(38)
        assets = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
        )
        search_action = self.search_edit.addAction(
            QIcon(str(assets / "search.svg")),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        search_action.triggered.connect(
            lambda _checked=False: self.search_edit.setFocus()
        )
        self.clear_button = QPushButton()
        self.clear_button.setObjectName("FilterAction")
        self.clear_button.setIcon(QIcon(str(assets / "filter.svg")))
        self.clear_button.setIconSize(QSize(22, 22))
        self.clear_button.clicked.connect(
            lambda _checked=False: self.clear()
        )
        root.addWidget(self.search_edit)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(5)
        self.combos: dict[str, QComboBox] = {}
        self.combo_labels: dict[str, QLabel] = {}
        for index, key in enumerate(self.FILTER_KEYS):
            label = QLabel()
            label.setObjectName("FilterLabel")
            combo = QComboBox()
            combo.setObjectName("FilterCombo")
            combo.setMinimumWidth(105)
            combo.setMinimumHeight(36)
            combo.currentIndexChanged.connect(
                lambda _index: self.changed.emit()
            )
            self.combo_labels[key] = label
            self.combos[key] = combo
            grid.addWidget(label, 0, index)
            grid.addWidget(combo, 1, index)

        color_container = QWidget()
        color_container.setObjectName("Transparent")
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(4)
        self.color_button = QPushButton()
        self.color_button.setObjectName("FilterAction")
        self.color_button.setIcon(
            QIcon(str(assets / "color-picker.svg"))
        )
        self.color_button.setIconSize(QSize(21, 21))
        self.color_button.setMinimumWidth(132)
        self.color_button.setMinimumHeight(36)
        self.color_button.clicked.connect(self._choose_color)
        self.color_clear_button = QPushButton("×")
        self.color_clear_button.setObjectName("FilterAction")
        self.color_clear_button.setFixedWidth(32)
        self.color_clear_button.clicked.connect(self._clear_color)
        color_layout.addWidget(self.color_button, 1)
        color_layout.addWidget(self.color_clear_button)
        grid.addWidget(
            color_container,
            1,
            len(self.FILTER_KEYS),
        )
        grid.addWidget(
            self.clear_button,
            1,
            len(self.FILTER_KEYS) + 1,
        )

        for column in range(len(self.FILTER_KEYS) + 2):
            grid.setColumnStretch(column, 1)
        root.addLayout(grid)

        self.search_edit.textChanged.connect(lambda _value: self.changed.emit())
        self.set_language(language)

    def set_language(self, language: str) -> None:
        self.language = language
        for key, combo in self.combos.items():
            self.combo_labels[key].setText(text(language, key))
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(text(language, "any_value"), "")
            for value, fa_label, en_label in OPTIONS[key]:
                if not value:
                    continue
                combo.addItem(option_label(language, key, value), value)
            combo.setCurrentIndex(max(combo.findData(current), 0))
            combo.blockSignals(False)

        self.search_edit.setPlaceholderText(text(language, "keyword_search"))
        self.clear_button.setText(text(language, "clear_filters"))
        self.clear_button.setToolTip(text(language, "clear_filters"))
        self._update_color_button()

    def query(self) -> str:
        return self.search_edit.text().strip()

    def filters(self) -> dict[str, object]:
        return {
            key: combo.currentData()
            for key, combo in self.combos.items()
            if combo.currentData() not in ("", None)
        }

    def selected_color(self) -> str:
        return self._selected_color

    def has_criteria(self) -> bool:
        return bool(
            self.query()
            or self.filters()
            or self._selected_color
        )

    def _choose_color(self) -> None:
        dialog = ColorPickerDialog(
            self.language,
            self._selected_color,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._selected_color = dialog.selected_color()
        self._update_color_button()
        self.changed.emit()

    def _clear_color(self) -> None:
        if not self._selected_color:
            return
        self._selected_color = ""
        self._update_color_button()
        self.changed.emit()

    def _update_color_button(self) -> None:
        label = text(self.language, "similar_color")
        self.color_button.setText(label)
        self.color_clear_button.setToolTip(text(self.language, "clear_color"))
        self.color_clear_button.setVisible(bool(self._selected_color))
        if not self._selected_color:
            self.color_button.setStyleSheet("")
            self.color_button.setToolTip(text(self.language, "select_similar_color"))
            return
        color = QColor(self._selected_color)
        foreground = "#111514" if color.lightness() > 150 else "#F7F5EE"
        self.color_button.setToolTip(self._selected_color)
        self.color_button.setStyleSheet(
            f"background:{self._selected_color}; color:{foreground};"
            "border:1px solid #D5AE62; font-weight:650;"
        )

    def clear(self) -> None:
        self.search_edit.blockSignals(True)
        self.search_edit.clear()
        self.search_edit.blockSignals(False)
        for combo in self.combos.values():
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)
        self._selected_color = ""
        self._update_color_button()
        self.changed.emit()


class ProjectCard(QFrame):
    CARD_WIDTH = 240
    CARD_HEIGHT = 326

    open_timeline = Signal(str)
    open_gallery = Signal(str)
    rename_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(
        self,
        project: Project,
        thumbnails: list[Path],
        palette: list[str],
        language: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.project = project
        self.setObjectName("ProjectCard")
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 10)
        root.setSpacing(8)

        mosaic = QFrame()
        self.mosaic = mosaic
        mosaic.setObjectName("Mosaic")
        mosaic.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        grid = QGridLayout(mosaic)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        for index in range(4):
            preview = QLabel()
            preview.setObjectName("MosaicCell")
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview.setFixedSize(104, 104)
            if index < len(thumbnails):
                pixmap = QPixmap(str(thumbnails[index]))
                target = QSize(104, 104)
                expanded = pixmap.scaled(
                    target,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = max(0, (expanded.width() - target.width()) // 2)
                y = max(0, (expanded.height() - target.height()) // 2)
                preview.setPixmap(expanded.copy(x, y, target.width(), target.height()))
            else:
                preview.setText("＋" if index == 0 and not thumbnails else "")
            grid.addWidget(preview, index // 2, index % 2)
        root.addWidget(mosaic, 1)

        palette_bar = QFrame()
        palette_bar.setObjectName("LibraryPalette")
        palette_bar.setFixedHeight(26)
        palette_bar.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        palette_layout = QHBoxLayout(palette_bar)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setSpacing(0)
        display_colors = list(palette[:5])
        while len(display_colors) < 5:
            display_colors.append(
                display_colors[-1]
                if display_colors
                else "#15191A"
            )
        for color in display_colors:
            swatch = QFrame()
            swatch.setStyleSheet(
                f"background:{color}; border:none;"
            )
            swatch.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )
            palette_layout.addWidget(swatch, 1)
        root.addWidget(palette_bar)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(4)
        labels = QVBoxLayout()
        labels.setSpacing(0)
        name = QLabel(project.name)
        name.setObjectName("CardTitle")
        name.setWordWrap(False)
        name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        count = QLabel(text(language, "captures_count", count=project.capture_count))
        count.setObjectName("CardCount")
        count.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        labels.addWidget(name)
        labels.addWidget(count)
        footer.addLayout(labels, 1)

        menu_button = QPushButton("⋮")
        menu_button.setObjectName("CardMenu")
        menu_button.setFixedSize(30, 42)
        menu_button.setToolTip(text(language, "open_project"))
        menu = QMenu(menu_button)
        timeline_action = menu.addAction(text(language, "open_timeline"))
        gallery_action = menu.addAction(text(language, "open_gallery"))
        rename_action = menu.addAction(text(language, "rename_project"))
        menu.addSeparator()
        delete_action = menu.addAction(text(language, "delete_project"))
        timeline_action.triggered.connect(
            lambda _checked=False: self.open_timeline.emit(project.id)
        )
        gallery_action.triggered.connect(
            lambda _checked=False: self.open_gallery.emit(project.id)
        )
        rename_action.triggered.connect(
            lambda _checked=False: self.rename_requested.emit(project.id)
        )
        delete_action.triggered.connect(
            lambda _checked=False: self.delete_requested.emit(project.id)
        )
        menu_button.clicked.connect(
            lambda _checked=False: menu.exec(
                menu_button.mapToGlobal(menu_button.rect().bottomRight())
            )
        )
        footer.addWidget(menu_button)
        root.addLayout(footer)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(text(language, "double_click_gallery"))

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.mosaic.geometry().contains(
                event.position().toPoint()
            )
        ):
            self.open_gallery.emit(self.project.id)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
