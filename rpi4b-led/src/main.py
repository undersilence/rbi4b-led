import logging
import argparse
from typing import List
from led_matrix import LEDMatrix
from apps import MenuApp, ClockApp, SnakeApp, TetrisApp, ScreenTestApp
import pygame
import sys
from logging.handlers import RotatingFileHandler
from input_manager import InputManager

# Setup logging
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=1
)  # 5 MB max size
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[log_handler, console_handler],
)


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="LED Matrix Application")
    parser.add_argument(
        "--simulate", action="store_true", help="Enable simulation mode"
    )
    parser.add_argument(
        "--width", type=int, default=10, help="Width of the screen in pixels"
    )
    parser.add_argument(
        "--height", type=int, default=10, help="Height of the screen in pixels"
    )
    parser.add_argument(
        "--pixel-width", type=int, default=1, help="Width of a single pixel"
    )
    parser.add_argument(
        "--pixel-height", type=int, default=1, help="Height of a single pixel"
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="frequency of frames per second"
    )
    parser.add_argument(
        "--turn-off-leds", action="store_true", help="Turn off all LEDs and exit"
    )
    args = parser.parse_args()

    pygame.init()
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        logging.info(f"Joystick {joystick.get_name()} added.")

    width = args.width
    height = args.height
    pixel_width = args.pixel_width
    pixel_height = args.pixel_height
    led_count = width * height * pixel_width * pixel_height  # Total number of LEDs
    pin = 18  # GPIO pin for the LED strip
    simulate = args.simulate  # Set simulation mode based on command line argument

    # Initialize the InputManager with joysticks
    input_manager = InputManager(joysticks)

    try:
        # Initialize the LED matrix
        matrix = LEDMatrix(
            width,
            height,
            led_count,
            pin,
            args.pixel_width,
            args.pixel_height,
            simulate=simulate,
        )

        matrix.clear()
        matrix.show()

        if args.turn_off_leds:
            return

        # Menu options
        app_items = [
            ClockApp(matrix, target_fps=args.fps),
            TetrisApp(matrix, target_fps=args.fps),
            SnakeApp(matrix, target_fps=args.fps),
            ScreenTestApp(matrix, target_fps=args.fps, clear_before_render=False),
        ]

        # Initialize the menu app
        menu_app = MenuApp(matrix, target_fps=args.fps)

        # Register all apps
        for app in app_items:
            menu_app.reg_app(app)

        menu_app.execute()
    except:
        logging.error("An error occurred", exc_info=True)
    finally:
        logging.debug("exit")
        matrix.clear()
        matrix.show()


if __name__ == "__main__":
    main()
