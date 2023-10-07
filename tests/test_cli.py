"""Unit test collection for the command-line interface functions."""

import socket
import sys
from io import BytesIO
from typing import Optional
from unittest.mock import patch

import pytest

from gutenberg2kindle import cli


def _getpass_mock(message: str) -> str:
    print(message)
    return "m0ck-p4ssw0rd"


def test_get_parser() -> None:
    """
    Unit tests for the function that returns a parser for
    the tool's CLi
    """

    parser = cli.get_parser()
    assert isinstance(parser.description, str)
    assert "A CLI tool" in parser.description
    assert parser.epilog == "Happy reading! :-)"


def test_format_setting() -> None:
    """Unit tests for the setting formatting function"""

    assert cli.format_setting("name", "value") == "name:\t\tvalue"
    assert cli.format_setting("smtp_port", "123") == "smtp_port:\t\t123"


def test_version_handler(capfd: pytest.CaptureFixture) -> None:
    """Unit tests for the version handler of the CLI"""

    with patch.object(sys, "argv", ["gutenberg2kindle", "version"]):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == f"gutenberg2kindle version {cli.__version__}\n"


def test_main_config_handlers(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """Unit tests for the get-config and set-config handlers of the CLI"""
    monkeypatch.setattr(cli, "setup_settings", lambda: None)

    # get-config with name
    monkeypatch.setattr(cli, "get_config", lambda _: "test-value")
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "get-config",
            "--name",
            "smtp_server",
        ],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == "test-value\n"

    # get-config without name
    monkeypatch.setattr(cli, "get_config", lambda _: {"a": 1, "b": 2})
    with patch.object(sys, "argv", ["gutenberg2kindle", "get-config"]):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == "a:\t\t1\nb:\t\t2\n"

    # set-config with proper params
    monkeypatch.setattr(cli, "set_config", lambda *_: None)
    with patch.object(
        sys,
        "argv",
        ["gutenberg2kindle", "set-config", "--name", "smtp_server", "--value", "test"],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == "smtp_server:\t\ttest\n"

    # set-config without name
    monkeypatch.setattr(cli, "set_config", lambda *_: None)
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "set-config",
        ],
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert out == "Please specify a setting name with the `--name` flag\n"

    # set-config without value
    monkeypatch.setattr(cli, "set_config", lambda *_: None)
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "set-config",
            "--name",
            "smtp_server",
        ],
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert out == "Please specify a setting value with the `--value` flag\n"


def test_main_send_handler_if_book_is_none(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when a book can't be found
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", lambda _: None)
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--book-id",
            "1234",
        ],
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Book `1234` could not be downloaded!\n"
        )


def test_main_send_handler_if_book_is_none_with_ignore_errors(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when a book can't be found
    but the user requests to ignore errors
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", lambda _: None)
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--ignore-errors",
            "--book-id",
            "1234",
        ],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Book `1234` could not be downloaded!\n"
            "Skipping book `1234`...\n"
        )


def test_main_send_handler_if_book_is_none_multiple_books(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when a book can't be found
    and multiple books were requested
    """

    def _download_book(book_id: int) -> Optional[BytesIO]:
        if book_id == 5678:
            return None
        return BytesIO(b"test")

    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", _download_book)
    monkeypatch.setattr("getpass.getpass", _getpass_mock)
    monkeypatch.setattr(cli, "send_book", lambda book_id, *_: book_id != "5678")

    with patch.object(
        sys, "argv", ["gutenberg2kindle", "send", "--book-id", "1234", "5678", "9101"]
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Sending book `1234`...\n"
            "Book `1234` sent!\n"
            "Book `5678` could not be downloaded!\n"
        )


def test_main_send_handler_if_book_is_none_multiple_books_with_ignore_errors(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when a book can't be found
    and multiple books were requested when the user asks to ignore errors
    """

    def _download_book(book_id: int) -> Optional[BytesIO]:
        if book_id == 5678:
            return None
        return BytesIO(b"test")

    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", _download_book)
    monkeypatch.setattr("getpass.getpass", _getpass_mock)
    monkeypatch.setattr(cli, "send_book", lambda book_id, *_: book_id != "5678")

    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--ignore-errors",
            "--book-id",
            "1234",
            "5678",
            "9101",
        ],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Sending book `1234`...\n"
            "Book `1234` sent!\n"
            "Book `5678` could not be downloaded!\n"
            "Skipping book `5678`...\n"
            "Sending book `9101`...\n"
            "Book `9101` sent!\n"
            "2 books sent successfully!\n"
        )


def test_main_send_handler_if_email_cant_be_sent(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when the email can't be sent
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", lambda _: BytesIO(b"book content"))
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    def _send_book_monkeypatch(book_id: int, book: BytesIO, password: str) -> None:
        raise socket.error("smtp error!")

    monkeypatch.setattr(cli, "send_book", _send_book_monkeypatch)

    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--book-id",
            "1234",
        ],
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Sending book `1234`...\n"
            "SMTP credentials are invalid! "
            "Please validate your current config.\n"
            "Server error message: smtp error!\n"
        )


def test_main_send_handler_if_email_is_sent(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when the email is sent
    successfully
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", lambda _: BytesIO(b"book content"))
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    monkeypatch.setattr(cli, "send_book", lambda *_: True)
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--book-id",
            "1234",
        ],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Sending book `1234`...\n"
            "Book `1234` sent!\n"
        )

    # multiple books at once
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--book-id",
            "1234",
            "5678",
            "9876",
        ],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Sending book `1234`...\n"
            "Book `1234` sent!\n"
            "Sending book `5678`...\n"
            "Book `5678` sent!\n"
            "Sending book `9876`...\n"
            "Book `9876` sent!\n"
            "3 books sent successfully!\n"
        )


def test_main_send_handler_max_file_size_limit(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture
) -> None:
    """
    Unit tests for the `send` handler of the CLI when one book exceeds
    the file size limit.

    Note that this only tests that the right message appears, as it doesn't actually
    reach the `send_book` function.
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(cli, "download_book", lambda _: BytesIO(b"book content"))
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    monkeypatch.setattr(cli, "send_book", lambda book_id, *_: book_id != 5678)

    # multiple books at once
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--book-id",
            "1234",
            "5678",
            "9876",
        ],
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == (
            "Please enter your SMTP password: \n"
            "Sending book `1234`...\n"
            "Book `1234` sent!\n"
            "Sending book `5678`...\n"
            "Book `5678` could not be sent, please check its file size.\n"
            "Sending book `9876`...\n"
            "Book `9876` sent!\n"
            "2 books sent successfully!\n"
        )
