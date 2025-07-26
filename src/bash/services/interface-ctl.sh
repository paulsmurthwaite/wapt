#!/bin/bash
set -e

#
# interface-ctl.sh
#
# A centralized utility to manage the wireless interface state, mode, and resets.
#

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"

# ─── Configs ───
source "$CONFIG_DIR/global.conf"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"

# ─── Core Functions ───

function set_up() {
    print_action "Setting interface UP"
    sudo ip link set "$INTERFACE" up

    print_waiting "Verifying interface is administratively UP..."
    for i in {1..10}; do
        # This pattern is robust against 'set -e' by ignoring the exit code of 'ip'
        local link_status
        link_status=$(ip link show "$INTERFACE" 2>/dev/null || true)
        # We check for the administrative 'UP' flag, not the operational 'state UP'.
        # This is what 'ip link set up' controls directly.
        if [[ "$link_status" =~ \<([^>]*?,)?UP(,[^>]*?)?\> ]]; then
            print_success "Interface is administratively UP"
            return 0
        fi
        sleep 1
    done

    print_fail "Timeout: Failed to bring interface $INTERFACE up." >&2
    return 1
}

function set_down() {
    print_action "Setting interface DOWN"
    sudo ip link set "$INTERFACE" down

    print_waiting "Verifying interface is DOWN..."
    for i in {1..10}; do
        # This pattern is robust against 'set -e'
        local link_status
        link_status=$(ip link show "$INTERFACE" 2>/dev/null || true)
        if [[ "$link_status" != *"state UP"* ]]; then
            print_success "Interface is DOWN"
            sudo ip addr flush dev "$INTERFACE"
            # It's safer to check if ethtool succeeds before using its output
            if HWADDR=$(ethtool -P "$INTERFACE" 2>/dev/null | awk '{print $3}'); then
                if [[ -n "$HWADDR" ]]; then
                    sudo ip link set "$INTERFACE" address "$HWADDR"
                fi
            fi
            return 0
        fi
        sleep 1
    done

    print_fail "Timeout: Failed to verify interface $INTERFACE is DOWN." >&2
    return 1
}

function set_mode() {
    local mode="$1" # 'managed' or 'monitor'
    set_down
    print_action "Setting interface mode ${mode^^}"
    sudo iw dev "$INTERFACE" set type "$mode"
    set_up
}

function setup_for_ap() {
    print_action "Configuring interface for AP mode..."
    set_down
    # We do not need to set 'managed' mode. hostapd will handle setting 'ap' mode.
    print_action "Assigning static IP ${GATEWAY}"
    sudo ip addr add "${GATEWAY}/24" dev "$INTERFACE"
    set_up
}

function reset_soft() {
    print_action "Performing soft reset"
    # The most reliable way to "soft reset" an interface to a default managed
    # state is to restart the service that manages it.
    print_action "Restarting NetworkManager to reset interface states..."
    if systemctl is-active --quiet NetworkManager; then
        sudo systemctl restart NetworkManager
    else
        sudo systemctl start NetworkManager
    fi
    print_waiting "Waiting for NetworkManager to re-initialize..."
    sleep 5 # Give NM a moment to bring interfaces back up.
    print_success "Soft reset complete."
}

function reset_hard() {
    # This function is self-contained and manages NetworkManager itself.
    print_action "Temporarily stopping NetworkManager for exclusive interface control"
    sudo systemctl stop NetworkManager
    sleep 1

    set_down # Ensure interface is down before touching the driver

    local driver
    # The '|| true' prevents script exit if the driver link is temporarily gone
    driver=$(basename "$(readlink -f "/sys/class/net/$INTERFACE/device/driver")" 2>/dev/null || true)

    if [ -z "$driver" ]; then
        print_fail "Could not determine driver for $INTERFACE. Unable to perform hard reset." >&2
        exit 1
    fi

    # Special handling for Intel drivers which have dependencies
    if [[ "$driver" == "iwlwifi" || "$driver" == "iwlmvm" ]]; then
        print_action "Performing hard reset for Intel driver (iwlmvm, iwlwifi)"
        # Unload dependent module first, then the base driver. Ignore errors if not loaded.
        sudo rmmod iwlmvm 2>/dev/null || true
        sudo rmmod iwlwifi 2>/dev/null || true
        sleep 1
        print_action "Reloading driver iwlwifi"
        # Probing the base module is often sufficient for the kernel to load dependencies.
        sudo modprobe iwlwifi
    else
        # Generic driver reset for simple, single-module drivers
        print_action "Performing hard reset (Unloading $driver)"
        sudo rmmod "$driver" 2>/dev/null || true
        sleep 1
        print_action "Reloading driver $driver"
        sudo modprobe "$driver"
    fi

    # Wait for the interface to reappear before continuing. This is more reliable than a fixed sleep.
    print_waiting "Waiting for interface $INTERFACE to be ready..."
    for i in {1..10}; do
        if [[ -d "/sys/class/net/$INTERFACE" ]]; then
            break
        fi
        sleep 1
    done

    if [[ ! -d "/sys/class/net/$INTERFACE" ]]; then
        print_fail "Interface $INTERFACE did not reappear after driver reload." >&2
        exit 1
    fi

    # Now, perform a soft reset to bring everything back up cleanly.
    reset_soft
}

function get_status() {
    # Get administrative state, which is more reliable than operational state
    local link_status
    link_status=$(ip link show "$INTERFACE" 2>/dev/null || true)
    local mode
    mode=$(iw dev "$INTERFACE" info 2>/dev/null | awk '/type/ {print $2}')

    print_none "Interface: $INTERFACE"
    if [[ "$link_status" == *"state UP"* ]]; then
        print_none "State: UP"
    else
        print_none "State: DOWN"
    fi
    print_none "Mode: ${mode:-N/A}"
}

# ─── Main Logic ───

ACTION="$1"
SUB_ACTION="$2"

# Special case for hard reset, which is now self-contained.
if [[ "$ACTION" == "reset" && "$SUB_ACTION" == "hard" ]]; then
    reset_hard
    exit 0
fi

# Special case for soft reset, which has its own network management logic.
if [[ "$ACTION" == "reset" && "$SUB_ACTION" == "soft" ]]; then
    reset_soft
    exit 0
fi

# For state-changing operations, we must ensure NetworkManager and wpa_supplicant
# are not running, as they can interfere with manual 'ip' and 'iw' commands.
nm_control_needed=false
case "$ACTION" in
    up|down|mode|setup-ap) nm_control_needed=true ;; # Exclude reset, which is now self-contained
esac

nm_was_running=false
wpa_was_running=false

if [[ "$nm_control_needed" == true ]]; then
    if systemctl is-active --quiet NetworkManager; then
        nm_was_running=true
        print_action "Temporarily stopping NetworkManager for exclusive interface control"
        sudo systemctl stop NetworkManager
        sleep 1 # Allow time for resources to be released
    fi
    if pgrep wpa_supplicant > /dev/null; then
        wpa_was_running=true
        print_action "Temporarily stopping wpa_supplicant for exclusive interface control"
        sudo pkill wpa_supplicant
    fi
fi

case "$ACTION" in
    status) get_status ;;
    up) set_up ;;
    down) set_down ;;
    setup-ap) setup_for_ap ;;
    mode)
        if [[ "$SUB_ACTION" != "managed" && "$SUB_ACTION" != "monitor" ]]; then
            print_fail "Usage: $0 mode {managed|monitor}" >&2; exit 1
        fi
        set_mode "$SUB_ACTION"
        ;;
    reset)
        if [[ "$SUB_ACTION" != "soft" && "$SUB_ACTION" != "hard" ]]; then
            print_fail "Usage: $0 reset {soft|hard}" >&2; exit 1
        fi
        [[ "$SUB_ACTION" == "soft" ]] && reset_soft || reset_hard
        ;;
    *)
        print_fail "Invalid action. Usage: $0 {status|up|down|mode|reset|setup-ap}" >&2; exit 1
        ;;
esac

action_exit_code=$?

# Restart services only if we were the ones to stop them.
if [[ "$nm_was_running" == true ]]; then
    # Do not restart NM if we just set up for AP mode, as hostapd needs it stopped.
    # The stop-ap.sh script is responsible for restoring it.
    if [[ "$ACTION" != "setup-ap" ]]; then
        print_action "Restoring NetworkManager"
        sudo systemctl start NetworkManager
    fi
fi

# Note: wpa_supplicant is typically managed by NetworkManager, so restarting
# NM is usually sufficient to bring it back up if needed. We don't restart
# it manually to avoid conflicts.

exit "$action_exit_code"