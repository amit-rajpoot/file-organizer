from pathlib import Path

from organizer.models import FileInfo, Operation


EXT_FOLDERS = {
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",

    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",

    ".mp4": "Videos",
    ".mkv": "Videos",

    ".mp3": "Music",
    ".wav": "Music",

    ".zip": "Archives",
    ".rar": "Archives",
}


def folder_for_ext(ext:str) -> str:
    return EXT_FOLDERS.get(ext.lower(),"Other")


def plan_sort(
    files: list[FileInfo],
    root: Path,
) -> list[Operation]:
    operations: list[Operation] = []
    planned_destinations: set[Path] = set()

    for file in files:
        folder = folder_for_ext(file.ext)
        destination = root / folder / file.path.name

        if destination in planned_destinations: #for skip the file
            file_skip = Operation(
                kind="skip",
                source=file.path,
                destination=destination,
                reason="Destination collision: another file has the same destination",
            )

            operations.append(file_skip)
            continue

        planned_destinations.add(destination)

        file_move = Operation(
            kind="move",
            source=file.path,
            destination=destination,
            reason=f"Sort {file.ext} file into {folder}",
        )

        operations.append(file_move)

    return operations
