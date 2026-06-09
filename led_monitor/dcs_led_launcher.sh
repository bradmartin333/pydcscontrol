#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "error: please run the launcher with sudo"
    exit 1
fi

SCRIPT_PATH="$(dirname "$0")/dcs_led.sh"
LOG_FILE="$(dirname "$0")/dcs_monitor.log"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "error: cannot find $SCRIPT_PATH"
    exit 1
fi

echo "starting dcs monitor in the background..."
nohup "$SCRIPT_PATH" > "$LOG_FILE" 2>&1 &
PID=$!
echo "monitor successfully started with PID: $PID"
echo "you can view the live output using: tail -f $LOG_FILE"
