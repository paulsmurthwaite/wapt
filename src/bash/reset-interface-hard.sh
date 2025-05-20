#!/bin/bash

# Load helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/print.sh"

# Read driver
DRIVER=$(basename "$(readlink /sys/class/net/$INTERFACE/device/driver)")

# Unload
print_action "Interface hard reset (Unload $DRIVER)"
sudo rmmod $DRIVER

# Reload
print_action "Interface hard reset (Reload $DRIVER)"
sudo modprobe $DRIVER
sleep 5