from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from organizer.models import FileInfo
from organizer.hasher import hash_first_chunk

def group_by_size(
        files: Iterable[FileInfo]
        ) -> dict[int, list[FileInfo]]:
    groups: dict[int, list[FileInfo]] = defaultdict(list)

    for file in files:
        groups[file.size].append(file)

    return dict(groups)

def duplicate_candidates(
        groups: dict[int, list[FileInfo]]
        ) -> list[FileInfo]:

    candidates = []

    for files in groups.values():
        if len(files) < 2:
            continue

        candidates.extend(files)

    return candidates

def group_by_first_chunk(
        files: list[FileInfo],        
) -> dict[str, list[FileInfo]]:

    groups: dict[str, list[FileInfo]] = {}

    for file in files:
        chunk_hash = hash_first_chunk(file.path)

        if chunk_hash not in groups:
            groups[chunk_hash] = []

        groups[chunk_hash].append(file)

    return groups