import dataclasses
import datetime
import pathlib
import tempfile
import typing
import unittest

import rename_media.common

import test_rename_media.fixtures as fixtures


class CommonTestCase(unittest.TestCase):
    temp_dir: tempfile.TemporaryDirectory = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix='rename-media-common_tests')

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @staticmethod
    def rename_implementation():
        def extract_creation_date(_: pathlib.Path) -> typing.Optional[datetime.datetime]:
            return None

        extensions = {'med1a': 'media', 'media': 'media'}
        impl = rename_media.common.RenameImplementation(extensions, extract_creation_date)
        return impl

    @staticmethod
    def file_information(file_name='foo.med1a'):
        file_info = rename_media.common.FileInformation(
            path=pathlib.Path(f'/tmp/{file_name}'),
            dir=pathlib.Path('/tmp'),
            name=file_name.split('.')[0],
            extension=file_name.split('.')[1],
            date_created=datetime.datetime.fromisoformat('2025-11-30T10:11:00')
        )
        return file_info

    def test_file_information(self):
        # success
        file_information = rename_media.common.FileInformation.instance(fixtures.FIXTURE_IMG_01_JPG)

        self.assertEqual(file_information.path, fixtures.FIXTURE_IMG_01_JPG)
        self.assertTrue(str(file_information.dir) in str(fixtures.FIXTURE_IMG_01_JPG))
        self.assertEqual(file_information.extension, 'JPG')
        self.assertEqual(file_information.name, 'IMG_0001')
        self.assertIsNone(file_information.date_created)

        # failed
        with self.assertRaises(RuntimeError) as _:
            _ = rename_media.common.FileInformation.instance(fixtures.FIXTURE_DIR)

    def test_rename(self):
        # success tests
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_success')

        from_file_info = rename_media.common.FileInformation.instance(directory / 'IMG_0001.JPG')
        to_file_info = rename_media.common.FileInformation.instance(directory / 'IMG_0001_renamed.jpg')

        to_file_info_renamed = rename_media.common.rename_file(from_file_info, to_file_info)
        self.assertEqual(to_file_info_renamed, to_file_info)
        self.assertTrue(to_file_info_renamed.path.exists())

        # fail tests
        directory = fixtures.copy_fixtures(self.temp_dir, 'rename_failed')

        from_file_info = rename_media.common.FileInformation.instance(directory / 'IMG_0001.JPG')
        to_file_info = rename_media.common.FileInformation.instance(directory / 'IMG_0002.JPEG')

        with self.assertRaises(FileExistsError) as _:
            _ = rename_media.common.rename_file(from_file_info, to_file_info)

    def test_is_supported_file_extension(self):
        impl = self.rename_implementation()

        self.assertTrue(impl.is_supported_file_extension('media'))
        self.assertTrue(impl.is_supported_file_extension('MEDIA'))
        self.assertTrue(impl.is_supported_file_extension('med1a'))
        self.assertFalse(impl.is_supported_file_extension('bar'))

    def test_normalize_file_extension(self):
        impl = self.rename_implementation()

        self.assertEqual(impl.normalize_file_extension('media'), 'media')
        self.assertEqual(impl.normalize_file_extension('MEDIA'), 'media')
        self.assertEqual(impl.normalize_file_extension('med1a'), 'media')

        with self.assertRaises(KeyError) as _:
            _ = impl.normalize_file_extension('bar')

    def test_create_renamed_file_information(self):
        file_info = self.file_information()
        impl = self.rename_implementation()

        # no prefix, no suffix
        file_info_expected = dataclasses.replace(
            file_info,
            path=pathlib.Path('/tmp/20251130T101100.media'),
            name='20251130T101100',
            extension='media'
        )
        file_info_renamed = impl.create_renamed_file_information(file_info, '', '')
        self.assertEqual(file_info_renamed, file_info_expected)

        # with prefix, no suffix
        file_info_expected = dataclasses.replace(
            file_info,
            path=pathlib.Path('/tmp/prefix_20251130T101100.media'),
            name='prefix_20251130T101100',
            extension='media'
        )
        file_info_renamed = impl.create_renamed_file_information(file_info, 'prefix_', '')
        self.assertEqual(file_info_renamed, file_info_expected)

        # no prefix, with suffix
        file_info_expected = dataclasses.replace(
            file_info,
            path=pathlib.Path('/tmp/20251130T101100_suffix.media'),
            name='20251130T101100_suffix',
            extension='media'
        )
        file_info_renamed = impl.create_renamed_file_information(file_info, '', '_suffix')
        self.assertEqual(file_info_renamed, file_info_expected)

        # with prefix, with suffix
        file_info_expected = dataclasses.replace(
            file_info,
            path=pathlib.Path('/tmp/prefix_20251130T101100_suffix.media'),
            name='prefix_20251130T101100_suffix',
            extension='media'
        )
        file_info_renamed = impl.create_renamed_file_information(file_info, 'prefix_', '_suffix')
        self.assertEqual(file_info_renamed, file_info_expected)
