#!/bin/bash
# Utility: Stops any running access point launched from WAPT
# Usage: # ./stop-ap.sh

set -e

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"
UTILITIES_DIR="$BASH_DIR/utilities"
SERVICES_DIR="$BASH_DIR/services"

# ─── Configs ───
source "$CONFIG_DIR/global.conf"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"

# Stop hostapd
if pgrep hostapd > /dev/null; then
    print_action "Stopping hostapd"
    sudo pkill hostapd
else
    print_warn "hostapd not running"
fi

# Remove AP status file
rm -f /tmp/wapt_ap_active

# Stop dnsmasq
if pgrep dnsmasq > /dev/null; then
    print_action "Stopping dnsmasq"
    sudo pkill dnsmasq
else
    print_warn "dnsmasq not running"
fi

# Restore systemd-resolved
print_action "Restoring systemd-resolved"
sudo systemctl start systemd-resolved

# Relink /etc/resolv.conf
print_action "Relinking /etc/resolv.conf"
sudo rm -f /etc/resolv.conf
sudo ln -s /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# Flush iptables
print_action "Flushing iptables"
sudo iptables -F
sudo iptables -t nat -F

# Disable IP forwarding
echo 0 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# Reset Wi-Fi interface
print_action "Resetting interface $INTERFACE"
bash "$SERVICES_DIR/reset-interface-soft.sh"

# Re-enable NetworkManager
print_action "Starting NetworkManager"
sudo systemctl start NetworkManager

print_success "Access point shut down"