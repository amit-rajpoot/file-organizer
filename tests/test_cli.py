
from pathlib import Path

from organizer.cli import build_parser, main


def test_dry_run_is_default(tmp_path: Path):
    parser = build_parser()
    args = parser.parse_args(["organize", str(tmp_path)])

    assert args.command == "organize"
    assert args.apply is False


def test_apply_flag(tmp_path: Path):
    parser = build_parser()
    args = parser.parse_args(["organize", str(tmp_path), "--apply"])

    assert args.command == "organize"
    assert args.apply is True


def test_main_apply_moves_file(tmp_path: Path, capsys):
    source = tmp_path / "photo.jpg"
    source.write_text("test image", encoding="utf-8")

    main(["organize", str(tmp_path), "--apply"])

    destination = tmp_path / "Images" / "photo.jpg"

    assert destination.read_text(encoding="utf-8") == "test image"
    assert not source.exists()

    output = capsys.readouterr().out
    assert "move:" in output
