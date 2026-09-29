from collections import defaultdict
from collections.abc import Callable , Iterable
from pathlib import Path

from organizer.models import FileInfo , Operation

hashFn = Callable[[Path],str]

EXT_FOLDERS = {
    "Images": {"jpg", "jpeg", "png", "gif", "webp", "bmp"},
    "Documents": {"pdf", "doc", "docx", "txt", "md", "odt"},
    "Videos": {"mp4", "mkv", "mov", "avi"},
    "Audio": {"mp3", "wav", "flac", "m4a"},
    "Archives": {"zip", "tar", "gz", "rar", "7z"},
}

def folder_for_ext(ext: str) -> str:
    for folder ,exts in EXT_FOLDERS.items():
        if ext in exts:
            return folder
    return "Other"

