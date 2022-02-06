"""Unit tests for the auxiliary module that handles configuration values"""

import random
from datetime import datetime
from io import StringIO
from typing import Union

import pytest
import usersettings  # type: ignore

from gutenberg2kindle import config


def _generate_new_settings_instance() -> usersettings.Settings:
    """Mocks the config instance used by the app for each test"""

    random_id = int(datetime.now().timestamp()) + random.randint(0, 1000)
    test_app_id = f"test.gutenberg2kindle.test_{random_id}"
    return usersettings.Settings(test_app_id)


def test_get_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests for the function that retrieves a config variable"""
    monkeypatch.setattr(config, "settings", _generate_new_settings_instance())

    with pytest.raises(
        ValueError,
        match="`pokemon` is not a valid setting name"
    ):
        config.get_config("pokemon")

    test_setting_value_1 = random.randint(0, 100)
    test_setting_value_2 = f"test{random.randint(0, 100)}"
    config.settings.add_setting(
        config.SETTINGS_SMTP_PORT, int, test_setting_value_1
    )
    config.settings.add_setting(
        config.SETTINGS_SMTP_SERVER, str, test_setting_value_2
    )
    config.settings.load_settings()

    assert config.get_config(config.SETTINGS_SMTP_PORT) == test_setting_value_1
    assert (
        config.get_config(config.SETTINGS_SMTP_SERVER) == test_setting_value_2
    )

    assert config.get_config() == {
        config.SETTINGS_SMTP_PORT: test_setting_value_1,
        config.SETTINGS_SMTP_SERVER: test_setting_value_2,
    }


def test_set_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests for the function that stores a config variable"""
    monkeypatch.setattr(config, "settings", _generate_new_settings_instance())

    with pytest.raises(
        ValueError,
        match="`pokemon` is not a valid setting name"
    ):
        config.set_config("pokemon", 151)

    with pytest.raises(
        ValueError,
        match="`pokemon` is not a valid format"
    ):
        config.set_config(config.SETTINGS_FORMAT, "pokemon")

    config.settings.add_setting(
        config.SETTINGS_SMTP_SERVER, str, ""
    )
    config.settings.load_settings()

    assert config.get_config(config.SETTINGS_SMTP_SERVER) == ""
    config.set_config(config.SETTINGS_SMTP_SERVER, "mail.example.org")
    assert config.get_config(config.SETTINGS_SMTP_SERVER) == "mail.example.org"


def test_setup_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests for the function that boots up settings"""
    monkeypatch.setattr(config, "settings", _generate_new_settings_instance())

    for setting in config.AVAILABLE_SETTINGS:
        assert setting not in config.settings

    config.setup_settings()

    for setting in config.AVAILABLE_SETTINGS:
        assert setting in config.settings


def test_interactive_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests for the interactive config funcionality"""
    monkeypatch.setattr(config, "settings", _generate_new_settings_instance())
    config.setup_settings()
    default_settings: dict[str, Union[str, int]] = config.settings.copy()

    # all blank
    monkeypatch.setattr("sys.stdin", StringIO("\n\n\n\n\n"))
    config.interactive_config()
    new_settings_1 = config.get_config()
    assert default_settings == new_settings_1

    # changing values
    monkeypatch.setattr(
        "sys.stdin",
        StringIO(
            "localhost\n8080\nexample@example.org\n"
            "kindle@example.org\nno_images\n"
            )
        )
    config.interactive_config()
    new_settings_2 = config.get_config()
    assert default_settings != new_settings_2
    assert new_settings_2 == {
        "smtp_server": "localhost",
        "smtp_port": 8080,
        "sender_email": "example@example.org",
        "kindle_email": "kindle@example.org",
        "format": "no_images",
    }
