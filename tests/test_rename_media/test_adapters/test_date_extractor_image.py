import unittest
import pathlib
import tempfile
import datetime

from rename_media.adapters import date_extractor
from test_rename_media import fixtures


class ExifDateExtractorTestCase(unittest.TestCase):
    def setUp(self):
        self.extractor = date_extractor.ExifDateExtractor()

    def test_is_supported_file_with_supported(self):
        self.assertTrue(self.extractor.is_supported_file(fixtures.FIXTURE_IMG_01_JPG))
        self.assertTrue(self.extractor.is_supported_file(fixtures.FIXTURE_IMG_02_JPEG))
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = pathlib.Path(f.name)
        try:
            self.assertTrue(self.extractor.is_supported_file(temp_path))
        finally:
            temp_path.unlink()

    def test_is_supported_file_with_unsupported(self):
        self.assertFalse(self.extractor.is_supported_file(fixtures.FIXTURE_VIDEO_01_MP4))

    def test_get_date_with_exif(self):
        date = self.extractor.get_date(fixtures.FIXTURE_IMG_01_JPG)
        self.assertIsInstance(date, datetime.datetime)
        self.assertEqual(datetime.datetime.fromisoformat('2025-11-09T16:38:56+00:00'), date)

    def test_get_date_no_exif(self):
        date = self.extractor.get_date(fixtures.FIXTURE_VIDEO_01_MP4)
        self.assertIsNone(date)

    def test_get_date_invalid_file(self):
        # Use a directory
        with self.assertRaises(IsADirectoryError):
            self.extractor.get_date(fixtures.FIXTURE_DIR)

        # Use non-existing file
        path = fixtures.FIXTURE_DIR / 'nonexistent.jpg'
        date = self.extractor.get_date(path)
        self.assertIsNone(date)
