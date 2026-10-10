import argparse
from collections import Counter
from pathlib import Path

from organizer.duplicates import find_duplicates
from organizer.executor import execute_operation
from organizer.journal import create_run_id, undo_last
from organizer.planner import plan_sort
from organizer.scanner import scan_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe file organizer and duplicate finder.")
    commands = parser.add_subparsers(dest="command", required=True)

    organize = commands.add_parser("organize", help="Preview or execute file sorting.")
    organize.add_argument("directory", type=Path)
    organize.add_argument("--apply", action="store_true", help="Move files; default is dry-run.")

    duplicates = commands.add_parser("duplicates", help="Find exact-content duplicates.")
    duplicates.add_argument("directory", type=Path)

    stats = commands.add_parser("stats", help="Show directory statistics.")
    stats.add_argument("directory", type=Path)

    undo = commands.add_parser("undo", help="Undo the latest recorded run.")
    undo.add_argument("--last", action="store_true", required=True)
    undo.add_argument("--directory", type=Path, default=Path.cwd(),
                      help="Directory containing the journal (default: current directory)")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "undo":
        journal = args.directory.expanduser().resolve() / ".organizer-journal.jsonl"
        count = undo_last(journal)
        print(f"Undid {count} operation(s).")
        return

    directory = args.directory.expanduser().resolve()
    files = list(scan_directory(directory))

    if args.command == "organize":
        operations = plan_sort(files, directory)
        run_id = create_run_id() if args.apply else None
        journal = directory / ".organizer-journal.jsonl"
        for operation in operations:
            print(f"{operation.kind}: {operation.source} -> {operation.destination} ({operation.reason})")
            if args.apply and operation.kind == "move":
                try:
                    execute_operation(operation, journal, run_id)
                except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
                    print(f"  ERROR: {exc}")
        if not args.apply:
            print("Dry-run only. No files were moved. Use --apply to execute.")
        return

    if args.command == "duplicates":
        groups = find_duplicates(files)
        if not groups:
            print("No duplicate files found.")
            return
        for number, group in enumerate(groups, 1):
            print(f"Duplicate group {number}:")
            for item in group:
                print(f"  {item.path}")
        print(f"Found {len(groups)} duplicate group(s).")
        return

    if args.command == "stats":
        counts = Counter(item.ext or "[no extension]" for item in files)
        print(f"Directory: {directory}")
        print(f"Files: {len(files)}")
        print(f"Total bytes: {sum(item.size for item in files)}")
        for ext, count in sorted(counts.items()):
            print(f"{ext}: {count}")


if __name__ == "__main__":
    main()
