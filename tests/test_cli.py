"""Unit test collection for the command-line interface functions."""

import socket
import sys
from io import BytesIO
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


def test_main_config_handlers(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture,
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
    with patch.object(
        sys, "argv", ["gutenberg2kindle", "get-config"]
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert out == "a:\t\t1\nb:\t\t2\n"

    # set-config with proper params
    monkeypatch.setattr(cli, "set_config", lambda *_: None)
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "set-config",
            "--name",
            "smtp_server",
            "--value",
            "test"
        ]
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
        ]
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert (
            out == "Please specify a setting name with the `--name` flag\n"
        )

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
        ]
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert (
            out == "Please specify a setting value with the `--value` flag\n"
        )


def test_main_send_handler_if_book_is_none(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture,
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
        ]
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert (
            out == (
                "Please enter your SMTP password: \n"
                "Book `1234` could not be downloaded!\n"
            )
        )


def test_main_send_handler_if_email_cant_be_sent(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture,
) -> None:
    """
    Unit tests for the `send` handler of the CLI when the email can't be sent
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(
        cli, "download_book", lambda _: BytesIO(b"book content")
    )
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    def _send_book_monkeypatch(
        book_id: int, book: BytesIO, password: str
    ) -> None:
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
        ]
    ):
        with pytest.raises(SystemExit, match="1"):
            cli.main()
        out, _ = capfd.readouterr()
        assert (
            out == (
                "Please enter your SMTP password: \n"
                "Sending book `1234`...\n"
                "SMTP credentials are invalid! "
                "Please validate your current config.\n"
                "Server error message: smtp error!\n"
            )
        )


def test_main_send_handler_if_email_is_sent(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture,
) -> None:
    """
    Unit tests for the `send` handler of the CLI when the email is sent
    successfully
    """
    monkeypatch.setattr(cli, "setup_settings", lambda: None)
    monkeypatch.setattr(
        cli, "download_book", lambda _: BytesIO(b"book content")
    )
    monkeypatch.setattr("getpass.getpass", _getpass_mock)

    monkeypatch.setattr(cli, "send_book", lambda *_: None)
    with patch.object(
        sys,
        "argv",
        [
            "gutenberg2kindle",
            "send",
            "--book-id",
            "1234",
        ]
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert (
            out == (
                "Please enter your SMTP password: \n"
                "Sending book `1234`...\n"
                "Book `1234` sent!\n"
            )
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
        ]
    ):
        cli.main()
        out, _ = capfd.readouterr()
        assert (
            out == (
                "Please enter your SMTP password: \n"
                "Sending book `1234`...\n"
                "Book `1234` sent!\n"
                "Sending book `5678`...\n"
                "Book `5678` sent!\n"
                "Sending book `9876`...\n"
                "Book `9876` sent!\n"
                "3 books sent successfully!\n"
            )
        )
