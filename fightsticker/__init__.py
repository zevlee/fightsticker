from json import dumps, loads
from os.path import dirname, join

from platformdirs import user_config_dir

# Version
__version__ = "0.8.0"
# Application name
APPNAME = "Fightsticker"
# Application ID
ID = "me.zevlee.Fightsticker"
# Application directory
APPDIR = dirname(dirname(__file__))
# Config directory
CONF = user_config_dir(APPNAME)
# Default parameters
DEFAULT = {
    "app": True,
    "stic": 0.2,
    "trig": 0.8,
    "trad": "",
    "leve": ""
}
# Available layouts
LAYOUTS = ("Traditional", "Leverless")
# Traditional layout parameters
LAYOUT_TRADITIONAL = {
    "background": (0, 0),
    "select": (50, 318),
    "start": (50, 318),
    "guide": (50, 318),
    "stick": (83, 155),
    "x": (303, 201),
    "y": (388, 231),
    "rb": (477, 219),
    "lb": (567, 191),
    "a": (294, 102),
    "b": (379, 133),
    "rt": (468, 121),
    "lt": (557, 93),
}
# Traditional layout images
IMAGES_TRADITIONAL = {
    "background": "background.png",
    "select": "transparent.png",
    "start": "transparent.png",
    "guide": "transparent.png",
    "stick": "button.png",
    "x": "button.png",
    "y": "button.png",
    "rb": "button.png",
    "lb": "button.png",
    "a": "button.png",
    "b": "button.png",
    "rt": "button.png",
    "lt": "button.png",
}
# Leverless layout parameters
LAYOUT_LEVERLESS = {
    "background": (0, 0),
    "select": (50, 318),
    "start": (50, 318),
    "guide": (50, 318),
    "up": (296, 19),
    "down": (187, 209),
    "left": (105, 209),
    "right": (261, 173),
    "x": (339, 206),
    "y": (414, 239),
    "rb": (497, 237),
    "lb": (579, 229),
    "a": (331, 125),
    "b": (409, 156),
    "rt": (496, 156),
    "lt": (578, 142),
}
# Leverless layout images
IMAGES_LEVERLESS = {
    "background": "backgroundlv.png",
    "select": "transparent.png",
    "start": "transparent.png",
    "guide": "transparent.png",
    "up": "buttonlvlg.png",
    "down": "buttonlv.png",
    "left": "buttonlv.png",
    "right": "buttonlv.png",
    "x": "buttonlv.png",
    "y": "buttonlv.png",
    "rb": "buttonlv.png",
    "lb": "buttonlv.png",
    "a": "buttonlv.png",
    "b": "buttonlv.png",
    "rt": "buttonlv.png",
    "lt": "buttonlv.png",
}
# Window width
WINDOW_WIDTH = 680
# Window height
WINDOW_HEIGHT = 390


def read_config(filename):
    """
    Given a filename `filename`, return the configuration dictionary or
    the default configuration if `filename` is not found
    
    :param filename: Filename
    :type filename: str
    :return: Configuration dictionary
    :rtype: dict
    """
    try:
        config = loads(open(join(CONF, filename), "r").read())
    except FileNotFoundError:
        config = DEFAULT
    return config


def validate_config(filename, default="RESET"):
    """
    Given a filename `filename`, replace the file with filename `default`
    if it is not valid
    
    :param filename: Config filename
    :type filename: str
    :param default: Default filename
    :type default: str
    """
    overwrite = False
    default_config = read_config(default)
    config = read_config(filename)
    # Remove invalid keys
    for key in [k for k in config.keys() if k not in DEFAULT.keys()]:
        config.pop(key)
        overwrite = True
    # Add missing keys
    for key in [k for k in DEFAULT.keys() if k not in config.keys()]:
        config[key] = default_config[key]
        overwrite = True
    # Validate config options
    if not isinstance(config["app"], int):
        config[k] = default_config["app"]
        overwrite = True
    # Overwrite filename if there is an error
    if overwrite:
        with open(join(CONF, filename), "w") as c:
            c.write(dumps(config))
            c.close()
