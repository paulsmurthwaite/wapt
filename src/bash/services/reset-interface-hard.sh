#!/bin/bash

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"
SERVICES_DIR="$BASH_DIR/services"

# ─── Configs ───
source "$CONFIG_DIR/global.conf"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"

# Read driver
DRIVER=$(basename "$(readlink /sys/class/net/$INTERFACE/device/driver)")

# Unload
print_action "Interface hard reset (Unload $DRIVER)"
sudo rmmod $DRIVER

# Reload
print_action "Interface hard reset (Reload $DRIVER)"
sudo modprobe $DRIVER
sleep 5