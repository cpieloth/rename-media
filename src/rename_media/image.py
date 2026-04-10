import datetime
import logging
import pathlib

import exif

from rename_media import common

logger = logging.getLogger(__name__)

SUPPORTED_TYPES_MAPPING = {'jpg': 'jpg', 'jpeg': 'jpg', 'png': 'png'}


def extract_creation_date(file_path: pathlib.Path) -> datetime.datetime | None:
    try:
        with open(file_path, 'rb') as image_file:
            image = exif.Image(image_file)
    except IsADirectoryError:
        raise
    except Exception as ex:  # noqa: BLE001
        logger.debug('Could not create exif.Image for %s: %s', file_path, ex)
        return None

    if not image.has_exif:
        logger.debug('No EXIF found: %s', file_path)
        return None

    return datetime.datetime.strptime(image.datetime, '%Y:%m:%d %H:%M:%S').replace(tzinfo=datetime.UTC)


def instance() -> common.RenameImplementation:
    return common.RenameImplementation(SUPPORTED_TYPES_MAPPING, extract_creation_date)
