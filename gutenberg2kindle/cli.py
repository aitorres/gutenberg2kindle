"""
Functions and other helpers for `gutenberg2kindle`'s command-line interface.
"""

import argparse
from typing import Final

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

    return parser


def main() -> None:
    """
    Run the tool's CLI
    """

    get_parser()
    raise NotImplementedError("CLI not implemented!")


if __name__ == "__main__":
    main()
