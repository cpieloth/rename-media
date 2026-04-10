import dataclasses
import datetime
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


def rename_file(from_file_info: FileInformation, to_file_info: FileInformation) -> FileInformation:
    if to_file_info.path.exists():
        raise FileExistsError(f'File already exists: {to_file_info.path}')

    from_file_info.path.rename(to_file_info.path)
    return to_file_info


@dataclasses.dataclass
class Result:
    old_name: pathlib.Path
    new_name: pathlib.Path
    error_str: str | None


@dataclasses.dataclass
class RenameImplementation:
    supported_types_mapping: dict[str, str]
    extract_creation_date: typing.Callable[[pathlib.Path], datetime.datetime | None]

    def is_supported_file_extension(self, extension: str) -> bool:
        return extension.lower() in self.supported_types_mapping

    def normalize_file_extension(self, extension: str) -> str:
        return self.supported_types_mapping[extension.lower()]

    def create_renamed_file_information(self, file_info: FileInformation, prefix: str, suffix: str) -> FileInformation:
        assert file_info.date_created is not None

        name = f'{prefix}{file_info.date_created.strftime("%Y%m%dT%H%M%S")}{suffix}'
        extension = self.normalize_file_extension(file_info.extension)
        path = file_info.path.parent.joinpath(f'{name}.{extension}')

        return FileInformation(path, file_info.dir, name, extension, file_info.date_created)

    def get_supported_files(self, directory: pathlib.Path) -> typing.Iterator[FileInformation]:
        for path in directory.iterdir():
            try:
                file_info = FileInformation.instance(path)
            except RuntimeError:
                logger.debug('Skip directory: %s', path)
                continue

            if not self.is_supported_file_extension(file_info.extension):
                logger.debug('Skip non-image: %s', file_info.path)
                continue

            yield file_info

    def rename_with_date(self, directory: pathlib.Path, prefix: str = '', suffix: str = '') -> typing.Iterator[Result]:
        for file_info in self.get_supported_files(directory):
            logger.debug('Supported file: %s', file_info)

            # extract & prepare
            file_info.date_created = self.extract_creation_date(file_info.path)
            if not file_info.date_created:
                logger.info('Could not rename "%s", because no date found.', file_info.path)
                yield Result(file_info.path, file_info.path, 'No date found.')
                continue

            # rename
            try:
                new_file_info = self.create_renamed_file_information(file_info, prefix, suffix)
                logger.debug('new_file_info=%s', new_file_info)

                new_file_info = rename_file(file_info, new_file_info)
                yield Result(file_info.path, new_file_info.path, None)
            except FileExistsError as ferr:
                logger.warning('Could not rename "%s": %s', file_info.path, ferr)
                yield Result(file_info.path, file_info.path, 'File exists.')
            except Exception as ex:  # noqa: BLE001
                logger.error('Rename error for file "%s": %s', file_info.path, ex)
                yield Result(file_info.path, file_info.path, 'Unknown error.')
