import logging
import pathlib

from rename_media.core import model, ports

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES_MAPPING = {'jpg': 'jpg', 'jpeg': 'jpg', 'png': 'png'}
SUPPORTED_VIDEO_TYPES_MAPPING = {'mp4': 'mp4', 'mov': 'mov'}

SUPPORTED_TYPES_MAPPING = SUPPORTED_IMAGE_TYPES_MAPPING | SUPPORTED_VIDEO_TYPES_MAPPING


def normalize_file_extension(extension: str) -> str:
    return SUPPORTED_TYPES_MAPPING.get(extension.lower(), extension.lower())


def create_new_file_path(file_info: model.FileInformation, prefix: str, suffix: str) -> pathlib.Path:
    assert file_info.date_created is not None  # TODO
    name = f'{prefix}{file_info.date_created.strftime("%Y%m%dT%H%M%S")}{suffix}'
    extension = normalize_file_extension(file_info.extension)
    return file_info.dir.joinpath(f'{name}.{extension}')


def rename_file(old_file_path: pathlib.Path, new_file_path: pathlib.Path) -> pathlib.Path:
    if old_file_path == new_file_path:
        return new_file_path

    if new_file_path.exists():
        raise FileExistsError(f'File already exists: {new_file_path}')

    target_path = old_file_path.rename(new_file_path)
    return target_path


def rename_file_with_date(
    file_path: pathlib.Path, date_extractor: ports.DateExtractor, prefix: str, suffix: str
) -> pathlib.Path:
    logger.debug('Processing file: %s', file_path)

    # Check file type support
    if not date_extractor.is_supported_file(file_path):
        raise model.RenameError(file_path, 'File type not supported.')

    # Parse general file information
    file_info = model.FileInformation.instance(file_path)

    # Get date
    file_info.date_created = date_extractor.get_date(file_info.path)
    if not file_info.date_created:
        raise model.RenameError(file_path, 'No date found.')
    logger.debug('file_info: %s', file_info)

    # Create new filename
    new_file_path = create_new_file_path(file_info, prefix, suffix)
    logger.debug('New file path: %s', new_file_path)

    # Execute rename
    try:
        return rename_file(file_info.path, new_file_path)
    except FileExistsError as e:
        raise model.RenameError(file_path, f'File already exists: {new_file_path}') from e
    except OSError as e:
        raise model.RenameError(file_path, 'File operation error.') from e
