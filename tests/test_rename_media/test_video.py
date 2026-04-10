import datetime
import os.path
import pathlib
import tempfile
import unittest

import rename_media.common
import rename_media.video

import test_rename_media.fixtures as fixtures


class VideoTestCase(unittest.TestCase):
    temp_dir: tempfile.TemporaryDirectory = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix='rename-media-video_tests')

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_extract_creation_date(self):
        # success
        date = rename_media.video.extract_creation_date(fixtures.FIXTURE_VIDEO_01_MP4)
        self.assertEqual(datetime.datetime(2025, 11, 30, 10, 10, 39), date)

        # failed
        with self.assertRaises(IsADirectoryError) as _:
            rename_media.video.extract_creation_date(fixtures.FIXTURE_DIR)

    def test_rename_with_date_directory(self):
        impl = rename_media.video.instance()

        # failed
        with self.assertRaises(NotADirectoryError) as _:
            next(impl.rename_with_date(pathlib.Path(__file__)))

        directory = pathlib.Path(os.path.dirname(__file__))
        for result in impl.rename_with_date(directory):
            self.assertEqual(result.old_name, result.new_name)
            self.assertIsNotNone(result.error_str)

        # success
        # no prefix and no suffix
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_no-prefix_no-suffix')

        expected = {'20251130T101039.mp4'}

        for result in impl.rename_with_date(directory):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix only
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_prefix')

        expected = {'prefix_20251130T101039.mp4'}

        for result in impl.rename_with_date(directory, 'prefix_'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # suffix only
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_suffix')

        expected = {'20251130T101039_suffix.mp4'}

        for result in impl.rename_with_date(directory, suffix='_suffix'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix and suffix
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_prefix_suffix')

        expected = {'prefix_20251130T101039_suffix.mp4'}

        for result in impl.rename_with_date(directory, 'prefix_', '_suffix'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))
