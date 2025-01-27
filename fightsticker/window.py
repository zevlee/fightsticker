from os.path import join
from platform import system
from sys import argv

from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gio

from . import *
from .about import About
from .preferences import Preferences
from .arg_parser import ArgParser
from .fightstick import run


class Window(Gtk.ApplicationWindow):
    """
    Main window
    
    :param app: Application
    :type app: Gtk.Application
    """
    def __init__(self, app):
        """
        Constructor
        """
        super().__init__(application=app, resizable=False)

        # Add icon
        self.set_icon_name(ID)
        
        # Set up header
        header = Gtk.HeaderBar()

        # Build menu
        builder = Gtk.Builder.new_from_file(
            join(APPDIR, "gui", "menu.xml")
        )
        menu = builder.get_object("app-menu")
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu)

        # Add menu actions
        action = Gio.SimpleAction.new("prefs", None)
        action.connect("activate", self.on_prefs_clicked)
        app.add_action(action)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about_clicked)
        app.add_action(action)

        # Set decoration layout
        if system() == "Darwin":
            header.set_decoration_layout("close,minimize,maximize:")
            header.pack_start(menu_button)
        else:
            header.set_decoration_layout(":minimize,maximize,close")
            header.pack_end(menu_button)

        # Add header
        self.set_titlebar(header)

        # Set up grid
        spacing = 20
        grid = Gtk.Grid(
            row_homogeneous=False,
            column_homogeneous=True,
            margin_start=spacing,
            margin_end=spacing,
            margin_top=spacing,
            margin_bottom=spacing,
            row_spacing=spacing,
            column_spacing=spacing
        )

        # Logo
        filename = join(APPDIR, "logo", f"{ID}.png")
        logo = Gtk.Picture.new_for_filename(filename)

        # Layout label and dropdown box
        layout = Gtk.Label(halign=Gtk.Align.START)
        layout.set_markup("<b>Layout</b>")
        self.dropdown = Gtk.DropDown()
        strings = Gtk.StringList()
        self.dropdown.props.model = strings
        for item in LAYOUTS:
            strings.append(item)
        
        # Launch button
        launch = Gtk.Button(label="Launch")
        launch.connect("clicked", self.on_launch_clicked)

        # Attach widgets to grid
        widgets = [
            [logo],
            [layout, self.dropdown],
            [launch]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.set_child(grid)

        # Open stored preferences
        self.config = read_config("settings.json")

        # Command line arguments
        parser = ArgParser()
        args = argv[1:]
        option = parser.parse_args(args)
        if option.TRADITIONAL:
            self.close()
            run(layout="traditional", config=self.config)
        elif option.LEVERLESS:
            self.close()
            run(layout="leverless", config=self.config)

    def on_prefs_clicked(self, action, param):
        """
        Open preferences window
        
        :param action: Action
        :type action: Gio.SimpleAction
        :param param: Parameter
        :type param: NoneType
        """
        prefs = Preferences(self)
        prefs.show()

    def on_about_clicked(self, action, param):
        """
        Open about dialog window
        
        :param action: Action
        :type action: Gio.SimpleAction
        :param param: Parameter
        :type param: NoneType
        """
        about = About(self)
        about.show()

    def on_launch_clicked(self, button):
        """
        Launch the selected layout
        
        :param button: Button
        :type button: Gtk.Button
        """
        self.close()
        match self.dropdown.props.selected_item.props.string:
            case "Traditional":
                run(layout="traditional", config=self.config)
            case "Leverless":
                run(layout="leverless", config=self.config)
