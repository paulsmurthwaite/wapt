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
source "$HELPERS_DIR/fn_services.sh"

# Stop hostapd
if pgrep hostapd > /dev/null; then
    print_action "Stopping hostapd"
    sudo pkill hostapd
else
    print_warn "hostapd not running"
fi

# Remove AP status file
rm -f /tmp/wapt_ap_active

# ─── Stop Local Services ───
stop_dns_service
stop_ntp_service
stop_http_server

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