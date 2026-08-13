import json
import logging
import os
import threading
import time

import keyboard
import mouse

import config

logger = logging.getLogger(__name__)

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_settings.json")


class Binder:
    def __init__(self):
        self.selected_element = None
        self.element_type = None
        self.is_listening = False
        self.macro_running = False
        self.delay_seconds = 1.0
        self.hold_enabled = config.HOLD_ENABLED
        self.hold_duration = config.HOLD_DURATION
        self.on_update_ui = None
        self.on_cancel_ui = None
        self.after_func = None
        self._macro_lock = threading.Lock()
        self._bind_lock = threading.Lock()

        self.load_settings()

    # ---- persistence ----
    def load_settings(self):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return
        self.element_type = data.get("element_type", self.element_type)
        self.selected_element = data.get("selected_element", self.selected_element)
        self.delay_seconds = data.get("delay_seconds", self.delay_seconds)
        self.hold_enabled = data.get("hold_enabled", self.hold_enabled)
        self.hold_duration = data.get("hold_duration", self.hold_duration)

    def save_settings(self):
        data = {
            "element_type": self.element_type,
            "selected_element": self.selected_element,
            "delay_seconds": self.delay_seconds,
            "hold_enabled": self.hold_enabled,
            "hold_duration": self.hold_duration,
        }
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            logger.exception("Failed to save settings to %s", SETTINGS_PATH)

    # ---- binding capture ----
    def _on_key_event(self, event):
        if event.event_type != keyboard.KEY_DOWN:
            return
        if event.name == "esc":
            self._finish_binding(cancelled=True)
            return
        self._finish_binding(element_type="key", element=event.name)

    def _on_mouse_event(self, event):
        if isinstance(event, mouse.ButtonEvent) and event.event_type == mouse.DOWN:
            self._finish_binding(element_type="mouse", element=event.button)

    def _finish_binding(self, element_type=None, element=None, cancelled=False):
        with self._bind_lock:
            if not self.is_listening:
                return
            self.is_listening = False
            keyboard.unhook(self._on_key_event)
            mouse.unhook(self._on_mouse_event)
            if not cancelled:
                self.element_type = element_type
                self.selected_element = element
                self.save_settings()

        if not self.after_func:
            return
        if cancelled:
            if self.on_cancel_ui:
                self.after_func(0, self.on_cancel_ui)
        elif self.on_update_ui:
            self.after_func(0, self.on_update_ui)

    def start_binding(self):
        if self.is_listening or self.macro_running:
            return
        self.is_listening = True
        keyboard.hook(self._on_key_event, suppress=True)
        mouse.hook(self._on_mouse_event)

    # ---- macro loop ----
    def clicker_loop(self):
        while self.macro_running:
            if self.element_type == "key":
                try:
                    if self.hold_enabled:
                        keyboard.press(self.selected_element)
                        time.sleep(self.hold_duration)
                        keyboard.release(self.selected_element)
                    else:
                        keyboard.send(self.selected_element)
                except Exception:
                    logger.exception("Failed to send key %r", self.selected_element)
            elif self.element_type == "mouse":
                try:
                    btn = self.selected_element
                    if btn == "middle":
                        btn = "wheel"
                    if self.hold_enabled:
                        mouse.press(button=btn)
                        time.sleep(self.hold_duration)
                        mouse.release(button=btn)
                    else:
                        mouse.click(button=btn)
                except Exception:
                    logger.exception("Failed to send mouse click %r", self.selected_element)
            time.sleep(self.delay_seconds)

    def start_macro(self, delay):
        with self._macro_lock:
            if self.macro_running:
                return
            self.delay_seconds = delay
            self.macro_running = True
            self.save_settings()
            threading.Thread(target=self.clicker_loop, daemon=True).start()

    def stop_macro(self):
        with self._macro_lock:
            self.macro_running = False

    def shutdown(self):
        self.stop_macro()
        if self.is_listening:
            self._finish_binding(cancelled=True)
