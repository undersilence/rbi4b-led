from typing import List
from pygame import Color, event, KEYDOWN, JOYBUTTONDOWN
import pygame
import logging

from .base import BaseApp, GamepadButtons
from led_matrix import LEDMatrix


class MenuApp(BaseApp):
    def __init__(
        self,
        apps: List[BaseApp],
        matrix: LEDMatrix,
        target_fps=30,
        clear_before_render=True,
    ) -> None:
        super().__init__(matrix, target_fps, clear_before_render)
        self.apps = apps
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            logging.info(f"Joystick {joystick.get_name()} added.")

    def reset(self) -> None:
        self.current_row = 0
        self.target_row = 0
        self.animation_progress = 0
        self.switch_time = 0.2  # Adjust this value to control the animation speed
        self.direction = 0  # -1 for left, 1 for right

    def update(self, delta_time: float) -> None:
        for e in pygame.event.get():
            if e.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(e.device_index)
                joystick.init()
                self.joysticks.append(joystick)
                logging.info(f"Joystick {joystick.get_name()} added.")
            elif e.type == pygame.JOYDEVICEREMOVED:
                for joystick in self.joysticks:
                    if joystick.get_instance_id() == e.instance_id:
                        logging.info(f"Joystick {joystick.get_name()} removed.")
                        self.joysticks.remove(joystick)
            elif e.type == JOYBUTTONDOWN:
                if e.button == GamepadButtons.A:  # Confirm button
                    if self.current_row < len(self.apps):
                        self.apps[self.current_row].execute()
            elif e.type == KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.target_row = self.current_row - 1
                    self.direction = -1
                elif e.key == pygame.K_RIGHT:
                    self.target_row = self.current_row + 1
                    self.direction = 1
                elif e.key == pygame.K_RETURN:
                    if self.current_row < len(self.apps):
                        self.apps[self.current_row].execute()
            elif e.type == pygame.JOYHATMOTION:
                if e.value[0] == -1:  # Left
                    self.target_row = self.current_row - 1
                    self.direction = -1
                elif e.value[0] == 1:  # Right
                    self.target_row = self.current_row + 1
                    self.direction = 1
            elif e.type == pygame.JOYAXISMOTION:
                if e.axis == 0:  # Horizontal axis
                    if e.value < -0.5:  # Left
                        self.target_row = self.current_row - 1
                        self.direction = -1
                    elif e.value > 0.5:  # Right
                        self.target_row = self.current_row + 1
                        self.direction = 1

        self.target_row = (self.target_row + len(self.apps)) % len(self.apps)

        if self.current_row != self.target_row:
            self.animation_progress += delta_time / self.switch_time
            if self.animation_progress >= 1:
                self.animation_progress = 0
                self.current_row = self.target_row

    def render(self) -> None:
        self.matrix.clear()
        old_icon = self.apps[self.current_row].ICON
        new_icon = self.apps[self.target_row].ICON
        icon_width = len(old_icon[0])
        icon_height = len(old_icon)
        x_offset = (self.matrix.width - icon_width) // 2
        y_offset = (self.matrix.height - icon_height) // 2

        if self.current_row != self.target_row:
            offset = int(self.animation_progress * self.matrix.width)
            if self.direction == 1:  # Right
                self.matrix.draw_sprite(
                    x_offset - offset,
                    y_offset,
                    [
                        [
                            (255, 255, 255) if pixel == "#" else (0, 0, 0)
                            for pixel in row
                        ]
                        for row in old_icon
                    ],
                )
                self.matrix.draw_sprite(
                    x_offset + self.matrix.width - offset,
                    y_offset,
                    [
                        [
                            (255, 255, 255) if pixel == "#" else (0, 0, 0)
                            for pixel in row
                        ]
                        for row in new_icon
                    ],
                )
            else:  # Left
                self.matrix.draw_sprite(
                    x_offset + offset,
                    y_offset,
                    [
                        [
                            (255, 255, 255) if pixel == "#" else (0, 0, 0)
                            for pixel in row
                        ]
                        for row in old_icon
                    ],
                )
                self.matrix.draw_sprite(
                    x_offset - self.matrix.width + offset,
                    y_offset,
                    [
                        [
                            (255, 255, 255) if pixel == "#" else (0, 0, 0)
                            for pixel in row
                        ]
                        for row in new_icon
                    ],
                )
        else:
            self.matrix.draw_sprite(
                x_offset,
                y_offset,
                [
                    [(255, 255, 255) if pixel == "#" else (0, 0, 0) for pixel in row]
                    for row in old_icon
                ],
            )
