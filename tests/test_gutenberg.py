"""Unit tests for the helper functions that connect to Project Gutenberg"""

from dataclasses import dataclass

import pytest

from gutenberg2kindle import gutenberg


@dataclass(frozen=True)
class ResponseMock:
    """
    Wrapper to mock a `requests` response during unit tests
    """

    content: bytes
    status_code: int = 200


def test_download_book(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture,
) -> None:
    """Unit test for the function that downloads a book's content"""

    # error
    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            b"",
            status_code=500
        )
    )
    book_response_1 = gutenberg.download_book(12345)
    out, _ = capfd.readouterr()
    assert book_response_1 is None
    assert out == "Invalid status code `500` while fetching book 12345\n"

    # success
    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            b"book content",
            status_code=200
        )
    )
    book_response_2 = gutenberg.download_book(12345)
    assert book_response_2 is not None
    assert book_response_2.read() == b"book content"
