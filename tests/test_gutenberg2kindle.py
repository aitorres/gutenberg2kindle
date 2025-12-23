"""General unit tests for the project"""

from gutenberg2kindle import __version__


def test_version():
    """Ensure that Python's version variable has the expected value"""

    assert __version__ == "0.8.0"
