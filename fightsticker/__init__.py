from json import dumps, loads
from os.path import dirname, join

from platformdirs import user_config_dir

# Version
__version__ = "0.5.0"
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
    "dbg": False,
    "stick": 0.2,
    "trigger": 0.8
}
# Available layouts
LAYOUTS = ("Traditional", "Leverless")
# Traditional layout parameters
LAYOUT_TRADITIONAL = {
    "background": (0, 0),
    "select": (50, 318),
    "start": (50, 318),
    "stick": (118, 153),
    "a": (256, 83),
    "b": (336, 113),
    "x": (275, 173),
    "y": (354, 203),
    "rb": (440, 202),
    "lb": (527, 199),
    "rt": (421, 112),
    "lt": (507, 109),
}
# Traditional layout images
IMAGES_TRADITIONAL = {
    "background": "background.png",
    "select": "transparent.png",
    "start": "transparent.png",
    "stick": "button.png",
    "a": "button.png",
    "b": "button.png",
    "x": "button.png",
    "y": "button.png",
    "rb": "button.png",
    "lb": "button.png",
    "rt": "button.png",
    "lt": "button.png",
}
# Leverless layout parameters
LAYOUT_LEVERLESS = {
    "background": (0, 0),
    "select": (50, 318),
    "start": (50, 318),
    "up": (237, 10),
    "down": (133, 217),
    "left": (47, 217),
    "right": (209, 176),
    "a": (284, 124),
    "b": (364, 158),
    "x": (290, 214),
    "y": (369, 247),
    "rb": (456, 246),
    "lb": (543, 234),
    "rt": (456, 159),
    "lt": (540, 146),
}
# Leverless layout images
IMAGES_LEVERLESS = {
    "background": "backgroundHB.png",
    "select": "transparent.png",
    "start": "transparent.png",
    "up": "buttonhblg.png",
    "down": "buttonhb.png",
    "left": "buttonhb.png",
    "right": "buttonhb.png",
    "a": "buttonhb.png",
    "b": "buttonhb.png",
    "x": "buttonhb.png",
    "y": "buttonhb.png",
    "rb": "buttonhb.png",
    "lb": "buttonhb.png",
    "rt": "buttonhb.png",
    "lt": "buttonhb.png",
}
# Window width
WINDOW_WIDTH = 640
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
    for k in ["app", "dbg"]:
        if not isinstance(config[k], int):
            config[k] = default_config[k]
            overwrite = True
    # Overwrite filename if there is an error
    if overwrite:
        with open(join(CONF, filename), "w") as c:
            c.write(dumps(config))
            c.close()
