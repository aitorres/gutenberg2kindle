"""Unit tests for the helper functions that connect to Project Gutenberg"""

from dataclasses import dataclass

import pytest

from gutenberg2kindle import gutenberg
from gutenberg2kindle.config import (
    FORMAT_AUTO,
    FORMAT_IMAGES,
    FORMAT_NO_IMAGES,
)


@dataclass(frozen=True)
class ResponseMock:
    """
    Wrapper to mock a `requests` response during unit tests
    """

    content: bytes
    status_code: int = 200


def test_fetch_book_from_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Unit test for the function that downloads a book's content
    from the book's URL.
    """

    # error
    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            b"",
            status_code=500
        )
    )
    book_response_1 = gutenberg.fetch_book_from_url(
        "https://www.gutenberg.org/ebooks/1.kindle"
    )
    assert book_response_1 is None

    # success
    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            b"book content",
            status_code=200
        )
    )
    book_response_2 = gutenberg.fetch_book_from_url(
        "https://www.gutenberg.org/ebooks/1.kindle"
    )
    assert book_response_2 is not None
    assert book_response_2.read() == b"book content"


def test_download_book(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Unit test for the function that downloads a book's content
    from the book's ID, determining the file to download from the set
    format.
    """

    monkeypatch.setattr(
        "requests.get",
        lambda url: ResponseMock(
            (
                b"image book content"
                if ".images" in url
                else b"book content"
            ),
            status_code=200
        )
    )
    book_id = 1234

    # no images
    monkeypatch.setattr(gutenberg, "get_config", lambda _: FORMAT_NO_IMAGES)
    book_response_1 = gutenberg.download_book(book_id)
    assert book_response_1 is not None
    assert book_response_1.read() == b"book content"

    # images
    monkeypatch.setattr(gutenberg, "get_config", lambda _: FORMAT_IMAGES)
    book_response_2 = gutenberg.download_book(book_id)
    assert book_response_2 is not None
    assert book_response_2.read() == b"image book content"

    # auto, image available
    monkeypatch.setattr(gutenberg, "get_config", lambda _: FORMAT_AUTO)
    book_response_3 = gutenberg.download_book(book_id)
    assert book_response_3 is not None
    assert book_response_3.read() == b"image book content"

    # auto, image not available
    monkeypatch.setattr(
        "requests.get",
        lambda url: ResponseMock(
            (
                b"image book content"
                if ".images" in url
                else b"book content"
            ),
            status_code=(
                500 if ".images" in url else 200
            )
        )
    )
    book_response_3 = gutenberg.download_book(book_id)
    assert book_response_3 is not None
    assert book_response_3.read() == b"book content"

    # invalid format
    monkeypatch.setattr(gutenberg, "get_config", lambda _: "INVALID_FORMAT")
    with pytest.raises(ValueError, match="INVALID_FORMAT is an invalid format"):
        gutenberg.download_book(book_id)
