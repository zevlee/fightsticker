from os import remove
from os.path import exists, join
from sys import argv
from urllib.request import urlopen
from configparser import ConfigParser, ParsingError, NoSectionError

import pyglet
from pyglet.math import Mat4, Vec3

from . import *
from .arg_parser import ArgParser
from .logger import logger

# Set up the debugging
parser = ArgParser()
args = argv[1:]
option = parser.parse_args(args)
if option.DEBUG:
    logger.setLevel("DEBUG")
logger.debug("Debugging Active")

# Load the images directories
pyglet.resource.path.append(join(CONF, "images"))
pyglet.resource.path.append(join(APPDIR, "images"))
pyglet.resource.reindex()


class _BaseScene:
    def activate(self):
        pass

    def deactivate(self):
        pass


class RetryScene(_BaseScene):
    """
    A scene that tells you to try again if no stick is detected
    """
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        img = pyglet.resource.image("missing.png")
        self.sprite = pyglet.sprite.Sprite(img=img, batch=self.batch)


class LayoutScene(_BaseScene):
    """
    Layout scene, with common methods ready to be wired
    
    :param layout: Layout mapping
    :type layout: dict
    :param images: Images mapping
    :type images: dict
    """
    def __init__(self, layout, images):
        """
        Constructor
        """
        self.layout = layout
        self.images = images
        self.batch = pyglet.graphics.Batch()
        # Ordered groups to handle draw order of the sprites
        self.bg = pyglet.graphics.Group(0)
        self.fg = pyglet.graphics.Group(1)
        # Initialize the layout
        self._init_layout()
        # Mapping of input names to sprite names
        self.button_mapping = {
            "back": self.select_spr,
            "start": self.start_spr,
            "guide": self.guide_spr,
            "x": self.x_spr,
            "y": self.y_spr,
            "rightshoulder": self.rb_spr,
            "leftshoulder": self.lb_spr,
            "a": self.a_spr,
            "b": self.b_spr,
            "righttrigger": self.rt_spr,
            "lefttrigger": self.lt_spr
        }

    def _make_sprite(self, name, group, visible=True):
        """
        Helper function to make a Sprite
        """
        try:
            image = pyglet.resource.image(self.images[name])
        except KeyError:
            image = "none.png"
        try:
            position = self.layout[name]
        except KeyError:
            position = 0, 0
        sprite = pyglet.sprite.Sprite(
            image, *position, batch=self.batch, group=group
        )
        sprite.visible = visible
        return sprite

    def _init_layout(self):
        """
        Create all sprites using helper function (name, batch, group,
        visible)
        """
        pass

    def on_button_press(self, controller, button):
        """
        Event to show a button when pressed
        """
        logger.debug(f"Pressed Button: {button}")
        pressed_button = self.button_mapping.get(button, None)
        if pressed_button:
            pressed_button.visible = True

    def on_button_release(self, controller, button):
        """
        Event to hide the sprite when the button is released
        """
        pressed_button = self.button_mapping.get(button, None)
        if pressed_button:
            pressed_button.visible = False

    def on_trigger_motion(self, controller, trigger, value):
        """
        Math to draw trigger inputs or hide them
        """
        logger.debug(f"Pulled Trigger: {trigger}")
        if trigger == "lefttrigger":
            if value > self.manager.trigger_deadzone:
                self.lt_spr.visible = True
            elif value < self.manager.trigger_deadzone:
                self.lt_spr.visible = False
        if trigger == "righttrigger":
            if value > self.manager.trigger_deadzone:
                self.rt_spr.visible = True
            elif value < self.manager.trigger_deadzone:
                self.rt_spr.visible = False

    def on_stick_motion(self, controller, stick, vector):
        """
        Math to draw stick inputs in their correct location
        """
        pass

    def on_dpad_motion(self, controller, vector):
        """
        Math to draw dpad inputs in their correct location
        """
        pass


class TraditionalScene(LayoutScene):
    """
    Traditional layout scene, all fightstick events wired up
    
    :param layout: Layout mapping
    :type layout: dict
    :param images: Images mapping
    :type images: dict
    """
    def __init__(self, layout, images):
        """
        Constructor
        """
        super().__init__(layout, images)

    def _init_layout(self):
        """
        Create all sprites using helper function (name, batch, group,
        visible)
        """
        self.background = self._make_sprite("background", self.bg)
        self.select_spr = self._make_sprite("select", self.fg, False)
        self.start_spr = self._make_sprite("start", self.fg, False)
        self.guide_spr = self._make_sprite("guide", self.fg, False)
        self.stick_spr = self._make_sprite("stick", self.fg)
        self.x_spr = self._make_sprite("x", self.fg, False)
        self.y_spr = self._make_sprite("y", self.fg, False)
        self.rb_spr = self._make_sprite("rb", self.fg, False)
        self.lb_spr = self._make_sprite("lb", self.fg, False)
        self.a_spr = self._make_sprite("a", self.fg, False)
        self.b_spr = self._make_sprite("b", self.fg, False)
        self.rt_spr = self._make_sprite("rt", self.fg, False)
        self.lt_spr = self._make_sprite("lt", self.fg, False)

    def on_stick_motion(self, controller, stick, vector):
        """
        Math to draw stick inputs in their correct location
        """
        logger.debug(f"Moved Stick: {stick}, {vector.x, vector.y}")
        if stick == "leftstick":
            xpos, ypos = self.layout["stick"]
            if 1 > vector.length() > self.manager.stick_deadzone:
                xpos += vector.x * 50
                ypos += vector.y * 50
            elif vector.length() > self.manager.stick_deadzone:
                # Normalize the vector if its length exceeds 1.0,
                # capping the distance from the center to a max of 50
                # in all directions
                xpos += vector.normalize().x * 50
                ypos += vector.normalize().y * 50
            self.stick_spr.position = xpos, ypos, 0

    def on_dpad_motion(self, controller, vector):
        """
        Math to draw dpad inputs in their correct location
        """
        logger.debug(f"Moved Dpad: {vector.x, vector.y}")
        xpos, ypos = self.layout["stick"]
        xpos += vector.normalize().x * 50
        ypos += vector.normalize().y * 50
        self.stick_spr.position = xpos, ypos, 0


class LeverlessScene(LayoutScene):
    """
    Leverless layout scene, all fightstick events wired up
    
    :param layout: Layout mapping
    :type layout: dict
    :param images: Images mapping
    :type images: dict
    """
    def __init__(self, layout, images):
        """
        Constructor
        """
        super().__init__(layout, images)

    def _init_layout(self):
        """
        Create all sprites using helper function (name, batch, group,
        visible)
        """
        self.background = self._make_sprite("background", self.bg)
        self.select_spr = self._make_sprite("select", self.fg, False)
        self.start_spr = self._make_sprite("start", self.fg, False)
        self.guide_spr = self._make_sprite("guide", self.fg, False)
        self.up_spr = self._make_sprite("up", self.fg, False)
        self.down_spr = self._make_sprite("down", self.fg, False)
        self.left_spr = self._make_sprite("left", self.fg, False)
        self.right_spr = self._make_sprite("right", self.fg, False)
        self.x_spr = self._make_sprite("x", self.fg, False)
        self.y_spr = self._make_sprite("y", self.fg, False)
        self.rb_spr = self._make_sprite("rb", self.fg, False)
        self.lb_spr = self._make_sprite("lb", self.fg, False)
        self.a_spr = self._make_sprite("a", self.fg, False)
        self.b_spr = self._make_sprite("b", self.fg, False)
        self.rt_spr = self._make_sprite("rt", self.fg, False)
        self.lt_spr = self._make_sprite("lt", self.fg, False)

    def on_stick_motion(self, controller, stick, vector):
        """
        Have the stick inputs alert the main window to draw the sprites
        """
        logger.debug(f"Moved Stick: {stick}, {vector.x, vector.y}")
        if stick == "leftstick":
            self.up_spr.visible = vector.y > self.manager.stick_deadzone
            self.down_spr.visible = vector.y < -self.manager.stick_deadzone
            self.left_spr.visible = vector.x < -self.manager.stick_deadzone
            self.right_spr.visible = vector.x > self.manager.stick_deadzone

    def on_dpad_motion(self, controller, vector):
        """
        Have the dpad hats alert the main window to draw the sprites
        """
        logger.debug(f"Moved Dpad: {vector.x, vector.y}")
        self.up_spr.visible = vector.y > 0
        self.down_spr.visible = vector.y < 0
        self.left_spr.visible = vector.x < 0
        self.right_spr.visible = vector.x > 0


class PadScene(LayoutScene):
    """
    Pad layout scene, all fightstick events wired up
    
    :param layout: Layout mapping
    :type layout: dict
    :param images: Images mapping
    :type images: dict
    """
    def __init__(self, layout, images):
        """
        Constructor
        """
        super().__init__(layout, images)

    def _init_layout(self):
        """
        Create all sprites using helper function (name, batch, group,
        visible)
        """
        self.background = self._make_sprite("background", self.bg)
        self.select_spr = self._make_sprite("select", self.fg, False)
        self.start_spr = self._make_sprite("start", self.fg, False)
        self.guide_spr = self._make_sprite("guide", self.fg, False)
        self.leftstick_spr = self._make_sprite("leftstick", self.fg)
        self.rightstick_spr = self._make_sprite("rightstick", self.fg)
        self.up_spr = self._make_sprite("up", self.fg, False)
        self.down_spr = self._make_sprite("down", self.fg, False)
        self.left_spr = self._make_sprite("left", self.fg, False)
        self.right_spr = self._make_sprite("right", self.fg, False)
        self.diag_spr = self._make_sprite("diag", self.fg, False)
        self.x_spr = self._make_sprite("x", self.fg, False)
        self.y_spr = self._make_sprite("y", self.fg, False)
        self.rb_spr = self._make_sprite("rb", self.fg, False)
        self.lb_spr = self._make_sprite("lb", self.fg, False)
        self.a_spr = self._make_sprite("a", self.fg, False)
        self.b_spr = self._make_sprite("b", self.fg, False)
        self.rt_spr = self._make_sprite("rt", self.fg, False)
        self.lt_spr = self._make_sprite("lt", self.fg, False)

    def on_stick_motion(self, controller, stick, vector):
        """
        Math to draw stick inputs in their correct location
        """
        logger.debug(f"Moved Stick: {stick}, {vector.x, vector.y}")
        xpos, ypos = self.layout[stick]
        if 1 > vector.length() > self.manager.stick_deadzone:
            xpos += vector.x * 45
            ypos += vector.y * 45
        elif vector.length() > self.manager.stick_deadzone:
            # Normalize the vector if its length exceeds 1.0,
            # capping the distance from the center to a max of 45
            # in all directions
            xpos += vector.normalize().x * 45
            ypos += vector.normalize().y * 45
        if stick == "leftstick":
            self.leftstick_spr.position = xpos, ypos, 0
        else:
            self.rightstick_spr.position = xpos, ypos, 0

    def on_dpad_motion(self, controller, vector):
        """
        Have the dpad hats alert the main window to draw the sprites
        """
        logger.debug(f"Moved Dpad: {vector.x, vector.y}")
        self.up_spr.visible = vector.y > 0
        self.down_spr.visible = vector.y < 0
        self.left_spr.visible = vector.x < 0
        self.right_spr.visible = vector.x > 0
        # Initialize diagonal sprite position parameters
        xpos, ypos = self.layout["up"][0], self.layout["right"][1]
        # Calculate the width and height of the diagonal sprite through
        # the relationship with the position of the up and right
        # sprites, as they represent the top left and bottom right
        # corners of the sprite
        diag_x = self.layout["right"][0] - self.layout["up"][0]
        diag_y = self.layout["up"][1] - self.layout["right"][1]
        # Determine diagonal sprite orientation and position
        if self.up_spr.visible and self.left_spr.visible:
            self.diag_spr.rotation = 0
            self.diag_spr.position = xpos, ypos, 0
        elif self.up_spr.visible and self.right_spr.visible:
            self.diag_spr.rotation = 90
            self.diag_spr.position = xpos, ypos + diag_y, 0
        elif self.down_spr.visible and self.right_spr.visible:
            self.diag_spr.rotation = 180
            self.diag_spr.position = xpos + diag_x, ypos + diag_y, 0
        elif self.down_spr.visible and self.left_spr.visible:
            self.diag_spr.rotation = 270
            self.diag_spr.position = xpos + diag_x, ypos, 0
        # Now display the diagonal sprite if x- and y-axis sprites are
        # simultaneously active
        if (
            (self.up_spr.visible or self.down_spr.visible)
            and (self.left_spr.visible or self.right_spr.visible)
        ):
            self.diag_spr.visible = True
        else:
            self.diag_spr.visible = False            


class SceneManager:
    """
    A Scene Management class.

    The SceneManager is responsible for switching between
    the various scenes cleanly. This includes setting and
    removing Window and Controller events handlers. Global
    state (deadzone, etc.) is also defined here.
    
    :param window_instance: Window instance
    :type window_instance: pyglet.window.xlib.XlibWindow
    :param layout: Layout option, traditional or leverless
    :type layout: str
    :param config: Configuration
    :type config: dict
    """
    def __init__(self, window_instance, layout="traditional", config=DEFAULT):
        """
        Constructor
        """
        self.window = window_instance
        self.window.push_handlers(self)

        self.fightstick = None

        # Set up configuration parser
        config_parser = ConfigParser()
        config_parser.add_section("layout")
        config_parser.add_section("images")
        # Read the layout file
        layout_file = config[layout[:4]]
        if layout == "pad":
            layout_conf = LAYOUT_PAD
            images_conf = IMAGES_PAD
        elif layout == "leverless":
            layout_conf = LAYOUT_LEVERLESS
            images_conf = IMAGES_LEVERLESS
        else:
            layout_conf = LAYOUT_TRADITIONAL
            images_conf = IMAGES_TRADITIONAL
        if config_parser.read(layout_file):
            try:
                for k, v in config_parser.items("layout"):
                    x, y = v.split(", ")
                    layout_conf[k] = int(x), int(y)
                for k, v in config_parser.items("images"):
                    images_conf[k] = v
            except (KeyError, ParsingError, NoSectionError):
                logger.debug(
                    "Invalid theme/layout.ini. Falling back to default."
                )

        # Set up scene instances
        self._scenes = {}
        self._current_scene = None
        if layout == "pad":
            self.add_scene(
                "main", PadScene(layout_conf, images_conf)
            )
        elif layout == "leverless":
            self.add_scene(
                "main", LeverlessScene(layout_conf, images_conf)
            )
        else:
            self.add_scene(
                "main", TraditionalScene(layout_conf, images_conf)
            )
        self.add_scene("retry", RetryScene())

        # Instantiate a ControllerManager to handle hot-plugging
        self.controller_manager = pyglet.input.ControllerManager()
        self.controller_manager.on_connect = self.on_controller_connect
        self.controller_manager.on_disconnect = self.on_controller_disconnect

        # Set scene depending on if there is a controller
        controllers = self.controller_manager.get_controllers()
        if controllers:
            self.on_controller_connect(controllers[0])
            self.set_scene("main")
        else:
            self.set_scene("retry")

        # Global state for all scenes
        self.stick_deadzone = config["stic"]
        self.trigger_deadzone = config["trig"]

    def on_controller_connect(self, controller):
        """
        Detect if a controller is connected
        """
        if not self.fightstick:
            controller.open()
            self.fightstick = controller
            self.fightstick.push_handlers(self._current_scene)
            self.set_scene("main")
        else:
            logger.debug(
                f"A Controller is already connected: {self.fightstick}"
            )

    def on_controller_disconnect(self, controller):
        """
        Detect if a controller is disconnected
        """
        if self.fightstick == controller:
            self.fightstick.remove_handlers(self._current_scene)
            self.fightstick = None
            self.set_scene("retry")

    def add_scene(self, name, instance):
        """
        Add a scene
        """
        instance.manager = self
        self._scenes[name] = instance

    def set_scene(self, name):
        """
        Set a scene
        """
        if self._current_scene:
            self.window.remove_handlers(self._current_scene)
            self._current_scene.deactivate()
            if self.fightstick:
                self.fightstick.remove_handlers(self._current_scene)

        new_scene = self._scenes[name]
        self.window.push_handlers(new_scene)
        if self.fightstick:
            self.fightstick.push_handlers(new_scene)

        self._current_scene = new_scene
        self._current_scene.activate()

    def enforce_aspect_ratio(self, dt):
        """
        Enforce aspect ratio by readjusting the window height
        """
        aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
        target_width = int(self.window.height * aspect_ratio)
        target_height = int(self.window.width / aspect_ratio)

        if (
            self.window.width != target_width
            and self.window.height != target_height
        ):
            self.window.set_size(self.window.width, target_height)

    def on_draw(self):
        """
        Draw
        """
        self.window.clear()
        self._current_scene.batch.draw()

    def on_resize(self, width, height):
        """
        Resize
        """
        projection_matrix = Mat4.orthogonal_projection(
            0, width, 0, height, 0, 1
        )
        scale_x = width / WINDOW_WIDTH
        scale_y = height / WINDOW_HEIGHT
        self.window.projection = projection_matrix.scale(
            Vec3(scale_x, scale_y, 1)
        )
        self.window.viewport = 0, 0, width, height
        return pyglet.event.EVENT_HANDLED


def run(layout, config, parent=None) -> None:
    """
    Run the fightstick app
    
    :param layout: Layout option, tradtional or leverless
    :type layout: str
    :param config: Configuration
    :type config: dict
    :param parent: Parent window
    :type parent: Gtk.Window
    """
    # Create the main window. Use ConfigParser to set a static
    # controller status of unplugged
    window = pyglet.window.Window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        caption="Fightsticker",
        resizable=True,
        vsync=False
    )
    logger.debug("Layout window created")
    # Close the parent window. We put the window closing here so that
    # the pyglet window inherits the icon of the application
    if parent:
        parent.close()
    # Instantiate the scene manager
    scene_manager = SceneManager(
        window_instance=window, layout=layout, config=config
    )
    # Enforce aspect ratio by readjusting the window height
    pyglet.clock.schedule_interval(
        scene_manager.enforce_aspect_ratio, 0.3
    )
    # Run the application
    pyglet.app.run()
