import dataclasses
import datetime
import pathlib


@dataclasses.dataclass(frozen=False)
class FileInformation:
    path: pathlib.Path
    dir: pathlib.Path
    name: str
    extension: str
    date_created: datetime.datetime | None

    @classmethod
    def instance(cls, path: pathlib.Path) -> 'FileInformation':
        if path.is_dir():
            raise NotAFileError(path)
        return cls(path, path.parent, path.stem, path.suffix.strip('.'), None)


class NotAFileError(IsADirectoryError):
    def __init__(self, file_path: pathlib.Path):
        super().__init__(f'Path is not a file: {file_path}')
        self.file_path = file_path


class RenameError(Exception):
    def __init__(self, file_path: pathlib.Path, message: str):
        super().__init__(f'Error renaming file "{file_path}": {message}')
        self.file_path = file_path
        self.message = message
