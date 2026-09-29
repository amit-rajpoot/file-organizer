import hashlib
from pathlib import Path

# READ -> HASH -> RETURN

def hash_file(path:Path , chunk_size: int = 65536) -> str:
    h = hashlib.sha256() 
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)

        return h.hexdigest()

def hash_first_chunk(path: Path, chunk_size: int = 4096) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        chunk = file.read(chunk_size)

    hasher.update(chunk)

    return hasher.hexdigest()