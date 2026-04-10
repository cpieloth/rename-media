import os
import pathlib
import shutil
import tempfile


FIXTURE_DIR = (pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures').resolve()

FIXTURE_IMG_01_JPG = (pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'IMG_0001.JPG').resolve()
FIXTURE_IMG_02_JPEG = (pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'IMG_0002.JPEG').resolve()
FIXTURE_IMG_03_JPG = (pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'IMG_0003.jpg').resolve()

FIXTURE_VIDEO_01_MP4 = (pathlib.Path(os.path.dirname(__file__)) / '..' / 'fixtures' / '20251130_111037.mp4').resolve()


def copy_fixtures(parent_folder: tempfile.TemporaryDirectory, folder_name: str):
    dst_path = pathlib.Path(parent_folder.name) / folder_name
    shutil.copytree(FIXTURE_DIR, dst_path)
    return dst_path
