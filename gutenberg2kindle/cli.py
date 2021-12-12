"""
Functions and other helpers for `gutenberg2kindle`'s command-line interface.
"""

import argparse
import socket
import sys
from typing import Final, Optional, Union

from gutenberg2kindle.config import (
    AVAILABLE_SETTINGS,
    get_config,
    set_config,
    setup_settings,
)
from gutenberg2kindle.email import send_book
from gutenberg2kindle.gutenberg import download_book

COMMAND_SEND: Final[str] = "send"
COMMAND_GET_CONFIG: Final[str] = "get-config"
COMMAND_SET_CONFIG: Final[str] = "set-config"
AVAILABLE_COMMANDS: Final[list[str]] = [
    COMMAND_SEND,
    COMMAND_GET_CONFIG,
    COMMAND_SET_CONFIG,
]


def get_parser() -> argparse.ArgumentParser:
    """
    Generate and return a parser for the CLI tool
    """
    parser = argparse.ArgumentParser(
        prog="gutenberg2kindle",
        description=(
            "A CLI tool to download and send ebooks "
            "from Project Gutenberg to a Kindle email "
            "address via SMTP"
        ),
        epilog="Happy reading! :-)"
    )
    parser.add_argument(
        "command",
        metavar="COMMAND",
        type=str,
        choices=AVAILABLE_COMMANDS,
        help=(
            "Command to use. Supported options allow the user to "
            "either set the tool's config options, read the current "
            "config, or send some books using the current config."
        ),
    )
    parser.add_argument(
        "--book-id",
        metavar="BOOK_ID",
        type=int,
        help=(
            "ID of the Project Gutenberg book you want to download."
        ),
    )
    parser.add_argument(
        "--name",
        metavar="NAME",
        type=str,
        choices=AVAILABLE_SETTINGS,
        help=(
            "Setting to get / set, whenever these commands are used."
        ),
    )
    parser.add_argument(
        "--value",
        metavar="VALUE",
        type=str,
        help=(
            "Value to set for the specified setting name, if required."
        ),
    )

    return parser


def format_setting(name: str, value: Union[str, int]) -> str:
    """Formats a setting with its value for printing"""
    return f"{name}:\t\t{value}"


def main() -> None:
    """
    Run the tool's CLI
    """

    # setup tool
    setup_settings()

    # parse arguments
    parser = get_parser()
    args = parser.parse_args()

    # cast certain arguments to expected types
    command: str = args.command
    name: Optional[str] = args.name
    value: Optional[str] = args.value

    if command == "send":
        book_id: int = args.book_id
        book = download_book(book_id)

        if book is None:
            print(f"Book `{book_id}` could not be downloaded!")
            sys.exit(1)

        print("Sending book...")
        try:
            send_book(book_id, book)
        except socket.error as err:  # pylint: disable=no-member
            print(
                "SMTP credentials are invalid! "
                "Please validate your current config.\n"
                f"Server error message: {err}"
            )
            sys.exit(1)

        print("Book sent!")

    elif command == "get-config":
        stored_value = get_config(name)

        if isinstance(stored_value, dict):
            for setting_name, setting_value in stored_value.items():
                print(format_setting(setting_name, setting_value))
        else:
            print(stored_value)

    elif command == "set-config":
        if name is None:
            print("Please specify a setting name with the `--name` flag")
            sys.exit(1)

        if value is None:
            print("Please specify a setting value with the `--value` flag")
            sys.exit(1)

        set_config(name, value)
        print(format_setting(name, value))


if __name__ == "__main__":
    main()
