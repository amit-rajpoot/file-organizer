
from organizer import main


def test_main(capsys):
    main()

    captured = capsys.readouterr()

    assert captured.out == "Hello from file-organizer!\n"
