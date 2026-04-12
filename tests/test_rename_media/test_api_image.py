import os
import pathlib
import tempfile
import unittest

from rename_media import api
from test_rename_media import fixtures


class ApiImageTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix='rename-media-image_tests')

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_rename_images_failed(self):
        with self.assertRaises(NotADirectoryError) as _:
            next(api.rename_images(pathlib.Path(__file__)))

        directory = pathlib.Path(os.path.dirname(__file__))
        for result in api.rename_images(directory):
            self.assertEqual(result.old_name, result.new_name)
            self.assertIsNotNone(result.error_str)

    def test_rename_images_success(self):
        # no prefix and no suffix
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_no-prefix_no-suffix')

        expected = {'20251109T163856.jpg', '20251109T163911.jpg', '20251109T163922.jpg'}

        for result in api.rename_images(directory):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix only
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_prefix')

        expected = {'prefix_20251109T163856.jpg', 'prefix_20251109T163911.jpg', 'prefix_20251109T163922.jpg'}

        for result in api.rename_images(directory, 'prefix_'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # suffix only
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_suffix')

        expected = {'20251109T163856_suffix.jpg', '20251109T163911_suffix.jpg', '20251109T163922_suffix.jpg'}

        for result in api.rename_images(directory, suffix='_suffix'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix and suffix
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_with_date_prefix_suffix')

        expected = {
            'prefix_20251109T163856_suffix.jpg',
            'prefix_20251109T163911_suffix.jpg',
            'prefix_20251109T163922_suffix.jpg',
        }

        for result in api.rename_images(directory, 'prefix_', '_suffix'):
            self.assertIsNone(result.error_str)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))
