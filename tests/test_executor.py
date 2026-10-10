
from pathlib import Path

import pytest

from organizer.executor import execute_operation
from organizer.models import Operation


def test_execute_move(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    source.write_text("test image")

    operation = Operation(
        kind="move",
        source=source,
        destination=destination,
        reason="Test move",
    )

    execute_operation(operation)

    assert not source.exists()
    assert destination.read_text() == "test image"


def test_execute_move_rejects_existing_destination(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    source.write_text("new content")
    destination.parent.mkdir()
    destination.write_text("important existing content")

    operation = Operation(
        kind="move",
        source=source,
        destination=destination,
        reason="Test collision",
    )

    with pytest.raises(FileExistsError):
        execute_operation(operation)

    assert source.read_text() == "new content"
    assert destination.read_text() == "important existing content"


def test_execute_skip_does_nothing(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    source.write_text("original content")

    operation = Operation(
        kind="skip",
        source=source,
        destination=tmp_path / "Images" / "photo.jpg",
        reason="Destination collision",
    )

    execute_operation(operation)

    assert source.exists()
    assert source.read_text() == "original content"
    assert not (tmp_path / "Images").exists()


def test_execute_move_without_destination(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    source.write_text("original content")

    operation = Operation(
        kind="move",
        source=source,
        destination=None,
        reason="Missing destination",
    )

    with pytest.raises(
        ValueError,
        match="Move operation requires a destination",
    ):
        execute_operation(operation)

    assert source.exists()
    assert source.read_text() == "original content"


def test_execute_move_missing_source(tmp_path: Path):
    source = tmp_path / "missing.jpg"
    destination = tmp_path / "Images" / "missing.jpg"

    operation = Operation(
        kind="move",
        source=source,
        destination=destination,
        reason="Source file missing",
    )

    with pytest.raises(FileNotFoundError):
        execute_operation(operation)

    assert not destination.exists()


def test_execute_move_preserves_existing_destination(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    source.write_text("new content")
    destination.parent.mkdir()
    destination.write_text("important existing content")

    operation = Operation(
        kind="move",
        source=source,
        destination=destination,
        reason="Test overwrite protection",
    )

    with pytest.raises(FileExistsError):
        execute_operation(operation)

    assert source.read_text() == "new content"
    assert destination.read_text() == "important existing content"
