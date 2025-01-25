from os import remove
from os.path import exists, join
from sys import argv
from urllib.request import urlopen
from configparser import ConfigParser, ParsingError, NoSectionError

import pyglet
from pyglet.util import debug_print
from pyglet.math import Mat4, Vec3

from . import APPDIR, CONF, LAYOUTS
from . import LAYOUT_TRADITIONAL as L_TRA
from . import IMAGES_TRADITIONAL as I_TRA
from . import LAYOUT_LEVERLESS as L_LEV
from . import IMAGES_LEVERLESS as I_LEV

# Set up the debugging flag calls.
_debug_flag = len(argv) > 1 and argv[1] in ('-D', '-d', '--debug')
_debug_print = debug_print(_debug_flag)
_debug_print("Debugging Active")

# Load the theme from the /theme folder.
pyglet.resource.path.append(join(CONF, "theme"))
pyglet.resource.reindex()
_debug_print("Theme Loaded")

# Create the main window. Use configParser to set a static controller status of unplugged.
config = ConfigParser()
config.add_section('layout')
config.add_section('images')
config.add_section('deadzones')
_debug_print("Main window created")


class _BaseScene:
    def activate(self):
        pass

    def deactivate(self):
        pass


class RetryScene(_BaseScene):
    """
    A scene that tells you to try again if no stick is detected.
    """
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.missing_img = pyglet.resource.image("missing.png")
        self.sprite = pyglet.sprite.Sprite(img=pyglet.resource.image("missing.png"), batch=self.batch)


class ConfigScene(_BaseScene):
    """
    A scene to allow deadzone configuration.
    """
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        bar = pyglet.resource.image("bar.png")
        knob = pyglet.resource.image("knob.png")
        bg_img = pyglet.resource.image('deadzone.png')
        self.bg = pyglet.sprite.Sprite(bg_img, batch=self.batch, group=pyglet.graphics.Group(-1))

        self.stick_slider = pyglet.gui.Slider(100, 150, bar, knob, edge=0, batch=self.batch)
        self.stick_slider.set_handler('on_change', self._stick_slider_handler)
        self.stick_label = pyglet.text.Label("", x=380, y=150, batch=self.batch)

        self.trigger_slider = pyglet.gui.Slider(100, 100, bar, knob, edge=0, batch=self.batch)
        self.trigger_slider.set_handler('on_change', self._trigger_slider_handler)
        self.trigger_label = pyglet.text.Label("", x=380, y=100, batch=self.batch)

    def activate(self):
        self.stick_slider.value = self.manager.stick_deadzone * 100
        self.trigger_slider.value = self.manager.trigger_deadzone * 100
        self.stick_label.text = f"Stick Deadzone: {round(self.manager.stick_deadzone * 100, 2)}"
        self.trigger_label.text = f"Trigger Deadzone: {round(self.manager.trigger_deadzone * 100, 2)}"
        self.manager.window.push_handlers(self.stick_slider)
        self.manager.window.push_handlers(self.trigger_slider)

    def deactivate(self):
        self.manager.window.remove_handlers(self.stick_slider)
        self.manager.window.remove_handlers(self.trigger_slider)
        # save_configuration()

    def _stick_slider_handler(self, slider, value):
        self.stick_label.text = f"Stick Deadzone: {round(value, 2)}"
        scaled_value = round(value / 100, 2)
        self.manager.stick_deadzone = scaled_value
        config.set('deadzones', 'stick', str(scaled_value))

    def _trigger_slider_handler(self, slider, value):
        self.trigger_label.text = f"Trigger Deadzone: {round(value, 2)}"
        scaled_value = round(value / 100, 2)
        self.manager.trigger_deadzone = scaled_value
        config.set('deadzones', 'trigger', str(scaled_value))

    def on_button_press(self, controller, button):
        if button == "guide":
            self.manager.set_scene('main')

    def on_key_press(self, key, modifiers):
        self.manager.set_scene('main')
        return pyglet.event.EVENT_HANDLED


class LayoutScene(_BaseScene):
    """
    Layout scene, with common methods ready to be wired
    """
    def __init__(self, layout, images):
        self.layout = layout
        self.images = images
        self.batch = pyglet.graphics.Batch()
        # Ordered groups to handle draw order of the sprites.
        self.bg = pyglet.graphics.Group(0)
        self.fg = pyglet.graphics.Group(1)
        # Initialize the layout
        self._init_layout()
        # Mapping of (Input names : Sprite names).
        self.button_mapping = {
            "a": self.a_spr,
            "b": self.b_spr,
            "x": self.x_spr,
            "y": self.y_spr,
            "rightshoulder": self.rb_spr,
            "leftshoulder": self.lb_spr,
            "righttrigger": self.rt_spr,
            "lefttrigger": self.lt_spr,
            "back": self.select_spr,
            "start": self.start_spr
        }

    def _make_sprite(self, name, group, visible=True):
        # Helper function to make a Sprite.
        image = pyglet.resource.image(self.images[name])
        position = self.layout[name]
        sprite = pyglet.sprite.Sprite(image, *position, batch=self.batch, group=group)
        sprite.visible = visible
        return sprite

    def _init_layout(self):
        # Create all sprites using helper function (name, batch, group, visible).
        pass

    def on_key_press(self, key, modifiers):
        if key == pyglet.window.key.F1:
            self.manager.set_scene('config')

    # Event to show a button when pressed.
    def on_button_press(self, controller, button):
        assert _debug_print(f"Pressed Button: {button}")
        if button == "guide":
            self.manager.set_scene('config')
        pressed_button = self.button_mapping.get(button, None)
        if pressed_button:
            pressed_button.visible = True

    # Event to hide the sprite when the button is released.
    def on_button_release(self, controller, button):
        pressed_button = self.button_mapping.get(button, None)
        if pressed_button:
            pressed_button.visible = False

    # Math to draw trigger inputs or hide them.
    def on_trigger_motion(self, controller, trigger, value):
        assert _debug_print(f"Pulled Trigger: {trigger}")
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

    # Math to draw stick inputs in their correct location.
    def on_stick_motion(self, controller, stick, vector):
        pass

    # Math to draw dpad inputs in their correct location.
    def on_dpad_motion(self, controller, vector):
        pass


class TraditionalScene(LayoutScene):
    """
    Traditional layout scene, all fightstick events wired up
    """
    def __init__(self, layout=L_TRA, images=I_TRA):
        super().__init__(layout, images)

    def _init_layout(self):
        # Create all sprites using helper function (name, batch, group, visible).
        self.background = self._make_sprite('background', self.bg)
        self.select_spr = self._make_sprite('select', self.fg, False)
        self.start_spr = self._make_sprite('start', self.fg, False)
        self.stick_spr = self._make_sprite('stick', self.fg)
        self.a_spr = self._make_sprite('a', self.fg, False)
        self.b_spr = self._make_sprite('b', self.fg, False)
        self.x_spr = self._make_sprite('x', self.fg, False)
        self.y_spr = self._make_sprite('y', self.fg, False)
        self.rb_spr = self._make_sprite('rb', self.fg, False)
        self.lb_spr = self._make_sprite('lb', self.fg, False)
        self.rt_spr = self._make_sprite('rt', self.fg, False)
        self.lt_spr = self._make_sprite('lt', self.fg, False)

    # Math to draw stick inputs in their correct location.
    def on_stick_motion(self, controller, stick, vector):
        assert _debug_print(f"Moved Stick: {stick}, {vector.x, vector.y}")
        if stick == "leftstick":
            center_x, center_y = self.layout['stick']
            if vector.length() > self.manager.stick_deadzone:
                center_x += vector.x * 50
                center_y += vector.y * 50
            self.stick_spr.position = center_x, center_y, 0

    # Math to draw dpad inputs in their correct location.
    def on_dpad_motion(self, controller, vector):
        assert _debug_print(f"Moved Dpad: {vector.x, vector.y}")
        center_x, center_y = self.layout["stick"]
        center_x += vector.x * 50
        center_y += vector.y * 50
        self.stick_spr.position = center_x, center_y, 0


class LeverlessScene(LayoutScene):
    """
    Leverless layout scene, all fightstick events wired up
    """
    def __init__(self, layout=L_LEV, images=I_LEV):
        super().__init__(layout, images)

    def _init_layout(self):
        # Create all sprites using helper function (name, batch, group, visible).
        self.background = self._make_sprite('background', self.bg)
        self.select_spr = self._make_sprite('select', self.fg, False)
        self.start_spr = self._make_sprite('start', self.fg, False)
        self.up_spr = self._make_sprite("up", self.fg, False)
        self.down_spr = self._make_sprite("down", self.fg, False)
        self.left_spr = self._make_sprite("left", self.fg, False)
        self.right_spr = self._make_sprite("right", self.fg, False)
        self.a_spr = self._make_sprite('a', self.fg, False)
        self.b_spr = self._make_sprite('b', self.fg, False)
        self.x_spr = self._make_sprite('x', self.fg, False)
        self.y_spr = self._make_sprite('y', self.fg, False)
        self.rb_spr = self._make_sprite('rb', self.fg, False)
        self.lb_spr = self._make_sprite('lb', self.fg, False)
        self.rt_spr = self._make_sprite('rt', self.fg, False)
        self.lt_spr = self._make_sprite('lt', self.fg, False)

    # Have the stick inputs alert the main window to draw the sprites.
    def on_stick_motion(self, controller, stick, vector):
        assert _debug_print(f"Moved Stick: {stick}, {vector.x, vector.y}")
        if stick == "leftstick":
            self.up_spr.visible = vector.y > self.manager.stick_deadzone
            self.down_spr.visible = vector.y < -self.manager.stick_deadzone
            self.left_spr.visible = vector.x < -self.manager.stick_deadzone
            self.right_spr.visible = vector.x > self.manager.stick_deadzone

    # Have the dpad hats alert the main window to draw the sprites.
    def on_dpad_motion(self, controller, vector):
        assert _debug_print(f"Moved Dpad: {vector.x, vector.y}")
        self.up_spr.visible = vector.y > 0
        self.down_spr.visible = vector.y < 0
        self.left_spr.visible = vector.x < 0
        self.right_spr.visible = vector.x > 0


#####################################################
#   SceneManager class to handle Scene Switching:
#####################################################

class SceneManager:
    """A Scene Management class.

    The SceneManager is responsible for switching between
    the various scenes cleanly. This includes setting and
    removing Window and Controller events handlers. Global
    state (deadzone, etc.) is also defined here.

    """
    def __init__(self, window_instance, layout="traditional"):
        self.window = window_instance
        self.window.push_handlers(self)

        self.fightstick = None

        # Set up Scene instances:
        self._scenes = {}
        self._current_scene = None
        if layout == "leverless":
            self.add_scene('main', LeverlessScene())
        else:
            self.add_scene('main', TraditionalScene())
        # self.add_scene('main', MainScene(layout))
        self.add_scene('retry', RetryScene())
        self.add_scene('config', ConfigScene())

        # Instantiation a ControllerManager to handle hot-plugging:
        self.controller_manager = pyglet.input.ControllerManager()
        self.controller_manager.on_connect = self.on_controller_connect
        self.controller_manager.on_disconnect = self.on_controller_disconnect

        # Set Scene depending on if there is a Controller:
        controllers = self.controller_manager.get_controllers()
        if controllers:
            self.on_controller_connect(controllers[0])
            self.set_scene('main')
        else:
            self.set_scene('retry')

        # Global state for all Scenes:
        self.stick_deadzone = float(config.get('deadzones', 'stick', fallback='0.2'))
        self.trigger_deadzone = float(config.get('deadzones', 'trigger', fallback='0.8'))

    # Detect if a controller is connected.
    def on_controller_connect(self, controller):
        if not self.fightstick:
            controller.open()
            self.fightstick = controller
            self.fightstick.push_handlers(self._current_scene)
            self.set_scene('main')
        else:
            _debug_print(f"A Controller is already connected: {self.fightstick}")

    # Detect if a controller is disconnected.
    def on_controller_disconnect(self, controller):
        if self.fightstick == controller:
            self.fightstick.remove_handlers(self._current_scene)
            self.fightstick = None
            self.set_scene('retry')

    def add_scene(self, name, instance):
        instance.manager = self
        self._scenes[name] = instance

    def set_scene(self, name):
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
        # Enforce aspect ratio by readjusting the window height.
        aspect_ratio = 1.641025641
        target_width = int(self.window.height * aspect_ratio)
        target_height = int(self.window.width / aspect_ratio)

        if self.window.width != target_width and self.window.height != target_height:
            self.window.set_size(self.window.width, target_height)

    # Window Events:
    def on_draw(self):
        self.window.clear()
        self._current_scene.batch.draw()

    def on_resize(self, width, height):
        projection_matrix = Mat4.orthogonal_projection(0, width, 0, height, 0, 1)
        scale_x = width / 640.0
        scale_y = height / 390.0
        self.window.projection = projection_matrix.scale(Vec3(scale_x, scale_y, 1))
        self.window.viewport = 0, 0, width, height
        return pyglet.event.EVENT_HANDLED


def run(layout):
    # Create the main window. Use configParser to set a static controller status of unplugged.
    window = pyglet.window.Window(
        640, 390, caption="Fightsticker", resizable=True, vsync=False
    )
    window.set_icon(pyglet.resource.image("icon.png"))

    scene_manager = SceneManager(window_instance=window, layout=layout)
    # Enforce aspect ratio by readjusting the window height.
    pyglet.clock.schedule_interval(scene_manager.enforce_aspect_ratio, 0.3)
    pyglet.app.run()
