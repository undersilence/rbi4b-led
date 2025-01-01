#!/bin/bash

set -e

echo "Installing node-virtual-gamepads dependencies..."
cd ./node-virtual-gamepads && npm install
echo "node-virtual-gamepads dependencies installed."

echo "Setup completed successfully."