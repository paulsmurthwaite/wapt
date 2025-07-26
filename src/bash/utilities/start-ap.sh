#!/bin/bash
set -e

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"
SERVICES_DIR="$BASH_DIR/services"
UTILITIES_DIR="$BASH_DIR/utilities"

# ─── Helpers ───
# Source helpers early for logging and utility functions.
source "$HELPERS_DIR/fn_print.sh"

# ─── Profile ───
PROFILE="$1"
PROFILE_PATH="$CONFIG_DIR/${PROFILE}.cfg"

# ─── Validate arguments ───
if [[ -z "$PROFILE" || ! -f "$PROFILE_PATH" ]]; then
    print_fail "Invalid profile specified or file not found: $PROFILE_PATH"
    exit 1
fi

# ─── Configs ───
source "$CONFIG_DIR/global.conf"
source "$PROFILE_PATH"
source "$HELPERS_DIR/fn_services.sh"

# Determine NAT status from script arguments
if [[ " $@ " =~ " nat " ]]; then
  NAT_ENABLED=true
  NAT_STATUS="NAT"
else
  NAT_ENABLED=false
  NAT_STATUS="No NAT"
fi

# ─── Export for envsubst and BSSID support ───
export INTERFACE SSID CHANNEL HIDDEN WPA_MODE PASSPHRASE BSSID

# ─── Start AP ───
print_info "Launching Access Point"

# ─── Generate hostapd.conf ───
if [[ -z "$WPA_MODE" ]]; then
    print_action "Launching unencrypted AP - skipping WPA config"
    # Strip all WPA-related directives from the template for an open AP
    grep -v '^wpa=' "$CONFIG_DIR/hostapd.conf.template" \
    | grep -v '^wpa_passphrase=' \
    | grep -v '^wpa_key_mgmt=' \
    | grep -v '^rsn_pairwise=' \
    | grep -v '^wpa_pairwise=' \
    | envsubst > /tmp/hostapd.conf
else
    print_action "Launching encrypted AP - applying WPA config"
    envsubst < "$CONFIG_DIR/hostapd.conf.template" > /tmp/hostapd.conf
fi

# ─── Assign BSSID ───
if [[ -z "$BSSID" ]]; then
    BSSID=$(cat /sys/class/net/"$INTERFACE"/address)
fi

export BSSID

# ─── Interface ───
bash "$SERVICES_DIR/interface-ctl.sh" setup-ap

# ─── IP forwarding ───
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# ─── hostapd ───
sudo hostapd /tmp/hostapd.conf -B
if ! pgrep hostapd > /dev/null; then
    print_fail "hostapd failed to start"
    exit 1
fi

# ─── AP status flag ───
echo "$(date +%s)|$SSID|$BSSID|$CHANNEL|$NAT_STATUS" > /tmp/ap_active
print_success "Access Point launch successful"

# ─── NAT ───
if [ "$NAT_ENABLED" = true ]; then
    print_action "Starting NAT: Client Internet access ENABLED"
    sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o "$FWD_INTERFACE" -j MASQUERADE
    sudo iptables -A FORWARD -i "$INTERFACE" -o "$FWD_INTERFACE" -j ACCEPT
    sudo iptables -A FORWARD -i "$FWD_INTERFACE" -o "$INTERFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT
else
    print_action "Skipping NAT: Client Internet access DISABLED"
fi

# ─── Services ───
start_dns_service
start_ntp_service
start_http_server