import tempfile
import unittest

from rename_media.adapters import date_extractor
from rename_media.core import model, use_cases
from test_rename_media import fixtures


class UseCasesTestCase(unittest.TestCase):
    temp_dir: tempfile.TemporaryDirectory = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix='rename-media-common_tests')

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_normalize_file_extension_supported(self):
        self.assertEqual(use_cases.normalize_file_extension('jpg'), 'jpg')
        self.assertEqual(use_cases.normalize_file_extension('JPG'), 'jpg')
        self.assertEqual(use_cases.normalize_file_extension('jpeg'), 'jpg')
        self.assertEqual(use_cases.normalize_file_extension('JPEG'), 'jpg')

        self.assertEqual(use_cases.normalize_file_extension('png'), 'png')
        self.assertEqual(use_cases.normalize_file_extension('PNG'), 'png')

        self.assertEqual(use_cases.normalize_file_extension('mp4'), 'mp4')
        self.assertEqual(use_cases.normalize_file_extension('MP4'), 'mp4')

    def test_normalize_file_extension_unsupported(self):
        self.assertEqual(use_cases.normalize_file_extension('txt'), 'txt')
        self.assertEqual(use_cases.normalize_file_extension('TXT'), 'txt')

    def test_create_new_file_path(self):
        file_info = model.FileInformation.instance(fixtures.FIXTURE_IMG_01_JPG)
        file_info.date_created = date_extractor.ExifDateExtractor().get_date(file_info.path)

        new_file_path = use_cases.create_new_file_path(file_info, '', '')
        self.assertEqual(f'{new_file_path.stem}{new_file_path.suffix}', '20251109T163856.jpg')

        new_file_path = use_cases.create_new_file_path(file_info, 'prefix_', '')
        self.assertEqual(f'{new_file_path.stem}{new_file_path.suffix}', 'prefix_20251109T163856.jpg')

        new_file_path = use_cases.create_new_file_path(file_info, '', '_suffix')
        self.assertEqual(f'{new_file_path.stem}{new_file_path.suffix}', '20251109T163856_suffix.jpg')

        new_file_path = use_cases.create_new_file_path(file_info, 'prefix_', '_suffix')
        self.assertEqual(f'{new_file_path.stem}{new_file_path.suffix}', 'prefix_20251109T163856_suffix.jpg')

    def test_rename_file_image_success(self):
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_file_image_success_1')
        file_name = f'{fixtures.FIXTURE_IMG_01_JPG.stem}{fixtures.FIXTURE_IMG_01_JPG.suffix}'
        new_file_path = use_cases.rename_file_with_date(
            directory / file_name, date_extractor.ExifDateExtractor(), '', ''
        )
        self.assertEqual(new_file_path, directory / '20251109T163856.jpg')

        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_file_image_success_2')
        file_name = f'{fixtures.FIXTURE_IMG_01_JPG.stem}{fixtures.FIXTURE_IMG_01_JPG.suffix}'
        new_file_path = use_cases.rename_file_with_date(
            directory / file_name, date_extractor.ExifDateExtractor(), 'prefix_', ''
        )
        self.assertEqual(new_file_path, directory / 'prefix_20251109T163856.jpg')

        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_file_image_success_3')
        file_name = f'{fixtures.FIXTURE_IMG_01_JPG.stem}{fixtures.FIXTURE_IMG_01_JPG.suffix}'
        new_file_path = use_cases.rename_file_with_date(
            directory / file_name, date_extractor.ExifDateExtractor(), '', '_suffix'
        )
        self.assertEqual(new_file_path, directory / '20251109T163856_suffix.jpg')

        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_file_image_success_4')
        file_name = f'{fixtures.FIXTURE_IMG_01_JPG.stem}{fixtures.FIXTURE_IMG_01_JPG.suffix}'
        new_file_path = use_cases.rename_file_with_date(
            directory / file_name, date_extractor.ExifDateExtractor(), 'prefix_', '_suffix'
        )
        self.assertEqual(new_file_path, directory / 'prefix_20251109T163856_suffix.jpg')

    def test_rename_file_image_fail(self):
        file_path = fixtures.FIXTURE_DIR / 'nonexistent.jpg'
        with self.assertRaises(model.RenameError) as cm:
            _ = use_cases.rename_file_with_date(file_path, date_extractor.ExifDateExtractor(), '', '')
        self.assertEqual(file_path, cm.exception.file_path)

    def test_rename_file_video_success(self):
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_file_video')
        file_name = f'{fixtures.FIXTURE_VIDEO_01_MP4.stem}{fixtures.FIXTURE_VIDEO_01_MP4.suffix}'
        new_file_path = use_cases.rename_file_with_date(
            directory / file_name, date_extractor.VideoMetainfoDateExtractor(), '', ''
        )
        self.assertEqual(new_file_path, directory / '20251130T101039.mp4')
