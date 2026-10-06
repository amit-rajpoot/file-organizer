from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from organizer.duplicates import duplicate_candidates, find_duplicates, first_chunk_candidates, get_content_hash, group_by_first_chunk, group_by_hash, group_by_size
from organizer.hasher import hash_file
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

def test_first_chunk_candidates():
    now = datetime.now()

    file1 = FileInfo(
        path=Path("/tmp/file1"),
        size=1000,
        mtime=now,
        ext="",
    )

    file2 = FileInfo(
        path=Path("/tmp/file2"),
        size=1000,
        mtime=now,
        ext="",
    )

    file3 = FileInfo(
        path=Path("/tmp/file3"),
        size=2000,
        mtime=now,
        ext="",
    )

    groups = {
        "hash-a": [file1, file2],
        "hash-b": [file3],
    }

    result = first_chunk_candidates(groups)

    assert len(result) == 2
    assert file1 in result
    assert file2 in result
    assert file3 not in result

def test_group_by_hash(tmp_path: Path):
    now = datetime.now()

    file1_path = tmp_path / "file1.txt"
    file2_path = tmp_path / "copy.txt"
    file3_path = tmp_path / "different.txt"

    file1_path.write_bytes(b"hello world")
    file2_path.write_bytes(b"hello world")
    file3_path.write_bytes(b"something else")

    file1 = FileInfo(
        path=file1_path,
        size=file1_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    file2 = FileInfo(
        path=file2_path,
        size=file2_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    file3 = FileInfo(
        path=file3_path,
        size=file3_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    result = group_by_hash([file1, file2, file3])

    assert len(result) == 2

    groups = list(result.values())

    assert any(
        file1 in group and file2 in group
        for group in groups
    )

    assert any(
        file3 in group
        for group in groups
    )

def test_find_duplicates_with_same_content(tmp_path: Path):
    content = b"hello world" * 1000

    file1_path = tmp_path / "file1.txt"
    file2_path = tmp_path / "copy.txt"
    file3_path = tmp_path / "different.txt"

    file1_path.write_bytes(content)
    file2_path.write_bytes(content)
    file3_path.write_bytes(b"something different" * 1000)

    now = datetime.now()

    file1 = FileInfo(
        path=file1_path,
        size=file1_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    file2 = FileInfo(
        path=file2_path,
        size=file2_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    file3 = FileInfo(
        path=file3_path,
        size=file3_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    result = find_duplicates([file1, file2, file3])

    assert len(result) == 1
    assert len(result[0]) == 2

    assert file1 in result[0]
    assert file2 in result[0]
    assert file3 not in result[0]

def test_find_duplicates_only_full_hashes_first_chunk_candidates(
    tmp_path: Path,
):
    now = datetime.now()

    common = b"A" * 4096

    file1_path = tmp_path / "file1.bin"
    file2_path = tmp_path / "file2.bin"
    file3_path = tmp_path / "file3.bin"

    file1_path.write_bytes(common + b"one")
    file2_path.write_bytes(common + b"two")
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

    with patch(
        "organizer.duplicates.hash_file",
        wraps=__import__("organizer.hasher", fromlist=["hash_file"]).hash_file,
    ) as mock_hash:
        find_duplicates([file1, file2, file3])

    assert mock_hash.call_count == 2

def test_find_duplicates_requires_full_hash(tmp_path: Path):
    now = datetime.now()

    common = b"A" * 4096

    file1_path = tmp_path / "file1.bin"
    file2_path = tmp_path / "file2.bin"

    file1_path.write_bytes(common + b"file one")
    file2_path.write_bytes(common + b"file two")

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

    result = find_duplicates([file1, file2])

    assert result == []

def test_group_by_hash_uses_existing_content_hash(tmp_path: Path):
    now = datetime.now()

    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello world")

    file = FileInfo(
        path=file_path,
        size=file_path.stat().st_size,
        mtime=now,
        ext=".txt",
        content_hash="precomputed-hash",
    )

    with patch(
        "organizer.duplicates.hash_file"
    ) as mock_hash:
        result = group_by_hash([file])

    mock_hash.assert_not_called()

    assert "precomputed-hash" in result
    assert result["precomputed-hash"] == [file]

def test_group_by_hash_reuses_hash_for_same_file(
    tmp_path: Path,
):
    now = datetime.now()

    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello world")

    file = FileInfo(
        path=file_path,
        size=file_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )
    hash_cache = {}

    with patch(
    "organizer.duplicates.hash_file",
    wraps=hash_file) as mock_hash:
     first_result = group_by_hash([file], hash_cache)
     second_result = group_by_hash([file], hash_cache)

    assert mock_hash.call_count == 1

    assert first_result == second_result

def test_hash_cache_detects_changed_file(tmp_path: Path):
    now = datetime.now()

    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello")

    file = FileInfo(
        path=file_path,
        size=file_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    hash_cache: dict[Path, tuple[int, float, str]] = {
        file_path: (
            file.size,
            100.0,
            "old-hash",
        )
    }

    file_path.write_bytes(b"goodbye")

    new_size = file_path.stat().st_size
    new_mtime = file_path.stat().st_mtime

    assert (
        hash_cache[file_path][0] != new_size
        or hash_cache[file_path][1] != new_mtime
    )

def test_group_by_hash_rehashes_when_file_changes(
    tmp_path: Path,
):
    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello")

    now = datetime.now()

    file = FileInfo(
        path=file_path,
        size=file_path.stat().st_size,
        mtime=now,
        ext=".txt",
    )

    hash_cache: dict[Path, tuple[int, float, str]] = {}

    with patch(
        "organizer.duplicates.hash_file",
        wraps=hash_file,
    ) as mock_hash:

        # First time → hash calculate hoga
        group_by_hash([file], hash_cache)

        assert mock_hash.call_count == 1

        # File ka content change
        file_path.write_bytes(b"goodbye")

        # Same path, but file change ho chuki hai
        updated_file = FileInfo(
            path=file_path,
            size=file_path.stat().st_size,
            mtime=datetime.fromtimestamp(
                file_path.stat().st_mtime
            ),
            ext=".txt",
        )

        group_by_hash([updated_file], hash_cache)

        # File change hui → old cache use nahi hona chahiye
        assert mock_hash.call_count == 2

def test_get_content_hash_uses_existing_content_hash(
    tmp_path: Path,
):
    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello")

    file = FileInfo(
        path=file_path,
        size=file_path.stat().st_size,
        mtime=datetime.now(),
        ext=".txt",
        content_hash="already-known-hash",
    )

    hash_cache: dict[Path, tuple[int, float, str]] = {}

    with patch("organizer.duplicates.hash_file") as mock_hash:
        result = get_content_hash(file, hash_cache)

    assert result == "already-known-hash"
    mock_hash.assert_not_called()

def test_get_content_hash_uses_valid_cache(
    tmp_path: Path,
):
    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello")

    size = file_path.stat().st_size
    mtime = file_path.stat().st_mtime

    file = FileInfo(
        path=file_path,
        size=size,
        mtime=datetime.fromtimestamp(mtime),
        ext=".txt",
    )

    hash_cache = {
        file_path: (
            size,
            mtime,
            "cached-hash",
        )
    }

    with patch("organizer.duplicates.hash_file") as mock_hash:
        result = get_content_hash(file, hash_cache)

    assert result == "cached-hash"
    mock_hash.assert_not_called()

def test_get_content_hash_calculates_when_cache_missing(
    tmp_path: Path,
):
    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello")

    file = FileInfo(
        path=file_path,
        size=file_path.stat().st_size,
        mtime=datetime.now(),
        ext=".txt",
    )

    hash_cache = {}

    with patch(
        "organizer.duplicates.hash_file",
        return_value="new-hash",
    ) as mock_hash:
        result = get_content_hash(file, hash_cache)

    assert result == "new-hash"
    mock_hash.assert_called_once_with(file_path)

    assert file_path in hash_cache
    assert hash_cache[file_path][2] == "new-hash"

def test_get_content_hash_rehashes_invalid_cache(
    tmp_path: Path,
):
    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"hello")

    old_size = file_path.stat().st_size
    old_mtime = file_path.stat().st_mtime

    file_path.write_bytes(b"goodbye world")

    new_size = file_path.stat().st_size
    new_mtime = file_path.stat().st_mtime

    file = FileInfo(
        path=file_path,
        size=new_size,
        mtime=datetime.fromtimestamp(new_mtime),
        ext=".txt",
    )

    hash_cache = {
        file_path: (
            old_size,
            old_mtime,
            "old-hash",
        )
    }

    with patch(
        "organizer.duplicates.hash_file",
        return_value="new-hash",
    ) as mock_hash:
        result = get_content_hash(file, hash_cache)

    assert result == "new-hash"

    mock_hash.assert_called_once_with(file_path)

    assert hash_cache[file_path] == (
        new_size,
        new_mtime,
        "new-hash",
    )