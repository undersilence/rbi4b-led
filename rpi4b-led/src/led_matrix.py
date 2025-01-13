from rpi_ws281x import PixelStrip, Color
import os
import sys

class LEDMatrix:

    def __init__(self, width, height, led_count, pin, pixel_width=1, pixel_height=1, freq_hz=800000, dma=10, brightness=255, invert=False, channel=0, simulate=False):
        self.width = width
        self.height = height
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.led_count = led_count
        self.simulate = simulate
        if not simulate:
            self.strip = PixelStrip(led_count, pin, freq_hz, dma, invert, brightness, channel)
            self.strip.begin()
        self.pixels = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
            if not self.simulate:
                for dx in range(self.pixel_width):
                    for dy in range(self.pixel_height):
                        actual_x = x * self.pixel_width + dx
                        actual_y = (self.height - 1 - y) * self.pixel_height + dy  # Adjust for physical coordinate system
                        led_index = self._get_led_index(actual_x, actual_y)
                        self.strip.setPixelColor(led_index, Color(color[1], color[0], color[2]))  # Ensure correct RGB order

    def _get_led_index(self, x, y):
        """Calculate the actual LED index for a given (x, y) coordinate."""
        if y % 2 == 0:
            # Even row: left to right
            return y * self.width * self.pixel_width + x
        else:
            # Odd row: right to left
            return y * self.width * self.pixel_width + (self.width * self.pixel_width - 1 - x)

    def show(self):
        if self.simulate:
            print("\033[H\033[J", end="")  # Clear screen and move cursor to the top-left corner
            for row in self.pixels:
                for pixel in row:
                    print(self._color_to_char(pixel), end="")
                print()
            sys.stdout.flush()
        else:
            self.strip.show()

    def _color_to_char(self, color):
        if color == (0, 0, 0):
            return "\033[48;2;0;0;0m  \033[0m"  # Black background
        return f"\033[48;2;{color[0]};{color[1]};{color[2]}m  \033[0m"  # Colored background

    def clear(self):
        self.pixels = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        if not self.simulate:
            for i in range(self.led_count):
                self.strip.setPixelColor(i, 0)

    def draw_sprite(self, x_offset, y_offset, sprite):
        for y, row in enumerate(sprite):
            for x, color in enumerate(row):
                if 0 <= x + x_offset < self.width and 0 <= y + y_offset < self.height:
                    self.set_pixel(x + x_offset, y + y_offset, color)