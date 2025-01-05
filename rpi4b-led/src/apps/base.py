import functools
import time
import pygame
from led_matrix import LEDMatrix
import math
from typing import List, Tuple, Dict
import logging
from input_manager import InputManager, GamepadButtons

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

    def disconnect_device(self, joystick_id) -> None:
        for i in range(len(self._input_devices)):
            if self._input_devices[i] == joystick_id:
                self._input_devices[i] = None
        
        self._available_devices = [joystick_id for joystick_id in self._input_devices if joystick_id is not None]

    def connect_device(self) -> None:
        joystick_ids = self._input_manager.get_joystick_ids()

        for i in range(len(self._input_devices)):
            if self._input_devices[i] is None:
                for joystick_id in joystick_ids:
                    if joystick_id not in self._input_devices:
                        self._input_devices[i] = joystick_id
                        break
                    
        self._available_devices = [joystick_id for joystick_id in self._input_devices if joystick_id is not None]
        
    def handle_events(self) -> None:
        for e in pygame.event.get():
            if e.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(e.device_index)
                joystick.init()
                self.on_add_joystick(joystick)
                logging.info(f"Joystick {joystick.get_name()} added.")

            elif e.type == pygame.JOYDEVICEREMOVED:
                for joystick in self._input_manager._joysticks:
                    if joystick.get_instance_id() == e.instance_id:
                        self.on_remove_joystick(joystick)
                        logging.info(f"Joystick {joystick.get_name()} removed.")
    
    def get_joystick_id(self, device_index: int = -1) -> int:
        """
        Get the joystick ID for the player at the given index, if default value is used, return the first available player ID.
        """
        if device_index < 0:
            return self._available_devices[0] if self._available_devices else None
        return self._input_devices[device_index]
    
    def is_pressed(self, button, device_index: int = -1):
        joystick_id = self.get_joystick_id(device_index)
        if joystick_id is None:
            return False
        return self._input_manager.is_pressed(joystick_id, button)

    def is_holding(self, button, device_index: int = -1):
        joystick_id = self.get_joystick_id(device_index)
        if joystick_id is None:
            return False
        return self._input_manager.is_holding(joystick_id, button)
    
    def is_released(self, button, device_index: int = -1):
        joystick_id = self.get_joystick_id(device_index)
        if joystick_id is None:
            return False
        return self._input_manager.is_released(joystick_id, button)
    
    def get_axis(self, axis: int, device_index: int = -1):
        joystick_id = self.get_joystick_id(device_index)
        if joystick_id is None:
            return False
        return self._input_manager.get_axis(joystick_id, axis)
    
    def get_axes(self, device_index: int = -1):
        joystick_id = self.get_joystick_id(device_index)
        if joystick_id is None:
            return [0, 0]
        return self._input_manager.get_axes(joystick_id)