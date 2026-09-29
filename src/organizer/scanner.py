from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from organizer.models import FileInfo


def scan_directory(directory: Path) -> Iterator[FileInfo]:
    for path in directory.rglob("*"):
        if not path.is_file():
            continue

        stat = path.stat()

        yield FileInfo(
            path=path,
            size=stat.st_size,
            mtime=datetime.fromtimestamp(stat.st_mtime),
            ext=path.suffix.lower(),
        )