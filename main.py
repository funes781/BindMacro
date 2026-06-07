import threading
import time
import tkinter as tk
from tkinter import messagebox
import keyboard  # Low-level keyboard operations
import mouse  # Low-level mouse operations

# ==========================================
# CONFIGURATION
# ==========================================
START_KEY = "."

# --- Global Variables ---
selected_element = None
element_type = None
is_listening = False
macro_running = False
delay_seconds = 1.0


def center_window(window, width=420, height=130):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


# --- 1. Binding Logic ---
def capture_binding():
    global selected_element, element_type, is_listening

    # Block until any keyboard key or mouse button is pressed
    while is_listening:
        # Check keyboard
        key_event = keyboard.read_event(suppress=True)
        if key_event.event_type == keyboard.KEY_DOWN:
            selected_element = key_event.name
            element_type = "key"
            break

    is_listening = False
    root.after(0, update_ui_after_bind)


def start_binding():
    global is_listening
    if is_listening or macro_running:
        return

    is_listening = True
    btn_key.config(text="...", fg="red")
    # Run binding hardware capture in a separate thread to keep GUI alive
    threading.Thread(target=capture_binding, daemon=True).start()


def update_ui_after_bind():
    if selected_element:
        btn_key.config(text=f"{selected_element.upper()}", fg="black")


# --- 2. Macro Loop Logic (Infinite until toggled off) ---
def clicker_loop():
    global macro_running
    while macro_running:
        if element_type == "key":
            try:
                keyboard.send(selected_element)
            except Exception:
                pass
        elif element_type == "mouse":
            try:
                # Map pynput/standard names to low-level mouse library names
                btn = selected_element
                if btn == "middle":
                    btn = "wheel"
                mouse.click(button=btn)
            except Exception:
                pass

        # Precise sleep intervals inside the thread loop
        time.sleep(delay_seconds)


def toggle_macro():
    global macro_running, delay_seconds

    if not selected_element:
        messagebox.showwarning("Warning", "Please bind a key or mouse button first!")
        return

    try:
        delay_seconds = float(entry_delay.get())
        if delay_seconds <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Delay must be a positive number!")
        return

    if not macro_running:
        macro_running = True
        btn_run.config(text=f"STOP ({START_KEY})", bg="red", fg="white")
        # Launching the infinite loop in a dedicated background thread
        threading.Thread(target=clicker_loop, daemon=True).start()
    else:
        macro_running = False
        btn_run.config(
            text=f"Run ({START_KEY})", bg="SystemButtonFace", fg="black"
        )


# --- 3. Global Trigger Hotkey Setup ---
def setup_global_hotkey():
    # Installs a global hardware hook that listens for START_KEY execution
    keyboard.add_hotkey(START_KEY, lambda: root.after(0, toggle_macro) if root.focus_get() != entry_delay else None)


# --- 4. GUI Layout ---
root = tk.Tk()
root.title("Key & Mouse Binder")
center_window(root, 420, 130)
root.resizable(False, False)
root.grid_columnconfigure(0, weight=1)

# Top Panel
top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, pady=15, padx=10)

label_key = tk.Label(top_frame, text="Key:")
label_key.pack(side="left", padx=2)

btn_key = tk.Button(
    top_frame, text="[ Click to bind ]", width=18, command=start_binding, bg="white"
)
btn_key.pack(side="left", padx=10)

label_delay = tk.Label(top_frame, text="Delay:")
label_delay.pack(side="left", padx=2)

entry_delay = tk.Entry(top_frame, width=6)
entry_delay.insert(0, "1.0")
entry_delay.pack(side="left", padx=2)

label_sec = tk.Label(top_frame, text="sec")
label_sec.pack(side="left", padx=2)

# Bottom Panel
bottom_frame = tk.Frame(root)
bottom_frame.grid(row=1, column=0, pady=10)

btn_run = tk.Button(
    bottom_frame, text=f"Run ({START_KEY})", command=toggle_macro, width=12
)
btn_run.pack(side="left", padx=10)

# Initialize global hotkey hooking
setup_global_hotkey()

root.mainloop()
