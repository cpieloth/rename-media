import unittest

from rename_media.core import model
from test_rename_media import fixtures


class FileInformationTestCase(unittest.TestCase):
    def test_file_information_success(self):
        file_information = model.FileInformation.instance(fixtures.FIXTURE_IMG_01_JPG)

        self.assertEqual(file_information.path, fixtures.FIXTURE_IMG_01_JPG)
        self.assertTrue(str(file_information.dir) in str(fixtures.FIXTURE_IMG_01_JPG))
        self.assertEqual(file_information.extension, 'JPG')
        self.assertEqual(file_information.name, 'IMG_0001')
        self.assertIsNone(file_information.date_created)

    def test_file_information_failed(self):
        with self.assertRaises(model.NotAFileError) as cm:
            _ = model.FileInformation.instance(fixtures.FIXTURE_DIR)
        self.assertEqual(cm.exception.file_path, fixtures.FIXTURE_DIR)
