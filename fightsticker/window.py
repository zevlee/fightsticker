from os.path import join
from tkinter import *
from tkinter import ttk
from . import APPDIR, LAYOUTS
from .fightstick import main as main_traditional
from .fightstick_hb import main as main_leverless


class Window(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Grid layout
        self.grid(row=0, column=0, sticky=NSEW)
        # Logo
        image = PhotoImage(
            file=join(APPDIR, "logo", "me.zevlee.Fightsticker.png")
        )
        image_label = ttk.Label(self, image=image)
        image_label.image = image
        image_label.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        # Option Menu Label
        label = ttk.Label(self, text="Layout")
        label.grid(row=1, column=0, sticky=NSEW)
        # Option Menu
        self.option_var = StringVar(self)
        menu = ttk.OptionMenu(self, self.option_var, LAYOUTS[0], *LAYOUTS)
        menu.grid(row=1, column=1, sticky=NSEW)
        # Launch Button
        button = ttk.Button(
            self, text="Launch", command=lambda: self._launch()
        )
        button.grid(row=2, column=0, columnspan=2, sticky=NSEW)    
        # Padding
        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
    
    def _launch(self):
        match self.option_var.get():
            case "Traditional":
                main_traditional()
            case "Leverless":
                main_leverless()
        