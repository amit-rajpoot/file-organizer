from collections import defaultdict
from collections.abc import Iterable

from organizer.models import FileInfo
from organizer.hasher import hash_file, hash_first_chunk

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



def first_chunk_candidates(
    groups: dict[str, list[FileInfo]],
) -> list[FileInfo]:
    candidates = []

    for files in groups.values():
        if len(files) < 2:
            continue

        candidates.extend(files)

    return candidates

def group_by_hash(
    files: list[FileInfo],
) -> dict[str, list[FileInfo]]:
    groups: dict[str, list[FileInfo]] = {}

    for file in files:
        content_hash = hash_file(file.path)

        if content_hash not in groups:
            groups[content_hash] = []

        groups[content_hash].append(file)

    return groups

def find_duplicates(
    files: Iterable[FileInfo],
) -> list[list[FileInfo]]:
    files = list(files)

    size_groups = group_by_size(files)

    size_candidates = duplicate_candidates(size_groups)

    chunk_groups = group_by_first_chunk(size_candidates)

    chunk_candidates = first_chunk_candidates(chunk_groups)

    hash_groups = group_by_hash(chunk_candidates)

    return [
        group
        for group in hash_groups.values()
        if len(group) > 1
    ]


