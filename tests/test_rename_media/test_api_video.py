import os
import pathlib
import tempfile
import unittest

from rename_media import api
from test_rename_media import fixtures


class ApiVideoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix='rename-media-video_tests')

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_rename_videos_failed(self):
        with self.assertRaises(NotADirectoryError) as _:
            next(api.rename_videos(pathlib.Path(__file__)))

        directory = pathlib.Path(os.path.dirname(__file__))
        for result in api.rename_videos(directory):
            self.assertEqual(result.old_name, result.new_name)
            self.assertIsNotNone(result.error_str)

    def test_rename_videos_success(self):
        # no prefix and no suffix
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_no-prefix_no-suffix')

        expected = {'20251130T101039.mp4'}

        for result in api.rename_videos(directory):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix only
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_prefix')

        expected = {'prefix_20251130T101039.mp4'}

        for result in api.rename_videos(directory, 'prefix_'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # suffix only
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_suffix')

        expected = {'20251130T101039_suffix.mp4'}

        for result in api.rename_videos(directory, suffix='_suffix'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix and suffix
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_prefix_suffix')

        expected = {'prefix_20251130T101039_suffix.mp4'}

        for result in api.rename_videos(directory, 'prefix_', '_suffix'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))
