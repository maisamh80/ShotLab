from __future__ import annotations

import ast
import unittest
from pathlib import Path

from shotlab.i18n import OPTIONS, STRINGS, option_label
from shotlab.ui.styles import stylesheet


ROOT = Path(__file__).resolve().parents[1]


class FinalUiContractTests(unittest.TestCase):
    def test_pdf_font_weight_uses_qt_weight_enum(self) -> None:
        source_path = ROOT / "shotlab" / "pdf_export.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        font_function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_font"
        )
        set_weight_calls = [
            node
            for node in ast.walk(font_function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "setWeight"
        ]
        self.assertEqual(len(set_weight_calls), 1)
        argument = set_weight_calls[0].args[0]
        self.assertFalse(
            isinstance(argument, ast.Name) and argument.id == "weight",
            "QFont.setWeight must receive QFont.Weight, not a raw integer.",
        )
        enum_members = {
            node.attr
            for node in ast.walk(font_function)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "QFont"
            and node.value.attr == "Weight"
        }
        self.assertIn("Normal", enum_members)
        self.assertIn("Bold", enum_members)

    def test_final_filter_taxonomy_is_available(self) -> None:
        self.assertIn(
            "shoulder_level",
            {value for value, _fa, _en in OPTIONS["camera_angle"]},
        )
        self.assertIn(
            "ground_level",
            {value for value, _fa, _en in OPTIONS["camera_angle"]},
        )
        self.assertIn(
            "split_diopter",
            {value for value, _fa, _en in OPTIONS["lens_type"]},
        )
        self.assertIn(
            "high_noon",
            {value for value, _fa, _en in OPTIONS["time_of_day"]},
        )

    def test_persian_and_english_copy_stay_in_sync(self) -> None:
        self.assertEqual(set(STRINGS["fa"]), set(STRINGS["en"]))

    def test_only_location_and_time_options_are_localized_in_persian(self) -> None:
        self.assertEqual(
            option_label("fa", "location_type", "interior"),
            "داخلی",
        )
        self.assertEqual(
            option_label("fa", "time_of_day", "day"),
            "روز",
        )
        self.assertEqual(
            option_label("fa", "shot_size", "CU"),
            "Close-Up",
        )
        self.assertEqual(
            option_label("fa", "key_quality", "soft"),
            "Soft",
        )

    def test_full_vazirmatn_package_and_persian_override_are_bundled(self) -> None:
        fonts = ROOT / "assets" / "fonts"
        self.assertTrue(
            (fonts / "Vazirmatn-VariableFont_wght.ttf").is_file()
        )
        self.assertTrue((fonts / "Vazirmatn-Regular.ttf").is_file())
        self.assertTrue((fonts / "Vazirmatn-Bold.ttf").is_file())
        self.assertFalse(
            (fonts / "Vazirmatn-Arabic-Variable.ttf").exists()
        )
        self.assertIn(
            'font-family: "Vazirmatn";',
            stylesheet("dark", "fa"),
        )

    def test_correction_layout_contracts_are_present(self) -> None:
        main_source = (
            ROOT / "shotlab" / "ui" / "main_window.py"
        ).read_text(encoding="utf-8")
        styles_source = (
            ROOT / "shotlab" / "ui" / "styles.py"
        ).read_text(encoding="utf-8")
        pdf_source = (
            ROOT / "shotlab" / "pdf_export.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "self.shell_layout.setDirection("
            "QBoxLayout.Direction.LeftToRight)",
            main_source.replace("\n", "").replace(" ", ""),
        )
        self.assertNotIn("index // 3", main_source)
        self.assertIn("ProjectCard.CARD_WIDTH", main_source)
        self.assertGreaterEqual(
            main_source.count('setObjectName("NeutralSectionTitle")'),
            2,
        )
        self.assertIn('self.theme_button.setText("☾"', main_source)
        self.assertIn("QSize(24, 24)", main_source)
        self.assertIn(
            "QSplitter#CaptureVerticalSplitter::handle",
            styles_source,
        )
        self.assertIn(
            "QPushButton#TransportButton:checked",
            styles_source,
        )
        self.assertIn(
            "QSplitter#CaptureVerticalSplitter::handle:vertical:hover",
            styles_source,
        )
        self.assertIn("per_page = columns * rows_per_page", pdf_source)
        self.assertNotIn("QFontMetricsF", pdf_source)
        self.assertIn(
            "palette_label_rect.bottom() + 5",
            pdf_source,
        )

    def test_workspace_exit_and_clickable_cursor_contracts_are_present(
        self,
    ) -> None:
        main_source = (
            ROOT / "shotlab" / "ui" / "main_window.py"
        ).read_text(encoding="utf-8")
        widgets_source = (
            ROOT / "shotlab" / "ui" / "widgets.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "self.stack.currentChanged.connect(self._workspace_changed)",
            main_source,
        )
        self.assertIn(
            "if self.stack.currentWidget() is not self.capture_page:",
            main_source,
        )
        self.assertIn("self.player.pause()", main_source)
        self.assertIn(
            "Qt.CursorShape.PointingHandCursor",
            main_source,
        )
        self.assertGreaterEqual(
            widgets_source.count("Qt.CursorShape.PointingHandCursor"),
            4,
        )

    def test_editable_equal_width_palette_contracts_are_present(self) -> None:
        main_source = (
            ROOT / "shotlab" / "ui" / "main_window.py"
        ).read_text(encoding="utf-8")
        widgets_source = (
            ROOT / "shotlab" / "ui" / "widgets.py"
        ).read_text(encoding="utf-8")
        pdf_source = (
            ROOT / "shotlab" / "pdf_export.py"
        ).read_text(encoding="utf-8")
        self.assertIn("class FrameColorPickerLabel", widgets_source)
        self.assertNotIn("percentage_text", widgets_source)
        self.assertIn('text(self.language, "copy_color_code")', main_source)
        self.assertIn(
            'text(self.language, "pick_color_from_frame")',
            main_source,
        )
        self.assertIn("layout.setStretch(index, 1)", main_source)
        self.assertIn("equal_width = palette_rect.width()", pdf_source)
        self.assertNotIn("color_percentages", pdf_source)
        self.assertEqual(STRINGS["en"]["copy_color_code"], "Copy Color Code")
        self.assertEqual(
            STRINGS["en"]["pick_color_from_frame"],
            "Pick Color from Frame",
        )

    def test_persian_shell_and_pdf_header_keep_reserved_geometry(
        self,
    ) -> None:
        main_source = (
            ROOT / "shotlab" / "ui" / "main_window.py"
        ).read_text(encoding="utf-8")
        pdf_source = (
            ROOT / "shotlab" / "pdf_export.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "self.central_shell.setLayoutDirection(",
            main_source,
        )
        self.assertIn(
            "Qt.LayoutDirection.LeftToRight",
            main_source,
        )
        self.assertIn(
            "logo_rect.left() - header_gap - page_rect.left()",
            pdf_source,
        )
        self.assertIn(
            "text_left = logo_rect.right() + header_gap",
            pdf_source,
        )

    def test_stable_release_sidebar_notes_and_version_contracts(
        self,
    ) -> None:
        main_source = (
            ROOT / "shotlab" / "ui" / "main_window.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "self.sidebar.setLayoutDirection("
            "Qt.LayoutDirection.LeftToRight)",
            main_source.replace("\n", "").replace(" ", ""),
        )
        self.assertNotIn('"text-align: right;"', main_source)
        self.assertIn("notes: str | None = None", main_source)
        self.assertIn("if notes is not None:", main_source)
        self.assertIn('notes_value = QLabel(notes or "—")', main_source)

        self.assertIn(
            '__version__ = "1.0.0"',
            (ROOT / "shotlab" / "__init__.py").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn(
            '#define MyAppVersion "1.0.0"',
            (ROOT / "installer" / "ShotLab.iss").read_text(
                encoding="utf-8"
            ),
        )
        version_info = (
            ROOT / "packaging" / "version_info.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("filevers=(1, 0, 0, 0)", version_info)
        self.assertIn("StringStruct('ProductVersion', '1.0.0')", version_info)


if __name__ == "__main__":
    unittest.main()
