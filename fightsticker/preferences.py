from json import dumps
from os.path import join
from platform import system
from shutil import copyfile

from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw

from . import *


class Preferences(Gtk.Window):
    """
    Preferences window
    
    :param parent: Parent window
    :type parent: Gtk.Window
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super().__init__(
            modal=True,
            transient_for=parent,
            resizable=False,
            title="Preferences"
        )

        # Set up header
        header = Gtk.HeaderBar()

        # Set decoration layout
        if system() == "Darwin":
            header.set_decoration_layout("close,minimize,maximize:")
        else:
            header.set_decoration_layout(":minimize,maximize,close")

        # Add header
        self.set_titlebar(header)

        # Set up grid
        spacing = 20
        grid = Gtk.Grid(
            row_homogeneous=True,
            column_homogeneous=True,
            margin_start=spacing,
            margin_end=spacing,
            margin_top=spacing,
            margin_bottom=spacing,
            row_spacing=spacing,
            column_spacing=spacing
        )

        # Open stored preferences
        self.config = read_config("settings.json")

        # Appearance check button
        self.app = Gtk.CheckButton(label="Dark Mode")
        self.app.set_active(self.config["app"])

        # Debug mode check button
        self.dbg = Gtk.CheckButton(label="Debug Mode")
        self.dbg.set_active(self.config["dbg"])

        # Stick deadzone label and entry field
        stick = Gtk.Label(halign=Gtk.Align.START)
        stick.set_markup("<b>Stick Deadzone</b>")
        self.stick = Gtk.Entry()
        self.stick.set_text(str(self.config["stick"]))

        # Trigger deadzone label and entry field
        trigger = Gtk.Label(halign=Gtk.Align.START)
        trigger.set_markup("<b>Trigger Deadzone</b>")
        self.trigger = Gtk.Entry()
        self.trigger.set_text(str(self.config["trigger"]))

        # Restore defaults button
        restore_button = Gtk.Button(label="Restore Defaults")
        restore_button.connect("clicked", self.on_restore_clicked)

        # Cancel and save buttons
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_clicked)

        # Attach widgets to grid
        widgets = [
            [self.app],
            [self.dbg],
            [stick, self.stick],
            [trigger, self.trigger],
            [restore_button],
            [cancel_button, save_button]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.set_child(grid)

    def on_cancel_clicked(self, button):
        """
        Close preferences window without saving
        
        :param button: Button
        :type button: Gtk.Button
        """
        self.destroy()

    def on_restore_clicked(self, button):
        """
        Restore default values
        
        :param button: Button
        :type button: Gtk.Button
        """
        self.app.set_active(DEFAULT["app"])
        self.dbg.set_active(DEFAULT["dbg"])
        self.stick.set_text(str(DEFAULT["stick"]))
        self.trigger.set_text(str(DEFAULT["trigger"]))

    def on_save_clicked(self, button):
        """
        Save preferences then close dialog
        
        :param button: Button
        :type button: Gtk.Button
        """
        # Save preferences
        with open(join(CONF, "settings.json"), "w") as c:
            self.config["app"] = self.app.get_active()
            self.config["dbg"] = self.dbg.get_active()
            self.config["stick"] = float(self.stick.get_text())
            self.config["trigger"] = float(self.trigger.get_text())
            c.write(dumps(self.config))
            c.close()
        # Set color scheme
        application = self.get_transient_for().get_application()
        if self.app.get_active():
            application.get_style_manager().set_color_scheme(
                Adw.ColorScheme.FORCE_DARK
            )
        else:
            application.get_style_manager().set_color_scheme(
                Adw.ColorScheme.FORCE_LIGHT
            )
        self.destroy()
