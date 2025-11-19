import dataclasses
import datetime
import logging
import pathlib
import pymediainfo
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


SUPPORTED_TYPES_MAPPING = {'mp4': 'mp4'}


def is_supported_file_extension(extension: str) -> bool:
    return extension.lower() in SUPPORTED_TYPES_MAPPING


def normalize_file_extension(extension: str) -> str:
    return SUPPORTED_TYPES_MAPPING[extension.lower()]


def extract_creation_date(file_path: pathlib.Path) -> typing.Optional[datetime.datetime]:
    try:
        media_info = pymediainfo.MediaInfo.parse(file_path)
        general_track = media_info.general_tracks[0]
        encoded_date = datetime.datetime.strptime(general_track.encoded_date, '%Y-%m-%d %H:%M:%S %Z')
        modification_date = datetime.datetime.strptime(
            general_track.file_last_modification_date__local, '%Y-%m-%d %H:%M:%S'
        )
    except OSError:
        raise
    except Exception as ex:
        logger.debug('Could not create pymediainfo.MediaInfo or get attribute for %s: %s', file_path, ex)
        return None

    # check for correct timezone
    if encoded_date == modification_date:
        return encoded_date

    # if only hours are different, then timezone can differ, try to correct
    diff_seconds = abs(encoded_date - modification_date).total_seconds()
    if diff_seconds < (24 * 60 * 60) and diff_seconds % (60 * 60) == 0:
        logger.debug('Use modification_date: %s', file_path)
        return modification_date
    else:
        logger.debug('Use encoded_date: %s', file_path)
        return encoded_date


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
