import os
import shutil
from pathlib import Path

from organizer.journal import record_operation
from organizer.models import Operation


def execute_operation(
    operation: Operation,
    journal_path: Path | None = None,
    run_id: str | None = None,
) -> bool:
    """Execute a move and optionally record it. Return True on successful move."""
    if operation.kind != "move":
        return False
    if operation.destination is None:
        raise ValueError("Move operation requires a destination")
    if not operation.source.is_file():
        raise FileNotFoundError(f"Source file does not exist: {operation.source}")
    if journal_path is not None and not run_id:
        raise ValueError("run_id is required when journaling a move")

    destination = operation.destination
    destination.parent.mkdir(parents=True, exist_ok=True)


    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        destination.unlink()
        shutil.move(str(operation.source), str(destination))
    except Exception:
        try:
            if destination.is_file() and destination.stat().st_size == 0:
                destination.unlink()
        except OSError:
            pass
        raise

    if journal_path is not None:
        record_operation(journal_path, operation, run_id or "")
    return True
