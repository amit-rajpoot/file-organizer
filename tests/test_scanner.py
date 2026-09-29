from pathlib import Path

from organizer.scanner import scan_directory

def test_scan_directory_recursively(tmp_path: Path):
    root_file = tmp_path / "photo.jpg"

    nested_dir = tmp_path / "Documents"
    nested_dir.mkdir()

    nested_file = nested_dir / "report.pdf"

    root_file.write_bytes(b"hello")
    nested_file.write_bytes(b"world")

    files = list(scan_directory(tmp_path))

    assert len(files) == 2

    names = {file.path.name for file in files}

    assert "photo.jpg" in names
    assert "report.pdf" in names