from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QMarginsF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
    QTextOption,
)
from PySide6.QtSvg import QSvgRenderer

from .i18n import option_label, text
from .media import format_timecode
from .models import Capture
from .repository import Repository


GOLD = QColor("#D8B365")
INK = QColor("#232323")
MUTED = QColor("#8A8A88")
PAPER = QColor("#FFFFFF")
IMAGE_FALLBACK = QColor("#232323")
PDF_CARD_MIN_HEIGHT = 540.0
PDF_CARD_GAP = 28.0


def _font(language: str, size: float, weight: int = 400) -> QFont:
    family = "Vazirmatn" if language == "fa" else "Inter"
    font = QFont(family)
    font.setPointSizeF(size)
    # PySide6 6.8+ requires QFont.Weight rather than a raw integer.
    # Clamp custom design weights to Qt's supported enum range.
    supported_weights = (
        QFont.Weight.Thin,
        QFont.Weight.ExtraLight,
        QFont.Weight.Light,
        QFont.Weight.Normal,
        QFont.Weight.Medium,
        QFont.Weight.DemiBold,
        QFont.Weight.Bold,
        QFont.Weight.ExtraBold,
        QFont.Weight.Black,
    )
    font.setWeight(
        min(
            supported_weights,
            key=lambda candidate: abs(int(candidate) - int(weight)),
        )
    )
    return font


def _logo_image(path: Path, size: QSize) -> QImage:
    image = QImage(
        size,
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    image.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(str(path))
    painter = QPainter(image)
    if renderer.isValid():
        renderer.render(painter)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn
        )
        painter.fillRect(image.rect(), GOLD)
    painter.end()
    return image


def _draw_text(
    painter: QPainter,
    rect: QRectF,
    value: str,
    language: str,
    size: float,
    color: QColor = INK,
    weight: int = 400,
    alignment: Qt.AlignmentFlag | None = None,
    word_wrap: bool = False,
) -> None:
    painter.setPen(color)
    painter.setFont(_font(language, size, weight))
    option = QTextOption()
    option.setTextDirection(
        Qt.LayoutDirection.RightToLeft
        if language == "fa"
        else Qt.LayoutDirection.LeftToRight
    )
    option.setAlignment(
        alignment
        or (
            Qt.AlignmentFlag.AlignRight
            if language == "fa"
            else Qt.AlignmentFlag.AlignLeft
        )
    )
    option.setWrapMode(
        QTextOption.WrapMode.WordWrap
        if word_wrap
        else QTextOption.WrapMode.NoWrap
    )
    painter.drawText(rect, value, option)


def _draw_header(
    painter: QPainter,
    page_rect: QRectF,
    language: str,
    page_number: int,
    logo: QImage,
) -> float:
    logo_width = min(250.0, page_rect.width() * 0.25)
    logo_height = logo_width * logo.height() / max(logo.width(), 1)
    logo_rect = QRectF(
        page_rect.right() - logo_width
        if language == "fa"
        else page_rect.left(),
        page_rect.top(),
        logo_width,
        logo_height,
    )
    painter.drawImage(logo_rect, logo)
    header_text = (
        f"خروجی گرفته‌شده از نرم‌افزار ShotLab | صفحه {page_number:02d}"
        if language == "fa"
        else f"Exported from ShotLab | Page {page_number:02d}"
    )
    header_gap = 28.0
    if language == "fa":
        text_rect = QRectF(
            page_rect.left(),
            page_rect.top() + 8,
            max(
                1.0,
                logo_rect.left() - header_gap - page_rect.left(),
            ),
            logo_height,
        )
    else:
        text_left = logo_rect.right() + header_gap
        text_rect = QRectF(
            text_left,
            page_rect.top() + 8,
            max(1.0, page_rect.right() - text_left),
            logo_height,
        )
    _draw_text(
        painter,
        text_rect,
        header_text,
        language,
        9.5,
        MUTED,
        400,
        (
            Qt.AlignmentFlag.AlignLeft
            if language == "fa"
            else Qt.AlignmentFlag.AlignRight
        ),
    )
    return page_rect.top() + logo_height + 38


def _editorial_rows(
    capture: Capture,
    language: str,
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for key in (
        "shot_size",
        "camera_angle",
        "location_type",
        "lens_type",
        "time_of_day",
        "lighting_style",
        "key_quality",
    ):
        value = capture.editorial.get(key)
        rows.append(
            (
                text(language, key),
                option_label(language, key, value) if value else "",
            )
        )
    separator = "، " if language == "fa" else ", "
    rows.extend(
        [
            (
                text(language, "mood"),
                separator.join(capture.editorial.get("mood", [])),
            ),
            (
                text(language, "tags"),
                separator.join(capture.editorial.get("tags", [])),
            ),
            (
                text(language, "notes"),
                str(capture.editorial.get("notes") or ""),
            ),
        ]
    )
    return rows


def _draw_capture_card(
    painter: QPainter,
    rect: QRectF,
    capture: Capture,
    repository: Repository,
    language: str,
    fps: float,
    include_annotations: bool,
    single_column: bool,
) -> None:
    title = str(
        capture.editorial.get("title")
        or (
            f"فریم {capture.capture_number}"
            if language == "fa"
            else f"Frame {capture.capture_number}"
        )
    )
    timecode = (
        text(language, "imported_image")
        if capture.source_pts is None
        else format_timecode(capture.source_time_ms, fps)
    )
    line_height = 34.0
    title_width = rect.width() * 0.68
    title_rect = QRectF(rect.left(), rect.top(), title_width, line_height)
    time_rect = QRectF(
        rect.right() - (rect.width() - title_width),
        rect.top(),
        rect.width() - title_width,
        line_height,
    )
    if language == "fa":
        title_rect, time_rect = time_rect, title_rect
    _draw_text(
        painter,
        title_rect,
        title,
        language,
        10.5,
        INK,
        600,
        (
            Qt.AlignmentFlag.AlignRight
            if language == "fa"
            else Qt.AlignmentFlag.AlignLeft
        ),
    )
    _draw_text(
        painter,
        time_rect,
        timecode,
        "en",
        8.5,
        MUTED,
        400,
        (
            Qt.AlignmentFlag.AlignLeft
            if language == "fa"
            else Qt.AlignmentFlag.AlignRight
        ),
    )

    image_top = rect.top() + line_height
    image_path = (
        repository.display_image_path(capture)
        if include_annotations
        else repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
    )
    source = QImage(str(image_path))
    if single_column and not source.isNull():
        # A single-column export gives each frame its own page. Size the
        # image area from the frame's real aspect ratio so the picture spans
        # the available width without artificial black letterboxing.
        metadata_height = 12 + 22 + 5 + 28 + 18 + 10 * 27
        max_image_height = max(
            1.0,
            rect.bottom() - image_top - metadata_height,
        )
        scale = min(
            rect.width() / max(source.width(), 1),
            max_image_height / max(source.height(), 1),
        )
        image_width = source.width() * scale
        image_height = source.height() * scale
        image_rect = QRectF(
            rect.center().x() - image_width / 2,
            image_top,
            image_width,
            image_height,
        )
        painter.drawImage(image_rect, source)
    else:
        image_height = min(
            rect.width() * 9.0 / 16.0,
            rect.height() * 0.48,
        )
        image_rect = QRectF(
            rect.left(),
            image_top,
            rect.width(),
            image_height,
        )
        painter.fillRect(image_rect, IMAGE_FALLBACK)
    if not single_column and not source.isNull():
        scaled = source.scaled(
            round(image_rect.width()),
            round(image_rect.height()),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        image_target = QRectF(
            image_rect.center().x() - scaled.width() / 2,
            image_rect.center().y() - scaled.height() / 2,
            scaled.width(),
            scaled.height(),
        )
        painter.drawImage(image_target, scaled)

    palette_top = image_rect.bottom() + 12
    palette_text = text(language, "color_palette_short")
    # The label has its own row so it can never be covered by the palette,
    # including narrow three-column layouts and Persian text.
    palette_label_rect = QRectF(
        rect.left(),
        palette_top,
        rect.width(),
        22,
    )
    palette_rect = QRectF(
        rect.left(),
        palette_label_rect.bottom() + 5,
        rect.width(),
        28,
    )
    _draw_text(
        painter,
        palette_label_rect,
        palette_text,
        language,
        9.0,
        INK,
        500,
        (
            Qt.AlignmentFlag.AlignRight
            if language == "fa"
            else Qt.AlignmentFlag.AlignLeft
        ),
    )
    colors = list(capture.analysis.get("dominant_colors", []))[:5]
    if not colors:
        colors = ["#D9D9D9"]
    cursor = palette_rect.left()
    equal_width = palette_rect.width() / max(len(colors), 1)
    for index, color in enumerate(colors):
        width = (
            palette_rect.right() - cursor
            if index == len(colors) - 1
            else equal_width
        )
        painter.fillRect(
            QRectF(cursor, palette_rect.top(), width, palette_rect.height()),
            QColor(color),
        )
        cursor += width

    rows_top = palette_rect.bottom() + 18
    available_height = max(80.0, rect.bottom() - rows_top)
    row_height = min(27.0, available_height / 10.0)
    for index, (label, value) in enumerate(
        _editorial_rows(capture, language)
    ):
        row_rect = QRectF(
            rect.left(),
            rows_top + index * row_height,
            rect.width(),
            row_height,
        )
        content = f"{label}: {value}" if value else f"{label}:"
        _draw_text(
            painter,
            row_rect,
            content,
            language,
            8.5,
            INK,
            400,
            (
                Qt.AlignmentFlag.AlignRight
                if language == "fa"
                else Qt.AlignmentFlag.AlignLeft
            ),
            word_wrap=index == 9,
        )


def export_captures_pdf(
    destination: Path,
    captures: Iterable[Capture],
    repository: Repository,
    language: str,
    columns: int,
    assets_root: Path,
    fps: float = 24.0,
    include_annotations: bool = False,
) -> int:
    capture_list = list(captures)
    if not capture_list:
        raise ValueError(text(language, "pdf_no_frames"))
    columns = max(1, min(int(columns), 3))

    writer = QPdfWriter(str(destination))
    writer.setTitle("ShotLab Visual Reference Export")
    writer.setCreator("ShotLab by StoryEco")
    writer.setResolution(144)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(
        QMarginsF(12, 12, 12, 12),
        QPageLayout.Unit.Millimeter,
    )

    painter = QPainter(writer)
    if not painter.isActive():
        raise OSError(text(language, "pdf_write_failed"))
    page_rect = QRectF(0, 0, writer.width(), writer.height())
    logo = _logo_image(
        assets_root / "final_ui" / "logo.svg",
        QSize(720, 178),
    )
    gap = PDF_CARD_GAP
    logo_width = min(250.0, page_rect.width() * 0.25)
    logo_height = logo_width * logo.height() / max(logo.width(), 1)
    content_top = page_rect.top() + logo_height + 38
    available_height = max(1.0, page_rect.bottom() - content_top)
    rows_per_page = (
        1
        if columns == 1
        else max(
            1,
            int(
                (available_height + gap)
                // (PDF_CARD_MIN_HEIGHT + gap)
            ),
        )
    )
    per_page = columns * rows_per_page
    page_count = math.ceil(len(capture_list) / per_page)

    try:
        for page_index in range(page_count):
            if page_index:
                writer.newPage()
            content_top = _draw_header(
                painter,
                page_rect,
                language,
                page_index + 1,
                logo,
            )
            card_width = (
                page_rect.width() - gap * (columns - 1)
            ) / columns
            card_height = (
                page_rect.bottom()
                - content_top
                - gap * (rows_per_page - 1)
            ) / rows_per_page
            page_items = capture_list[
                page_index * per_page : (page_index + 1) * per_page
            ]
            for position, capture in enumerate(page_items):
                row = position // columns
                logical_column = position % columns
                column = (
                    columns - logical_column - 1
                    if language == "fa"
                    else logical_column
                )
                card_rect = QRectF(
                    page_rect.left() + column * (card_width + gap),
                    content_top + row * (card_height + gap),
                    card_width,
                    card_height,
                )
                _draw_capture_card(
                    painter,
                    card_rect,
                    capture,
                    repository,
                    language,
                    max(float(fps), 1.0),
                    include_annotations,
                    columns == 1,
                )
    finally:
        painter.end()
    return len(capture_list)
