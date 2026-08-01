"""ShotLab release-quality regression checks."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from PIL import Image

from shotlab.analysis import aggregate_palette, analyze_image
from shotlab.backup import export_library, restore_library
from shotlab.repository import Repository
from shotlab.session import CaptureSession


def make_test_video(path: Path) -> None:
    completed = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=#203a66:s=640x360:d=1:r=24",
            "-f",
            "lavfi",
            "-i",
            "color=c=#d28a38:s=640x360:d=1:r=24",
            "-filter_complex",
            "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p",
            "-c:v",
            "libx264",
            "-y",
            str(path),
        ],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))


def make_large_test_video(path: Path) -> None:
    completed = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=#315b82:s=2048x1024:d=0.5:r=4",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-y",
            str(path),
        ],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="shotlab-test-")
        self.root = Path(self.temp.name)
        self.repository = Repository(self.root / "data")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_project_name_is_the_only_required_field(self) -> None:
        with self.assertRaises(ValueError):
            self.repository.create_project("   ")

        project = self.repository.create_project("My Film")
        self.assertEqual(project.name, "My Film")
        self.assertEqual(project.optional, {})
        self.assertEqual(project.capture_count, 0)

    def test_project_rename_and_recoverable_delete(self) -> None:
        project = self.repository.create_project("Original Name")
        renamed = self.repository.rename_project(project.id, "Renamed Project")
        self.assertEqual(renamed.name, "Renamed Project")

        project_folder = self.repository.project_folder(project.id)
        self.assertTrue(project_folder.is_dir())
        recovery = self.repository.delete_project(project.id)
        self.assertIsNone(self.repository.get_project(project.id))
        self.assertFalse(project_folder.exists())
        self.assertTrue(recovery.is_dir())
        self.assertTrue((recovery / "project.json").is_file())
        reopened_repository = Repository(self.repository.data_root)
        self.assertIsNone(reopened_repository.get_project(project.id))
        self.assertEqual(reopened_repository.list_projects(), [])

    def test_video_path_is_never_persisted_in_library_data(self) -> None:
        video = self.root / "very-private-source-name.mp4"
        make_test_video(video)
        project = self.repository.create_project("No Path Leak")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        session.attach_video(video)

        manifest = (
            self.repository.project_folder(project.id) / "project.json"
        ).read_text(encoding="utf-8")
        self.assertNotIn(str(video), manifest)
        self.assertNotIn(video.name, manifest)
        database_bytes = self.repository.database_path.read_bytes()
        self.assertNotIn(str(video).encode("utf-8"), database_bytes)
        self.assertNotIn(video.name.encode("utf-8"), database_bytes)

        with closing(
            sqlite3.connect(self.repository.database_path)
        ) as connection:
            schema = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type='table'"
            ).fetchall()
            columns = "\n".join(row[0] or "" for row in schema)
        self.assertNotIn("source_path", columns.lower())
        self.assertNotIn("video_path", columns.lower())
        session.close_video()
        self.assertIsNone(session.video)

    def test_capture_confirm_and_edit_workflow(self) -> None:
        video = self.root / "source.mp4"
        make_test_video(video)
        project = self.repository.create_project("Capture Flow")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        metadata = session.attach_video(video)
        self.assertEqual(metadata.duration_ms, 2000)

        draft = session.create_draft(1250)
        self.assertTrue(Path(draft.image_path).is_file())
        self.assertLessEqual(abs(draft.source_time_ms - 1250), 50)
        self.assertIsNotNone(draft.source_pts)
        self.assertEqual(len(draft.analysis["dominant_colors"]), 5)
        self.assertEqual(
            set(draft.analysis),
            {"dominant_colors", "color_percentages"},
        )
        self.assertAlmostEqual(
            sum(draft.analysis["color_percentages"]),
            100.0,
            places=1,
        )
        self.assertEqual(draft.editorial["lighting_style"], "")
        self.assertNotIn("backlight", draft.editorial)

        capture = self.repository.confirm_draft(
            draft,
            {
                **draft.editorial,
                "title": "Warm frame",
                "shot_size": "MS",
                "time_of_day": "day",
                "tags": ["warm", "reference"],
                "backlight": True,
            },
        )
        self.assertEqual(capture.capture_number, 1)
        self.assertEqual(capture.editorial["title"], "Warm frame")
        self.assertNotIn("backlight", capture.editorial)
        self.assertTrue(
            self.repository.resolve_project_file(
                project.id,
                capture.image_rel_path,
            ).is_file()
        )

        updated = self.repository.update_capture_editorial(
            capture.id,
            {**capture.editorial, "notes": "Corrected by user"},
        )
        self.assertEqual(updated.editorial["notes"], "Corrected by user")

        annotations = [
            {
                "type": "arrow",
                "points": [[0.2, 0.3], [0.7, 0.6]],
                "color": "#D8B365",
                "width": 5,
            }
        ]
        annotated = self.repository.update_capture_annotations(
            capture.id,
            annotations,
        )
        self.assertEqual(annotated.annotations, annotations)
        annotated_full = self.repository.annotated_image_path(annotated)
        annotated_thumb = self.repository.annotated_thumbnail_path(annotated)
        annotated_full.parent.mkdir(parents=True, exist_ok=True)
        annotated_full.write_bytes(b"annotated-preview")
        annotated_thumb.write_bytes(b"annotated-thumbnail")
        self.assertEqual(
            self.repository.display_image_path(annotated),
            annotated_full,
        )
        self.assertEqual(
            self.repository.display_thumbnail_path(annotated),
            annotated_thumb,
        )

        project_after = self.repository.get_project(project.id)
        self.assertIsNotNone(project_after)
        self.assertEqual(project_after.capture_count, 1)

        payload = json.loads(
            (
                self.repository.project_folder(project.id) / "project.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(payload["captures"]), 1)
        self.assertEqual(payload["captures"][0]["editorial"]["notes"], "Corrected by user")
        self.assertEqual(
            payload["captures"][0]["annotations"],
            annotations,
        )
        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn(str(video), serialized)
        self.assertNotIn(video.name, serialized)
        self.assertNotIn(video.name.encode("utf-8"), self.repository.database_path.read_bytes())
        self.assertEqual(
            [result.id for result in self.repository.search_captures("Warm MS")],
            [capture.id],
        )
        self.assertEqual(
            [result.id for result in self.repository.search_captures("reference")],
            [capture.id],
        )
        self.assertEqual(
            [result.id for result in self.repository.search_captures("روز")],
            [capture.id],
        )
        self.assertEqual(
            [result.id for result in self.repository.search_captures("نمای متوسط")],
            [capture.id],
        )
        self.assertEqual(
            [
                result.id
                for result in self.repository.filter_captures(
                    filters={"shot_size": "MS", "time_of_day": "day"}
                )
            ],
            [capture.id],
        )
        self.assertEqual(
            self.repository.filter_captures(
                filters={"shot_size": "CU"},
            ),
            [],
        )
        self.assertEqual(
            self.repository.project_thumbnails(project.id),
            [annotated_thumb],
        )
        self.assertEqual(self.repository.search_captures("does-not-exist"), [])

    def test_fingerprint_mismatch_requires_confirmation(self) -> None:
        first = self.root / "first.mp4"
        second = self.root / "second.mp4"
        make_test_video(first)
        completed = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "color=c=green:s=320x240:d=1:r=25",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-y",
                str(second),
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)

        project = self.repository.create_project("Fingerprint")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        session.attach_video(first)
        session.close_video()
        with self.assertRaisesRegex(ValueError, "SOURCE_FINGERPRINT_MISMATCH"):
            session.attach_video(second)

        session.attach_video(second, allow_mismatch=True)
        self.assertEqual(session.video.path, second.resolve())
        updated = self.repository.get_project(project.id)
        self.assertEqual(
            updated.source_fingerprint,
            session.video.metadata.fingerprint_payload(),
        )

    def test_displayed_frame_capture_keeps_exact_frame_and_time(self) -> None:
        video = self.root / "timeline-source.mp4"
        make_test_video(video)
        project = self.repository.create_project("Exact Displayed Frame")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        session.attach_video(video)

        displayed = self.root / "displayed.jpg"
        Image.new("RGB", (640, 360), "#e32472").save(
            displayed,
            "JPEG",
            quality=100,
        )
        draft = session.create_draft_from_displayed_frame(1375, displayed)
        self.assertEqual(draft.source_time_ms, 1375)
        self.assertEqual(draft.source_pts, 1.375)
        self.assertFalse(displayed.exists())
        with Image.open(draft.image_path) as captured:
            red, green, blue = captured.resize((1, 1)).getpixel((0, 0))
        self.assertGreater(red, 200)
        self.assertLess(green, 80)
        self.assertGreater(blue, 80)

    def test_source_frame_storage_sizes(self) -> None:
        video = self.root / "large-source.mp4"
        make_large_test_video(video)
        project = self.repository.create_project("Storage Sizes")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        session.attach_video(video)

        expected_sizes = {
            "actual": (2048, 1024),
            "medium": (1280, 640),
            "small": (720, 360),
        }
        for mode, expected_size in expected_sizes.items():
            displayed = self.root / f"displayed-{mode}.jpg"
            Image.new("RGB", (640, 320), "#315b82").save(displayed, "JPEG")
            draft = session.create_draft_from_source_frame(
                250,
                displayed,
                mode,
            )
            self.assertFalse(displayed.exists())
            with Image.open(draft.image_path) as captured:
                self.assertEqual(captured.size, expected_size)

    def test_manual_image_import_creates_editable_palette_draft(self) -> None:
        source = self.root / "reference.png"
        Image.new("RGB", (1600, 900), "#C8874C").save(source, "PNG")
        project = self.repository.create_project("Still References")
        session = CaptureSession(self.repository)
        session.open_project(project.id)

        draft = session.create_draft_from_image(source, "small")
        self.assertTrue(source.is_file())
        self.assertIsNone(draft.source_pts)
        self.assertEqual(draft.source_time_ms, 0)
        self.assertEqual(len(draft.analysis["dominant_colors"]), 5)
        self.assertAlmostEqual(
            sum(draft.analysis["color_percentages"]),
            100.0,
            places=1,
        )
        with Image.open(draft.image_path) as imported:
            self.assertEqual(imported.size, (720, 405))

        capture = self.repository.confirm_draft(
            draft,
            {**draft.editorial, "title": "Manual reference"},
        )
        self.assertIsNone(capture.source_pts)
        self.assertEqual(capture.editorial["title"], "Manual reference")
        edited_analysis = dict(capture.analysis)
        edited_colors = list(edited_analysis["dominant_colors"])
        edited_colors[2] = "#12ABEF"
        edited_analysis["dominant_colors"] = edited_colors
        capture = self.repository.update_capture_analysis(
            capture.id,
            edited_analysis,
        )
        self.assertEqual(capture.analysis["dominant_colors"][2], "#12ABEF")
        reopened = Repository(self.repository.data_root)
        reopened_capture = reopened.get_capture(capture.id)
        self.assertIsNotNone(reopened_capture)
        self.assertIsNone(reopened_capture.source_pts)
        self.assertEqual(
            reopened_capture.analysis["dominant_colors"][2],
            "#12ABEF",
        )
        self.assertNotIn(
            source.name.encode("utf-8"),
            self.repository.database_path.read_bytes(),
        )
        image_path = self.repository.resolve_project_file(
            capture.project_id,
            capture.image_rel_path,
        )
        thumbnail_path = self.repository.resolve_project_file(
            capture.project_id,
            capture.thumbnail_rel_path,
        )
        recovery = self.repository.delete_capture(capture.id)
        self.assertIsNone(self.repository.get_capture(capture.id))
        self.assertFalse(image_path.exists())
        self.assertFalse(thumbnail_path.exists())
        self.assertEqual(len(list(recovery.iterdir())), 2)
        reopened_after_delete = Repository(self.repository.data_root)
        self.assertIsNone(reopened_after_delete.get_capture(capture.id))
        self.assertEqual(
            reopened_after_delete.list_captures(project.id),
            [],
        )
        manifest = json.loads(
            (
                self.repository.project_folder(project.id)
                / "project.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["captures"], [])

    def test_palette_percentages_measure_image_coverage(self) -> None:
        source = self.root / "coverage.png"
        image = Image.new("RGB", (100, 100), "#D64232")
        image.paste("#2456A4", (0, 0, 25, 100))
        image.save(source, "PNG")

        analysis = analyze_image(source)
        percentages = sorted(
            analysis["color_percentages"],
            reverse=True,
        )
        self.assertAlmostEqual(percentages[0], 75.0, delta=0.1)
        self.assertAlmostEqual(percentages[1], 25.0, delta=0.1)
        self.assertAlmostEqual(sum(percentages), 100.0, places=1)

    def test_library_palette_averages_color_mood_by_coverage(self) -> None:
        palette = aggregate_palette(
            [
                {
                    "dominant_colors": ["#C04030", "#2020A0"],
                    "color_percentages": [80.0, 20.0],
                },
                {
                    "dominant_colors": ["#E06040", "#2020B0"],
                    "color_percentages": [80.0, 20.0],
                },
            ],
            count=2,
        )
        self.assertEqual(len(palette), 2)
        red = tuple(
            int(palette[0][index : index + 2], 16)
            for index in (1, 3, 5)
        )
        blue = tuple(
            int(palette[1][index : index + 2], 16)
            for index in (1, 3, 5)
        )
        self.assertGreater(red[0], 190)
        self.assertLess(red[1], 110)
        self.assertLess(red[2], 90)
        self.assertLess(blue[0], 70)
        self.assertGreater(blue[2], 140)

    def test_hex_and_manual_color_filters_include_nearby_colors(self) -> None:
        project = self.repository.create_project("Color Search")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        captures = {}
        for name, color in (
            ("exact", "#737170"),
            ("near", "#7B7978"),
            ("far", "#2A6CB0"),
        ):
            source = self.root / f"{name}.png"
            Image.new("RGB", (320, 180), color).save(source, "PNG")
            draft = session.create_draft_from_image(source, "actual")
            captures[name] = self.repository.confirm_draft(
                draft,
                {**draft.editorial, "title": name},
            )

        self.repository.update_capture_analysis(
            captures["far"].id,
            {
                "dominant_colors": [
                    "#2A6CB0",
                    "#193D70",
                    "#737170",
                    "#101820",
                    "#7B7978",
                ],
                "color_percentages": [45.0, 30.0, 15.0, 7.0, 3.0],
            },
        )
        searched = self.repository.search_captures("#737170")
        self.assertEqual(
            [capture.id for capture in searched],
            [captures["exact"].id, captures["near"].id],
        )
        searched_without_hash = self.repository.search_captures("737170")
        self.assertEqual(
            [capture.id for capture in searched_without_hash],
            [captures["exact"].id, captures["near"].id],
        )
        manually_filtered = self.repository.filter_captures(
            color_hex="737170",
        )
        self.assertEqual(
            [capture.id for capture in manually_filtered],
            [captures["exact"].id, captures["near"].id],
        )
        combined = self.repository.search_captures("near 737170")
        self.assertEqual(
            [capture.id for capture in combined],
            [captures["near"].id],
        )

    def test_export_and_restore_library_without_source_video(self) -> None:
        video = self.root / "backup-source.mp4"
        make_test_video(video)
        project = self.repository.create_project("Portable Library")
        session = CaptureSession(self.repository)
        session.open_project(project.id)
        session.attach_video(video)
        draft = session.create_draft(500)
        self.repository.confirm_draft(
            draft,
            {**draft.editorial, "title": "Backup frame", "tags": ["portable"]},
        )

        archive = export_library(self.repository, self.root / "library.shotlab")
        self.assertTrue(archive.is_file())
        self.assertNotIn(video.name.encode("utf-8"), archive.read_bytes())

        second_repository = Repository(self.root / "restored-data")
        restore_library(second_repository, archive)
        restored_projects = second_repository.list_projects()
        self.assertEqual(len(restored_projects), 1)
        self.assertEqual(restored_projects[0].name, "Portable Library")
        restored_captures = second_repository.list_captures(restored_projects[0].id)
        self.assertEqual(len(restored_captures), 1)
        self.assertEqual(restored_captures[0].editorial["title"], "Backup frame")


if __name__ == "__main__":
    unittest.main()
