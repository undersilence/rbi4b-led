import time
import math
from typing import List, Tuple
from pygame import key, K_ESCAPE
from led_matrix import LEDMatrix

from .base import BaseApp, GamepadButtons, FONT, VfxUtils
from input_manager import InputManager


class ClockApp(BaseApp):
    ICON = ["  ###  ", " #   # ", "#  #  #", "#  ## #", "#     #", " #   # ", "  ###  "]

    # X_X:X_X
    padding = [1, 1, 0, 0, 0, 0, 0, 0, 1, 0]

    def update(self, delta_time: float) -> None:
        
        if self.is_pressed(GamepadButtons.BACK):
            self.keep_running = False
        
        now = time.localtime()
        self.current_hour = now.tm_hour
        self.current_minute = now.tm_min
        self.current_second = now.tm_sec
        self.milliseconds = int(time.time() * 1000) % 1000
        self.brightness = VfxUtils.breath_curve(
            self.milliseconds, 1000
        )  # Breathing effect
        self.current_time = f"{self.current_hour:02}:{self.current_minute:02}"

    def render(self) -> None:
        total_width = sum(len(FONT[char][0]) for char in self.current_time) + sum(
            self.padding
        )  # Calculate total width
        x_offset = (
            self.matrix.width - total_width
        ) // 2  # Center the clock horizontally
        y_offset = (self.matrix.height - 5) // 2  # Center vertically
        for idx, char in enumerate(self.current_time):
            x_offset += self.padding[idx * 2]
            pattern = FONT[char]
            if char == ":":
                base_color = self.get_color_from_time()
                color = (
                    int(base_color[0] * self.brightness),
                    int(base_color[1] * self.brightness),
                    int(base_color[2] * self.brightness),
                )
            else:
                color = self.get_color_from_time()
            sprite = [
                [color if pixel == "#" else (0, 0, 0) for pixel in row]
                for row in pattern
            ]
            self.matrix.draw_sprite(x_offset, y_offset, sprite)
            x_offset += (
                len(pattern[0]) + self.padding[idx * 2 + 1]
            )  # No extra space for colon, space for other characters

    def get_color_from_time(self) -> Tuple[int, int, int]:
        """Map the current time to a color in the 0-255 rainbow color wheel."""
        total_seconds = (
            self.current_hour * 3600 + self.current_minute * 60 + self.current_second
        )
        color_position = int((total_seconds / 86400) * 255)  # Map to 0-255
        return VfxUtils.wheel(color_position)
