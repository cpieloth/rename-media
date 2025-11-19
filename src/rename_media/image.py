import dataclasses
import datetime

import exif
import logging
import pathlib
import typing


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class FileInformation:
    path: pathlib.Path
    dir: pathlib.Path
    name: str
    extension: str
    date_created: datetime.datetime | None

    @classmethod
    def instance(cls, path: pathlib.Path):
        if path.is_dir():
            raise RuntimeError(f'Path is not a file: {path}')
        return cls(path, path.parent, path.stem, path.suffix.strip('.'), None)


@dataclasses.dataclass
class Result:
    old_name: pathlib.Path
    new_name: pathlib.Path
    result: bool


SUPPORTED_TYPES_MAPPING = {'jpg': 'jpg', 'jpeg': 'jpg', 'png': 'png'}


def is_supported_file_extension(extension: str) -> bool:
    return extension.lower() in SUPPORTED_TYPES_MAPPING


def normalize_file_extension(extension: str) -> str:
    return SUPPORTED_TYPES_MAPPING[extension.lower()]


def extract_creation_date(file_path: pathlib.Path) -> typing.Optional[datetime.datetime]:
    try:
        with open(file_path, 'rb') as image_file:
            image = exif.Image(image_file)
    except IsADirectoryError:
        raise
    except Exception as ex:
        logger.debug('Could not create exif.Image: %s', ex)
        return None

    if not image.has_exif:
        logger.debug('No EXIF found: %s', file_path)
        return None

    return datetime.datetime.strptime(image.datetime, '%Y:%m:%d %H:%M:%S')


def create_renamed_file_information(file_info: FileInformation, prefix: str, suffix: str) -> FileInformation:
    assert file_info.date_created is not None

    name = f'{prefix}{file_info.date_created.strftime("%Y%m%dT%H%M%S")}{suffix}'
    extension = normalize_file_extension(file_info.extension)
    path = file_info.path.parent.joinpath(f'{name}.{extension}')

    return FileInformation(path, file_info.dir, name, extension, file_info.date_created)


def rename_file(file_info: FileInformation, prefix: str, suffix: str) -> FileInformation:
    new_file_info = create_renamed_file_information(file_info, prefix, suffix)
    logger.debug('new_file_info=%s', new_file_info)

    if new_file_info.path.exists():
        raise FileExistsError(f'File already exists: {new_file_info.path}')

    file_info.path.rename(new_file_info.path)
    return new_file_info


def rename_with_date(directory: pathlib.Path, prefix: str = '', suffix: str = '') -> typing.Iterator[Result]:
    for path in directory.iterdir():
        # filter
        try:
            file_info = FileInformation.instance(path)
            logger.debug('file_info=%s', file_info)
        except RuntimeError:
            logger.debug('Skip directory: %s', path)
            continue

        if not is_supported_file_extension(file_info.extension):
            logger.debug('Skip non-image: %s', file_info.path)
            yield Result(path, path, False)
            continue

        # extract & prepare
        file_info.date_created = extract_creation_date(file_info.path)
        if not file_info.date_created:
            logger.info('Could not rename "%s", because no date found.', file_info.path)
            yield Result(path, path, False)
            continue

        # rename
        try:
            new_file_info = rename_file(file_info, prefix, suffix)
            yield Result(path, new_file_info.path, True)
        except FileExistsError as ferr:
            logger.warning('Could not rename "%s": %s', file_info.path, ferr)
            yield Result(path, path, False)
        except Exception as ex:
            logger.error('Rename error for file "%s": %s', path, ex)
            yield Result(path, path, False)
