from pathlib import Path

from organizer.hasher import hash_file, hash_first_chunk


def test_same_content_has_same_hash(tmp_path: Path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_bytes(b"hello world")
    file2.write_bytes(b"hello world")

    assert hash_file(file1) == hash_file(file2)


def test_different_content_has_different_hash(tmp_path: Path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_bytes(b"hello")
    file2.write_bytes(b"goodbye")

    assert hash_file(file1) != hash_file(file2)


def test_hash_is_string(tmp_path: Path):
    file = tmp_path / "file.txt"
    file.write_bytes(b"hello")

    result = hash_file(file)

    assert isinstance(result, str)


def test_first_chunk_can_match_but_full_hash_can_differ(tmp_path: Path):
    file1 = tmp_path / "file1.bin"
    file2 = tmp_path / "file2.bin"

    first_4kb = b"A" * 4096

    file1.write_bytes(first_4kb + b"file one")
    file2.write_bytes(first_4kb + b"file two")

    assert hash_first_chunk(file1) == hash_first_chunk(file2)

    assert hash_file(file1) != hash_file(file2)