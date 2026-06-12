import threading
import time
import keyboard
import mouse
import config

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
        self.after_func = None

    def capture_binding(self):
        while self.is_listening:
            key_event = keyboard.read_event(suppress=True)
            if key_event.event_type == keyboard.KEY_DOWN:
                self.selected_element = key_event.name
                self.element_type = "key"
                break
        self.is_listening = False
        if self.after_func and self.on_update_ui:
            self.after_func(0, self.on_update_ui)

    def start_binding(self):
        self.is_listening = True
        threading.Thread(target=self.capture_binding, daemon=True).start()

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
                    pass
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
                    pass
            time.sleep(self.delay_seconds)

    def start_macro(self, delay):
        self.delay_seconds = delay
        self.macro_running = True
        threading.Thread(target=self.clicker_loop, daemon=True).start()

    def stop_macro(self):
        self.macro_running = False
