#!/bin/bash

start() {
    echo "Starting tasks..."
    sudo node ./node-virtual-gamepads/main.js > ./node-virtual-gamepads.log 2>&1 &
    echo $! > ./node-virtual-gamepads.pid
    sudo python3 ./rpi4b-led/src/main.py --width 18 --height 9 --pixel-width 2 > ./rpi4b-led.log 2>&1 &
    echo $! > ./rpi4b-led.pid
    echo "Tasks started."
}

stop() {
    echo "Stopping tasks..."
    if [ -f ./node-virtual-gamepads.pid ]; then
        PID=$(cat ./node-virtual-gamepads.pid)
        echo "Stopping node-virtual-gamepads with PID $PID"
        sudo kill $PID
        if [ $? -eq 0 ]; then
            echo "Successfully stopped node-virtual-gamepads"
            rm ./node-virtual-gamepads.pid
        else
            echo "Failed to stop node-virtual-gamepads"
        fi
    else
        echo "node-virtual-gamepads.pid file not found"
    fi

    if [ -f ./rpi4b-led.pid ]; then
        PID=$(cat ./rpi4b-led.pid)
        echo "Stopping rpi4b-led with PID $PID"
        sudo kill $PID
        if [ $? -eq 0 ]; then
            echo "Successfully stopped rpi4b-led"
            rm ./rpi4b-led.pid
        else
            echo "Failed to stop rpi4b-led"
        fi
    else
        echo "rpi4b-led.pid file not found"
    fi

    echo "Turning off all LED lights..."
    sudo python3 ./rpi4b-led/src/main.py --turn-off-leds --width 18 --height 9 --pixel-width 2
    echo "All LED lights turned off."

    echo "Tasks stopped."
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac