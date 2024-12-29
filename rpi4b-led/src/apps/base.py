import time
import pygame
from led_matrix import LEDMatrix
import math
from typing import List, Tuple

import logging

class GamepadButtons:
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    GUIDE = 8
    LEFTSTICK = 9
    RIGHTSTICK = 10


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
        index = int((t * freq / duration) * len(VfxUtils.BREATH_CURVE_TABLE)) % len(VfxUtils.BREATH_CURVE_TABLE)
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

    def execute(self) -> None:
        self.keep_running = True
        delta_time_ms = 0
        self.reset()
        logging.info(f"Running {self.info()} with fps={self.target_fps}")
        while self.keep_running:
            if self.clear_before_render:
                self.matrix.clear()
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