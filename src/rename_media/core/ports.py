import datetime
import pathlib
from typing import Protocol


class DateExtractor(Protocol):
    def is_supported_file(self, file_path: pathlib.Path) -> bool: ...

    def get_date(self, file_path: pathlib.Path) -> datetime.datetime | None: ...
