import time
from pygame import event, KEYDOWN, K_ESCAPE, JOYBUTTONDOWN
from led_matrix import LEDMatrix
from .base import BaseApp, GamepadButtons, VfxUtils
from typing import List, Tuple
import math


class ScreenTestApp(BaseApp):
    ICON = [" ######", " #    #", " #    #", " #    #", " #    #", " #    #", " ######"]

    def reset(self):
        self.clear_before_render = False  # No need to clean the screen before rendering
        self.effect_index = 0
        self.effects = [self.marquee, self.white_screen, self.color_wipe, self.rainbow, self.rainbow_cycle]
        self.effect_timer = 0

    def update(self, delta_time: float) -> None:
        for e in event.get():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.keep_running = False
            elif e.type == JOYBUTTONDOWN:
                if e.button == GamepadButtons.BACK:
                    self.keep_running = False
                else:
                    self.effect_timer = 0
                    self.effect_index = (self.effect_index + 1) % len(self.effects)

        self.effect_timer += delta_time
        if self.effect_timer > 10:  # Change effect every 10 seconds
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
        
    def marquee(self) -> None:
        t = time.time()
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                seed = x + y + int(t * 100)
                if seed % 2 == 0:
                    self.matrix.set_pixel(x, y, VfxUtils.wheel(seed & 255))
                else:
                    self.matrix.set_pixel(x, y, (0, 0, 0))

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
