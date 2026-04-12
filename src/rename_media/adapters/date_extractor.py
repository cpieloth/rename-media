import datetime
import logging
import pathlib

import exif
import pymediainfo

from rename_media.core import ports, use_cases

logger = logging.getLogger(__name__)


class ExifDateExtractor(ports.DateExtractor):
    """Adapter for extracting creation dates from image EXIF data."""

    def is_supported_file(self, file_path: pathlib.Path) -> bool:
        return file_path.suffix.strip('.').lower() in use_cases.SUPPORTED_IMAGE_TYPES_MAPPING

    def get_date(self, file_path: pathlib.Path) -> datetime.datetime | None:
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


class VideoMetainfoDateExtractor(ports.DateExtractor):
    """Adapter for extracting creation dates from video metadata."""

    def is_supported_file(self, file_path: pathlib.Path) -> bool:
        return file_path.suffix.strip('.').lower() in use_cases.SUPPORTED_VIDEO_TYPES_MAPPING

    def get_date(self, file_path: pathlib.Path) -> datetime.datetime | None:
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
