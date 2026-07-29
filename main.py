from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from shotlab.config import configure_bundled_tools, default_data_root
from shotlab.repository import Repository
from shotlab.session import CaptureSession
from shotlab.ui.main_window import MainWindow


def load_bundled_fonts() -> None:
    font_root = Path(__file__).resolve().parent / "assets" / "fonts"
    for font_path in sorted(font_root.glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(font_path))


def main() -> int:
    configure_bundled_tools()
    QCoreApplication.setOrganizationName("StoryEco")
    QCoreApplication.setApplicationName("ShotLab")
    application = QApplication(sys.argv)
    application.setStyle("Fusion")
    load_bundled_fonts()
    application.setWindowIcon(
        QIcon(str(Path(__file__).resolve().parent / "assets" / "app-icon.png"))
    )

    try:
        repository = Repository(default_data_root())
        session = CaptureSession(repository)
        window = MainWindow(repository, session)
        window.showMaximized()
    except Exception as exc:
        QMessageBox.critical(None, "ShotLab", str(exc))
        return 1
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
