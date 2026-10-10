
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from organizer.hasher import hash_file


def create_files(directory: Path, count: int = 8) -> list[Path]:
    paths = []

    for index in range(count):
        path = directory / f"file_{index}.bin"

        # Create a 16 MB test file.
        with path.open("wb") as file:
            block = b"0123456789abcdef" * 65536

            for _ in range(16):
                file.write(block)

        paths.append(path)

    return paths


def measure(label, function, paths):
    start = perf_counter()
    results = function(paths)
    elapsed = perf_counter() - start

    print(f"{label:25} {elapsed:.3f} seconds")
    assert len(results) == len(paths)


def sequential(paths):
    return [hash_file(path) for path in paths]


def threaded(paths):
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(hash_file, paths))


def processed(paths):
    with ProcessPoolExecutor(max_workers=8) as pool:
        return list(pool.map(hash_file, paths))


def main():
    with TemporaryDirectory() as temp:
        paths = create_files(Path(temp))

        # Warm up the filesystem cache before comparing approaches.
        sequential(paths)

        measure("Sequential", sequential, paths)
        measure("Threads (8 workers)", threaded, paths)
        measure("Processes (8 workers)", processed, paths)


if __name__ == "__main__":
    main()
