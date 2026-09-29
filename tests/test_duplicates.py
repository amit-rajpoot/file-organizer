from datetime import datetime
from pathlib import Path

from organizer.duplicates import duplicate_candidates, group_by_first_chunk, group_by_size
from organizer.models import FileInfo


def test_group_by_size():
    now = datetime.now()

    file1 = FileInfo(
        path=Path("/tmp/photo.jpg"),
        size=1000,
        mtime=now,
        ext=".jpg",
    )

    file2 = FileInfo(
        path=Path("/tmp/copy.jpg"),
        size=1000,
        mtime=now,
        ext=".jpg",
    )

    file3 = FileInfo(
        path=Path("/tmp/report.pdf"),
        size=2000,
        mtime=now,
        ext=".pdf",
    )

    result = group_by_size([file1, file2, file3])

    assert len(result[1000]) == 2
    assert len(result[2000]) == 1

def test_duplicate_candidates():
    now = datetime.now()

    file1 = FileInfo(
        path=Path("/tmp/photo.jpg"),
        size=1000,
        mtime=now,
        ext=".jpg",
    )

    file2 = FileInfo(
        path=Path("/tmp/copy.jpg"),
        size=1000,
        mtime=now,
        ext=".jpg",
    )

    file3 = FileInfo(
        path=Path("/tmp/report.pdf"),
        size=2000,
        mtime=now,
        ext=".pdf",
    )

    groups = group_by_size([file1, file2, file3])

    result = duplicate_candidates(groups)

    assert len(result) == 2
    assert file1 in result
    assert file2 in result
    assert file3 not in result

def test_group_by_first_chunk(tmp_path: Path):
    now = datetime.now()

    first_4kb = b"A" * 4096

    file1_path = tmp_path / "file1.bin"
    file2_path = tmp_path / "file2.bin"
    file3_path = tmp_path / "file3.bin"

    file1_path.write_bytes(first_4kb + b"one")
    file2_path.write_bytes(first_4kb + b"two")
    file3_path.write_bytes(b"B" * 4096 + b"three")

    file1 = FileInfo(
        path=file1_path,
        size=file1_path.stat().st_size,
        mtime=now,
        ext=".bin",
    )

    file2 = FileInfo(
        path=file2_path,
        size=file2_path.stat().st_size,
        mtime=now,
        ext=".bin",
    )

    file3 = FileInfo(
        path=file3_path,
        size=file3_path.stat().st_size,
        mtime=now,
        ext=".bin",
    )

    result = group_by_first_chunk([file1, file2, file3])

    matching_groups = [
        files for files in result.values()
        if file1 in files
    ]

    assert len(matching_groups) == 1
    assert file2 in matching_groups[0]
    assert file3 not in matching_groups[0]