import hashlib
from pathlib import Path

def hashfile(path:Path , chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
        return h.hexdigest()

def hash_head(path:Path , n: int = 4096) -> str:
    with path.open("rb") as f:
        return hashlib.sha256(f.read(n)).hexdigest()