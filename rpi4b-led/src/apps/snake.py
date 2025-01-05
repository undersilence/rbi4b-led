import random
from typing import List, Tuple
from pygame import (
    Color,
    event,
    KEYDOWN,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    JOYBUTTONDOWN,
    JOYBUTTONUP,
    JOYAXISMOTION,
    K_ESCAPE,
    key,
)
from led_matrix import LEDMatrix
from .base import BaseApp, GamepadButtons, FONT, VfxUtils
import math


class SnakeApp(BaseApp):
    ICON = [" ##### ", "     # ", " ### # ", " # # # ", " # # # ", " #   # ", " ##### "]

    def reset(self) -> None:
        self.reset_game_state()
        self.bind_device()
        
    def reset_game_state(self) -> None:
        self.snake: List[Tuple[int, int]] = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)  # Initial direction: right
        self.food: List[Tuple[int, int]] = []
        self.score = 0
        self.food_timer = 0
        self.food_interval = random.uniform(3, 5)  # Generate food every 3 to 5 seconds
        self.speed = 1
        self.max_speed = 3  # Maximum speed multiplier
        self.speed_multiplier = 1
        self.move_timer = 0
        self.move_interval = 0.5  # Snake moves every 0.5 seconds
        self.game_over = False  # Game over flag
        self.show_score_timer = 0

        self.food.append(self._generate_food())

    def _generate_food(self) -> Tuple[int, int]:
        while True:
            food = (
                random.randint(0, self.matrix.width - 1),
                random.randint(0, self.matrix.height - 1),
            )
            if food not in self.snake and food not in self.food:
                return food
    
    def update(self, delta_time: float) -> None:
        if self.is_holding(GamepadButtons.A):
            self.speed_multiplier = 2
        else:
            self.speed_multiplier = 1

        if self.is_pressed(GamepadButtons.START):
            self.reset_game_state()
        elif self.is_pressed(GamepadButtons.BACK):
            self.keep_running = False

        axis_0, axis_1 = self.get_axes()
        if axis_0 < -0.5 and self.direction != (1, 0):  # Left
            self.direction = (-1, 0)
        elif axis_0 > 0.5 and self.direction != (-1, 0):  # Right
            self.direction = (1, 0)
        if axis_1 < -0.5 and self.direction != (0, 1):  # Up
            self.direction = (0, -1)
        elif axis_1 > 0.5 and self.direction != (0, -1):  # Down
            self.direction = (0, 1)

        if self.game_over:
            self.show_score_timer -= delta_time
            if self.show_score_timer <= 0:
                self.reset_game_state()
            return

        self.food_timer += delta_time
        self.move_timer += delta_time * self.speed * self.speed_multiplier

        if self.food_timer >= self.food_interval and len(self.food) < 3:
            self.food_timer = 0
            self.food_interval = random.uniform(3, 4)  # Reset food interval
            self.food.append(self._generate_food())

        if self.move_timer >= self.move_interval:
            self.move_timer = 0

            # Move snake
            new_head = (
                self.snake[0][0] + self.direction[0],
                self.snake[0][1] + self.direction[1],
            )
            if new_head in self.snake or not (
                0 <= new_head[0] < self.matrix.width
                and 0 <= new_head[1] < self.matrix.height
            ):
                self.game_over = True  # Snake collided with itself or the wall
                self.show_score_timer = 3  # Show score for 3 seconds
            else:
                self.snake.insert(0, new_head)
                if new_head in self.food:
                    self.food.remove(new_head)
                    self.score += 1
                    self.speed = min(
                        1 + self.score / 10, self.max_speed
                    )  # Increase speed based on score
                else:
                    self.snake.pop()

    def render(self) -> None:
        if self.game_over:
            self._show_score()
            return

        for segment in self.snake:
            self.matrix.set_pixel(segment[0], segment[1], (0, 255, 0))  # Green snake
        for f in self.food:
            self.matrix.set_pixel(f[0], f[1], (255, 0, 0))  # Red food

    def _show_score(self) -> None:
        score_str = f"{self.score}"
        x_offset = (self.matrix.width - len(score_str) * 4) // 2
        y_offset = (self.matrix.height - 5) // 2  # Center vertically
        brightness = VfxUtils.breath_curve(
            self.show_score_timer, 3, 2
        )  # Breathing effect
        for i, char in enumerate(score_str):
            pattern = FONT[char]
            color = (
                int(255 * brightness),
                int(255 * brightness),
                int(255 * brightness),
            )
            self.matrix.draw_sprite(
                x_offset + i * 4,
                y_offset,
                [
                    [color if pixel == "#" else (0, 0, 0) for pixel in row]
                    for row in pattern
                ],
            )