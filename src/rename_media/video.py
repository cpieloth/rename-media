import datetime
import logging
import pathlib

import pymediainfo

from rename_media import common

logger = logging.getLogger(__name__)

SUPPORTED_TYPES_MAPPING = {'mp4': 'mp4'}


def extract_creation_date(file_path: pathlib.Path) -> datetime.datetime | None:
    if not file_path.is_file():
        raise IsADirectoryError(f'{file_path} is not a file')

    try:
        media_info = pymediainfo.MediaInfo.parse(file_path)
        general_track = media_info.general_tracks[0]
        encoded_date = datetime.datetime.strptime(general_track.encoded_date, '%Y-%m-%d %H:%M:%S %Z').replace(
            tzinfo=datetime.UTC
        )
        modification_date = datetime.datetime.strptime(
            general_track.file_last_modification_date__local, '%Y-%m-%d %H:%M:%S'
        ).replace(tzinfo=datetime.UTC)
    except OSError:
        raise
    except Exception as ex:  # noqa: BLE001
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


def instance() -> common.RenameImplementation:
    return common.RenameImplementation(SUPPORTED_TYPES_MAPPING, extract_creation_date)
