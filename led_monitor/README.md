# DCS Controller LED Monitor

1. Flash the `led_monitor.ino` sketch to your Arduino board
1. Put the 2 shell scripts on your DCS Controller host PC
1. Run `dcs_led_launcher.sh` to start the monitor in the background and start logging

## Notes

- You will likely need to customize this for your needs
- The script will try to automatically detect your Arduino on /dev/ttyUSB*
- The script is designed to exit on controller or arduino disconnect

## LED States

| Color | Description |
| --- | --- |
| `GREEN` | DCS is available and channels 1 and 2 are set to continuous and > 0mA |
| `BLUE` | DCS is available but channels 1 and 2 are not set to continuous and > 0mA |
| `RED` | DCS is not available |
