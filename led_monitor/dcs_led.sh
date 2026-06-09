#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "error: root privileges required for tcpdump"
    exit 1
fi

DCS_IP="192.168.0.1"
DCS_PORT=777                 
PING_INTERVAL=5
CURRENT_STATE="NONE"

echo "initializing usb connection..."
for port in /dev/ttyUSB*; do
    if [ -e "$port" ]; then
        SERIAL_PORT="$port"
        break
    fi
done

if [ -z "$SERIAL_PORT" ]; then
    echo "error: failed to locate a ttyUSB device. exiting."
    exit 1
fi

echo "connected to $SERIAL_PORT"
stty -F "$SERIAL_PORT" 9600 raw -echo -echoe -echok -echoctl -echoke
exec 3<> "$SERIAL_PORT"

# Give the Arduino 2 seconds to finish its initial boot sequence
sleep 2

set_led() {
    local state=$1
    
    if [ "$CURRENT_STATE" != "$state" ]; then
        echo "state changing to $state"
        case $state in
            GREEN) echo -e "R0\nG1\nB0" >&3 2>/dev/null ;;
            BLUE)  echo -e "R0\nG0\nB1" >&3 2>/dev/null ;;
            RED)   echo -e "R1\nG0\nB0" >&3 2>/dev/null ;;
            OFF)   echo -e "R0\nG0\nB0" >&3 2>/dev/null ;;
        esac
        CURRENT_STATE=$state
    fi
    
    if [ "$state" == "RED" ]; then
        echo "red state triggered. exiting program."
        exit 1
    fi
}

# Clear the LED immediately after USB connection is established
set_led "OFF"

echo "starting monitor loop..."

buffer=""
last_ping=$(date +%s)

while true; do
    now=$(date +%s)

    if [ ! -e "$SERIAL_PORT" ]; then
        echo "error: usb connection lost. exiting."
        exit 1
    fi

    if (( now - last_ping >= PING_INTERVAL )); then
        if ! ping -c 1 -W 1 "$DCS_IP" >/dev/null 2>&1; then
            echo "ping to controller failed."
            set_led "RED"
        fi
        last_ping=$now
    fi

    if read -t 1 -r line; then
        buffer="$buffer $line"

        if [[ "$line" == *"</channelConfig>"* ]]; then
            ch1=$(echo "$buffer" | grep -o '<channel id="1"[^>]*>' | tail -n 1)
            ch2=$(echo "$buffer" | grep -o '<channel id="2"[^>]*>' | tail -n 1)

            if [[ "$ch1" == *'mode="1"'* && "$ch1" != *'current="0"'* ]] && \
               [[ "$ch2" == *'mode="1"'* && "$ch2" != *'current="0"'* ]]; then
                set_led "GREEN"
            else
                set_led "BLUE"
            fi
            buffer=""
        fi
    fi

done < <(tcpdump -l -i any -A -s 0 "src host $DCS_IP and tcp port $DCS_PORT" 2>/dev/null)