import time
from led_matrix import LEDMatrix
from .base import BaseApp, GamepadButtons, VfxUtils
from typing import List, Tuple
import math
import random

def color_temperature_to_rgb(kelvin: int) -> Tuple[int, int, int]:
    # Convert color temperature in Kelvin to RGB
    temp = kelvin / 100.0
    if temp <= 66:
        red = 255
        green = temp
        green = 99.4708025861 * math.log(green) - 161.1195681661
        if temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
    else:
        red = temp - 60
        red = 329.698727446 * (red ** -0.1332047592)
        green = temp - 60
        green = 288.1221695283 * (green ** -0.0755148492)
        blue = 255

    return (
        max(0, min(255, int(red))),
        max(0, min(255, int(green))),
        max(0, min(255, int(blue))),
    )
    
class ScreenTestApp(BaseApp):
    ICON = [" ######", " #    #", " #    #", " #    #", " #    #", " #    #", " ######"]
    EFFECT_DURATION = 3600 * 24 * 365 * 100  # 100 years

    def reset(self):
        self.clear_before_render = False  # No need to clean the screen before rendering
        self.effect_index = 0
        self.effects = [self.breathing_wall, self.white_screen, self.color_wipe, self.rainbow, self.rainbow_cycle]
        self.effect_timer = 0
        self.breathing_frequencies = [
            [random.uniform(0.05, 0.15) for _ in range(self.matrix.width)]
            for _ in range(self.matrix.height)
        ]

    def update(self, delta_time: float) -> None:
        
        if self.is_pressed(GamepadButtons.BACK):
            self.keep_running = False
        elif self.is_pressed(GamepadButtons.A):
            self.effect_timer = 0
            self.effect_index = (self.effect_index + 1) % len(self.effects)
                
        self.effect_timer += delta_time
        if self.effect_timer > self.EFFECT_DURATION:  # Change effect every 10 seconds
            self.effect_timer = 0
            self.effect_index = (self.effect_index + 1) % len(self.effects)

    def render(self) -> None:
        self.matrix.clear()
        self.effects[self.effect_index]()
        self.matrix.show()

    def white_screen(self) -> None:
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                self.matrix.set_pixel(x, y, (255, 255, 255))

    def color_wipe(self, wait_ms=10) -> None:
        w, h = self.matrix.width, self.matrix.height
        count = int(self.effect_timer * 1000 / wait_ms) % (w * h)
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                idx = y * w + x
                if idx < count:
                    self.matrix.set_pixel(x, y, VfxUtils.wheel((x + y + count) & 255))

    def rainbow(self, wait_ms=10) -> None:
        count = int(self.effect_timer * 1000 / wait_ms)
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                self.matrix.set_pixel(x, y, VfxUtils.wheel((x + y + count) & 255))

    def rainbow_cycle(self, wait_ms=10) -> None:
        count = int(self.effect_timer * 1000 / wait_ms)
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                self.matrix.set_pixel(
                    x,
                    y,
                    VfxUtils.wheel((int(x * 256 / self.matrix.width) + count) & 255),
                )
                
    def breathing_wall(self, wait_ms=10) -> None:
        base_color = color_temperature_to_rgb(3000)
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                # Calculate brightness for each row, decreasing from bottom to top
                brightness = (y + 1) / self.matrix.height
                # Apply a sine wave for breathing effect with added randomness
                frequency = self.breathing_frequencies[y][x]
                breath = (math.sin(self.effect_timer * 2 * math.pi * frequency) + 1) / 2
                breath = 0.5 + 0.5 * breath  # Ensure it doesn't go completely dark
                final_brightness = brightness * breath
                # Set the pixel color with the calculated brightness
                final_color = tuple(int(c * final_brightness) for c in base_color)
                self.matrix.set_pixel(x, y, final_color)