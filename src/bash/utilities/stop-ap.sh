#!/bin/bash
set -e

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"
SERVICES_DIR="$BASH_DIR/services"
UTILITIES_DIR="$BASH_DIR/utilities"

# ─── Configs ───
source "$CONFIG_DIR/global.conf"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"
source "$HELPERS_DIR/fn_services.sh"

# ─── AP status flag ───
rm -f /tmp/ap_active

# ─── Services ───
stop_http_server
stop_ntp_service
stop_dns_service

# ─── NAT ───
print_action "Stopping NAT"
sudo iptables -F
sudo iptables -t nat -F

# ─── IP forwarding ───
echo 0 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# ─── hostapd ───
if pgrep hostapd > /dev/null; then
    sudo pkill hostapd
else
    print_warn "hostapd not running"
fi

# ─── Interface ───
print_action "Resetting interface $INTERFACE"
bash "$SERVICES_DIR/reset-interface-soft.sh"
print_success "Interface $INTERFACE reset"

# ─── NetworkManager ───
sudo systemctl start NetworkManager

print_success "Access Point shutdown successful"