
import json
from pathlib import Path

import pytest

from organizer.journal import (
    create_run_id,
    get_undo_operations,
    read_journal,
    record_operation,
    undo_last,
    undo_operation,
)
from organizer.models import Operation


def test_record_move_operation(tmp_path: Path):
    journal_path = tmp_path / "journal.jsonl"

    operation = Operation(
        kind="move",
        source=tmp_path / "photo.jpg",
        destination=tmp_path / "Images" / "photo.jpg",
        reason="Sort image file",
    )

    record_operation(journal_path, operation, "run-001")

    entry = json.loads(
        journal_path.read_text(encoding="utf-8").strip()
    )

    assert entry["kind"] == "move"
    assert entry["run_id"] == "run-001"
    assert entry["source"] == str(operation.source)
    assert entry["destination"] == str(operation.destination)


def test_skip_operation_is_not_recorded(tmp_path: Path):
    journal_path = tmp_path / "journal.jsonl"

    operation = Operation(
        kind="skip",
        source=tmp_path / "photo.jpg",
        destination=None,
        reason="Destination already planned",
    )

    record_operation(journal_path, operation, "run-001")

    assert not journal_path.exists()


def test_multiple_operations_are_appended(tmp_path: Path):
    journal_path = tmp_path / "journal.jsonl"

    first = Operation(
        kind="move",
        source=tmp_path / "photo.jpg",
        destination=tmp_path / "Images" / "photo.jpg",
        reason="Sort image",
    )

    second = Operation(
        kind="move",
        source=tmp_path / "notes.pdf",
        destination=tmp_path / "Documents" / "notes.pdf",
        reason="Sort document",
    )

    record_operation(journal_path, first, "run-001")
    record_operation(journal_path, second, "run-001")

    lines = journal_path.read_text(
        encoding="utf-8"
    ).splitlines()

    entries = [json.loads(line) for line in lines]

    assert len(entries) == 2
    assert entries[0]["source"] == str(first.source)
    assert entries[1]["source"] == str(second.source)
    assert all(
        entry["run_id"] == "run-001"
        for entry in entries
    )


def test_read_journal_returns_recorded_operations(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    operation = Operation(
        kind="move",
        source=tmp_path / "photo.jpg",
        destination=tmp_path / "Images" / "photo.jpg",
        reason="Sort image",
    )

    record_operation(journal_path, operation, "run-001")

    entries = read_journal(journal_path)

    assert len(entries) == 1
    assert entries[0]["run_id"] == "run-001"
    assert entries[0]["source"] == str(operation.source)
    assert entries[0]["destination"] == str(operation.destination)


def test_read_missing_journal_returns_empty_list(
    tmp_path: Path,
):
    journal_path = tmp_path / "missing.jsonl"

    assert read_journal(journal_path) == []


def test_read_invalid_journal_entry_raises_error(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    journal_path.write_text(
        '{"kind": "delete", "source": "/tmp/photo.jpg"}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid journal entry"):
        read_journal(journal_path)


def test_undo_operations_are_in_reverse_order(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    first = Operation(
        kind="move",
        source=tmp_path / "photo.jpg",
        destination=tmp_path / "Images" / "photo.jpg",
        reason="Sort image",
    )

    second = Operation(
        kind="move",
        source=tmp_path / "notes.pdf",
        destination=tmp_path / "Documents" / "notes.pdf",
        reason="Sort document",
    )

    record_operation(journal_path, first, "run-001")
    record_operation(journal_path, second, "run-001")

    entries = get_undo_operations(journal_path)

    assert len(entries) == 2
    assert entries[0]["source"] == str(second.source)
    assert entries[1]["source"] == str(first.source)


def test_undo_operation_restores_file(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    destination.parent.mkdir()
    destination.write_text("test image", encoding="utf-8")

    entry = {
        "kind": "move",
        "run_id": "run-001",
        "source": str(source),
        "destination": str(destination),
    }

    undo_operation(entry)

    assert source.read_text(encoding="utf-8") == "test image"
    assert not destination.exists()


def test_undo_last_restores_all_recorded_files(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    first_source = tmp_path / "photo.jpg"
    first_destination = tmp_path / "Images" / "photo.jpg"

    second_source = tmp_path / "notes.pdf"
    second_destination = tmp_path / "Documents" / "notes.pdf"

    first_destination.parent.mkdir(parents=True)
    second_destination.parent.mkdir(parents=True)

    first_destination.write_text("photo", encoding="utf-8")
    second_destination.write_text("notes", encoding="utf-8")

    record_operation(
        journal_path,
        Operation(
            kind="move",
            source=first_source,
            destination=first_destination,
            reason="Sort image",
        ),
        "run-001",
    )

    record_operation(
        journal_path,
        Operation(
            kind="move",
            source=second_source,
            destination=second_destination,
            reason="Sort document",
        ),
        "run-001",
    )

    count = undo_last(journal_path)

    assert count == 2
    assert first_source.read_text(encoding="utf-8") == "photo"
    assert second_source.read_text(encoding="utf-8") == "notes"
    assert not first_destination.exists()
    assert not second_destination.exists()


def test_create_run_id_is_unique():
    first_id = create_run_id()
    second_id = create_run_id()

    assert first_id
    assert second_id
    assert first_id != second_id


def test_read_journal_rejects_missing_run_id(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    journal_path.write_text(
        json.dumps({
            "kind": "move",
            "source": "/tmp/photo.jpg",
            "destination": "/tmp/Images/photo.jpg",
        }) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid journal entry"):
        read_journal(journal_path)


def test_undo_operations_select_only_latest_run(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    first = Operation(
        kind="move",
        source=tmp_path / "old.jpg",
        destination=tmp_path / "Images" / "old.jpg",
        reason="First run",
    )

    latest = Operation(
        kind="move",
        source=tmp_path / "new.jpg",
        destination=tmp_path / "Images" / "new.jpg",
        reason="Second run",
    )

    record_operation(journal_path, first, "run-001")
    record_operation(journal_path, latest, "run-002")

    entries = get_undo_operations(journal_path)

    assert len(entries) == 1
    assert entries[0]["run_id"] == "run-002"
    assert entries[0]["source"] == str(latest.source)


def test_undo_last_only_undoes_latest_run(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    old_source = tmp_path / "old.jpg"
    old_destination = tmp_path / "Images" / "old.jpg"

    new_source = tmp_path / "new.jpg"
    new_destination = tmp_path / "Images" / "new.jpg"

    old_destination.parent.mkdir(parents=True)
    old_destination.write_text("old content")
    new_destination.write_text("new content")

    old_operation = Operation(
        kind="move",
        source=old_source,
        destination=old_destination,
        reason="First run",
    )

    new_operation = Operation(
        kind="move",
        source=new_source,
        destination=new_destination,
        reason="Second run",
    )

    record_operation(journal_path, old_operation, "run-001")
    record_operation(journal_path, new_operation, "run-002")

    count = undo_last(journal_path)

    assert count == 1
    assert old_destination.read_text() == "old content"
    assert not old_source.exists()
    assert new_source.read_text() == "new content"
    assert not new_destination.exists()


def test_undo_last_does_not_repeat_same_run(
    tmp_path: Path,
):
    journal_path = tmp_path / "journal.jsonl"

    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    destination.parent.mkdir(parents=True)
    destination.write_text("photo content")

    operation = Operation(
        kind="move",
        source=source,
        destination=destination,
        reason="Sort image",
    )

    record_operation(journal_path, operation, "run-001")

    first_count = undo_last(journal_path)
    second_count = undo_last(journal_path)

    assert first_count == 1
    assert second_count == 0
    assert source.read_text() == "photo content"


def test_undo_last_records_undo_marker(tmp_path: Path):
    journal_path = tmp_path / "journal.jsonl"
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    destination.parent.mkdir(parents=True)
    destination.write_text("photo content", encoding="utf-8")

    operation = Operation(
        kind="move",
        source=source,
        destination=destination,
        reason="Sort image",
    )

    record_operation(journal_path, operation, "run-001")

    count = undo_last(journal_path)

    entries = [
        json.loads(line)
        for line in journal_path.read_text(encoding="utf-8").splitlines()
    ]

    assert count == 1
    assert entries[-1]["kind"] == "undo"
    assert entries[-1]["run_id"] == "run-001"


def test_undo_preserves_previous_run_history(tmp_path: Path):
    journal_path = tmp_path / "journal.jsonl"

    old_source = tmp_path / "old.txt"
    old_destination = tmp_path / "Old" / "old.txt"

    new_source = tmp_path / "new.txt"
    new_destination = tmp_path / "New" / "new.txt"

    old_destination.parent.mkdir(parents=True)
    new_destination.parent.mkdir(parents=True)

    old_destination.write_text("old content")
    new_destination.write_text("new content")

    old_operation = Operation(
        kind="move",
        source=old_source,
        destination=old_destination,
        reason="First run",
    )

    new_operation = Operation(
        kind="move",
        source=new_source,
        destination=new_destination,
        reason="Second run",
    )

    record_operation(journal_path, old_operation, "run-001")
    record_operation(journal_path, new_operation, "run-002")

    undo_last(journal_path)

    entries = read_journal(journal_path)

    assert any(
        entry["kind"] == "move"
        and entry["run_id"] == "run-001"
        for entry in entries
    )
    assert any(
        entry["kind"] == "undo"
        and entry["run_id"] == "run-002"
        for entry in entries
    )
    assert old_destination.read_text() == "old content"
    assert old_source == old_source


def test_undo_does_not_overwrite_existing_source(tmp_path: Path):
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"

    destination.parent.mkdir(parents=True)
    source.write_text("original content", encoding="utf-8")
    destination.write_text("moved content", encoding="utf-8")

    entry = {
        "kind": "move",
        "run_id": "run-001",
        "source": str(source),
        "destination": str(destination),
    }

    with pytest.raises(FileExistsError):
        undo_operation(entry)

    assert source.read_text(encoding="utf-8") == "original content"
    assert destination.read_text(encoding="utf-8") == "moved content"
