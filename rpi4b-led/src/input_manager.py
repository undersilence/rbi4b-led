import pygame
from typing import List, Dict
import logging
import copy


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
        
        self._joysticks = joysticks or []
        self.button_states: Dict[int, Dict[int, bool]] = {
            js.get_id(): {
                button: js.get_button(button) for button in range(GamepadButtons.NUM)
            }
            for js in self._joysticks
        }
        self.previous_button_states: Dict[int, Dict[int, bool]] = {
            js.get_id(): {
                button: js.get_button(button) for button in range(GamepadButtons.NUM)
            }
            for js in self._joysticks
        }
        self.axis_states: Dict[int, List[float]] = {
            js.get_id(): [0.0] * js.get_numaxes() for js in self._joysticks
        }
        self._initialized = True

    def update(self) -> None:
        self._update_joystick_states()

    def _update_joystick_states(self) -> None:
        for js in self._joysticks:
            joystick_id = js.get_id()
            current_button_states = {
                GamepadButtons.A: js.get_button(GamepadButtons.A),
                GamepadButtons.B: js.get_button(GamepadButtons.B),
                GamepadButtons.X: js.get_button(GamepadButtons.X),
                GamepadButtons.Y: js.get_button(GamepadButtons.Y),
                GamepadButtons.LB: js.get_button(GamepadButtons.LB),
                GamepadButtons.RB: js.get_button(GamepadButtons.RB),
                GamepadButtons.BACK: js.get_button(GamepadButtons.BACK),
                GamepadButtons.START: js.get_button(GamepadButtons.START),
            }

            self.previous_button_states[joystick_id].update(
                self.button_states[joystick_id]
            )
            self.button_states[joystick_id] = current_button_states

            # if (
            #     self.previous_button_states[joystick_id]
            #     != self.button_states[joystick_id]
            # ):
            #     logging.debug(
            #         f"Joystick {joystick_id} button states: {current_button_states}"
            #     )

            current_axis_states = [js.get_axis(i) for i in range(js.get_numaxes())]
            self.axis_states[joystick_id] = current_axis_states

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

    def get_axes(self, joystick_id: int) -> List[float]:
        return self.axis_states[joystick_id]

    def add_joystick(self, joystick: pygame.joystick.Joystick) -> None:
        if (joystick in self._joysticks):
            return
        
        joystick_id = joystick.get_id()
        self._joysticks.append(joystick)
        self.axis_states[joystick_id] = [0.0] * joystick.get_numaxes()
        self.button_states[joystick_id] = {
            button: joystick.get_button(button) for button in range(GamepadButtons.NUM)
        }
        self.previous_button_states[joystick_id] = {
            button: joystick.get_button(button) for button in range(GamepadButtons.NUM)
        }

    def remove_joystick(self, joystick: pygame.joystick.Joystick) -> None:
        joystick_id = joystick.get_id()
        self._joysticks.remove(joystick)
        
        del self.button_states[joystick_id]
        del self.axis_states[joystick_id]
        del self.previous_button_states[joystick_id]

    def get_joystick_ids(self) -> List[int]:
        return [js.get_id() for js in self._joysticks]
