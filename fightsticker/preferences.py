from json import dumps
from os.path import join
from platform import system
from shutil import copyfile

from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Adw, Gio

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

        # Stick deadzone label and entry field
        stic = Gtk.Label(halign=Gtk.Align.START)
        stic.set_markup("Stick Deadzone")
        self.stic = Gtk.Entry()
        self.stic.set_text(str(self.config["stic"]))

        # Trigger deadzone label and entry field
        trig = Gtk.Label(halign=Gtk.Align.START)
        trig.set_markup("Trigger Deadzone")
        self.trig = Gtk.Entry()
        self.trig.set_text(str(self.config["trig"]))

        # Traditional layout configuration file label, entry field, and
        # file chooser button
        trad = Gtk.Label(halign=Gtk.Align.START)
        trad.set_markup("Traditional Layout Configuration File")
        self.trad = Gtk.Entry()
        self.trad.set_text(str(self.config["trad"]))
        trad_button = Gtk.Button(label="Choose File")
        trad_button.connect("clicked", self.on_trad_clicked)

        # Leverless layout configuration file label, entry field, and
        # file chooser button
        leve = Gtk.Label(halign=Gtk.Align.START)
        leve.set_markup("Leverless Layout Configuration File")
        self.leve = Gtk.Entry()
        self.leve.set_text(str(self.config["leve"]))
        leve_button = Gtk.Button(label="Choose File")
        leve_button.connect("clicked", self.on_leve_clicked)

        # Appearance check button
        self.app = Gtk.CheckButton(label="Dark Mode")
        self.app.set_active(self.config["app"])

        # Debug mode check button
        self.dbg = Gtk.CheckButton(label="Debug Mode")
        self.dbg.set_active(self.config["dbg"])

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
            [stic, self.stic],
            [trig, self.trig],
            [trad],
            [self.trad, trad_button],
            [leve],
            [self.leve, leve_button],
            [self.app],
            [self.dbg],
            [restore_button],
            [cancel_button, save_button]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.set_child(grid)

    def on_trad_clicked(self, button):
        """
        Open dialog to choose word list
        
        :param button: Button
        :type button: Gtk.Button
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the traditional configuration file",
            transient_for=self,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(join(CONF, "layouts"))
        )
        dialog.connect("response", self._select_trad_file)
        dialog.show()

    def _select_trad_file(self, dialog, response):
        """
        Set file when chosen in dialog
        
        :param dialog: Dialog
        :type dialog: Gtk.FileChooserDialog
        :param response: Response from user
        :type response: int
        """
        if response == Gtk.ResponseType.OK:
            self.trad.set_text(Gio.File.get_path(dialog.get_file()))
        dialog.destroy()

    def on_leve_clicked(self, button):
        """
        Open dialog to choose word list
        
        :param button: Button
        :type button: Gtk.Button
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the leverless configuration file",
            transient_for=self,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(join(CONF, "layouts"))
        )
        dialog.connect("response", self._select_leve_file)
        dialog.show()

    def _select_leve_file(self, dialog, response):
        """
        Set file when chosen in dialog
        
        :param dialog: Dialog
        :type dialog: Gtk.FileChooserDialog
        :param response: Response from user
        :type response: int
        """
        if response == Gtk.ResponseType.OK:
            self.leve.set_text(Gio.File.get_path(dialog.get_file()))
        dialog.destroy()

    def on_restore_clicked(self, button):
        """
        Restore default values
        
        :param button: Button
        :type button: Gtk.Button
        """
        self.app.set_active(DEFAULT["app"])
        self.dbg.set_active(DEFAULT["dbg"])
        self.stic.set_text(str(DEFAULT["stic"]))
        self.trig.set_text(str(DEFAULT["trig"]))
        self.trad.set_text(str(DEFAULT["trad"]))
        self.leve.set_text(str(DEFAULT["leve"]))

    def on_cancel_clicked(self, button):
        """
        Close preferences window without saving
        
        :param button: Button
        :type button: Gtk.Button
        """
        self.destroy()

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
            self.config["stic"] = float(self.stic.get_text())
            self.config["trig"] = float(self.trig.get_text())
            self.config["trad"] = self.trad.get_text()
            self.config["leve"] = self.leve.get_text()
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
