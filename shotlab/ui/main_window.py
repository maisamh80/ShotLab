from __future__ import annotations

import traceback
import uuid
import shutil
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QRunnable,
    QSettings,
    QSize,
    Qt,
    QTimer,
    QThreadPool,
    QUrl,
    QVariantAnimation,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QImage,
    QKeySequence,
    QPainter,
    QPixmap,
    QShortcut,
)
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QApplication,
    QBoxLayout,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QStackedWidget,
    QStackedLayout,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..analysis import analyze_image
from ..backup import export_library, restore_library
from ..i18n import OPTIONS, option_label, text
from ..media import format_timecode
from ..models import Capture, CaptureDraft, Project
from ..pdf_export import export_captures_pdf
from ..repository import Repository
from ..session import CaptureSession
from .styles import stylesheet
from .widgets import (
    CaptureFilterPanel,
    ColorSwatch,
    HoverHoldLabel,
    ProjectCard,
    TimelineSlider,
)

def split_terms(value: str) -> list[str]:
    return [
        item.strip()
        for item in value.replace("،", ",").split(",")
        if item.strip()
    ]


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class CaptureWorker(QRunnable):
    def __init__(
        self,
        session: CaptureSession,
        time_ms: int,
        displayed_image_path: Path | None = None,
        storage_mode: str = "small",
    ) -> None:
        super().__init__()
        self.session = session
        self.time_ms = time_ms
        self.displayed_image_path = displayed_image_path
        self.storage_mode = storage_mode
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            if self.displayed_image_path:
                draft = self.session.create_draft_from_source_frame(
                    self.time_ms,
                    self.displayed_image_path,
                    self.storage_mode,
                )
            else:
                draft = self.session.create_draft(
                    self.time_ms,
                    self.storage_mode,
                )
        except Exception as exc:
            if self.displayed_image_path:
                self.displayed_image_path.unlink(missing_ok=True)
            traceback.print_exc()
            self.signals.failed.emit(str(exc))
        else:
            self.signals.finished.emit(draft)


class NewProjectDialog(QDialog):
    def __init__(
        self,
        language: str,
        parent=None,
        *,
        initial_name: str = "",
        rename: bool = False,
    ) -> None:
        super().__init__(parent)
        self.language = language
        self.rename = rename
        self.setObjectName("LibraryNameDialog")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if language == "fa"
            else Qt.LayoutDirection.LeftToRight
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        panel = QFrame()
        panel.setObjectName("DialogPanel")
        outer.addWidget(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        heading = QHBoxLayout()
        if not rename:
            icon = QLabel()
            icon.setPixmap(
                QPixmap(
                    str(
                        Path(__file__).resolve().parents[2]
                        / "assets"
                        / "final_ui"
                        / "libraries.svg"
                    )
                ).scaled(
                    QSize(27, 27),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            heading.addWidget(icon)
        title = QLabel(
            text(language, "project_name")
            if rename
            else text(language, "new_project")
        )
        title.setObjectName("DialogTitle")
        heading.addWidget(title, 1)
        layout.addLayout(heading)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(text(language, "project_name"))
        self.name_edit.setText(initial_name)
        self.name_edit.setMinimumHeight(42)
        layout.addWidget(self.name_edit)

        actions = QHBoxLayout()
        actions.setSpacing(14)
        submit_button = QPushButton(
            text(language, "ok")
            if rename
            else text(language, "create")
        )
        submit_button.setObjectName("Primary")
        cancel_button = QPushButton(text(language, "cancel"))
        cancel_button.setObjectName("WarningCancel")
        submit_button.setMinimumWidth(82 if rename else 196)
        cancel_button.setMinimumWidth(138)
        submit_button.setToolTip(submit_button.text())
        cancel_button.setToolTip(text(language, "cancel"))
        submit_button.clicked.connect(self._accept)
        cancel_button.clicked.connect(self.reject)
        actions.addWidget(submit_button)
        actions.addStretch()
        actions.addWidget(cancel_button)
        layout.addLayout(actions)
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    def _accept(self) -> None:
        if not self.name_edit.text().strip():
            ValidationDialog(
                text(self.language, "required_name"),
                self.language,
                self,
            ).exec()
            return
        self.accept()

    @property
    def project_name(self) -> str:
        return self.name_edit.text().strip()


class ConfirmationDialog(QDialog):
    def __init__(
        self,
        title_text: str,
        message_text: str,
        confirm_text: str,
        language: str,
        destructive: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ConfirmationDialog")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if language == "fa"
            else Qt.LayoutDirection.LeftToRight
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        panel = QFrame()
        panel.setObjectName("WarningDialog")
        root.addWidget(panel)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 28, 28, 28)
        panel_layout.setSpacing(14)

        warning_icon = QLabel()
        warning_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
            / "warning.svg"
        )
        warning_icon.setPixmap(
            QPixmap(str(warning_path)).scaled(
                QSize(88, 80),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        panel_layout.addWidget(warning_icon)

        title = QLabel(title_text)
        title.setObjectName("WarningTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)

        message = QLabel(message_text)
        message.setObjectName("WarningMessage")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(message)
        panel_layout.addSpacing(6)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        cancel_button = QPushButton(text(language, "cancel"))
        cancel_button.setObjectName("WarningCancel")
        cancel_button.setToolTip(text(language, "cancel"))
        cancel_button.clicked.connect(self.reject)
        confirm_button = QPushButton(confirm_text)
        confirm_button.setObjectName(
            "Destructive" if destructive else "Primary"
        )
        confirm_button.setToolTip(confirm_text)
        confirm_button.clicked.connect(self.accept)
        actions.addWidget(cancel_button, 1)
        actions.addWidget(confirm_button, 1)
        panel_layout.addLayout(actions)


class ValidationDialog(QDialog):
    def __init__(
        self,
        message_text: str,
        language: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ValidationDialog")
        self.setModal(True)
        self.setFixedWidth(410)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if language == "fa"
            else Qt.LayoutDirection.LeftToRight
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        panel = QFrame()
        panel.setObjectName("DialogPanel")
        outer.addWidget(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(20)

        message_row = QHBoxLayout()
        message_row.setSpacing(12)
        icon = QLabel()
        icon.setPixmap(
            QPixmap(
                str(
                    Path(__file__).resolve().parents[2]
                    / "assets"
                    / "final_ui"
                    / "warning.svg"
                )
            ).scaled(
                QSize(42, 38),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        message = QLabel(message_text)
        message.setObjectName("ValidationMessage")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_row.addWidget(icon)
        message_row.addWidget(message, 1)
        layout.addLayout(message_row)

        okay = QPushButton("OK")
        okay.setObjectName("WarningCancel")
        okay.setMinimumWidth(90)
        okay.clicked.connect(self.accept)
        layout.addWidget(
            okay,
            0,
            Qt.AlignmentFlag.AlignRight
            if language == "en"
            else Qt.AlignmentFlag.AlignLeft,
        )


class DeveloperCreditDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DeveloperCreditDialog")
        self.setModal(True)
        self.setFixedWidth(470)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        panel = QFrame()
        panel.setObjectName("DeveloperCreditPanel")
        root.addWidget(panel)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 18, 28, 26)
        panel_layout.setSpacing(14)

        top = QHBoxLayout()
        top.addStretch()
        close_button = QPushButton("×")
        close_button.setObjectName("WarningClose")
        close_button.setFixedSize(32, 32)
        close_button.setToolTip("Close")
        close_button.clicked.connect(self.accept)
        top.addWidget(close_button)
        panel_layout.addLayout(top)

        title = QLabel("SHOTLAB")
        title.setObjectName("DeveloperCreditTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)

        accent = QFrame()
        accent.setObjectName("DeveloperCreditAccent")
        accent.setFixedHeight(3)
        panel_layout.addWidget(accent)

        message = QLabel(
            "This program developed by Maisam Hosaini\n"
            "maisamh80@gmail.com\n"
            "Mobile number: +98 9123028981"
        )
        message.setObjectName("DeveloperCreditMessage")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        panel_layout.addWidget(message)
        panel_layout.addSpacing(4)

        okay_button = QPushButton("OK")
        okay_button.setObjectName("Primary")
        okay_button.setToolTip("OK")
        okay_button.clicked.connect(self.accept)
        panel_layout.addWidget(okay_button)


class PdfExportDialog(QDialog):
    def __init__(self, language: str, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self.scope = ""
        self.setObjectName("PdfExportDialog")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if language == "fa"
            else Qt.LayoutDirection.LeftToRight
        )
        self.setWindowTitle(text(language, "export_pdf"))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        panel = QFrame()
        panel.setObjectName("PdfDialogPanel")
        outer.addWidget(panel)

        root = QVBoxLayout(panel)
        root.setContentsMargins(28, 28, 28, 24)
        root.setSpacing(14)

        icon = QLabel()
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setPixmap(
            QPixmap(
                str(
                    Path(__file__).resolve().parents[2]
                    / "assets"
                    / "final_ui"
                    / "pdf.svg"
                )
            ).scaled(
                QSize(58, 76),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        title = QLabel(text(language, "export_pdf"))
        title.setObjectName("PdfDialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(icon)
        root.addWidget(title)

        columns_row = QHBoxLayout()
        columns_row.setSpacing(18)
        self.columns_group = QButtonGroup(self)
        for column_count in (1, 2, 3):
            radio = QRadioButton(
                text(
                    language,
                    f"pdf_{column_count}_column"
                    if column_count == 1
                    else f"pdf_{column_count}_columns",
                )
            )
            self.columns_group.addButton(radio, column_count)
            columns_row.addWidget(radio)
            if column_count == 1:
                radio.setChecked(True)
        root.addLayout(columns_row)

        for scope, key in (
            ("all", "pdf_all_libraries"),
            ("active", "pdf_last_active_library"),
            ("search", "pdf_search_results"),
        ):
            button = QPushButton(text(language, key))
            button.setObjectName("Primary")
            button.setMinimumHeight(44)
            button.clicked.connect(
                lambda _checked=False, selected=scope: self._choose_scope(
                    selected
                )
            )
            root.addWidget(button)

        cancel = QPushButton(text(language, "cancel"))
        cancel.setObjectName("WarningCancel")
        cancel.setMinimumSize(220, 44)
        cancel.clicked.connect(self.reject)
        root.addWidget(
            cancel,
            0,
            (
                Qt.AlignmentFlag.AlignLeft
                if language == "fa"
                else Qt.AlignmentFlag.AlignRight
            ),
        )

    def _choose_scope(self, scope: str) -> None:
        self.scope = scope
        self.accept()

    @property
    def columns(self) -> int:
        return max(1, self.columns_group.checkedId())


class MainWindow(QMainWindow):
    CAPTURE_THUMBNAIL_WIDTHS = (120, 150, 180, 220, 260)
    GALLERY_THUMBNAIL_WIDTHS = (130, 160, 190, 230, 280)
    SEARCH_THUMBNAIL_WIDTHS = (130, 160, 190, 230, 280)

    def __init__(self, repository: Repository, session: CaptureSession) -> None:
        super().__init__()
        self.repository = repository
        self.session = session
        self.settings = QSettings("StoryEco", "ShotLab")
        self.language = str(self.settings.value("language", "fa"))
        if self.language not in {"fa", "en"}:
            self.language = "fa"
        self.theme = str(self.settings.value("theme", "dark"))
        if self.theme not in {"dark", "light"}:
            self.theme = "dark"
        QApplication.instance().setProperty("shotlab_theme", self.theme)
        self.sidebar_collapsed = bool(
            self.settings.value("sidebar_collapsed", False, type=bool)
        )
        self.capture_thumbnail_index = max(
            0,
            min(
                int(self.settings.value("capture_thumbnail_index", 2)),
                len(self.CAPTURE_THUMBNAIL_WIDTHS) - 1,
            ),
        )
        self.gallery_thumbnail_index = max(
            0,
            min(
                int(self.settings.value("gallery_thumbnail_index", 2)),
                len(self.GALLERY_THUMBNAIL_WIDTHS) - 1,
            ),
        )
        self.search_thumbnail_index = max(
            0,
            min(
                int(self.settings.value("search_thumbnail_index", 2)),
                len(self.SEARCH_THUMBNAIL_WIDTHS) - 1,
            ),
        )
        self.frame_storage_mode = str(
            self.settings.value("frame_storage_mode", "small")
        )
        if self.frame_storage_mode not in {"actual", "medium", "small"}:
            self.frame_storage_mode = "small"
        self.thread_pool = QThreadPool.globalInstance()
        self.current_project: Project | None = None
        self.current_draft: CaptureDraft | None = None
        self.current_capture: Capture | None = None
        self.current_gallery_capture: Capture | None = None
        self._capture_worker: CaptureWorker | None = None
        self._displayed_frame = QImage()
        self._displayed_frame_time_ms = 0
        self._last_search_capture_ids: list[str] = []
        self._last_gallery_capture_ids: list[str] = []

        self.setWindowTitle("ShotLab")
        self.setWindowIcon(
            QIcon(
                str(
                    Path(__file__).resolve().parents[2]
                    / "assets"
                    / "app-icon.png"
                )
            )
        )
        self.resize(1920, 1009)
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(stylesheet(self.theme, self.language))

        self.central_shell = QWidget()
        self.central_shell.setObjectName("CentralShell")
        self.status_toast = QLabel(self.central_shell)
        self.status_toast.setObjectName("StatusToast")
        self.status_toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_toast.setWordWrap(True)
        self.status_toast.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self.status_toast.hide()
        self._status_toast_timer = QTimer(self)
        self._status_toast_timer.setSingleShot(True)
        self._status_toast_timer.timeout.connect(self.status_toast.hide)
        self.shell_layout = QBoxLayout(
            QBoxLayout.Direction.LeftToRight,
            self.central_shell,
        )
        self.shell_layout.setContentsMargins(0, 0, 0, 0)
        self.shell_layout.setSpacing(0)
        self._build_sidebar()
        self.stack = QStackedWidget()
        self.shell_layout.addWidget(self.sidebar)
        self.shell_layout.addWidget(self.stack, 1)
        self.setCentralWidget(self.central_shell)
        self._build_library_page()
        self._build_capture_page()
        self._build_gallery_page()
        self.stack.currentChanged.connect(self._workspace_changed)
        application = QApplication.instance()
        if application is not None:
            application.installEventFilter(self)
        self._apply_pointing_hand_cursors(self)
        self._bind_shortcuts()
        self._apply_language()
        self.refresh_projects()

    def _build_sidebar(self) -> None:
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(22, 28, 18, 20)
        self.sidebar_layout.setSpacing(10)

        self.brand_logo = HoverHoldLabel(5000)
        self.brand_logo.setObjectName("BrandLogo")
        self.brand_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_logo.setFixedSize(234, 66)
        self.brand_logo.hold_completed.connect(
            self._show_developer_credit
        )
        self.sidebar_layout.addWidget(
            self.brand_logo,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )
        self.collapse_sidebar_button = QPushButton(self.central_shell)
        self.collapse_sidebar_button.setObjectName("SidebarToggle")
        self.collapse_sidebar_button.setFixedSize(28, 48)
        self.collapse_sidebar_button.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addSpacing(22)

        self.sidebar_navigation_label = QLabel()
        self.sidebar_navigation_label.setObjectName("SidebarSection")
        self.sidebar_layout.addWidget(self.sidebar_navigation_label)
        self.nav_projects = self._nav_button(self.show_projects)
        self.nav_capture = self._nav_button(self.show_capture_workspace)
        self.nav_gallery = self._nav_button(self.show_current_gallery)
        self.nav_projects.setChecked(True)
        for button in (
            self.nav_projects,
            self.nav_capture,
            self.nav_gallery,
        ):
            self.sidebar_layout.addWidget(button)

        self.sidebar_layout.addSpacing(34)
        self.sidebar_data_label = QLabel("DATA")
        self.sidebar_data_label.setObjectName("SidebarSection")
        self.sidebar_layout.addWidget(self.sidebar_data_label)
        self.pdf_export_button = QPushButton()
        self.pdf_export_button.setObjectName("SidebarAction")
        self.pdf_export_button.clicked.connect(self.export_pdf)
        self.export_button = QPushButton()
        self.export_button.setObjectName("SidebarAction")
        self.export_button.clicked.connect(self.export_database)
        self.import_button = QPushButton()
        self.import_button.setObjectName("SidebarAction")
        self.import_button.clicked.connect(self.import_database)
        self.sidebar_layout.addWidget(self.pdf_export_button)
        self.sidebar_layout.addWidget(self.export_button)
        self.sidebar_layout.addWidget(self.import_button)

        final_assets = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
        )
        for button, icon_name in (
            (self.nav_projects, "libraries.svg"),
            (self.nav_capture, "capture.svg"),
            (self.nav_gallery, "gallery.svg"),
            (self.pdf_export_button, "pdf.svg"),
            (self.export_button, "export.svg"),
            (self.import_button, "import.svg"),
        ):
            button.setIcon(QIcon(str(final_assets / icon_name)))
            button.setIconSize(QSize(30, 30))

        self.sidebar_layout.addStretch()

        controls = QWidget()
        controls.setObjectName("Transparent")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(9)
        self.storage_caption = QLabel()
        self.storage_caption.setObjectName("SidebarFooter")
        self.storage_button = QPushButton()
        self.storage_button.setObjectName("RoundControl")
        self.storage_button.setFixedSize(44, 50)
        self.storage_menu = QMenu(self.storage_button)
        self.storage_actions: dict[str, QAction] = {}
        for mode in ("actual", "medium", "small"):
            action = QAction(self.storage_menu)
            action.triggered.connect(
                lambda _checked=False, selected=mode: self._set_frame_storage_mode(
                    selected
                )
            )
            self.storage_menu.addAction(action)
            self.storage_actions[mode] = action
        self.storage_button.setMenu(self.storage_menu)
        self.language_button = QPushButton()
        self.language_button.setObjectName("RoundControl")
        self.language_button.setFixedSize(44, 50)
        self.language_button.clicked.connect(self._toggle_language)
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("RoundControl")
        self.theme_button.setFixedSize(44, 50)
        self.theme_button.clicked.connect(self.toggle_theme)
        controls_layout.addWidget(self.storage_caption)
        controls_layout.addStretch()
        controls_layout.addWidget(self.storage_button)
        controls_layout.addWidget(self.language_button)
        controls_layout.addWidget(self.theme_button)
        self.sidebar_layout.addWidget(controls)
        self.sidebar_controls = controls
        self.developer_label = QLabel("Developed by: StoryEco.com")
        self.developer_label.setObjectName("SidebarFooter")
        self.developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label = QLabel(f"ShotLab v{__version__}")
        self.version_label.setObjectName("SidebarFooter")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(self.developer_label)
        self.sidebar_layout.addWidget(self.version_label)

    def _show_developer_credit(self) -> None:
        DeveloperCreditDialog(self).exec()

    def toggle_sidebar(self) -> None:
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.settings.setValue("sidebar_collapsed", self.sidebar_collapsed)
        self._apply_language(animate_sidebar=True)

    def _sidebar_content_widgets(self) -> tuple[QWidget, ...]:
        return (
            self.brand_logo,
            self.sidebar_navigation_label,
            self.sidebar_data_label,
            self.nav_projects,
            self.nav_capture,
            self.nav_gallery,
            self.pdf_export_button,
            self.export_button,
            self.import_button,
            self.sidebar_controls,
            self.theme_button,
            self.developer_label,
            self.version_label,
        )

    def _set_sidebar_content_visible(self, visible: bool) -> None:
        for widget in self._sidebar_content_widgets():
            widget.setVisible(visible)

    def _apply_sidebar_state(self, animated: bool = False) -> None:
        collapsed = self.sidebar_collapsed
        target_width = 46 if collapsed else 282
        margin = 7 if collapsed else 22
        trailing_margin = margin if collapsed else 18
        self.sidebar_layout.setContentsMargins(
            margin,
            28 if not collapsed else 14,
            trailing_margin,
            20 if not collapsed else 14,
        )

        self.collapse_sidebar_button.setText(
            "»" if collapsed else "«"
        )
        logo_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
            / "logo.svg"
        )
        source = QPixmap(str(logo_path))
        scaled = source.scaled(
            self.brand_logo.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        tinted = QPixmap(scaled.size())
        tinted.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, scaled)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(
            tinted.rect(),
            QColor("#d8b365"),
        )
        painter.end()
        self.brand_logo.setPixmap(tinted)

        previous_animation = getattr(self, "_sidebar_animation", None)
        if previous_animation is not None:
            previous_animation.stop()
            self._sidebar_animation = None

        if not animated or self.sidebar.width() == target_width:
            self.sidebar.setFixedWidth(target_width)
            self._set_sidebar_content_visible(not collapsed)
            self.shell_layout.activate()
            self._position_sidebar_toggle()
            self._position_status_toast()
            return

        self._set_sidebar_content_visible(False)
        animation = QVariantAnimation(self)
        animation.setDuration(240)
        animation.setStartValue(self.sidebar.width())
        animation.setEndValue(target_width)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def update_width(value) -> None:
            self.sidebar.setFixedWidth(int(value))
            self.shell_layout.activate()
            self._position_sidebar_toggle()
            self._position_status_toast()

        def finish_animation() -> None:
            self.sidebar.setFixedWidth(target_width)
            self._set_sidebar_content_visible(not collapsed)
            self.shell_layout.activate()
            self._position_sidebar_toggle()
            self._position_status_toast()
            if getattr(self, "_sidebar_animation", None) is animation:
                self._sidebar_animation = None

        animation.valueChanged.connect(update_width)
        animation.finished.connect(finish_animation)
        self._sidebar_animation = animation
        animation.start()

    def _position_sidebar_toggle(self) -> None:
        if not hasattr(self, "collapse_sidebar_button"):
            return
        sidebar_geometry = self.sidebar.geometry()
        boundary_x = sidebar_geometry.right() + 1
        x = boundary_x - self.collapse_sidebar_button.width() // 2
        y = (
            self.central_shell.height()
            - self.collapse_sidebar_button.height()
        ) // 2
        x = max(
            0,
            min(
                x,
                self.central_shell.width()
                - self.collapse_sidebar_button.width(),
            ),
        )
        self.collapse_sidebar_button.move(x, max(0, y))
        self.collapse_sidebar_button.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_sidebar_toggle()
        self._position_status_toast()

    def eventFilter(self, watched, event) -> bool:
        if event.type() in {
            QEvent.Type.Polish,
            QEvent.Type.Show,
            QEvent.Type.EnabledChange,
        }:
            self._apply_pointing_hand_cursor(watched)
        if (
            hasattr(self, "projects_scroll")
            and watched is self.projects_scroll.viewport()
            and event.type() == QEvent.Type.Resize
        ):
            QTimer.singleShot(0, self._reflow_project_cards)
        return super().eventFilter(watched, event)

    @staticmethod
    def _apply_pointing_hand_cursor(widget: object) -> None:
        if not isinstance(
            widget,
            (
                QAbstractButton,
                QAbstractItemView,
                QComboBox,
                QMenu,
                QSlider,
            ),
        ):
            return
        cursor = (
            Qt.CursorShape.PointingHandCursor
            if widget.isEnabled()
            else Qt.CursorShape.ArrowCursor
        )
        widget.setCursor(cursor)
        if isinstance(widget, QAbstractItemView):
            widget.viewport().setCursor(cursor)

    def _apply_pointing_hand_cursors(self, root: QWidget) -> None:
        self._apply_pointing_hand_cursor(root)
        for widget in root.findChildren(QWidget):
            self._apply_pointing_hand_cursor(widget)

    @Slot(int)
    def _workspace_changed(self, _index: int) -> None:
        if self.stack.currentWidget() is not self.capture_page:
            # Preserve the current position, but immediately stop video and
            # audio whenever the user leaves Capture Workspace.
            self.player.pause()

    def show_status(self, message: str, timeout_ms: int = 3000) -> None:
        if not message:
            return
        available_width = (
            self.stack.width()
            if hasattr(self, "stack")
            else self.central_shell.width()
        )
        self.status_toast.setMaximumWidth(max(300, round(available_width * 0.72)))
        self.status_toast.setText(message)
        self.status_toast.adjustSize()
        self._position_status_toast()
        self.status_toast.show()
        self.status_toast.raise_()
        self._status_toast_timer.start(max(500, int(timeout_ms)))

    def _position_status_toast(self) -> None:
        if (
            not hasattr(self, "status_toast")
            or not hasattr(self, "stack")
        ):
            return
        stack_geometry = self.stack.geometry()
        x = (
            stack_geometry.left()
            + (stack_geometry.width() - self.status_toast.width()) // 2
        )
        y = (
            self.central_shell.height()
            - self.status_toast.height()
            - 18
        )
        self.status_toast.move(max(8, x), max(8, y))

    def _nav_button(self, callback) -> QPushButton:
        button = QPushButton()
        button.setObjectName("Nav")
        button.setCheckable(True)
        button.clicked.connect(callback)
        return button

    def _thumbnail_button(self, icon_index: int, callback) -> QPushButton:
        button = QPushButton()
        button.setObjectName("ThumbnailSize")
        assets_path = Path(__file__).resolve().parents[2] / "assets"
        button.setIcon(
            QIcon(
                str(
                    assets_path
                    / "final_ui"
                    / ("zoom-in.svg" if icon_index == 0 else "zoom-out.svg")
                )
            )
        )
        button.setIconSize(
            QSize(30, 30) if icon_index == 0 else QSize(25, 25)
        )
        button.setFixedSize(42, 36)
        button.clicked.connect(callback)
        return button

    def _frame_delete_button(self, callback) -> QPushButton:
        button = QPushButton()
        button.setObjectName("ProjectDelete")
        button.setIcon(
            QIcon(
                str(
                    Path(__file__).resolve().parents[2]
                    / "assets"
                    / "final_ui"
                    / "delete.svg"
                )
            )
        )
        button.setIconSize(QSize(30, 30))
        button.setFixedSize(44, 40)
        button.clicked.connect(callback)
        return button

    @staticmethod
    def _set_thumbnail_dimensions(list_widget: QListWidget, width: int) -> None:
        height = round(width * 9 / 16)
        list_widget.setIconSize(QSize(width, height))
        list_widget.setGridSize(QSize(width + 30, height + 42))

    @staticmethod
    def _thumbnail_icon(path: Path, target: QSize) -> QIcon:
        source = QPixmap(str(path))
        if source.isNull():
            return QIcon()
        scaled = source.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled.width() - target.width()) // 2)
        y = max(0, (scaled.height() - target.height()) // 2)
        return QIcon(
            scaled.copy(
                x,
                y,
                target.width(),
                target.height(),
            )
        )

    def _apply_capture_thumbnail_size(self) -> None:
        width = self.CAPTURE_THUMBNAIL_WIDTHS[self.capture_thumbnail_index]
        self._set_thumbnail_dimensions(self.capture_list, width)
        self.capture_thumbnail_shrink_button.setEnabled(
            self.capture_thumbnail_index > 0
        )
        self.capture_thumbnail_grow_button.setEnabled(
            self.capture_thumbnail_index
            < len(self.CAPTURE_THUMBNAIL_WIDTHS) - 1
        )

    def change_capture_thumbnail_size(self, direction: int) -> None:
        next_index = max(
            0,
            min(
                self.capture_thumbnail_index + direction,
                len(self.CAPTURE_THUMBNAIL_WIDTHS) - 1,
            ),
        )
        if next_index == self.capture_thumbnail_index:
            return
        self.capture_thumbnail_index = next_index
        self.settings.setValue(
            "capture_thumbnail_index",
            self.capture_thumbnail_index,
        )
        self._apply_capture_thumbnail_size()
        self.refresh_captures()

    def _apply_gallery_thumbnail_size(self) -> None:
        width = self.GALLERY_THUMBNAIL_WIDTHS[self.gallery_thumbnail_index]
        self._set_thumbnail_dimensions(self.gallery_list, width)
        self.gallery_thumbnail_shrink_button.setEnabled(
            self.gallery_thumbnail_index > 0
        )
        self.gallery_thumbnail_grow_button.setEnabled(
            self.gallery_thumbnail_index
            < len(self.GALLERY_THUMBNAIL_WIDTHS) - 1
        )

    def change_gallery_thumbnail_size(self, direction: int) -> None:
        next_index = max(
            0,
            min(
                self.gallery_thumbnail_index + direction,
                len(self.GALLERY_THUMBNAIL_WIDTHS) - 1,
            ),
        )
        if next_index == self.gallery_thumbnail_index:
            return
        self.gallery_thumbnail_index = next_index
        self.settings.setValue(
            "gallery_thumbnail_index",
            self.gallery_thumbnail_index,
        )
        self._apply_gallery_thumbnail_size()
        selected_id = (
            self.current_gallery_capture.id
            if self.current_gallery_capture
            else None
        )
        self.refresh_gallery()
        if selected_id:
            self.show_gallery_capture(selected_id)

    def _apply_search_thumbnail_size(self) -> None:
        width = self.SEARCH_THUMBNAIL_WIDTHS[self.search_thumbnail_index]
        self._set_thumbnail_dimensions(self.global_results_list, width)
        self.search_thumbnail_shrink_button.setEnabled(
            self.search_thumbnail_index > 0
        )
        self.search_thumbnail_grow_button.setEnabled(
            self.search_thumbnail_index
            < len(self.SEARCH_THUMBNAIL_WIDTHS) - 1
        )

    def change_search_thumbnail_size(self, direction: int) -> None:
        next_index = max(
            0,
            min(
                self.search_thumbnail_index + direction,
                len(self.SEARCH_THUMBNAIL_WIDTHS) - 1,
            ),
        )
        if next_index == self.search_thumbnail_index:
            return
        self.search_thumbnail_index = next_index
        self.settings.setValue(
            "search_thumbnail_index",
            self.search_thumbnail_index,
        )
        self._apply_search_thumbnail_size()
        self._global_search_changed()

    def _build_library_page(self) -> None:
        self.library_page = QWidget()
        self.library_page.setObjectName("LibraryPage")
        root = QVBoxLayout(self.library_page)
        root.setContentsMargins(24, 24, 28, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        brand_box = QVBoxLayout()
        self.library_eyebrow = QLabel("YOUR VISUAL MEMORY")
        self.library_eyebrow.setObjectName("SectionEyebrow")
        self.library_eyebrow.hide()
        self.library_title = QLabel()
        self.library_title.setObjectName("Title")
        self.library_title.setMinimumHeight(42)
        brand_box.addWidget(self.library_eyebrow)
        brand_box.addWidget(self.library_title)
        self.new_project_button = QPushButton()
        self.new_project_button.setObjectName("Primary")
        self.new_project_button.clicked.connect(self.create_project)

        header.addLayout(brand_box)
        header.addStretch()
        header.addWidget(self.new_project_button)
        root.addLayout(header)

        self.library_filters = CaptureFilterPanel(self.language)
        self.library_filters.changed.connect(self._global_search_changed)
        root.addWidget(self.library_filters)

        self.library_content_stack = QStackedWidget()
        self.projects_scroll = QScrollArea()
        self.projects_scroll.setWidgetResizable(True)
        self.projects_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.project_grid_widget = QWidget()
        self.project_grid = QGridLayout(self.project_grid_widget)
        self.project_grid.setContentsMargins(0, 0, 0, 0)
        self.project_grid.setHorizontalSpacing(28)
        self.project_grid.setVerticalSpacing(24)
        self.project_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self._project_cards: list[ProjectCard] = []
        self._project_empty_state: QLabel | None = None
        self.projects_scroll.setWidget(self.project_grid_widget)
        self.projects_scroll.viewport().installEventFilter(self)
        self.library_content_stack.addWidget(self.projects_scroll)

        search_page = QWidget()
        search_layout = QVBoxLayout(search_page)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_toolbar = QHBoxLayout()
        search_toolbar.setContentsMargins(0, 0, 0, 0)
        search_toolbar.setSpacing(8)
        self.search_results_title = QLabel()
        self.search_results_title.setObjectName("NeutralSectionTitle")
        self.search_thumbnail_shrink_button = self._thumbnail_button(
            1,
            lambda _checked=False: self.change_search_thumbnail_size(-1),
        )
        self.search_zoom_label = QLabel()
        self.search_zoom_label.setObjectName("ToolbarCaption")
        self.search_thumbnail_grow_button = self._thumbnail_button(
            0,
            lambda _checked=False: self.change_search_thumbnail_size(1),
        )
        search_toolbar.addWidget(self.search_results_title)
        search_toolbar.addStretch()
        search_toolbar.addWidget(self.search_thumbnail_shrink_button)
        search_toolbar.addWidget(self.search_zoom_label)
        search_toolbar.addWidget(self.search_thumbnail_grow_button)
        self.global_results_list = QListWidget()
        self.global_results_list.setObjectName("ThumbnailList")
        self.global_results_list.setViewMode(QListView.ViewMode.IconMode)
        self.global_results_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.global_results_list.itemDoubleClicked.connect(
            self._global_result_clicked
        )
        self._apply_search_thumbnail_size()
        self.no_search_results_label = QLabel()
        self.no_search_results_label.setObjectName("Muted")
        self.no_search_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_layout.addLayout(search_toolbar)
        search_layout.addWidget(self.global_results_list, 1)
        search_layout.addWidget(self.no_search_results_label)
        self.library_content_stack.addWidget(search_page)
        root.addWidget(self.library_content_stack, 1)
        self.stack.addWidget(self.library_page)

    def _build_capture_page(self) -> None:
        self.capture_page = QWidget()
        self.capture_page.setObjectName("CapturePage")
        root = QVBoxLayout(self.capture_page)
        root.setContentsMargins(24, 24, 28, 24)
        root.setSpacing(18)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        title_box = QHBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(10)
        self.capture_workspace_title = QLabel()
        self.capture_workspace_title.setObjectName("Title")
        self.project_title_label = QLabel()
        self.project_title_label.setObjectName("WorkspaceProjectTitle")
        self.project_title_label.setMinimumHeight(42)
        title_box.addWidget(self.capture_workspace_title)
        title_box.addWidget(self.project_title_label)
        self.session_notice = QLabel()
        self.session_notice.setObjectName("SessionNotice")
        self.session_notice.setMaximumWidth(720)
        self.session_notice.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.capture_to_gallery_button = QPushButton()
        self.capture_to_gallery_button.setObjectName("Primary")
        self.capture_to_gallery_button.clicked.connect(
            self.show_current_gallery
        )
        self.video_button = QPushButton()
        self.video_button.setObjectName("Primary")
        self.video_button.clicked.connect(self.select_session_video)
        toolbar_layout.addLayout(title_box)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.session_notice)
        toolbar_layout.addWidget(self.video_button)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.capture_to_gallery_button)
        root.addLayout(toolbar_layout)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setObjectName("WorkspaceSplitter")
        main_splitter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        main_splitter.setHandleWidth(10)
        left = QWidget()
        self.capture_content = left
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.capture_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.capture_vertical_splitter.setObjectName("CaptureVerticalSplitter")
        self.capture_vertical_splitter.setChildrenCollapsible(False)
        self.capture_vertical_splitter.setHandleWidth(8)
        left_layout.addWidget(self.capture_vertical_splitter)

        playback_panel = QWidget()
        playback_layout = QVBoxLayout(playback_panel)
        playback_layout.setContentsMargins(0, 0, 0, 0)
        playback_layout.setSpacing(14)

        self.video_stage = QWidget()
        self.video_stage.setObjectName("VideoStage")
        video_stack = QStackedLayout(self.video_stage)
        video_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        video_stack.setContentsMargins(0, 0, 0, 0)
        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("VideoWidget")
        self.video_widget.setMinimumHeight(390)
        self.video_empty_label = QLabel()
        self.video_empty_label.setObjectName("VideoEmpty")
        self.video_empty_label.setWordWrap(True)
        self.video_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_empty_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        video_stack.addWidget(self.video_widget)
        video_stack.addWidget(self.video_empty_label)
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.7)
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        self.video_widget.videoSink().videoFrameChanged.connect(
            self._video_frame_changed
        )
        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.playbackStateChanged.connect(self._playback_changed)
        playback_layout.addWidget(self.video_stage, 1)

        transport = QFrame()
        transport.setObjectName("Transport")
        transport.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        transport_layout = QVBoxLayout(transport)
        transport_layout.setContentsMargins(14, 10, 14, 12)
        transport_layout.setSpacing(8)
        self.timeline = TimelineSlider()
        self.timeline.setRange(0, 0)
        self.timeline.sliderMoved.connect(self.player.setPosition)
        self.timeline.marker_clicked.connect(self.open_capture_by_id)
        transport_layout.addWidget(self.timeline)

        controls = QGridLayout()
        controls.setContentsMargins(0, 2, 0, 0)
        controls.setHorizontalSpacing(10)
        self.play_button = QPushButton()
        self.play_button.setObjectName("TransportButton")
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.play_video)
        self.pause_button = QPushButton()
        self.pause_button.setObjectName("TransportButton")
        self.pause_button.clicked.connect(self.pause_playback)
        self.back_frame_button = QPushButton()
        self.back_frame_button.setObjectName("TransportButton")
        self.back_frame_button.clicked.connect(lambda: self.step_frame(-1))
        self.forward_frame_button = QPushButton()
        self.forward_frame_button.setObjectName("TransportButton")
        self.forward_frame_button.clicked.connect(lambda: self.step_frame(1))
        navigator_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "final_ui"
        )
        for button, icon_name in (
            (self.back_frame_button, "previous-frame.svg"),
            (self.play_button, "play.svg"),
            (self.forward_frame_button, "next-frame.svg"),
        ):
            button.setIcon(QIcon(str(navigator_path / icon_name)))
            button.setIconSize(QSize(24, 24))
        self.pause_button.setIcon(
            QIcon(str(navigator_path / "pause.svg"))
        )
        self.pause_button.setIconSize(QSize(24, 24))
        for button in (
            self.back_frame_button,
            self.play_button,
            self.pause_button,
            self.forward_frame_button,
        ):
            button.setFixedSize(44, 36)

        self.timecode_label = QLabel("00:00:00:00 / 00:00:00:00")
        self.timecode_label.setObjectName("Timecode")
        self.timecode_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.capture_button = QPushButton()
        self.capture_button.setObjectName("Capture")
        self.capture_button.clicked.connect(self.capture_current_frame)
        center_controls = QWidget()
        center_controls.setObjectName("Transparent")
        center_layout = QHBoxLayout(center_controls)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(7)
        center_layout.addWidget(self.back_frame_button)
        center_layout.addWidget(self.play_button)
        center_layout.addWidget(self.pause_button)
        center_layout.addWidget(self.forward_frame_button)

        controls.addWidget(
            self.timecode_label,
            0,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        controls.addWidget(center_controls, 0, 1, Qt.AlignmentFlag.AlignCenter)
        controls.addWidget(
            self.capture_button,
            0,
            2,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        controls.setColumnStretch(0, 1)
        controls.setColumnStretch(2, 1)
        transport_layout.addLayout(controls)
        playback_layout.addWidget(transport)

        captures_panel = QWidget()
        captures_layout = QVBoxLayout(captures_panel)
        captures_layout.setContentsMargins(0, 12, 0, 0)
        captures_layout.setSpacing(10)
        captures_header = QHBoxLayout()
        self.captures_title = QLabel()
        self.captures_title.setObjectName("NeutralSectionTitle")
        self.capture_thumbnail_grow_button = self._thumbnail_button(
            0,
            lambda _checked=False: self.change_capture_thumbnail_size(1),
        )
        self.capture_thumbnail_shrink_button = self._thumbnail_button(
            1,
            lambda _checked=False: self.change_capture_thumbnail_size(-1),
        )
        self.capture_import_image_button = QPushButton()
        self.capture_import_image_button.setObjectName("ThumbnailImport")
        self.capture_import_image_button.setIcon(
            QIcon(
                str(
                    Path(__file__).resolve().parents[2]
                    / "assets"
                    / "final_ui"
                    / "import-frame.svg"
                )
            )
        )
        self.capture_import_image_button.setIconSize(QSize(31, 25))
        self.capture_import_image_button.setMinimumHeight(36)
        self.capture_import_image_button.clicked.connect(
            self.import_image_to_project
        )
        captures_header.addWidget(self.captures_title)
        captures_header.addStretch()
        self.capture_zoom_label = QLabel()
        self.capture_zoom_label.setObjectName("ToolbarCaption")
        captures_header.addWidget(self.capture_import_image_button)
        captures_header.addSpacing(18)
        captures_header.addWidget(self.capture_thumbnail_shrink_button)
        captures_header.addWidget(self.capture_zoom_label)
        captures_header.addWidget(self.capture_thumbnail_grow_button)
        captures_layout.addLayout(captures_header)
        self.capture_list = QListWidget()
        self.capture_list.setObjectName("ThumbnailList")
        self.capture_list.setViewMode(QListView.ViewMode.IconMode)
        self.capture_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.capture_list.itemClicked.connect(self._capture_item_clicked)
        capture_list_frame = QFrame()
        capture_list_frame.setObjectName("GalleryBrowser")
        capture_list_layout = QVBoxLayout(capture_list_frame)
        capture_list_layout.setContentsMargins(12, 12, 12, 12)
        capture_list_layout.addWidget(self.capture_list)
        captures_layout.addWidget(capture_list_frame, 1)

        self.capture_vertical_splitter.addWidget(playback_panel)
        self.capture_vertical_splitter.addWidget(captures_panel)
        self.capture_vertical_splitter.setSizes([650, 250])
        self._apply_capture_thumbnail_size()
        main_splitter.addWidget(left)

        self.inspector_frame = QFrame()
        self.inspector_frame.setObjectName("Inspector")
        inspector_layout = QVBoxLayout(self.inspector_frame)
        inspector_layout.setContentsMargins(16, 16, 16, 16)
        inspector_layout.setSpacing(10)
        inspector_heading = QHBoxLayout()
        inspector_heading.setContentsMargins(0, 0, 0, 0)
        self.inspector_title = QLabel()
        self.inspector_title.setObjectName("InspectorTitle")
        self.inspector_time = QLabel("00:00:00:00")
        self.inspector_time.setObjectName("InspectorTime")
        inspector_heading.addWidget(self.inspector_title, 1)
        inspector_heading.addWidget(self.inspector_time)
        inspector_layout.addLayout(inspector_heading)

        self.preview_label = QLabel()
        self.preview_label.setObjectName("FramePreview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(210)
        inspector_layout.addWidget(self.preview_label)

        self.palette_frame = QFrame()
        self.palette_caption = QLabel()
        self.palette_caption.setObjectName("Muted")
        self.palette_caption.hide()
        inspector_layout.addWidget(self.palette_caption)
        self.palette_layout = QHBoxLayout(self.palette_frame)
        self.palette_layout.setContentsMargins(0, 0, 0, 0)
        self.palette_layout.setSpacing(0)
        self.palette_swatches: list[ColorSwatch] = []
        for _ in range(5):
            swatch = ColorSwatch()
            swatch.setMinimumHeight(24)
            swatch.color_clicked.connect(self.copy_color_to_clipboard)
            self.palette_layout.addWidget(swatch)
            self.palette_swatches.append(swatch)
        inspector_layout.addWidget(self.palette_frame)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        form_widget = QWidget()
        self.form = QFormLayout(form_widget)
        self.form.setContentsMargins(0, 0, 0, 0)
        self.form.setHorizontalSpacing(12)
        self.form.setVerticalSpacing(7)
        self.form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        self.title_edit = QLineEdit()
        self.shot_size_combo = QComboBox()
        self.camera_angle_combo = QComboBox()
        self.location_combo = QComboBox()
        self.lens_combo = QComboBox()
        self.time_combo = QComboBox()
        self.lighting_combo = QComboBox()
        self.key_direction_combo = QComboBox()
        self.key_quality_combo = QComboBox()
        self.mood_edit = QLineEdit()
        self.tags_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(90)

        self.form_rows: list[tuple[QLabel, QWidget, str]] = []
        self._add_form_row("title", self.title_edit)
        self._add_form_row("shot_size", self.shot_size_combo)
        self._add_form_row("camera_angle", self.camera_angle_combo)
        self._add_form_row("location_type", self.location_combo)
        self._add_form_row("lens_type", self.lens_combo)
        self._add_form_row("time_of_day", self.time_combo)
        self._add_form_row("lighting_style", self.lighting_combo)
        self._add_form_row("key_quality", self.key_quality_combo)
        self._add_form_row("mood", self.mood_edit)
        self._add_form_row("tags", self.tags_edit)
        self._add_form_row("notes", self.notes_edit)
        scroll.setWidget(form_widget)
        inspector_layout.addWidget(scroll, 1)

        inspector_actions = QHBoxLayout()
        self.capture_delete_button = self._frame_delete_button(
            lambda _checked=False: self.delete_capture_frame(
                self.current_capture.id
                if self.current_capture
                else None
            )
        )
        self.discard_button = QPushButton()
        self.discard_button.setObjectName("Danger")
        self.discard_button.clicked.connect(self.discard_current_draft)
        self.confirm_button = QPushButton()
        self.confirm_button.setObjectName("Primary")
        self.confirm_button.clicked.connect(self.confirm_or_update)
        inspector_actions.addWidget(self.capture_delete_button)
        inspector_actions.addWidget(self.discard_button)
        inspector_actions.addWidget(self.confirm_button, 1)
        inspector_layout.addLayout(inspector_actions)
        main_splitter.addWidget(self.inspector_frame)
        self.inspector_frame.setMinimumWidth(390)
        self.inspector_frame.setMaximumWidth(470)
        main_splitter.setSizes([1160, 420])
        root.addWidget(main_splitter, 1)
        self.stack.addWidget(self.capture_page)
        self._set_inspector_enabled(False)

    def _build_gallery_page(self) -> None:
        self.gallery_page = QWidget()
        self.gallery_page.setObjectName("GalleryPage")
        root = QVBoxLayout(self.gallery_page)
        root.setContentsMargins(24, 24, 28, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        title_box = QHBoxLayout()
        title_box.setSpacing(10)
        self.gallery_workspace_title = QLabel()
        self.gallery_workspace_title.setObjectName("Title")
        self.gallery_title = QLabel()
        self.gallery_title.setObjectName("WorkspaceProjectTitle")
        self.gallery_title.setMinimumHeight(42)
        title_box.addWidget(self.gallery_workspace_title)
        title_box.addWidget(self.gallery_title)
        self.gallery_to_capture_button = QPushButton()
        self.gallery_to_capture_button.setObjectName("Primary")
        self.gallery_to_capture_button.clicked.connect(self.show_capture_workspace)
        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self.gallery_to_capture_button)
        root.addLayout(header)

        self.gallery_filters = CaptureFilterPanel(self.language)
        self.gallery_filters.changed.connect(self.refresh_gallery)
        root.addWidget(self.gallery_filters)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("WorkspaceSplitter")
        splitter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        splitter.setHandleWidth(10)
        gallery_column = QWidget()
        self.gallery_browser = gallery_column
        gallery_column.setObjectName("Transparent")
        gallery_browser_layout = QVBoxLayout(gallery_column)
        gallery_browser_layout.setContentsMargins(0, 0, 0, 0)
        gallery_browser_layout.setSpacing(12)
        gallery_browser_toolbar = QHBoxLayout()
        gallery_browser_toolbar.setContentsMargins(0, 0, 0, 0)
        self.gallery_thumbnail_grow_button = self._thumbnail_button(
            0,
            lambda _checked=False: self.change_gallery_thumbnail_size(1),
        )
        self.gallery_thumbnail_shrink_button = self._thumbnail_button(
            1,
            lambda _checked=False: self.change_gallery_thumbnail_size(-1),
        )
        self.gallery_import_image_button = QPushButton()
        self.gallery_import_image_button.setObjectName("ThumbnailImport")
        self.gallery_import_image_button.setIcon(
            QIcon(
                str(
                    Path(__file__).resolve().parents[2]
                    / "assets"
                    / "final_ui"
                    / "import-frame.svg"
                )
            )
        )
        self.gallery_import_image_button.setIconSize(QSize(31, 25))
        self.gallery_import_image_button.setMinimumHeight(36)
        self.gallery_import_image_button.clicked.connect(
            self.import_image_to_project
        )
        gallery_browser_toolbar.addWidget(
            self.gallery_thumbnail_shrink_button
        )
        self.gallery_zoom_label = QLabel()
        self.gallery_zoom_label.setObjectName("ToolbarCaption")
        gallery_browser_toolbar.addWidget(self.gallery_zoom_label)
        gallery_browser_toolbar.addWidget(
            self.gallery_thumbnail_grow_button
        )
        gallery_browser_toolbar.addSpacing(18)
        gallery_browser_toolbar.addWidget(
            self.gallery_import_image_button
        )
        gallery_browser_toolbar.addStretch()
        gallery_browser_layout.addLayout(gallery_browser_toolbar)

        gallery_list_frame = QFrame()
        gallery_list_frame.setObjectName("GalleryBrowser")
        gallery_list_layout = QVBoxLayout(gallery_list_frame)
        gallery_list_layout.setContentsMargins(12, 12, 12, 12)
        self.gallery_list = QListWidget()
        self.gallery_list.setObjectName("ThumbnailList")
        self.gallery_list.setViewMode(QListView.ViewMode.IconMode)
        self.gallery_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.gallery_list.itemClicked.connect(self._gallery_item_clicked)
        gallery_list_layout.addWidget(self.gallery_list)
        gallery_browser_layout.addWidget(gallery_list_frame, 1)
        self._apply_gallery_thumbnail_size()
        splitter.addWidget(gallery_column)

        detail = QFrame()
        self.gallery_inspector = detail
        detail.setObjectName("Inspector")
        detail.setMinimumWidth(390)
        detail.setMaximumWidth(470)
        detail_layout = QVBoxLayout(detail)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(10)
        detail_heading = QWidget()
        detail_heading.setObjectName("Transparent")
        detail_heading_layout = QHBoxLayout(detail_heading)
        detail_heading_layout.setContentsMargins(0, 0, 0, 0)
        detail_heading_layout.setSpacing(10)
        self.gallery_detail_title = QLabel()
        self.gallery_detail_title.setObjectName("DetailTitle")
        self.gallery_detail_title.setWordWrap(False)
        self.gallery_detail_time = QLabel()
        self.gallery_detail_time.setObjectName("DetailTime")
        detail_heading_layout.addWidget(self.gallery_detail_title, 1)
        detail_heading_layout.addWidget(self.gallery_detail_time)

        self.gallery_detail_image = QLabel()
        self.gallery_detail_image.setObjectName("FramePreview")
        self.gallery_detail_image.setMinimumHeight(220)
        self.gallery_detail_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gallery_detail_palette = QFrame()
        self.gallery_detail_palette.setObjectName("DetailPalette")
        self.gallery_palette_layout = QHBoxLayout(
            self.gallery_detail_palette
        )
        self.gallery_palette_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_palette_layout.setSpacing(0)
        self.gallery_palette_swatches: list[ColorSwatch] = []
        for _ in range(5):
            swatch = ColorSwatch()
            swatch.setMinimumHeight(28)
            swatch.color_clicked.connect(self.copy_color_to_clipboard)
            self.gallery_palette_layout.addWidget(swatch)
            self.gallery_palette_swatches.append(swatch)

        self.gallery_detail_scroll = QScrollArea()
        self.gallery_detail_scroll.setObjectName("DetailScroll")
        self.gallery_detail_scroll.setWidgetResizable(True)
        self.gallery_detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.gallery_detail_body = QWidget()
        self.gallery_detail_body.setObjectName("DetailBody")
        self.gallery_detail_rows_layout = QVBoxLayout(self.gallery_detail_body)
        self.gallery_detail_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_detail_rows_layout.setSpacing(8)
        self.gallery_detail_scroll.setWidget(self.gallery_detail_body)

        actions = QHBoxLayout()
        self.gallery_delete_button = self._frame_delete_button(
            lambda _checked=False: self.delete_capture_frame(
                self.current_gallery_capture.id
                if self.current_gallery_capture
                else None
            )
        )
        self.gallery_download_button = QPushButton()
        self.gallery_download_button.setObjectName("Primary")
        self.gallery_download_button.clicked.connect(self.download_gallery_frame)
        self.gallery_edit_button = QPushButton()
        self.gallery_edit_button.setObjectName("Primary")
        self.gallery_edit_button.clicked.connect(self.edit_gallery_frame)
        actions.addWidget(self.gallery_delete_button)
        actions.addWidget(self.gallery_download_button, 1)
        actions.addWidget(self.gallery_edit_button, 1)

        detail_layout.addWidget(detail_heading)
        detail_layout.addWidget(self.gallery_detail_image)
        detail_layout.addWidget(self.gallery_detail_palette)
        detail_layout.addWidget(self.gallery_detail_scroll, 1)
        detail_layout.addLayout(actions)
        splitter.addWidget(detail)
        splitter.setSizes([1160, 420])
        root.addWidget(splitter, 1)
        self.stack.addWidget(self.gallery_page)

    def _add_form_row(self, key: str, widget: QWidget) -> None:
        label = QLabel()
        label.setObjectName("FormLabel")
        self.form.addRow(label, widget)
        self.form_rows.append((label, widget, key))

    def _bind_shortcuts(self) -> None:
        self.shortcuts: list[QShortcut] = []
        for sequence, callback in (
            ("Space", self.toggle_playback),
            ("C", self.capture_current_frame),
            (QKeySequence(Qt.Key.Key_Left), lambda: self.step_frame(-1)),
            (QKeySequence(Qt.Key.Key_Right), lambda: self.step_frame(1)),
            ("J", lambda: self.seek_seconds(-5)),
            ("L", lambda: self.seek_seconds(5)),
            ("Escape", self.discard_current_draft),
        ):
            shortcut = QShortcut(
                sequence if isinstance(sequence, QKeySequence) else QKeySequence(sequence),
                self,
            )
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

    def _toggle_language(self) -> None:
        self.language = "en" if self.language == "fa" else "fa"
        self.settings.setValue("language", self.language)
        self._apply_language()

    def _set_frame_storage_mode(self, selected: str) -> None:
        if selected not in {"actual", "medium", "small"}:
            return
        if selected == self.frame_storage_mode:
            return
        if selected == "actual":
            dialog = ConfirmationDialog(
                text(self.language, "actual_size"),
                text(self.language, "actual_size_warning"),
                text(self.language, "use_actual_size"),
                self.language,
                parent=self,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                self._update_compact_controls()
                return
        self.frame_storage_mode = selected
        self.settings.setValue("frame_storage_mode", selected)
        self._update_compact_controls()

    def _update_compact_controls(self) -> None:
        storage_labels = {
            "actual": "AS",
            "medium": "M",
            "small": "S",
        }
        self.storage_button.setText(
            storage_labels.get(self.frame_storage_mode, "S")
        )
        self.language_button.setText(
            "فا" if self.language == "fa" else "EN"
        )
        self.theme_button.setText("☾" if self.theme == "dark" else "☀")

    def toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings.setValue("theme", self.theme)
        QApplication.instance().setProperty("shotlab_theme", self.theme)
        self._apply_language()

    def _apply_language(self, animate_sidebar: bool = False) -> None:
        is_fa = self.language == "fa"
        direction = (
            Qt.LayoutDirection.RightToLeft
            if is_fa
            else Qt.LayoutDirection.LeftToRight
        )
        # Keep the application shell physically left-to-right so the Sidebar
        # remains on the left. Only the page contents follow the language.
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.central_shell.setLayoutDirection(
            Qt.LayoutDirection.LeftToRight
        )
        application = QApplication.instance()
        if application is not None:
            application.setFont(
                QFont("Vazirmatn" if is_fa else "Inter", 10)
            )
        self.setStyleSheet(stylesheet(self.theme, self.language))
        for button in (
            self.nav_projects,
            self.nav_capture,
            self.nav_gallery,
            self.pdf_export_button,
            self.export_button,
            self.import_button,
        ):
            button.setStyleSheet(
                "text-align: center;"
                if self.sidebar_collapsed
                else "text-align: left;"
            )
        # The Sidebar keeps the approved English visual structure in both
        # languages: icons remain on the left and only the copy is translated.
        # Individual workspace pages still switch their text flow for Persian.
        self.shell_layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.sidebar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.stack.setLayoutDirection(direction)
        self.library_page.setLayoutDirection(direction)
        self.capture_page.setLayoutDirection(direction)
        self.gallery_page.setLayoutDirection(direction)
        self.capture_content.setLayoutDirection(direction)
        self.inspector_frame.setLayoutDirection(direction)
        self.gallery_browser.setLayoutDirection(direction)
        self.gallery_inspector.setLayoutDirection(direction)
        self.library_title.setText(
            f"{text(self.language, 'projects')} >"
        )
        self.new_project_button.setText(text(self.language, "new_project"))
        self.new_project_button.setToolTip(text(self.language, "new_project"))
        self.library_filters.set_language(self.language)
        self.search_results_title.setText(text(self.language, "search_results"))
        self.search_zoom_label.setText(text(self.language, "zoom"))
        self.search_thumbnail_grow_button.setToolTip(
            text(self.language, "increase_thumbnail_size")
        )
        self.search_thumbnail_shrink_button.setToolTip(
            text(self.language, "decrease_thumbnail_size")
        )
        self.no_search_results_label.setText(text(self.language, "no_search_results"))
        self.capture_to_gallery_button.setText(
            text(self.language, "gallery")
        )
        self.capture_to_gallery_button.setToolTip(
            text(self.language, "gallery")
        )
        self._update_video_toolbar()
        self.capture_button.setText(f"{text(self.language, 'capture')} (C)")
        self.capture_button.setToolTip(text(self.language, "capture"))
        self.play_button.setToolTip(text(self.language, "play"))
        self.pause_button.setToolTip(text(self.language, "pause"))
        self.back_frame_button.setToolTip(text(self.language, "previous_frame"))
        self.forward_frame_button.setToolTip(text(self.language, "next_frame"))
        self.inspector_title.setText(text(self.language, "shot_information"))
        self.video_empty_label.setText(text(self.language, "load_video_help"))
        self.palette_caption.setText(text(self.language, "color_palette"))
        self.captures_title.setText(text(self.language, "confirmed_frames"))
        self.capture_zoom_label.setText(text(self.language, "zoom"))
        self.capture_thumbnail_grow_button.setToolTip(
            text(self.language, "increase_thumbnail_size")
        )
        self.capture_thumbnail_shrink_button.setToolTip(
            text(self.language, "decrease_thumbnail_size")
        )
        self.capture_import_image_button.setToolTip(
            text(self.language, "import_image")
        )
        self.capture_import_image_button.setText(
            text(self.language, "import_image")
        )
        self.gallery_import_image_button.setText(
            text(self.language, "import_image")
        )
        self.gallery_import_image_button.setToolTip(
            text(self.language, "import_image")
        )
        self.capture_delete_button.setToolTip(
            text(self.language, "delete_frame")
        )
        self.discard_button.setText(text(self.language, "discard"))
        self.discard_button.setToolTip(text(self.language, "discard"))
        self.confirm_button.setText(
            text(
                self.language,
                "save_changes" if self.current_capture else "confirm",
            )
        )
        self.confirm_button.setToolTip(self.confirm_button.text())
        for label, _, key in self.form_rows:
            label.setText(text(self.language, key))
        self.sidebar_navigation_label.setText(text(self.language, "navigation"))
        self.sidebar_data_label.setText(text(self.language, "data_repository"))
        self.storage_caption.setText(text(self.language, "storing_size"))
        self.storage_actions["actual"].setText(
            f"{text(self.language, 'actual_size')}   AS"
        )
        self.storage_actions["medium"].setText(
            f"{text(self.language, 'medium_size')}   M"
        )
        self.storage_actions["small"].setText(
            f"{text(self.language, 'small_size')}   S"
        )
        self._update_compact_controls()
        self.storage_button.setToolTip(
            text(self.language, "frame_storage_size")
        )
        self.language_button.setToolTip(text(self.language, "language"))
        self.collapse_sidebar_button.setToolTip(
            text(
                self.language,
                "show_sidebar" if self.sidebar_collapsed else "hide_sidebar",
            )
        )
        self.nav_projects.setToolTip(text(self.language, "projects"))
        self.nav_capture.setToolTip(text(self.language, "capture_workspace"))
        self.nav_gallery.setToolTip(text(self.language, "gallery"))
        self.pdf_export_button.setToolTip(
            text(self.language, "export_pdf")
        )
        self.export_button.setToolTip(text(self.language, "export_database"))
        self.import_button.setToolTip(text(self.language, "import_database"))
        self.nav_projects.setText(text(self.language, "projects"))
        self.nav_capture.setText(text(self.language, "capture_workspace"))
        self.nav_gallery.setText(text(self.language, "gallery"))
        self.pdf_export_button.setText(text(self.language, "export_pdf"))
        self.export_button.setText(text(self.language, "export_database"))
        self.import_button.setText(text(self.language, "import_database"))
        self.developer_label.setText("Developed by: StoryEco.com")
        self.version_label.setText(f"ShotLab v{__version__}")
        self.theme_button.setToolTip(
            text(
                self.language,
                "light_mode" if self.theme == "dark" else "dark_mode",
            )
        )
        self._update_workspace_headings()
        self.gallery_to_capture_button.setText(text(self.language, "capture_workspace"))
        self.gallery_to_capture_button.setToolTip(
            text(self.language, "capture_workspace")
        )
        self.gallery_filters.set_language(self.language)
        self.gallery_zoom_label.setText(text(self.language, "zoom"))
        self.gallery_thumbnail_grow_button.setToolTip(
            text(self.language, "increase_thumbnail_size")
        )
        self.gallery_thumbnail_shrink_button.setToolTip(
            text(self.language, "decrease_thumbnail_size")
        )
        self.gallery_detail_title.setText(
            text(self.language, "shot_information")
        )
        self.gallery_download_button.setText(text(self.language, "download_frame"))
        self.gallery_download_button.setToolTip(
            text(self.language, "download_frame")
        )
        self.gallery_edit_button.setText(text(self.language, "edit_frame"))
        self.gallery_edit_button.setToolTip(text(self.language, "edit_frame"))
        self.gallery_delete_button.setToolTip(
            text(self.language, "delete_frame")
        )
        self._apply_sidebar_state(animated=animate_sidebar)
        self._rebuild_option_combos()
        self.refresh_projects()
        if self.current_gallery_capture:
            self.show_gallery_capture(self.current_gallery_capture.id)
        else:
            self._clear_gallery_detail()

    def _rebuild_option_combos(self) -> None:
        mapping = {
            "shot_size": self.shot_size_combo,
            "camera_angle": self.camera_angle_combo,
            "location_type": self.location_combo,
            "lens_type": self.lens_combo,
            "time_of_day": self.time_combo,
            "lighting_style": self.lighting_combo,
            "key_direction": self.key_direction_combo,
            "key_quality": self.key_quality_combo,
        }
        for key, combo in mapping.items():
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            for value, fa_label, en_label in OPTIONS[key]:
                combo.addItem(
                    option_label(self.language, key, value),
                    value,
                )
            index = combo.findData(current)
            combo.setCurrentIndex(max(index, 0))
            combo.blockSignals(False)

    def _project_column_count(self) -> int:
        if not hasattr(self, "projects_scroll"):
            return 1
        available_width = max(
            ProjectCard.CARD_WIDTH,
            self.projects_scroll.viewport().width(),
        )
        spacing = max(0, self.project_grid.horizontalSpacing())
        return max(
            1,
            (available_width + spacing)
            // (ProjectCard.CARD_WIDTH + spacing),
        )

    def _reflow_project_cards(self) -> None:
        if not hasattr(self, "project_grid"):
            return
        while self.project_grid.count():
            self.project_grid.takeAt(0)
        columns = self._project_column_count()
        if self._project_empty_state is not None:
            self.project_grid.addWidget(
                self._project_empty_state,
                0,
                0,
                1,
                columns,
            )
            return
        for index, card in enumerate(self._project_cards):
            self.project_grid.addWidget(
                card,
                index // columns,
                index % columns,
            )

    def refresh_projects(self) -> None:
        if not hasattr(self, "project_grid"):
            return
        while self.project_grid.count():
            item = self.project_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._project_cards = []
        self._project_empty_state = None
        projects = self.repository.list_projects()
        self.project_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop
            | (
                Qt.AlignmentFlag.AlignRight
                if self.language == "fa"
                else Qt.AlignmentFlag.AlignLeft
            )
        )
        if not projects:
            empty = QLabel(text(self.language, "no_projects"))
            empty.setObjectName("EmptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(240)
            self._project_empty_state = empty
        for index, project in enumerate(projects):
            card = ProjectCard(
                project,
                self.repository.project_thumbnails(project.id, 4),
                self.repository.project_palette(project.id, 5),
                self.language,
            )
            card.open_timeline.connect(self.open_project)
            card.open_gallery.connect(self.open_gallery)
            card.rename_requested.connect(self.rename_project)
            card.delete_requested.connect(self.delete_project)
            self._project_cards.append(card)
        self._reflow_project_cards()
        QTimer.singleShot(0, self._reflow_project_cards)
        has_project_destination = self.current_project is not None or bool(projects)
        self.nav_capture.setEnabled(has_project_destination)
        self.nav_gallery.setEnabled(has_project_destination)

    def create_project(self) -> None:
        dialog = NewProjectDialog(self.language, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            project = self.repository.create_project(dialog.project_name)
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.refresh_projects()
        self.show_status(text(self.language, "project_created"), 3000)
        self.open_project(project.id)

    def rename_project(self, project_id: str) -> None:
        project = self.repository.get_project(project_id)
        if not project:
            return
        dialog = NewProjectDialog(
            self.language,
            self,
            initial_name=project.name,
            rename=True,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            updated = self.repository.rename_project(
                project_id,
                dialog.project_name,
            )
        except Exception as exc:
            self.show_error(str(exc))
            return
        if self.current_project and self.current_project.id == project_id:
            self.current_project = updated
            self._update_workspace_headings()
        self.refresh_projects()
        self.show_status(
            text(self.language, "project_renamed"),
            3000,
        )

    def delete_project(self, project_id: str) -> None:
        project = self.repository.get_project(project_id)
        if not project:
            return
        if (
            self.current_project
            and self.current_project.id == project_id
            and self._capture_worker
        ):
            self.show_status(
                text(self.language, "project_busy"),
                3500,
            )
            return
        dialog = ConfirmationDialog(
            text(self.language, "delete_project"),
            text(
                self.language,
                "delete_project_question",
                name=project.name,
            ),
            text(self.language, "delete_project"),
            self.language,
            destructive=True,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.repository.delete_project(project_id)
        except Exception as exc:
            self.show_error(str(exc))
            return
        if str(self.settings.value("last_project_id", "") or "") == project_id:
            self.settings.remove("last_project_id")
        self.settings.remove(self._video_path_key(project_id))

        if self.current_project and self.current_project.id == project_id:
            self.player.stop()
            self.player.setSource(QUrl())
            self.session.close_project()
            self.current_project = None
            self.current_capture = None
            self.current_draft = None
            self.current_gallery_capture = None
            self._displayed_frame = QImage()
            self.timeline.setRange(0, 0)
            self.timeline.set_markers([])
        self.show_projects()
        self.show_status(
            text(self.language, "project_deleted"),
            4000,
        )

    def _global_search_changed(self) -> None:
        if not self.library_filters.has_criteria():
            self._last_search_capture_ids = []
            self.library_content_stack.setCurrentWidget(self.projects_scroll)
            return
        self.library_content_stack.setCurrentIndex(1)
        results = self.repository.filter_captures(
            query=self.library_filters.query(),
            filters=self.library_filters.filters(),
            color_hex=self.library_filters.selected_color(),
        )
        self._last_search_capture_ids = [
            capture.id for capture in results
        ]
        self.global_results_list.clear()
        for capture in results:
            project = self.repository.get_project(capture.project_id)
            project_name = project.name if project else ""
            title = capture.editorial.get("title") or f"Capture {capture.capture_number}"
            item = QListWidgetItem(f"{title}  ·  {project_name}")
            item.setToolTip(f"{title} · {project_name}")
            image = self.repository.resolve_project_file(
                capture.project_id,
                capture.thumbnail_rel_path,
            )
            item.setIcon(
                self._thumbnail_icon(
                    image,
                    self.global_results_list.iconSize(),
                )
            )
            item.setData(Qt.ItemDataRole.UserRole, capture.id)
            self.global_results_list.addItem(item)
        self.no_search_results_label.setVisible(not bool(results))

    def _global_result_clicked(self, item: QListWidgetItem) -> None:
        capture = self.repository.get_capture(
            str(item.data(Qt.ItemDataRole.UserRole))
        )
        if not capture:
            return
        self.open_gallery(capture.project_id)
        self.show_gallery_capture(capture.id)

    def refresh_gallery(self) -> None:
        self.gallery_list.clear()
        self.current_gallery_capture = None
        self._clear_gallery_detail()
        if not self.current_project:
            return
        captures = self.repository.filter_captures(
            query=self.gallery_filters.query(),
            filters=self.gallery_filters.filters(),
            project_id=self.current_project.id,
            color_hex=self.gallery_filters.selected_color(),
        )
        self._last_gallery_capture_ids = [
            capture.id for capture in captures
        ]
        fps = self.session.video.metadata.fps if self.session.video else 24.0
        for capture in captures:
            title = capture.editorial.get("title") or f"Capture {capture.capture_number}"
            timecode = self._capture_time_label(capture, fps)
            item = QListWidgetItem(f"{title}  ·  {timecode}")
            item.setToolTip(f"{title} · {timecode}")
            image = self.repository.resolve_project_file(
                capture.project_id,
                capture.thumbnail_rel_path,
            )
            item.setIcon(
                self._thumbnail_icon(
                    image,
                    self.gallery_list.iconSize(),
                )
            )
            item.setData(Qt.ItemDataRole.UserRole, capture.id)
            self.gallery_list.addItem(item)

    def _gallery_item_clicked(self, item: QListWidgetItem) -> None:
        self.show_gallery_capture(str(item.data(Qt.ItemDataRole.UserRole)))

    def _clear_gallery_detail_rows(self) -> None:
        while self.gallery_detail_rows_layout.count():
            item = self.gallery_detail_rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _set_gallery_detail_rows(
        self,
        entries: list[tuple[str, str]],
        notes: str | None = None,
    ) -> None:
        self._clear_gallery_detail_rows()

        if entries:
            title_label, title_value = entries[0]
            row = QFrame()
            row.setObjectName("DetailRow")
            row.setMinimumHeight(38)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 0, 10, 0)
            row_layout.setSpacing(10)
            key_label = QLabel(title_label)
            key_label.setObjectName("DetailKey")
            value_label = QLabel(title_value)
            value_label.setObjectName("DetailValue")
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            row_layout.addWidget(key_label)
            row_layout.addWidget(value_label, 1)
            self.gallery_detail_rows_layout.addWidget(row)

        metadata_entries = entries[1:9]
        if metadata_entries:
            metadata_grid = QWidget()
            metadata_grid.setObjectName("Transparent")
            grid = QGridLayout(metadata_grid)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(8)
            for index, (label_text, value_text) in enumerate(metadata_entries):
                value = QLabel(value_text or "—")
                value.setObjectName("DetailValueBox")
                value.setToolTip(label_text)
                value.setFixedHeight(38)
                value.setAlignment(
                    Qt.AlignmentFlag.AlignLeading
                    | Qt.AlignmentFlag.AlignVCenter
                )
                grid.addWidget(value, index // 2, index % 2)
            self.gallery_detail_rows_layout.addWidget(metadata_grid)

        for label_text, value_text in entries[9:]:
            row = QFrame()
            row.setObjectName("DetailRow")
            row.setMinimumHeight(38)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 0, 10, 0)
            row_layout.setSpacing(10)
            key_label = QLabel(label_text)
            key_label.setObjectName("DetailKey")
            value_label = QLabel(value_text)
            value_label.setObjectName("DetailValue")
            value_label.setWordWrap(True)
            row_layout.addWidget(key_label)
            row_layout.addWidget(value_label, 1)
            self.gallery_detail_rows_layout.addWidget(row)

        if notes is not None:
            notes_frame = QFrame()
            notes_frame.setObjectName("DetailNotes")
            notes_layout = QVBoxLayout(notes_frame)
            notes_layout.setContentsMargins(10, 7, 10, 8)
            notes_layout.setSpacing(4)
            notes_title = QLabel(text(self.language, "notes"))
            notes_title.setObjectName("DetailKey")
            notes_value = QLabel(notes or "—")
            notes_value.setObjectName("DetailNotesValue")
            notes_value.setWordWrap(True)
            notes_value.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            notes_layout.addWidget(notes_title)
            notes_layout.addWidget(notes_value)
            self.gallery_detail_rows_layout.addWidget(notes_frame)

        if not entries and notes is None:
            empty = QLabel(text(self.language, "no_frame_metadata"))
            empty.setObjectName("DetailEmpty")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(76)
            self.gallery_detail_rows_layout.addWidget(empty)

        self.gallery_detail_rows_layout.addStretch()

    def show_gallery_capture(self, capture_id: str) -> None:
        capture = self.repository.get_capture(capture_id)
        if not capture:
            return
        capture = self._ensure_palette_percentages(capture)
        self.current_gallery_capture = capture
        self.gallery_delete_button.setVisible(True)
        self.gallery_download_button.setEnabled(True)
        self.gallery_edit_button.setEnabled(True)
        title = capture.editorial.get("title") or f"Capture {capture.capture_number}"
        self.gallery_detail_title.setText(
            text(self.language, "shot_information")
        )
        self.gallery_detail_title.setToolTip(title)
        fps = self.session.video.metadata.fps if self.session.video else 24.0
        self.gallery_detail_time.setText(
            self._capture_time_label(capture, fps)
        )
        image_path = self.repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
        pixmap = QPixmap(str(image_path))
        self.gallery_detail_image.setPixmap(
            pixmap.scaled(
                self.gallery_detail_image.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self._apply_palette_analysis(
            self.gallery_palette_swatches,
            self.gallery_palette_layout,
            capture.analysis,
        )

        entries: list[tuple[str, str]] = [
            (text(self.language, "title"), str(title))
        ]
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
            entries.append(
                (
                    text(self.language, key),
                    option_label(self.language, key, value)
                    if value
                    else "",
                )
            )
        mood_values = capture.editorial.get("mood", [])
        entries.append(
            (
                text(self.language, "mood"),
                (
                    "، ".join(mood_values)
                    if self.language == "fa"
                    else ", ".join(mood_values)
                ),
            )
        )
        tag_values = capture.editorial.get("tags", [])
        entries.append(
            (
                text(self.language, "tags"),
                (
                    "، ".join(tag_values)
                    if self.language == "fa"
                    else ", ".join(tag_values)
                ),
            )
        )
        self._set_gallery_detail_rows(
            entries,
            str(capture.editorial.get("notes") or ""),
        )

    def _clear_gallery_detail(self) -> None:
        if not hasattr(self, "gallery_detail_image"):
            return
        self.gallery_detail_image.clear()
        self.gallery_detail_title.setText(
            text(self.language, "shot_information")
        )
        self.gallery_detail_time.clear()
        self.gallery_delete_button.setVisible(False)
        self.gallery_download_button.setEnabled(False)
        self.gallery_edit_button.setEnabled(False)
        self._set_gallery_detail_rows([])
        for swatch in self.gallery_palette_swatches:
            swatch.set_color("")

    def download_gallery_frame(self) -> None:
        capture = self.current_gallery_capture
        if not capture:
            return
        source = self.repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
        default_name = Path(capture.image_rel_path).name
        destination, _ = QFileDialog.getSaveFileName(
            self,
            text(self.language, "download_frame"),
            default_name,
            "JPEG Image (*.jpg)",
        )
        if not destination:
            return
        try:
            shutil.copy2(source, destination)
        except Exception as exc:
            self.show_error(str(exc))

    def edit_gallery_frame(self) -> None:
        if not self.current_gallery_capture:
            return
        capture_id = self.current_gallery_capture.id
        self.show_capture_workspace()
        self.open_capture_by_id(capture_id)

    def delete_capture_frame(self, capture_id: str | None) -> None:
        if not capture_id:
            return
        capture = self.repository.get_capture(capture_id)
        if not capture:
            return
        title = (
            capture.editorial.get("title")
            or f"Capture {capture.capture_number}"
        )
        dialog = ConfirmationDialog(
            text(self.language, "delete_frame"),
            text(
                self.language,
                "delete_frame_question",
                name=title,
            ),
            text(self.language, "delete_frame"),
            self.language,
            destructive=True,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.repository.delete_capture(capture.id)
        except Exception as exc:
            self.show_error(str(exc))
            return

        if self.current_capture and self.current_capture.id == capture.id:
            self.current_capture = None
            self._set_inspector_enabled(False)
        if (
            self.current_gallery_capture
            and self.current_gallery_capture.id == capture.id
        ):
            self.current_gallery_capture = None
            self._clear_gallery_detail()
        self.refresh_captures()
        if self.current_project:
            self.refresh_gallery()
        self.refresh_projects()
        self.show_status(
            text(self.language, "frame_deleted"),
            3500,
        )

    def _pdf_scope_captures(self, scope: str) -> list[Capture]:
        if scope == "all":
            captures: list[Capture] = []
            for project in self.repository.list_projects():
                captures.extend(
                    self.repository.list_captures(project.id)
                )
            return captures
        if scope == "active":
            project = self.current_project or self._last_project_candidate()
            return (
                self.repository.list_captures(project.id)
                if project
                else []
            )
        capture_ids = (
            self._last_search_capture_ids
            if self.stack.currentWidget() is self.library_page
            else self._last_gallery_capture_ids
        )
        return [
            capture
            for capture_id in capture_ids
            if (capture := self.repository.get_capture(capture_id))
            is not None
        ]

    def export_pdf(self) -> None:
        dialog = PdfExportDialog(self.language, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        captures = self._pdf_scope_captures(dialog.scope)
        if not captures:
            self.show_status(text(self.language, "pdf_no_frames"), 3500)
            return
        destination, _ = QFileDialog.getSaveFileName(
            self,
            text(self.language, "pdf_choose_destination"),
            "ShotLab_Reference.pdf",
            "PDF Document (*.pdf)",
        )
        if not destination:
            return
        output_path = Path(destination)
        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")
        fps = (
            self.session.video.metadata.fps
            if self.session.video
            else 24.0
        )
        try:
            count = export_captures_pdf(
                output_path,
                captures,
                self.repository,
                self.language,
                dialog.columns,
                Path(__file__).resolve().parents[2] / "assets",
                fps,
            )
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.show_status(
            text(self.language, "pdf_export_done", count=count),
            4500,
        )

    def export_database(self) -> None:
        destination, _ = QFileDialog.getSaveFileName(
            self,
            text(self.language, "choose_export"),
            "ShotLab_Library.shotlab",
            "ShotLab Library (*.shotlab)",
        )
        if not destination:
            return
        try:
            export_library(self.repository, Path(destination))
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.show_status(text(self.language, "export_done"), 4000)

    def import_database(self) -> None:
        archive, _ = QFileDialog.getOpenFileName(
            self,
            text(self.language, "choose_import"),
            "",
            "ShotLab Library (*.shotlab)",
        )
        if not archive:
            return
        dialog = ConfirmationDialog(
            text(self.language, "import_database"),
            text(self.language, "import_warning"),
            text(self.language, "import_database"),
            self.language,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.player.stop()
            self.player.setSource(QUrl())
            self.session.close_project()
            restore_library(self.repository, Path(archive))
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.current_project = None
        self.current_capture = None
        self.current_draft = None
        self.current_gallery_capture = None
        self.library_filters.clear()
        self.gallery_filters.clear()
        self.show_projects()
        self.show_status(text(self.language, "import_done"), 4000)

    def _last_project_candidate(self) -> Project | None:
        saved_id = str(self.settings.value("last_project_id", "") or "")
        if saved_id:
            saved_project = self.repository.get_project(saved_id)
            if saved_project:
                return saved_project
        projects = self.repository.list_projects()
        return projects[0] if projects else None

    def _update_workspace_headings(self) -> None:
        project_name = (
            self.current_project.name
            if self.current_project
            else ""
        )
        capture_title = text(self.language, "capture_workspace")
        gallery_title = text(self.language, "gallery")
        self.capture_workspace_title.setText(f"{capture_title} >")
        self.project_title_label.setText(project_name)
        self.gallery_workspace_title.setText(f"{gallery_title} >")
        self.gallery_title.setText(project_name)

    def _remember_project(self, project_id: str) -> None:
        self.settings.setValue("last_project_id", project_id)

    @staticmethod
    def _video_path_key(project_id: str) -> str:
        return f"video_paths/{project_id}"

    def _saved_video_path(self, project_id: str) -> Path | None:
        raw_path = str(
            self.settings.value(
                self._video_path_key(project_id),
                "",
            )
            or ""
        ).strip()
        return Path(raw_path) if raw_path else None

    def _remember_video_path(self, project_id: str, path: Path) -> None:
        self.settings.setValue(
            self._video_path_key(project_id),
            str(path.resolve()),
        )
        self.settings.sync()

    def _update_video_toolbar(self) -> None:
        if not hasattr(self, "video_button"):
            return
        has_active_video = bool(
            self.current_project
            and self.session.video
            and self.session.project_id == self.current_project.id
        )
        if hasattr(self, "video_empty_label"):
            self.video_empty_label.setVisible(not has_active_video)
        if not self.current_project:
            self.session_notice.clear()
            self.session_notice.hide()
            self.video_button.setText(text(self.language, "select_video"))
            self.video_button.setToolTip(self.video_button.text())
            return

        if (
            self.session.video
            and self.session.project_id == self.current_project.id
        ):
            path_text = str(self.session.video.path)
            self.session_notice.setText(path_text)
            self.session_notice.setToolTip(path_text)
            self.session_notice.show()
            self.video_button.setText(text(self.language, "change_video"))
            self.video_button.setToolTip(self.video_button.text())
            return

        project = (
            self.repository.get_project(self.current_project.id)
            or self.current_project
        )
        saved_path = self._saved_video_path(project.id)
        fresh_and_empty = (
            saved_path is None
            and project.source_fingerprint is None
            and project.capture_count == 0
        )
        if fresh_and_empty:
            self.session_notice.clear()
            self.session_notice.setToolTip("")
            self.session_notice.hide()
        else:
            self.session_notice.setText(
                text(self.language, "video_not_found_previous")
            )
            self.session_notice.setToolTip(
                str(saved_path) if saved_path else ""
            )
            self.session_notice.show()
        self.video_button.setText(text(self.language, "select_video"))
        self.video_button.setToolTip(self.video_button.text())

    def _activate_video_source(
        self,
        path: Path,
        metadata,
        autoplay: bool,
    ) -> None:
        resolved_path = path.resolve()
        self.player.setSource(
            QUrl.fromLocalFile(str(resolved_path))
        )
        self._displayed_frame = QImage()
        self._displayed_frame_time_ms = 0
        self.timeline.setRange(0, metadata.duration_ms)
        self.timeline.setValue(0)
        self.timecode_label.setText(
            f"{format_timecode(0, metadata.fps)} / "
            f"{format_timecode(metadata.duration_ms, metadata.fps)}"
        )
        self._update_video_toolbar()
        if autoplay:
            self.player.play()

    def _restore_saved_video(self) -> bool:
        if not self.current_project:
            self._update_video_toolbar()
            return False
        if (
            self.session.video
            and self.session.project_id == self.current_project.id
        ):
            self._update_video_toolbar()
            return True

        saved_path = self._saved_video_path(self.current_project.id)
        if not saved_path or not saved_path.is_file():
            self._update_video_toolbar()
            return False
        try:
            metadata = self.session.attach_video(saved_path)
        except Exception:
            self._update_video_toolbar()
            return False
        self._activate_video_source(
            saved_path,
            metadata,
            autoplay=False,
        )
        return True

    def _ensure_project_context(self) -> bool:
        if self.current_project:
            project = self.repository.get_project(self.current_project.id)
            if project:
                self.current_project = project
                if self.session.project_id != project.id:
                    self.session.open_project(project.id)
                if not self.session.video:
                    self._restore_saved_video()
                return True
            self.current_project = None

        project = self._last_project_candidate()
        if not project:
            return False
        try:
            self.current_project = self.session.open_project(project.id)
        except Exception as exc:
            self.show_error(str(exc))
            return False
        self.current_draft = None
        self.current_capture = None
        self.current_gallery_capture = None
        self._update_workspace_headings()
        self._remember_project(self.current_project.id)
        self._restore_saved_video()
        return True

    def open_project(self, project_id: str) -> None:
        try:
            self.current_project = self.session.open_project(project_id)
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.current_draft = None
        self.current_capture = None
        self.current_gallery_capture = None
        self._displayed_frame = QImage()
        self._displayed_frame_time_ms = 0
        self._remember_project(self.current_project.id)
        self._update_workspace_headings()
        self.player.stop()
        self.player.setSource(QUrl())
        self.timeline.setRange(0, 0)
        self.timeline.setValue(0)
        self.timecode_label.setText("00:00:00:00 / 00:00:00:00")
        self._set_inspector_enabled(False)
        self._restore_saved_video()
        self.refresh_captures()
        self._apply_language()
        self.stack.setCurrentWidget(self.capture_page)
        self._set_active_nav(self.nav_capture)

    def open_gallery(self, project_id: str) -> None:
        if not self.current_project or self.current_project.id != project_id:
            try:
                self.current_project = self.session.open_project(project_id)
            except Exception as exc:
                self.show_error(str(exc))
                return
        self._remember_project(self.current_project.id)
        self._update_workspace_headings()
        self.refresh_gallery()
        self.stack.setCurrentWidget(self.gallery_page)
        self._set_active_nav(self.nav_gallery)

    def show_projects(self) -> None:
        self.refresh_projects()
        self.stack.setCurrentWidget(self.library_page)
        self._set_active_nav(self.nav_projects)

    def show_capture_workspace(self) -> None:
        if not self._ensure_project_context():
            self.show_status(text(self.language, "select_project"), 2500)
            return
        self._update_workspace_headings()
        self.refresh_captures()
        self._update_video_toolbar()
        self.stack.setCurrentWidget(self.capture_page)
        self._set_active_nav(self.nav_capture)

    def show_current_gallery(self) -> None:
        if not self._ensure_project_context():
            self.show_status(text(self.language, "select_project"), 2500)
            return
        self.open_gallery(self.current_project.id)

    def _set_active_nav(self, active: QPushButton) -> None:
        for button in (
            self.nav_projects,
            self.nav_capture,
            self.nav_gallery,
        ):
            button.setChecked(button is active)

    def back_to_library(self) -> None:
        self.show_projects()

    def select_session_video(self) -> None:
        if not self.current_project:
            return
        saved_path = self._saved_video_path(self.current_project.id)
        start_directory = (
            str(saved_path.parent)
            if saved_path and saved_path.parent.exists()
            else ""
        )
        path, _ = QFileDialog.getOpenFileName(
            self,
            text(self.language, "select_video"),
            start_directory,
            text(self.language, "video_filter"),
        )
        if not path:
            return
        try:
            metadata = self.session.attach_video(Path(path))
        except ValueError as exc:
            if str(exc) != "SOURCE_FINGERPRINT_MISMATCH":
                self.show_error(str(exc))
                return
            dialog = ConfirmationDialog(
                text(self.language, "warning"),
                text(self.language, "source_mismatch"),
                text(self.language, "yes"),
                self.language,
                parent=self,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            try:
                metadata = self.session.attach_video(Path(path), allow_mismatch=True)
            except Exception as mismatch_exc:
                self.show_error(str(mismatch_exc))
                return
        except Exception as exc:
            self.show_error(str(exc))
            return

        selected_path = Path(path).resolve()
        self._remember_video_path(
            self.current_project.id,
            selected_path,
        )
        self._activate_video_source(
            selected_path,
            metadata,
            autoplay=True,
        )
        self.show_status(text(self.language, "video_attached"), 4000)

    def toggle_playback(self) -> None:
        if self.stack.currentWidget() is not self.capture_page or not self.session.video:
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def play_video(self) -> None:
        if self.stack.currentWidget() is not self.capture_page or not self.session.video:
            self.play_button.setChecked(False)
            return
        self.player.play()
        self.play_button.setChecked(True)

    def pause_playback(self) -> None:
        if not self.session.video:
            return
        self.player.pause()

    def _playback_changed(self, state) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.play_button.setChecked(playing)

    def _duration_changed(self, duration: int) -> None:
        if duration > 0:
            self.timeline.setMaximum(duration)

    def _position_changed(self, position: int) -> None:
        if not self.timeline.isSliderDown():
            self.timeline.setValue(position)
        fps = self.session.video.metadata.fps if self.session.video else 24.0
        duration = (
            self.session.video.metadata.duration_ms if self.session.video else 0
        )
        self.timecode_label.setText(
            f"{format_timecode(position, fps)} / {format_timecode(duration, fps)}"
        )
        if not self.current_capture and not self.current_draft:
            self.inspector_time.setText(format_timecode(position, fps))

    def step_frame(self, direction: int) -> None:
        if not self.session.video:
            return
        self.player.pause()
        frame_ms = max(1, round(1000 / max(self.session.video.metadata.fps, 1)))
        self.player.setPosition(
            max(
                0,
                min(
                    self.player.position() + direction * frame_ms,
                    self.session.video.metadata.duration_ms,
                ),
            )
        )

    def seek_seconds(self, seconds: int) -> None:
        if not self.session.video:
            return
        self.player.setPosition(
            max(
                0,
                min(
                    self.player.position() + seconds * 1000,
                    self.session.video.metadata.duration_ms,
                ),
            )
        )

    def import_image_to_project(self) -> None:
        if not self.current_project:
            self.show_status(text(self.language, "select_project"), 2500)
            return
        if self.current_draft or self._capture_worker:
            self.show_status(
                text(self.language, "finish_current_draft"),
                3500,
            )
            return
        source, _ = QFileDialog.getOpenFileName(
            self,
            text(self.language, "import_image"),
            "",
            text(self.language, "image_filter"),
        )
        if not source:
            return
        try:
            self.player.pause()
            draft = self.session.create_draft_from_image(
                Path(source),
                self.frame_storage_mode,
            )
        except Exception as exc:
            self.show_error(str(exc))
            return
        self._draft_ready(draft)
        self.show_status(
            text(self.language, "image_ready_for_review"),
            3500,
        )

    def capture_current_frame(self) -> None:
        if (
            self.stack.currentWidget() is not self.capture_page
            or not self.session.video
            or self.current_draft
            or self._capture_worker
        ):
            return
        if self._displayed_frame.isNull():
            self.show_status(
                text(self.language, "frame_not_ready"),
                3000,
            )
            return
        displayed_image = self._displayed_frame.copy()
        capture_time = self._displayed_frame_time_ms
        self.player.pause()
        self.capture_button.setEnabled(False)
        self.capture_button.setText(text(self.language, "processing"))
        displayed_path = (
            self.repository.data_root
            / "cache"
            / f"displayed_{uuid.uuid4().hex}.jpg"
        )
        if not displayed_image.save(str(displayed_path), "JPG", 96):
            self.capture_button.setEnabled(True)
            self.capture_button.setText(f"{text(self.language, 'capture')} (C)")
            self.show_error(text(self.language, "frame_save_failed"))
            return
        worker = CaptureWorker(
            self.session,
            capture_time,
            displayed_path,
            self.frame_storage_mode,
        )
        self._capture_worker = worker
        worker.signals.finished.connect(self._draft_ready)
        worker.signals.failed.connect(self._capture_failed)
        self.thread_pool.start(worker)

    @Slot(object)
    def _video_frame_changed(self, frame) -> None:
        if not frame or not frame.isValid():
            return
        image = frame.toImage()
        if image.isNull():
            return
        self._displayed_frame = image.copy()
        start_time_us = frame.startTime()
        self._displayed_frame_time_ms = (
            start_time_us // 1000
            if start_time_us is not None and start_time_us >= 0
            else self.player.position()
        )

    @Slot(object)
    def _draft_ready(self, draft: CaptureDraft) -> None:
        self._capture_worker = None
        self.capture_button.setEnabled(True)
        self.capture_button.setText(f"{text(self.language, 'capture')} (C)")
        self.current_draft = draft
        self.current_capture = None
        self._show_image(Path(draft.image_path))
        self._show_analysis(draft.analysis)
        self._populate_editor(draft.editorial)
        self._set_inspector_enabled(True)
        draft_position = (
            text(self.language, "imported_image")
            if draft.source_pts is None
            else format_timecode(
                draft.source_time_ms,
                self.session.video.metadata.fps
                if self.session.video
                else 24.0,
            )
        )
        self.inspector_title.setText(
            text(self.language, "shot_information")
        )
        self.inspector_time.setText(draft_position)
        self.confirm_button.setText(text(self.language, "confirm"))
        self.discard_button.setVisible(True)
        self.capture_delete_button.setVisible(False)
        self.stack.setCurrentWidget(self.capture_page)
        self._set_active_nav(self.nav_capture)

    @Slot(str)
    def _capture_failed(self, message: str) -> None:
        self._capture_worker = None
        self.capture_button.setEnabled(True)
        self.capture_button.setText(f"{text(self.language, 'capture')} (C)")
        self.show_error(message)

    def confirm_or_update(self) -> None:
        editorial = self._editorial_from_form()
        try:
            if self.current_draft:
                self.repository.confirm_draft(self.current_draft, editorial)
                self.current_draft = None
                message = text(self.language, "capture_saved")
            elif self.current_capture:
                self.current_capture = self.repository.update_capture_editorial(
                    self.current_capture.id,
                    editorial,
                )
                message = text(self.language, "changes_saved")
            else:
                return
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.show_status(message, 3000)
        self._set_inspector_enabled(False)
        self.current_capture = None
        self.refresh_captures()
        self.refresh_projects()
        if self.current_project:
            self.refresh_gallery()

    def discard_current_draft(self) -> None:
        if not self.current_draft:
            return
        self.repository.discard_draft(self.current_draft)
        self.current_draft = None
        self._set_inspector_enabled(False)

    def refresh_captures(self) -> None:
        self.capture_list.clear()
        if not self.current_project:
            return
        captures = self.repository.list_captures(self.current_project.id)
        markers: list[tuple[int, str]] = []
        fps = self.session.video.metadata.fps if self.session.video else 24.0
        for capture in captures:
            title = capture.editorial.get("title") or f"Capture {capture.capture_number}"
            timecode = self._capture_time_label(capture, fps)
            label = f"{title}  ·  {timecode}"
            item = QListWidgetItem(label)
            item.setToolTip(f"{title} · {timecode}")
            thumb = self.repository.resolve_project_file(
                capture.project_id,
                capture.thumbnail_rel_path,
            )
            item.setIcon(
                self._thumbnail_icon(
                    thumb,
                    self.capture_list.iconSize(),
                )
            )
            item.setData(Qt.ItemDataRole.UserRole, capture.id)
            self.capture_list.addItem(item)
            if capture.source_pts is not None:
                markers.append((capture.source_time_ms, capture.id))
        self.timeline.set_markers(markers)

    def _capture_time_label(self, capture: Capture, fps: float) -> str:
        if capture.source_pts is None:
            return text(self.language, "imported_image")
        return format_timecode(capture.source_time_ms, fps)

    def _capture_item_clicked(self, item: QListWidgetItem) -> None:
        self.open_capture_by_id(str(item.data(Qt.ItemDataRole.UserRole)))

    @Slot(str)
    def open_capture_by_id(self, capture_id: str) -> None:
        capture = self.repository.get_capture(capture_id)
        if not capture:
            return
        capture = self._ensure_palette_percentages(capture)
        if self.current_draft:
            self.repository.discard_draft(self.current_draft)
            self.current_draft = None
        self.current_capture = capture
        image = self.repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
        self._show_image(image)
        self._show_analysis(capture.analysis)
        self._populate_editor(capture.editorial)
        self._set_inspector_enabled(True)
        fps = self.session.video.metadata.fps if self.session.video else 24.0
        self.inspector_title.setText(
            text(self.language, "shot_information")
        )
        self.inspector_time.setText(
            self._capture_time_label(capture, fps)
        )
        self.confirm_button.setText(text(self.language, "save_changes"))
        self.discard_button.setVisible(False)
        self.capture_delete_button.setVisible(True)
        if self.session.video and capture.source_pts is not None:
            self.player.setPosition(capture.source_time_ms)

    def _set_inspector_enabled(self, enabled: bool) -> None:
        self.inspector_frame.setEnabled(enabled)
        if not enabled:
            self.capture_delete_button.setVisible(False)
            self.preview_label.clear()
            self.preview_label.setText(text(self.language, "select_frame"))
            self._populate_editor({})
            self._show_analysis({})
            self.inspector_title.setText(
                text(self.language, "shot_information")
            )
            self.inspector_time.setText("00:00:00:00")
            self.discard_button.setVisible(False)

    def _show_image(self, path: Path) -> None:
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.preview_label.clear()
            return
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _show_analysis(self, analysis: dict) -> None:
        self._apply_palette_analysis(
            self.palette_swatches,
            self.palette_layout,
            analysis,
        )

    @staticmethod
    def _apply_palette_analysis(
        swatches: list[ColorSwatch],
        layout: QHBoxLayout,
        analysis: dict,
    ) -> None:
        colors = analysis.get("dominant_colors", []) if analysis else []
        percentages = (
            analysis.get("color_percentages", [])
            if analysis
            else []
        )
        valid_color_count = min(len(colors), len(swatches))
        has_percentages = (
            valid_color_count > 0
            and len(percentages) >= valid_color_count
            and sum(
                max(0.0, float(value))
                for value in percentages[:valid_color_count]
            ) > 0
        )
        for index, swatch in enumerate(swatches):
            color = colors[index] if index < valid_color_count else ""
            percentage = (
                max(0.0, float(percentages[index]))
                if has_percentages and index < valid_color_count
                else None
            )
            swatch.set_color(color, percentage)

            if not colors:
                swatch.setVisible(True)
                layout.setStretch(index, 1)
                continue

            visible = bool(color) and (
                percentage is None or percentage > 0
            )
            swatch.setVisible(visible)
            if not visible:
                layout.setStretch(index, 0)
            elif percentage is None:
                layout.setStretch(index, 1)
            else:
                layout.setStretch(
                    index,
                    max(1, round(percentage * 10)),
                )

    def _ensure_palette_percentages(self, capture: Capture) -> Capture:
        colors = capture.analysis.get("dominant_colors", [])
        percentages = capture.analysis.get("color_percentages", [])
        if colors and len(percentages) >= len(colors):
            return capture
        image_path = self.repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
        try:
            analysis = analyze_image(image_path)
            return self.repository.update_capture_analysis(
                capture.id,
                analysis,
            )
        except Exception:
            return capture

    def copy_color_to_clipboard(self, color: str) -> None:
        QApplication.clipboard().setText(color)
        self.show_status(
            text(self.language, "color_copied", color=color),
            2600,
        )

    def _populate_editor(self, editorial: dict) -> None:
        self.title_edit.setText(str(editorial.get("title", "")))
        self._set_combo(self.shot_size_combo, editorial.get("shot_size", ""))
        self._set_combo(
            self.camera_angle_combo,
            editorial.get("camera_angle", ""),
        )
        self._set_combo(self.location_combo, editorial.get("location_type", ""))
        self._set_combo(self.lens_combo, editorial.get("lens_type", ""))
        self._set_combo(self.time_combo, editorial.get("time_of_day", ""))
        self._set_combo(
            self.lighting_combo,
            editorial.get("lighting_style", ""),
        )
        self._set_combo(
            self.key_direction_combo,
            editorial.get("key_direction", ""),
        )
        self._set_combo(
            self.key_quality_combo,
            editorial.get("key_quality", ""),
        )
        self.mood_edit.setText("، ".join(editorial.get("mood", [])))
        self.tags_edit.setText("، ".join(editorial.get("tags", [])))
        self.notes_edit.setPlainText(str(editorial.get("notes", "")))

    @staticmethod
    def _set_combo(combo: QComboBox, value: object) -> None:
        index = combo.findData(value)
        combo.setCurrentIndex(max(index, 0))

    def _editorial_from_form(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "shot_size": self.shot_size_combo.currentData() or "",
            "camera_angle": self.camera_angle_combo.currentData() or "",
            "location_type": self.location_combo.currentData() or "",
            "lens_type": self.lens_combo.currentData() or "",
            "time_of_day": self.time_combo.currentData() or "",
            "lighting_style": self.lighting_combo.currentData() or "",
            "key_direction": self.key_direction_combo.currentData() or "",
            "key_quality": self.key_quality_combo.currentData() or "",
            "mood": split_terms(self.mood_edit.text()),
            "tags": split_terms(self.tags_edit.text()),
            "notes": self.notes_edit.toPlainText().strip(),
        }

    def show_error(self, message: str) -> None:
        ValidationDialog(message, self.language, self).exec()

    def closeEvent(self, event) -> None:
        if self.current_draft:
            self.repository.discard_draft(self.current_draft)
        self.player.stop()
        self.player.setSource(QUrl())
        self.session.close_video()
        super().closeEvent(event)
