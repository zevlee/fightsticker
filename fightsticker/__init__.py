from os.path import dirname

# Version
__version__ = "0.2.0"
# Available layouts
LAYOUTS = ("Traditional", "Leverless")
# Application directory
APPDIR = dirname(dirname(__file__))
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
