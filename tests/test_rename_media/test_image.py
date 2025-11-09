import datetime
import os.path
import pathlib
import shutil
import tempfile
import unittest

import rename_media.image


class ImageTestCase(unittest.TestCase):
    FIXTURE_DIR = pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures'
    FIXTURE_IMG_01_JPG = pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'IMG_0001.JPG'
    FIXTURE_IMG_02_JPEG = pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'IMG_0002.JPEG'
    FIXTURE_IMG_03_JPG = pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'IMG_0003.jpg'

    temp_dir: tempfile.TemporaryDirectory = None

    @classmethod
    def _copy_fixtures(cls, folder_name):
        dst_path = pathlib.Path(cls.temp_dir.name) / folder_name
        shutil.copytree(cls.FIXTURE_DIR, dst_path)
        return dst_path

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix='rename-media_tests')

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_file_information_instance(self):
        file_info = rename_media.image.FileInformation.instance(self.FIXTURE_IMG_01_JPG)
        self.assertEqual(self.FIXTURE_IMG_01_JPG, file_info.path)
        self.assertTrue(str(file_info.dir) in str(self.FIXTURE_IMG_01_JPG))
        self.assertEqual('IMG_0001', file_info.name)
        self.assertEqual('JPG', file_info.extension)

        with self.assertRaises(RuntimeError) as _:
            _ = rename_media.image.FileInformation.instance(self.FIXTURE_DIR)

    def test_is_supported_file_extension(self):
        expected_false = ['wav', 'WAV', 'mp4']
        for extension in expected_false:
            self.assertFalse(rename_media.image.is_supported_file_extension(extension))

        expected_true = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']
        for extension in expected_true:
            self.assertTrue(rename_media.image.is_supported_file_extension(extension))

    def test_extract_creation_date_success(self):
        date = rename_media.image.extract_creation_date(self.FIXTURE_IMG_01_JPG)
        self.assertEqual(datetime.datetime.fromisoformat('2025-11-09T16:38:56'), date)

    def test_extract_creation_date_failed(self):
        with self.assertRaises(IsADirectoryError) as _:
            rename_media.image.extract_creation_date(self.FIXTURE_DIR)

    def test_normalize_file_suffix(self):
        extensions = [('jpg', 'jpg'), ('jpg', 'JPG'), ('jpg', 'jpeg'), ('jpg', 'JPEG'), ('png', 'png'), ('png', 'PNG')]
        for expected, extension in extensions:
            self.assertEqual(expected, rename_media.image.normalize_file_extension(extension))

    def test_create_renamed_file_information(self):
        pass
        # file_info = rename_media.image.FileInformation.instance(self.FIXTURE_DSC_02_JPEG)
        #
        # new_file_info = rename_media.image.create_renamed_file_information(file_info, 'prefix_', '')
        # # TODO
        #
        # new_file_info = rename_media.image.create_renamed_file_information(file_info, '', '_suffix')
        # # TODO
        #
        # new_file_info = rename_media.image.create_renamed_file_information(file_info, 'prefix_', '_suffix')
        # # TODO
        #
        # new_file_info = rename_media.image.create_renamed_file_information(file_info, '', '')
        # # TODO

    def test_rename_with_date_directory_failed(self):
        with self.assertRaises(NotADirectoryError) as _:
            next(rename_media.image.rename_with_date(pathlib.Path(__file__)))

        directory = pathlib.Path(os.path.dirname(__file__))
        for result in rename_media.image.rename_with_date(directory):
            self.assertEqual(result.old_name, result.new_name)
            self.assertFalse(result.result)

    def test_rename_with_date_directory_success(self):
        # no prefix and no suffix
        directory = self._copy_fixtures('rename_with_date_no-prefix_no-suffix')

        expected = {'20251109T163856.jpg', '20251109T163911.jpg', '20251109T163922.jpg'}

        for result in rename_media.image.rename_with_date(directory):
            self.assertTrue(result.result)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix only
        directory = self._copy_fixtures('rename_with_date_prefix')

        expected = {'prefix_20251109T163856.jpg', 'prefix_20251109T163911.jpg', 'prefix_20251109T163922.jpg'}

        for result in rename_media.image.rename_with_date(directory, 'prefix_'):
            self.assertTrue(result.result)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # suffix only
        directory = self._copy_fixtures('rename_with_date_suffix')

        expected = {'20251109T163856_suffix.jpg', '20251109T163911_suffix.jpg', '20251109T163922_suffix.jpg'}

        for result in rename_media.image.rename_with_date(directory, suffix='_suffix'):
            self.assertTrue(result.result)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))

        # prefix and suffix
        directory = self._copy_fixtures('rename_with_date_prefix_suffix')

        expected = {
            'prefix_20251109T163856_suffix.jpg',
            'prefix_20251109T163911_suffix.jpg',
            'prefix_20251109T163922_suffix.jpg',
        }

        for result in rename_media.image.rename_with_date(directory, 'prefix_', '_suffix'):
            self.assertTrue(result.result)
            expected.remove(result.new_name.name)
        self.assertEqual(0, len(expected))
