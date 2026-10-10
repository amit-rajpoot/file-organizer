
import json
from pathlib import Path
import shutil
import uuid

from organizer.models import Operation

def create_run_id() -> str:
    return uuid.uuid4().hex

def record_operation(
    journal_path: Path,
    operation: Operation,
    run_id: str
) -> None:
    if operation.kind != "move":
        return

    if operation.destination is None:
        raise ValueError("Move operation requires a destination")

    if not run_id:
        raise ValueError("run_id cannot be empty")
    
    entry = {
        "kind": "move",
        "run_id": run_id,
        "source": str(operation.source),
        "destination": str(operation.destination),
    }

    journal_path.parent.mkdir(parents=True, exist_ok=True)

    with journal_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")



def read_journal(journal_path: Path) -> list[dict[str, str]]:
    if not journal_path.exists():
        return []

    entries: list[dict[str, str]] = []

    with journal_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid journal entry") from exc

            if not isinstance(entry, dict):
                raise ValueError("Invalid journal entry")

            kind = entry.get("kind")

            if kind == "move":
                valid = (
                    isinstance(entry.get("run_id"), str)
                    and bool(entry["run_id"])
                    and isinstance(entry.get("source"), str)
                    and isinstance(entry.get("destination"), str)
                )
            elif kind == "undo":
                valid = (
                    isinstance(entry.get("run_id"), str)
                    and bool(entry["run_id"])
                )
            else:
                valid = False

            if not valid:
                raise ValueError("Invalid journal entry")

            entries.append(entry)

    return entries



def get_undo_operations(
    journal_path: Path,
) -> list[dict[str, str]]:
    entries = read_journal(journal_path)

    if not entries:
        return []

    undone_runs = {
        entry["run_id"]
        for entry in entries
        if entry["kind"] == "undo"
    }

    move_entries = [
        entry for entry in entries
        if entry["kind"] == "move"
    ]

    if not move_entries:
        return []

    latest_run_id = move_entries[-1]["run_id"]

    if latest_run_id in undone_runs:
        return []

    latest_entries = [
        entry for entry in move_entries
        if entry["run_id"] == latest_run_id
    ]

    return list(reversed(latest_entries))

def undo_operation(entry: dict[str, str]) -> None:
    source = Path(entry["source"])
    destination = Path(entry["destination"])

    if not destination.is_file():
        raise FileNotFoundError(
            f"Moved file not found: {destination}"
        )

    if source.exists():
        raise FileExistsError(
            f"Original location already exists: {source}"
                              )

    source.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(destination), str(source))


def undo_last(journal_path: Path) -> int:
    entries = get_undo_operations(journal_path)

    if not entries:
        return 0

    run_id = entries[0]["run_id"]

    for entry in entries:
        undo_operation(entry)

    undo_entry = {
        "kind": "undo",
        "run_id": run_id,
    }

    with journal_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(undo_entry) + "\n")

    return len(entries)



