#!/bin/bash

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"

# ─── Configs ───
source "$CONFIG_DIR/global.conf"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"

# Check if hostapd control socket exists for the interface
# We must use 'sudo test -S' because the user may not have permission to access /var/run/hostapd
if ! sudo test -S "/var/run/hostapd/$INTERFACE"; then
    # If the socket doesn't exist, the AP is not running. This is a normal state, not an error.
    echo "Access point is not running."
    exit 0
fi

# Run the command, redirecting stderr to stdout. We will inspect the
# output directly rather than relying on the exit code, which can be
# inconsistent for this command.
STATIONS_OUTPUT=$(sudo hostapd_cli -i "$INTERFACE" all_sta 2>&1)

# The most reliable way to check for connected stations is to look for a MAC
# address in the output. If one is found, we print the output.
if [[ "$STATIONS_OUTPUT" =~ ([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2} ]]; then
    echo "$STATIONS_OUTPUT"
else
    # If no MAC address is found, it means no stations are connected,
    # regardless of what the command's output or exit code was.
    echo "No connected stations found."
fi

exit 0
