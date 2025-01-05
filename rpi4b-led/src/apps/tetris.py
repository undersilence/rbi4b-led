import random
import math
from typing import List, Tuple
from pygame import key, K_LEFT, K_RIGHT, K_DOWN, K_UP, K_ESCAPE
from led_matrix import LEDMatrix
from .base import BaseApp, GamepadButtons, FONT, VfxUtils
from input_manager import InputManager

# Define the shapes and colors of the Tetris pieces
TETROMINOS = {
    "I": (
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        (0, 255, 255),
    ),  # Cyan
    "O": ([[1, 1], [1, 1]], (255, 255, 0)),  # Yellow
    "T": ([[0, 1, 0], [1, 1, 1], [0, 0, 0]], (128, 0, 128)),  # Purple
    "S": ([[0, 1, 1], [1, 1, 0], [0, 0, 0]], (0, 255, 0)),  # Green
    "Z": ([[1, 1, 0], [0, 1, 1], [0, 0, 0]], (255, 0, 0)),  # Red
    "J": ([[1, 0, 0], [1, 1, 1], [0, 0, 0]], (0, 0, 255)),  # Blue
    "L": ([[0, 0, 1], [1, 1, 1], [0, 0, 0]], (255, 165, 0)),  # Orange
}

# Wallkick offsets for different rotations (SRS)
WALLKICK_OFFSETS = {
    "I": {
        (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
    },
    "JLSTZ": {
        (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    },
}


class TetrisApp(BaseApp):
    ICON = [" ###   ", " # #   ", " # ####", " #    #", " #### #", "    # #", "    ###"]

    def reset(self) -> None:
        self.reset_game_state()

    def reset_game_state(self) -> None:
        self.board = [[0] * self.matrix.width for _ in range(self.matrix.height)]
        self.current_piece, self.current_color = self._new_piece()
        self.next_piece, self.next_color = self._new_piece()
        self.piece_x = self.matrix.width // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        self.score = 0
        self.drop_timer = 0
        self.drop_interval = 1  # Initial drop interval in seconds
        self.game_over = False
        self.show_score_timer = 0
        self.clear_lines_animation_timer = 0
        self.lines_to_clear = []
        self.rotation_state = 0
        self.move_direction = 0  # 0: no movement, -1: left, 1: right
        self.offset_x = 0
        self.hard_drop_ready = True

    def _new_piece(self) -> Tuple[List[List[int]], Tuple[int, int, int]]:
        return random.choice(list(TETROMINOS.values()))

    def _rotate_piece(
        self, piece: List[List[int]], clockwise: bool = True
    ) -> List[List[int]]:
        size = len(piece)
        new_piece = [[0] * size for _ in range(size)]
        for y in range(size):
            for x in range(size):
                if piece[y][x]:
                    if clockwise:
                        new_x = size - 1 - y
                        new_y = x
                    else:
                        new_x = y
                        new_y = size - 1 - x
                    new_piece[new_y][new_x] = piece[y][x]
        return new_piece

    def _valid_position(
        self, piece: List[List[int]], offset_x: int, offset_y: int
    ) -> bool:
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    new_x = x + offset_x
                    new_y = y + offset_y
                    if (
                        new_x < 0
                        or new_x >= self.matrix.width
                        or new_y >= self.matrix.height
                        or (new_y >= 0 and self.board[new_y][new_x])
                    ):
                        return False
        return True

    def _merge_piece(self) -> None:
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.piece_y + y][self.piece_x + x] = self.current_color

    def _clear_lines(self) -> None:
        self.lines_to_clear = [
            y for y, row in enumerate(self.board) if all(cell != 0 for cell in row)
        ]
        if self.lines_to_clear:
            self.clear_lines_animation_timer = 0.5  # 0.5 seconds animation

    def _perform_clear_lines(self) -> None:
        new_board = [
            row for y, row in enumerate(self.board) if y not in self.lines_to_clear
        ]
        lines_cleared = len(self.lines_to_clear)
        if lines_cleared == 1:
            self.score += 10
        elif lines_cleared == 2:
            self.score += 30
        elif lines_cleared == 3:
            self.score += 60
        elif lines_cleared == 4:
            self.score += 100
        new_board = [[0] * self.matrix.width for _ in range(lines_cleared)] + new_board
        self.board = new_board
        self.lines_to_clear = []
        self.drop_interval = max(
            0.1, 1 - self.score / 1000
        )  # Increase speed based on score

    def _try_rotate(self, clockwise: bool) -> bool:
        piece_type = "I" if self.current_piece == TETROMINOS["I"][0] else "JLSTZ"
        new_rotation_state = (self.rotation_state + (1 if clockwise else -1)) % 4
        rotated_piece = self._rotate_piece(self.current_piece, clockwise)

        # First try to rotate without wallkick
        if self._valid_position(rotated_piece, self.piece_x, self.piece_y):
            self.current_piece = rotated_piece
            self.rotation_state = new_rotation_state
            return True

        # If failed, try wallkick
        for offset_x, offset_y in WALLKICK_OFFSETS[piece_type][
            (self.rotation_state, new_rotation_state)
        ]:
            if self._valid_position(
                rotated_piece, self.piece_x + offset_x, self.piece_y + offset_y
            ):
                self.current_piece = rotated_piece
                self.piece_x += offset_x
                self.piece_y += offset_y
                self.rotation_state = new_rotation_state
                return True
        return False
    
    def update(self, delta_time: float) -> None:
        if self.is_pressed(GamepadButtons.A):
            self._try_rotate(clockwise=True)
        elif self.is_pressed(GamepadButtons.B):
            self._try_rotate(clockwise=False)
        elif self.is_pressed(GamepadButtons.START):
            self.reset_game_state()
        elif self.is_pressed(GamepadButtons.BACK):
            self.keep_running = False

        # Handle joystick axis motion
        axis_0, axis_1 = self.get_axes()

        if axis_0 < -0.5:
            self.move_direction = -1
        elif axis_0 > 0.5:
            self.move_direction = 1
        else:
            self.move_direction = 0

        if axis_1 < -0.8 and self.hard_drop_ready:  # Hard drop
            while self._valid_position(self.current_piece, self.piece_x, self.piece_y + 1):
                self.piece_y += 1
            self.drop_timer = self.drop_timer * 2 # Force immediate merge
            self.hard_drop_ready = False
        elif axis_1 > 0.8 and self._valid_position(self.current_piece, self.piece_x, self.piece_y + 1):  # Soft drop
            self.piece_y += 1
        elif axis_1 > -0.1:
            self.hard_drop_ready = True

        if self.game_over:
            self.show_score_timer -= delta_time
            if self.show_score_timer <= 0:
                self.reset_game_state()
                self.game_over = False
            return

        if self.clear_lines_animation_timer > 0:
            self.clear_lines_animation_timer -= delta_time
            if self.clear_lines_animation_timer <= 0:
                self._perform_clear_lines()
            return

        self.drop_timer += delta_time

        if self.move_direction == -1 and self._valid_position(self.current_piece, self.piece_x - 1, self.piece_y):
            self.offset_x -= 0.5
        elif self.move_direction == 1 and self._valid_position(self.current_piece, self.piece_x + 1, self.piece_y):
            self.offset_x += 0.5
            
        if abs(self.offset_x) >= 1.0:
            self.piece_x += int(self.offset_x)
            self.offset_x -= int(self.offset_x)

        if self.drop_timer >= self.drop_interval:
            self.drop_timer = 0
            if self._valid_position(self.current_piece, self.piece_x, self.piece_y + 1):
                self.piece_y += 1
            else:
                self._merge_piece()
                self._clear_lines()
                self.current_piece, self.current_color = self.next_piece, self.next_color
                self.next_piece, self.next_color = self._new_piece()
                self.piece_x = self.matrix.width // 2 - len(self.current_piece[0]) // 2
                self.piece_y = -1  # Start above the board
                self.rotation_state = int(random.uniform(0, 4))  # Random rotation state
                if not self._valid_position(self.current_piece, self.piece_x, self.piece_y):
                    self.game_over = True
                    self.show_score_timer = 3  # Show score for 5 seconds

    def render(self) -> None:
        if self.game_over:
            self._show_score()
            return

        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.matrix.set_pixel(x, y, cell)  # Use the stored color

        if self.clear_lines_animation_timer > 0:
            brightness = VfxUtils.breath_curve(self.clear_lines_animation_timer, 0.5, 1.5)
            for y in self.lines_to_clear:
                for x in range(self.matrix.width):
                    self.matrix.set_pixel(x, y, (int(brightness * 255), int(brightness * 255), int(brightness * 255)))  # Breathing effect
        else:
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        self.matrix.set_pixel(int(self.piece_x) + x, int(self.piece_y) + y, self.current_color)  # Current piece color

    def _show_score(self) -> None:
        score_str = f"{self.score}"
        x_offset = (self.matrix.width - len(score_str) * 4) // 2
        y_offset = (self.matrix.height - 5) // 2  # Center vertically
        brightness = int(VfxUtils.breath_curve(self.show_score_timer, 3, 2) * 255)  # Breathing effect
        for i, char in enumerate(score_str):
            pattern = FONT[char]
            color = (brightness, brightness, brightness)
            self.matrix.draw_sprite(
                x_offset + i * 4,
                y_offset,
                [
                    [color if pixel == "#" else (0, 0, 0) for pixel in row]
                    for row in pattern
                ],
            )
