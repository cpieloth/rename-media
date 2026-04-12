import dataclasses
import logging
import pathlib
import typing

from rename_media.adapters import date_extractor
from rename_media.core import model, ports, use_cases

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Result:
    old_name: pathlib.Path
    new_name: pathlib.Path
    error_str: str | None


class _RenameFilesWithDate:
    def __init__(self, supported_types: dict[str, str], date_extractor_adapter: ports.DateExtractor):
        self.supported_types = supported_types
        self.date_extractor = date_extractor_adapter

    def get_supported_files(self, directory: pathlib.Path) -> typing.Iterator[pathlib.Path]:
        for path in directory.iterdir():
            if path.is_dir():
                logger.debug('Skip directory: %s', path)
                continue

            if not path.suffix.strip('.').lower() in self.supported_types:
                logger.debug('Skip unsupported file type: %s', path)
                continue

            yield path

    def process_directory(self, directory: pathlib.Path, prefix: str = '', suffix: str = '') -> typing.Iterator[Result]:
        for file_path in self.get_supported_files(directory):
            try:
                new_file_path = use_cases.rename_file_with_date(file_path, self.date_extractor, prefix, suffix)
                yield Result(file_path, new_file_path, None)
            except (model.RenameError, model.NotAFileError) as e:
                yield Result(file_path, file_path, str(e))


def rename_images(directory: pathlib.Path, prefix: str = '', suffix: str = '') -> typing.Iterator[Result]:
    renamer = _RenameFilesWithDate(use_cases.SUPPORTED_IMAGE_TYPES_MAPPING, date_extractor.ExifDateExtractor())
    yield from renamer.process_directory(directory, prefix, suffix)


def rename_videos(directory: pathlib.Path, prefix: str = '', suffix: str = '') -> typing.Iterator[Result]:
    renamer = _RenameFilesWithDate(use_cases.SUPPORTED_VIDEO_TYPES_MAPPING, date_extractor.VideoMetainfoDateExtractor())
    yield from renamer.process_directory(directory, prefix, suffix)
