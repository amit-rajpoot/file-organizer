from datetime import datetime
from pathlib import Path

import pytest

from organizer.models import FileInfo , Operation

def test_file_info():
    file = FileInfo(
        path=Path("/home/user/Downloads/photo.jpg"),
        size=1024,
        mtime=datetime(2026, 9, 26, 20 , 0 ),
        ext=".jpg"
    )

    assert file.path.name == "photo.jpg"
    assert file.size == 1024
    assert file.ext == ".jpg"
    assert file.content_hash is None

def test_operation():
    operation = Operation(kind="move",
        source=Path("/downloads/photo.jpg"),
        destination=Path("/images/photo.jpg"),
        reason="sorted by extension"
        )

    assert operation.kind == "move"
    assert operation.source.name == "photo.jpg"
    assert operation.destination.name == "photo.jpg"


def test_file_info_is_frozen():
    file = FileInfo(
        path=Path("/tmp/test.txt"),
        size=100,
        mtime=datetime.now(),
        ext=".txt",
    )

    with pytest.raises(Exception):
        file.size = 200
