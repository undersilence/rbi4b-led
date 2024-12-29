# Raspberry Pi LED Matrix

This project is designed to control an LED matrix connected to a Raspberry Pi. It includes several applications such as a clock, Tetris game, snake game, and screen test to verify the display functionality.

## Requirements

- Python 3.7+
- Raspberry Pi with GPIO pins
- WS281x LED strip
- Pygame

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/raspberry-pi-led-matrix.git
    cd raspberry-pi-led-matrix
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:
    ```sh
    python src/main.py
    ```

## Command Line Arguments

- `--simulate`: Enable simulation mode (default: False)
- `--width`: Width of the screen in pixels (default: 10)
- `--height`: Height of the screen in pixels (default: 10)
- `--pixel-width`: Width of a single pixel (default: 1)
- `--pixel-height`: Height of a single pixel (default: 1)

Example:
```sh
python src/main.py --simulate --width 20 --height 10 --pixel-width 1 --pixel-height 1