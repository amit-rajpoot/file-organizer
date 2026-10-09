from datetime import datetime
from pathlib import Path

from organizer.models import FileInfo
from organizer.planner import folder_for_ext, plan_sort

def test_folder_for_ext():
    assert folder_for_ext(".jpg") == "Images"
    assert folder_for_ext(".pdf") == "Documents"
    assert folder_for_ext(".mp4") == "Videos"

def test_folder_for_ext_unknown():
    assert folder_for_ext(".xyz") == "Other"

def test_folder_for_ext_case_insensitive():
    assert folder_for_ext(".JPG") == "Images"

def test_plan_sort_creates_move_operation(tmp_path: Path):
    file_path = tmp_path / "photo.jpg"

    file = FileInfo(
        path=file_path,
        size=100,
        mtime=datetime.now(),
        ext=".jpg",
    )

    operations = plan_sort([file], tmp_path)

    assert len(operations) == 1

    operation = operations[0]

    assert operation.kind == "move"
    assert operation.source == file_path
    assert operation.destination == tmp_path / "Images" / "photo.jpg"

def test_plan_sort_multiple_files(tmp_path: Path):
    files = [
        FileInfo(
            path=tmp_path / "photo.jpg",
            size=100,
            mtime=datetime.now(),
            ext=".jpg",
        ),
        FileInfo(
            path=tmp_path / "notes.txt",
            size=200,
            mtime=datetime.now(),
            ext=".txt",
        ),
        FileInfo(
            path=tmp_path / "movie.mp4",
            size=300,
            mtime=datetime.now(),
            ext=".mp4",
        ),
    ]

    operations = plan_sort(files, tmp_path)

    assert len(operations) == 3

    assert operations[0].destination == tmp_path / "Images" / "photo.jpg"
    assert operations[1].destination == tmp_path / "Documents" / "notes.txt"
    assert operations[2].destination == tmp_path / "Videos" / "movie.mp4"

def test_plan_sort_unknown_extension(tmp_path: Path):
    file = FileInfo(
        path=tmp_path / "data.xyz",
        size=100,
        mtime=datetime.now(),
        ext=".xyz",
    )

    operations = plan_sort([file], tmp_path)

    assert operations[0].destination == tmp_path / "Other" / "data.xyz"


def test_plan_sort_does_not_create_directories(tmp_path: Path):
    file_path = tmp_path / "photo.jpg"

    file = FileInfo(
        path=file_path,
        size=100,
        mtime=datetime.now(),
        ext=".jpg",
    )

    plan_sort([file], tmp_path)

    assert not (tmp_path / "Images").exists()


def test_plan_sort_detects_duplicate_destinations(tmp_path: Path):
    file1 = FileInfo(
        path=tmp_path / "folder1" / "photo.jpg",
        size=100,
        mtime=datetime.now(),
        ext=".jpg",
    )

    file2 = FileInfo(
        path=tmp_path / "folder2" / "photo.jpg",
        size=200,
        mtime=datetime.now(),
        ext=".jpg",
    )

    operations = plan_sort([file1, file2], tmp_path)

    assert operations[0].destination == operations[1].destination


def test_plan_sort_skips_duplicate_destinations(tmp_path: Path):
    file1 = FileInfo(
        path=tmp_path / "folder1" / "photo.jpg",
        size=100,
        mtime=datetime.now(),
        ext=".jpg",
    )

    file2 = FileInfo(
        path=tmp_path / "folder2" / "photo.jpg",
        size=200,
        mtime=datetime.now(),
        ext=".jpg",
    )

    operations = plan_sort([file1, file2], tmp_path)

    assert operations[0].kind == "move"
    assert operations[1].kind == "skip"
    assert operations[0].destination == operations[1].destination


def test_plan_sort_creates_move_operation(tmp_path: Path):
    file = FileInfo(
        path=tmp_path / "photo.jpg",
        size=100,
        mtime=datetime.now(),
        ext=".jpg",
    )

    operations = plan_sort([file], tmp_path)

    assert operations[0].kind == "move"


def test_plan_sort_does_not_move_source_file(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    source.write_text("test image data")

    file = FileInfo(
        path=source,
        size=source.stat().st_size,
        mtime=datetime.now(),
        ext=".jpg",
    )

    operations = plan_sort([file], tmp_path)

    assert len(operations) == 1
    assert operations[0].kind == "move"
    assert source.exists()
    assert source.read_text() == "test image data"
    assert not (tmp_path / "Images" / "photo.jpg").exists()
