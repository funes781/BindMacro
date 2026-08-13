import tkinter as tk
from tkinter import messagebox
import keyboard
import config


def center_window(window, width=420, height=170):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_gui(binder):
    root = tk.Tk()
    root.title("Key & Mouse Binder")
    center_window(root)
    root.resizable(False, False)
    root.grid_columnconfigure(0, weight=1)

    # --- Top Panel ---
    top_frame = tk.Frame(root)
    top_frame.grid(row=0, column=0, pady=(15, 5), padx=10)

    label_key = tk.Label(top_frame, text="Key:")
    label_key.pack(side="left", padx=2)

    def start_binding():
        if binder.is_listening or binder.macro_running:
            return
        binder.start_binding()
        btn_key.config(text="... (Esc to cancel)", fg="red")

    def update_ui_after_bind():
        if binder.selected_element:
            btn_key.config(text=f"{binder.selected_element.upper()}", fg="black")

    def update_ui_after_cancel():
        label = binder.selected_element.upper() if binder.selected_element else "[ Click to bind ]"
        btn_key.config(text=label, fg="black")

    binder.on_update_ui = update_ui_after_bind
    binder.on_cancel_ui = update_ui_after_cancel
    binder.after_func = root.after

    initial_label = binder.selected_element.upper() if binder.selected_element else "[ Click to bind ]"
    btn_key = tk.Button(
        top_frame, text=initial_label, width=18,
        command=start_binding, bg="white"
    )
    btn_key.pack(side="left", padx=10)

    label_delay = tk.Label(top_frame, text="Delay:")
    label_delay.pack(side="left", padx=2)

    entry_delay = tk.Entry(top_frame, width=6)
    entry_delay.insert(0, str(binder.delay_seconds))
    entry_delay.pack(side="left", padx=2)

    label_sec = tk.Label(top_frame, text="sec")
    label_sec.pack(side="left", padx=2)

    # --- Middle Panel ---
    mid_frame = tk.Frame(root)
    mid_frame.grid(row=1, column=0, pady=5, padx=10)

    label_hold = tk.Label(mid_frame, text="Hold:")
    label_hold.pack(side="left", padx=2)

    hold_var = tk.BooleanVar(value=binder.hold_enabled)

    def toggle_hold():
        binder.hold_enabled = hold_var.get()
        binder.save_settings()

    chk_hold = tk.Checkbutton(mid_frame, variable=hold_var, command=toggle_hold)
    chk_hold.pack(side="left", padx=2)

    entry_hold = tk.Entry(mid_frame, width=6)
    entry_hold.insert(0, str(binder.hold_duration))

    def update_hold_duration(event=None):
        try:
            val = float(entry_hold.get())
            if val > 0:
                binder.hold_duration = val
                binder.save_settings()
        except ValueError:
            pass

    entry_hold.bind("<KeyRelease>", update_hold_duration)
    entry_hold.pack(side="left", padx=2)

    label_hold_sec = tk.Label(mid_frame, text="sec")
    label_hold_sec.pack(side="left", padx=2)

    # --- Bottom Panel ---
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=2, column=0, pady=(5, 15))

    def toggle_macro():
        if not binder.selected_element:
            messagebox.showwarning(
                "Warning", "Please bind a key or mouse button first!"
            )
            return
        try:
            delay = float(entry_delay.get())
            if delay <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Delay must be a positive number!")
            return
        if not binder.macro_running:
            binder.start_macro(delay)
            btn_run.config(text=f"STOP ({config.START_KEY})", bg="red", fg="white")
        else:
            binder.stop_macro()
            btn_run.config(
                text=f"Run ({config.START_KEY})",
                bg="SystemButtonFace", fg="black"
            )

    btn_run = tk.Button(
        bottom_frame, text=f"Run ({config.START_KEY})",
        command=toggle_macro, width=12
    )
    btn_run.pack(side="left", padx=10)

    keyboard.add_hotkey(
        config.START_KEY,
        lambda: (
            root.after(0, toggle_macro)
            if root.focus_get() not in (entry_delay, entry_hold)
            else None
        ),
    )

    def on_close():
        binder.shutdown()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    return root
