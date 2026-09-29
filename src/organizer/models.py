from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class FileInfo:
    path: Path
    size: int
    mtime: datetime
    ext: str
    content_hash: str | None = None


@dataclass(frozen=True)
class Operation:
    kind: Literal["move", "delete", "skip"]
    source: Path
    destination: Path | None
    reason: str