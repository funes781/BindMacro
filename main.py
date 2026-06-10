from binder import Binder
from gui import create_gui

if __name__ == "__main__":
    binder = Binder()
    root = create_gui(binder)
    root.mainloop()
