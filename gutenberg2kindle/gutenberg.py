"""Auxiliary functions to connect to Project Gutenberg's library"""

from io import BytesIO
from typing import Final, Optional

import requests

GUTENBERG_BOOK_BASE_URL: Final[str] = (
    "https://www.gutenberg.org/ebooks/{book_id}.kindle"
)


def download_book(book_id: int) -> Optional[BytesIO]:
    """
    Given a Gutenberg book ID as an integer, fetches the content
    of the book into memory and returns it wrapped in a BytesIO
    instance
    """

    book_url = GUTENBERG_BOOK_BASE_URL.format(book_id=book_id)

    response = requests.get(book_url)
    if response.status_code != 200:
        print(
            f"Invalid status code `{response.status_code}` "
            f"while fetching book {book_id}"
        )
        return None
    book_content = response.content

    memory_bytes = BytesIO()
    memory_bytes.write(book_content)
    memory_bytes.seek(0)
    return memory_bytes
