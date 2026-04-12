import unittest
import datetime

from rename_media.adapters import date_extractor
from test_rename_media import fixtures


class VideoMetainfoDateExtractorTestCase(unittest.TestCase):
    def setUp(self):
        self.extractor = date_extractor.VideoMetainfoDateExtractor()

    def test_is_supported_file_with_supported(self):
        self.assertTrue(self.extractor.is_supported_file(fixtures.FIXTURE_VIDEO_01_MP4))

    def test_is_supported_file_with_unsupported(self):
        self.assertFalse(self.extractor.is_supported_file(fixtures.FIXTURE_IMG_01_JPG))

    def test_get_date_with_exif(self):
        date = self.extractor.get_date(fixtures.FIXTURE_VIDEO_01_MP4)
        self.assertIsInstance(date, datetime.datetime)
        self.assertEqual(datetime.datetime.fromisoformat('2025-11-30T10:10:39+00:00'), date)

    def test_get_date_no_exif(self):
        date = self.extractor.get_date(fixtures.FIXTURE_IMG_01_JPG)
        self.assertIsNone(date)

    def test_get_date_invalid_file(self):
        # Use a directory
        with self.assertRaises(IsADirectoryError):
            self.extractor.get_date(fixtures.FIXTURE_DIR)
