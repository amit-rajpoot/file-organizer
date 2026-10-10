
import resource
from pathlib import Path
from tempfile import TemporaryDirectory

from organizer.hasher import hash_file


def peak_rss_mb() -> float:
    # Linux reports ru_maxrss in KiB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def main():
    with TemporaryDirectory() as temp:
        path = Path(temp) / "large_test.bin"

        # Create a 2 GiB sparse file.
        with path.open("wb") as file:
            file.truncate(2 * 1024**3)

        print(f"File size: {path.stat().st_size / 1024**3:.2f} GiB")

        digest = hash_file(path)

        print(f"SHA-256: {digest}")
        print(f"Peak process RSS: {peak_rss_mb():.2f} MiB")

        if peak_rss_mb() < 100:
            print("PASS: Peak RSS is below 100 MiB.")
        else:
            print("CHECK: Peak RSS reached 100 MiB or more.")


if __name__ == "__main__":
    main()
