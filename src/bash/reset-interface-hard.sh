#!/bin/bash

# Load environment
source "$(dirname "${BASH_SOURCE[0]}")/fn_load-env.sh"

# Read interface driver
DRIVER=$(basename "$(readlink /sys/class/net/$INTERFACE/device/driver)")

# Remove interface driver
echo "[INFO] Unloading interface $INTERFACE driver $DRIVER ..."
sudo rmmod $DRIVER

# Reload interface driver
echo "[INFO] Reloading interface $INTERFACE ..."
sudo modprobe $DRIVER
sleep 5