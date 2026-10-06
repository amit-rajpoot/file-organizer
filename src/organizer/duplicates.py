from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

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

def get_content_hash(
    file: FileInfo,
    hash_cache: dict[Path, tuple[int, float, str]],
) -> str:
    if file.content_hash is not None:
        return file.content_hash

    current_size = file.path.stat().st_size
    current_mtime = file.path.stat().st_mtime

    cached = hash_cache.get(file.path)

    if cached is not None:
        cached_size, cached_mtime, cached_hash = cached

        if (
            cached_size == current_size
            and cached_mtime == current_mtime
        ):
            return cached_hash

    content_hash = hash_file(file.path)

    hash_cache[file.path] = (
        current_size,
        current_mtime,
        content_hash,
    )

    return content_hash

def group_by_hash(
    files: list[FileInfo],
    hash_cache: dict[Path, tuple[int, float, str]] | None = None,
) -> dict[str, list[FileInfo]]:
    if hash_cache is None:
        hash_cache = {}

    groups: dict[str, list[FileInfo]] = {}

    for file in files:
        content_hash = get_content_hash(
            file,
            hash_cache,
        )

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

    hash_cache: dict[Path, tuple[int, float, str]] = {}

    hash_groups = group_by_hash(
    chunk_candidates,
    hash_cache
    )

    return [
        group
        for group in hash_groups.values()
        if len(group) > 1
    ]


