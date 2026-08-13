import json
import time
from unittest.mock import MagicMock, patch

import pytest

import binder as binder_module
from binder import Binder


@pytest.fixture(autouse=True)
def isolated_settings_path(tmp_path, monkeypatch):
    settings_file = tmp_path / "user_settings.json"
    monkeypatch.setattr(binder_module, "SETTINGS_PATH", str(settings_file))
    return settings_file


class _FakeButtonEvent:
    def __init__(self, event_type, button):
        self.event_type = event_type
        self.button = button


@pytest.fixture(autouse=True)
def mocked_io_libs():
    with patch.object(binder_module, "keyboard") as mock_keyboard, \
            patch.object(binder_module, "mouse") as mock_mouse:
        mock_keyboard.KEY_DOWN = "down"
        mock_mouse.DOWN = "down"
        mock_mouse.ButtonEvent = _FakeButtonEvent
        yield mock_keyboard, mock_mouse


def test_start_macro_sets_running_and_spawns_thread():
    b = Binder()
    b.selected_element = "a"
    b.element_type = "key"
    b.start_macro(0.01)
    assert b.macro_running is True
    time.sleep(0.03)
    b.stop_macro()
    assert b.macro_running is False


def test_start_macro_is_idempotent_while_running():
    b = Binder()
    b.selected_element = "a"
    b.element_type = "key"
    b.start_macro(1.0)
    with patch("threading.Thread") as mock_thread:
        b.start_macro(1.0)
        mock_thread.assert_not_called()
    b.stop_macro()


def test_finish_binding_sets_key_and_saves(mocked_io_libs):
    b = Binder()
    event = MagicMock()
    event.event_type = "down"
    event.name = "f"
    b.is_listening = True
    b._on_key_event(event)
    assert b.element_type == "key"
    assert b.selected_element == "f"
    assert b.is_listening is False


def test_finish_binding_cancelled_on_escape(mocked_io_libs):
    b = Binder()
    b.element_type = "key"
    b.selected_element = "old"
    event = MagicMock()
    event.event_type = "down"
    event.name = "esc"
    b.is_listening = True
    b._on_key_event(event)
    assert b.is_listening is False
    assert b.selected_element == "old"
    assert b.element_type == "key"


def test_mouse_binding(mocked_io_libs):
    b = Binder()
    event = _FakeButtonEvent(event_type="down", button="right")
    b.is_listening = True
    b._on_mouse_event(event)
    assert b.element_type == "mouse"
    assert b.selected_element == "right"


def test_save_and_load_settings_roundtrip(isolated_settings_path):
    b = Binder()
    b.element_type = "key"
    b.selected_element = "x"
    b.delay_seconds = 2.5
    b.hold_enabled = True
    b.hold_duration = 0.3
    b.save_settings()

    assert isolated_settings_path.exists()
    data = json.loads(isolated_settings_path.read_text())
    assert data["selected_element"] == "x"
    assert data["delay_seconds"] == 2.5

    b2 = Binder()
    assert b2.element_type == "key"
    assert b2.selected_element == "x"
    assert b2.delay_seconds == 2.5
    assert b2.hold_enabled is True
    assert b2.hold_duration == 0.3


def test_load_settings_ignores_missing_file(isolated_settings_path):
    b = Binder()
    assert b.selected_element is None
    assert b.delay_seconds == 1.0


def test_load_settings_ignores_corrupt_file(isolated_settings_path):
    isolated_settings_path.write_text("{not valid json")
    b = Binder()
    assert b.selected_element is None
