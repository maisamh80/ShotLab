from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QSettings, QSize, Qt
    from PySide6.QtGui import QFont, QFontDatabase
    from PySide6.QtWidgets import QApplication, QBoxLayout, QFrame, QLabel

    from main import load_bundled_fonts
    from shotlab.pdf_export import _font
    from shotlab.repository import Repository
    from shotlab.session import CaptureSession
    from shotlab.ui.main_window import MainWindow
except ModuleNotFoundError:
    QT_AVAILABLE = False
else:
    QT_AVAILABLE = True


@unittest.skipUnless(QT_AVAILABLE, "PySide6 is not installed in this environment")
class QtRuntimeSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])
        load_bundled_fonts()

    def test_pdf_font_accepts_design_weights(self) -> None:
        for weight in (200, 400, 500, 600):
            font = _font("en", 10.0, weight)
            self.assertIsInstance(font, QFont)

    def test_supplied_vazirmatn_family_is_registered(self) -> None:
        self.assertIn("Vazirmatn", QFontDatabase.families())

    def test_main_window_constructs_with_final_ui(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shotlab-ui-test-") as folder:
            settings_root = Path(folder) / "settings"
            settings_root.mkdir()
            QSettings.setDefaultFormat(QSettings.Format.IniFormat)
            QSettings.setPath(
                QSettings.Format.IniFormat,
                QSettings.Scope.UserScope,
                str(settings_root),
            )
            repository = Repository(Path(folder) / "data")
            session = CaptureSession(repository)
            window = MainWindow(repository, session)
            try:
                window.show()
                self.application.processEvents()
                self.assertEqual(window.sidebar.width(), 282)
                self.assertEqual(
                    window.shell_layout.direction(),
                    QBoxLayout.Direction.LeftToRight,
                )
                self.assertEqual(window.theme_button.text(), "☾")
                self.assertEqual(
                    window.play_button.iconSize(),
                    QSize(24, 24),
                )
                self.assertEqual(
                    window.search_results_title.objectName(),
                    "NeutralSectionTitle",
                )
                self.assertEqual(
                    window.captures_title.objectName(),
                    "NeutralSectionTitle",
                )
                self.assertEqual(
                    window.library_filters.FILTER_KEYS,
                    (
                        "shot_size",
                        "camera_angle",
                        "location_type",
                        "lens_type",
                        "time_of_day",
                        "lighting_style",
                        "key_quality",
                    ),
                )
                self.assertEqual(
                    window.play_button.cursor().shape(),
                    Qt.CursorShape.PointingHandCursor,
                )
                self.assertEqual(
                    window.gallery_list.viewport().cursor().shape(),
                    Qt.CursorShape.PointingHandCursor,
                )

                window.language = "fa"
                window._apply_language()
                self.application.processEvents()
                self.assertEqual(
                    window.layoutDirection(),
                    Qt.LayoutDirection.LeftToRight,
                )
                self.assertEqual(
                    window.sidebar.layoutDirection(),
                    Qt.LayoutDirection.LeftToRight,
                )
                self.assertIn(
                    "text-align: left;",
                    window.nav_projects.styleSheet(),
                )
                self.assertLess(
                    window.sidebar.geometry().right(),
                    window.stack.geometry().left(),
                )

                window._set_gallery_detail_rows(
                    [("Title", "Frame 1")],
                    "",
                )
                notes_frame = window.gallery_detail_body.findChild(
                    QFrame,
                    "DetailNotes",
                )
                self.assertIsNotNone(notes_frame)
                notes_value = notes_frame.findChild(
                    QLabel,
                    "DetailNotesValue",
                )
                self.assertIsNotNone(notes_value)
                self.assertEqual(notes_value.text(), "—")

                class PauseProbe:
                    def __init__(self) -> None:
                        self.calls = 0

                    def pause(self) -> None:
                        self.calls += 1

                original_player = window.player
                pause_probe = PauseProbe()
                window.player = pause_probe
                window.stack.setCurrentWidget(window.capture_page)
                window.stack.setCurrentWidget(window.library_page)
                self.application.processEvents()
                self.assertEqual(pause_probe.calls, 1)
                window.player = original_player
            finally:
                window.close()


if __name__ == "__main__":
    unittest.main()
