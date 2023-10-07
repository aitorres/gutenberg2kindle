"""Unit tests for the email helper module"""

from gutenberg2kindle import email


def test_create_base_email() -> None:
    """Unit tests to check that the base email is created properly"""

    sender_email = "sender@example.com"
    kindle_email = "kindle@example.com"

    message = email.create_base_email(sender_email, kindle_email)
    text = message.as_string()

    assert "Content-Type: multipart/mixed" in text
    assert "From: sender@example.com" in text
    assert "To: kindle@example.com" in text
    assert "Subject: Your Project Gutenberg ebook!" in text
    assert "- Sent with gutenberg2kindle. Happy reading!" in text


def test_bytes_to_mb() -> None:
    """Unit test to check that the bytes to MB calculation is done properly"""

    assert email.bytes_to_mb(0) == 0
    assert email.bytes_to_mb(1) == 1
    assert email.bytes_to_mb(1024) == 1
    assert email.bytes_to_mb(1025) == 1
    assert email.bytes_to_mb(1048576) == 1
    assert email.bytes_to_mb(1048577) == 2
    assert email.bytes_to_mb(10485760) == 10
    assert email.bytes_to_mb(10485761) == 11
    assert email.bytes_to_mb(104857600) == 100
