import pygame
from typing import List, Dict
import logging
import copy


class VirtualButtons:
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    NUM = 8


class NintendoButtons:
    A = 0
    B = 1
    X = 2
    Y = 3
    MINUS = 4
    HOME = 5
    PLUS = 6
    L_STICK_IN = 7
    R_STICK_IN = 8
    LEFT_BUMPER = 9
    RIGHT_BUMPER = 10
    D_PAD_UP = 11
    D_PAD_DOWN = 12
    D_PAD_LEFT = 13
    D_PAD_RIGHT = 14
    CAPTURE = 15
    NUM = 16


class GamepadType:
    VIRTUAL = "Virtual"
    NINTENDO = "Nintendo"
    NOSUPPORT = "Unknown"


def get_joystick_type(joystick: pygame.joystick.Joystick) -> GamepadType:
    if GamepadType.NINTENDO in joystick.get_name():
        return GamepadType.NINTENDO
    if GamepadType.VIRTUAL in joystick.get_name():
        return GamepadType.VIRTUAL
    return GamepadType.NOSUPPORT


class InputManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(InputManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, joysticks: List[pygame.joystick.Joystick] = None) -> None:
        if self._initialized:
            return

        self.joysticks: List[pygame.joystick.Joystick] = joysticks or []
        self.button_states: Dict[int, Dict[int, bool]] = {}
        self.previous_button_states: Dict[int, Dict[int, bool]] = {}
        self.axis_states: Dict[int, List[float]] = {}
        self.hats_states: Dict[int, List[int]] = {}
        for js in self.joysticks:
            self.update_joystick_states(js.get_instance_id(), js)
        self.previous_button_states = self.button_states.copy()
        self._initialized = True

    def update_joystick_states(self, joystick_id, joystick):
        self.button_states[joystick_id] = {
            button: joystick.get_button(button)
            for button in range(joystick.get_numbuttons())
        }
        self.axis_states[joystick_id] = [
            joystick.get_axis(i) for i in range(joystick.get_numaxes())
        ]
        self.hats_states[joystick_id] = [
            joystick.get_hat(i) for i in range(joystick.get_numhats())
        ]

    def update(self) -> None:
        for joystick in self.joysticks:
            joystick_id = joystick.get_instance_id()
            self.previous_button_states[joystick_id].update(
                self.button_states[joystick_id]
            )
            self.update_joystick_states(joystick_id, joystick)
            # if self.previous_button_states != self.button_states:
            #     logging.info(self.button_states)

    def is_pressed(self, joystick_id: int, button: int) -> bool:
        return (
            self.button_states[joystick_id][button]
            and not self.previous_button_states[joystick_id][button]
        )

    def is_holding(self, joystick_id: int, button: int) -> bool:
        return (
            self.button_states[joystick_id][button]
            and self.previous_button_states[joystick_id][button]
        )

    def is_released(self, joystick_id: int, button: int) -> bool:
        return (
            not self.button_states[joystick_id][button]
            and self.previous_button_states[joystick_id][button]
        )

    def get_axis(self, joystick_id: int, axis: int) -> float:
        return self.axis_states[joystick_id][axis]

    def get_hat(self, joystick_id: int, hat_id: int = 0) -> List[int]:
        return self.hats_states[joystick_id][hat_id]

    def add_joystick(self, joystick: pygame.joystick.Joystick) -> None:
        if joystick in self.joysticks:
            return

        joystick_id = joystick.get_instance_id()
        self.joysticks.append(joystick)
        self.update_joystick_states(joystick_id, joystick)
        self.previous_button_states[joystick_id] = self.button_states[joystick_id].copy()

    def remove_joystick(self, joystick: pygame.joystick.Joystick) -> None:
        joystick_id = joystick.get_instance_id()
        self.joysticks.remove(joystick)

        del self.button_states[joystick_id]
        del self.axis_states[joystick_id]
        del self.previous_button_states[joystick_id]
        del self.hats_states[joystick_id]
