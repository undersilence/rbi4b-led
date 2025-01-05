#!/bin/bash

start() {
    echo "Starting tasks..."

    # Start gamepad service and redirect output
    sudo node ./node-virtual-gamepads/main.js > ./node-virtual-gamepads.log 2>&1 &
    echo $! > ./node-virtual-gamepads.pid
    
    # Wait for gamepad service to initialize
    sleep 2
    
    # Start LED matrix and redirect output
    sudo python3 ./rpi4b-led/src/main.py --width 18 --height 9 --pixel-width 2 > ./rpi4b-led.log 2>&1 &
    echo $! > ./rpi4b-led.pid
    
    echo "Tasks started."
}


stop() {
    echo "Stopping tasks..."
    local timeout=10

    if [ -f ./node-virtual-gamepads.pid ]; then
        PID=$(cat ./node-virtual-gamepads.pid)
        echo "Stopping node-virtual-gamepads with PID $PID"
        
        # Kill main process and children
        sudo pkill -TERM -P $PID
        sudo kill -TERM $PID

        # Wait for process to die
        for i in $(seq 1 $timeout); do
            if ! ps -p $PID > /dev/null; then
                break
            fi
            sleep 1
        done

        # Force kill if still alive
        if ps -p $PID > /dev/null; then
            sudo pkill -KILL -P $PID
            sudo kill -KILL $PID
        fi

        rm -f ./node-virtual-gamepads.pid
    fi

    if [ -f ./rpi4b-led.pid ]; then
        PID=$(cat ./rpi4b-led.pid)
        echo "Stopping rpi4b-led with PID $PID"
        
        # Kill main process and children
        sudo pkill -TERM -P $PID
        sudo kill -TERM $PID

        # Wait for process to die
        for i in $(seq 1 $timeout); do
            if ! ps -p $PID > /dev/null; then
                break
            fi
            sleep 1
        done

        # Force kill if still alive
        if ps -p $PID > /dev/null; then
            sudo pkill -KILL -P $PID
            sudo kill -KILL $PID
        fi

        rm -f ./rpi4b-led.pid
    fi

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