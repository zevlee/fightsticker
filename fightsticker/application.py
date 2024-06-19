from tkinter import *
from tkinter import ttk
from .window import Window


class Application(Tk):
    def __init__(self, title="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)

    def do_startup(self):
        self.resizable(False, False)
        self.window = Window(self)

    def do_activate(self):
        self.mainloop()

    def run(self):
        self.do_startup()
        self.do_activate()
        return 0
