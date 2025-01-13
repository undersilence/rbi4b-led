import functools
import time
import pygame
from led_matrix import LEDMatrix
import math
from typing import List, Tuple, Dict
import logging
from input_manager import (
    GamepadType,
    InputManager,
    NintendoButtons,
    VirtualButtons,
    get_joystick_type,
)

FONT = {
    "0": ["###", "# #", "# #", "# #", "###"],
    "1": [" # ", "## ", " # ", " # ", "###"],
    "2": ["###", "  #", "###", "#  ", "###"],
    "3": ["###", "  #", "###", "  #", "###"],
    "4": ["# #", "# #", "###", "  #", "  #"],
    "5": ["###", "#  ", "###", "  #", "###"],
    "6": ["###", "#  ", "###", "# #", "###"],
    "7": ["###", "  #", "  #", "  #", "  #"],
    "8": ["###", "# #", "###", "# #", "###"],
    "9": ["###", "# #", "###", "  #", "###"],
    "A": [" # ", "# #", "###", "# #", "# #"],
    "B": ["## ", "# #", "## ", "# #", "## "],
    "C": [" ##", "#  ", "#  ", "#  ", " ##"],
    "D": ["## ", "# #", "# #", "# #", "## "],
    "E": ["###", "#  ", "## ", "#  ", "###"],
    "F": ["###", "#  ", "## ", "#  ", "#  "],
    "G": [" ##", "#  ", "# #", "# #", " ##"],
    "H": ["# #", "# #", "###", "# #", "# #"],
    "I": ["###", " # ", " # ", " # ", "###"],
    "J": ["  #", "  #", "  #", "# #", " # "],
    "K": ["# #", "# #", "## ", "# #", "# #"],
    "L": ["#  ", "#  ", "#  ", "#  ", "###"],
    "M": ["# #", "###", "###", "# #", "# #"],
    "N": ["# #", "###", "###", "###", "# #"],
    "O": [" # ", "# #", "# #", "# #", " # "],
    "P": ["## ", "# #", "## ", "#  ", "#  "],
    "Q": [" # ", "# #", "# #", " ##", "  #"],
    "R": ["## ", "# #", "## ", "# #", "# #"],
    "S": [" ##", "#  ", " # ", "  #", "## "],
    "T": ["###", " # ", " # ", " # ", " # "],
    "U": ["# #", "# #", "# #", "# #", "###"],
    "V": ["# #", "# #", "# #", "# #", " # "],
    "W": ["# #", "# #", "###", "###", "# #"],
    "X": ["# #", "# #", " # ", "# #", "# #"],
    "Y": ["# #", "# #", " # ", " # ", " # "],
    "Z": ["###", "  #", " # ", "#  ", "###"],
    ".": ["   ", "   ", "   ", "   ", " # "],
    ",": ["   ", "   ", "   ", " # ", "#  "],
    "!": [" # ", " # ", " # ", "   ", " # "],
    "?": ["###", "  #", " ##", "   ", " # "],
    "-": ["   ", "   ", "###", "   ", "   "],
    "_": ["   ", "   ", "   ", "   ", "###"],
    " ": ["   ", "   ", "   ", "   ", "   "],
    ":": ["   ", " # ", "   ", " # ", "   "],
}


# Basic Input Buttons
class GamepadButtons:
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    NUM = 8


InputMapping = {
    GamepadType.NINTENDO: {
        GamepadButtons.A: NintendoButtons.A,
        GamepadButtons.B: NintendoButtons.B,
        GamepadButtons.X: NintendoButtons.X,
        GamepadButtons.Y: NintendoButtons.Y,
        GamepadButtons.LB: NintendoButtons.LEFT_BUMPER,
        GamepadButtons.RB: NintendoButtons.RIGHT_BUMPER,
        GamepadButtons.BACK: NintendoButtons.MINUS,
        GamepadButtons.START: NintendoButtons.PLUS,
    },
    GamepadType.VIRTUAL: {
        GamepadButtons.A: VirtualButtons.A,
        GamepadButtons.B: VirtualButtons.B,
        GamepadButtons.X: VirtualButtons.X,
        GamepadButtons.Y: VirtualButtons.Y,
        GamepadButtons.LB: VirtualButtons.LB,
        GamepadButtons.RB: VirtualButtons.RB,
        GamepadButtons.BACK: VirtualButtons.BACK,
        GamepadButtons.START: VirtualButtons.START,
    },
}


class VfxUtils:
    @staticmethod
    def generate_breath_curve_table(size: int = 256) -> List[float]:
        return [0.5 * (1 + math.cos(2 * math.pi * i / size)) for i in range(size)]

    BREATH_CURVE_TABLE = generate_breath_curve_table()

    @staticmethod
    def breath_curve(t: float, duration: float, freq: float = 1) -> float:
        index = int((t * freq / duration) * len(VfxUtils.BREATH_CURVE_TABLE)) % len(
            VfxUtils.BREATH_CURVE_TABLE
        )
        return VfxUtils.BREATH_CURVE_TABLE[index]

    @staticmethod
    def wheel(pos: int) -> Tuple[int, int, int]:
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)


class BaseApp:
    ICON: List[str] = []

    def __init__(
        self, matrix: LEDMatrix, target_fps=30, clear_before_render=True
    ) -> None:
        self.matrix = matrix
        self.keep_running = True
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.clear_before_render = clear_before_render
        self._input_manager = InputManager()
        self._input_devices = [None] * 4  # Support up to 4 players
        self._available_devices = []

    def execute(self) -> None:
        delta_time_ms = 0
        self.keep_running = True
        self.connect_device()
        self.reset()
        logging.info(f"Running {self.info()} with fps={self.target_fps}")

        while self.keep_running:
            if self.clear_before_render:
                self.matrix.clear()
            self.handle_events()
            self._input_manager.update()
            self.update(delta_time_ms / 1000.0)
            self.render()
            self.matrix.show()
            delta_time_ms = self.clock.tick(self.target_fps)

        logging.info(f"Exiting {self.info()}")

    def reset(self) -> None:
        pass

    def update(self, delta_time) -> None:
        pass

    def render(self) -> None:
        pass

    def info(self) -> str:
        return self.__class__.__name__

    def on_remove_joystick(self, joystick) -> None:
        self._input_manager.remove_joystick(joystick)
        self.disconnect_device(joystick.get_id())

    def on_add_joystick(self, joystick) -> None:
        self._input_manager.add_joystick(joystick)
        self.connect_device()

    def refresh_available_devices(self) -> None:
        self._available_devices = [
            joystick_info
            for joystick_info in self._input_devices
            if joystick_info is not None
        ]

    def disconnect_device(self, joystick_id) -> None:
        for i in range(len(self._input_devices)):
            if self._input_devices[i] is None:
                continue
            current_joystick_id, _ = self._input_devices[i]
            if current_joystick_id == joystick_id:
                self._input_devices[i] = None

        self.refresh_available_devices()

    def connect_device(self) -> None:
        joystick_id_types = [
            (js.get_instance_id(), get_joystick_type(js))
            for js in self._input_manager.joysticks
        ]

        for i in range(len(self._input_devices)):
            if self._input_devices[i] is None:
                for joystick_info in joystick_id_types:
                    if joystick_info not in self._input_devices:
                        self._input_devices[i] = joystick_info
                        break

        self.refresh_available_devices()

    def handle_events(self) -> None:
        for e in pygame.event.get():
            if e.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(e.device_index)
                joystick.init()
                self.on_add_joystick(joystick)
                logging.info(f"Joystick {joystick.get_name()} added.")

            elif e.type == pygame.JOYDEVICEREMOVED:
                for joystick in self._input_manager.joysticks:
                    if joystick.get_instance_id() == e.instance_id:
                        self.on_remove_joystick(joystick)
                        logging.info(f"Joystick {joystick.get_name()} removed.")
            else:
                logging.info(e)

    def get_joystick_id_with_type(self, device_index: int = -1) -> int:
        """
        Get the joystick ID for the player at the given index, if default value is used, return the first available player ID.
        """
        if device_index < 0:
            return self._available_devices[0] if self._available_devices else None
        return self._input_devices[device_index]

    def is_pressed(self, button: GamepadButtons, device_index: int = -1):
        joystick_info = self.get_joystick_id_with_type(device_index)
        if joystick_info is None:
            return False
        
        joystick_id, joystick_type = joystick_info
        device_button = InputMapping[joystick_type][button]
        return self._input_manager.is_pressed(joystick_id, device_button)

    def is_holding(self, button: GamepadButtons, device_index: int = -1):
        joystick_info = self.get_joystick_id_with_type(device_index)
        if joystick_info is None:
            return False
        
        joystick_id, joystick_type = joystick_info
        device_button = InputMapping[joystick_type][button]
        return self._input_manager.is_holding(joystick_id, device_button)

    def is_released(self, button: GamepadButtons, device_index: int = -1):
        joystick_info = self.get_joystick_id_with_type(device_index)
        if joystick_info is None:
            return False
        
        joystick_id, joystick_type = joystick_info
        device_button = InputMapping[joystick_type][button]
        return self._input_manager.is_released(joystick_id, device_button)

    def get_vector(self, hat_id: int = 0, device_index: int = -1):
        joystick_info = self.get_joystick_id_with_type(device_index)
        if joystick_info is None:
            return [0, 0]
        
        joystick_id, joystick_type = joystick_info
        if joystick_type == GamepadType.NINTENDO:
            dpad_up = self._input_manager.is_holding(joystick_id, NintendoButtons.D_PAD_UP)
            dpad_down = self._input_manager.is_holding(joystick_id, NintendoButtons.D_PAD_DOWN)
            dpad_left = self._input_manager.is_holding(joystick_id, NintendoButtons.D_PAD_LEFT)
            dpad_right = self._input_manager.is_holding(joystick_id, NintendoButtons.D_PAD_RIGHT)
            
            x = -1 if dpad_left else 1 if dpad_right else 0
            y = -1 if dpad_up else 1 if dpad_down else 0
            return x, y
        else:
            return (
                self._input_manager.get_axis(joystick_id, 0),
                self._input_manager.get_axis(joystick_id, 1),
            )
