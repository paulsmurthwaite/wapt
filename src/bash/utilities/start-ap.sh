#!/bin/bash
set -e

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"
SERVICES_DIR="$BASH_DIR/services"
UTILITIES_DIR="$BASH_DIR/utilities"

# ─── Profile ───
PROFILE="$1"
PROFILE_PATH="$CONFIG_DIR/${PROFILE}.cfg"

# ─── Validate arguments ───
if [[ -z "$PROFILE" || ! -f "$PROFILE_PATH" ]]; then
    print_fail "Invalid profile. Usage: ./start-ap.sh <profile>"
    exit 1
fi

# ─── Configs ───
source "$CONFIG_DIR/global.conf"
source "$PROFILE_PATH"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"
source "$HELPERS_DIR/fn_services.sh"

# ─── Export for envsubst and BSSID support ───
export INTERFACE SSID CHANNEL HIDDEN WPA_MODE PASSPHRASE BSSID

# ─── Start AP ───
print_info "Launching Access Point"

# ─── Generate hostapd.conf ───
if [[ -z "$WPA_MODE" ]]; then
    print_action "Launching unencrypted AP - skipping WPA config"
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

# ─── NetworkManager ───
sudo systemctl stop NetworkManager

# ─── Interface ───
print_waiting "Configuring interface $INTERFACE"

bash "$SERVICES_DIR/set-interface-down.sh"  # IF Down
sudo ip addr add "${GATEWAY}/24" dev "$INTERFACE"
bash "$SERVICES_DIR/set-interface-up.sh"  # IF Up

print_success "Interface $INTERFACE configured"

# ─── IP forwarding ───
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# ─── hostapd ───
sudo hostapd /tmp/hostapd.conf -B
if ! pgrep hostapd > /dev/null; then
    print_fail "hostapd failed to start"
    exit 1
fi

# ─── AP status flag ───
echo "$(date +%s)|$SSID|$BSSID|$CHANNEL" > /tmp/ap_active
print_success "Access Point launch successful"

# ─── Apply NAT rules ───
print_action "Starting NAT: Client Internet access ENABLED"
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o "$FWD_INTERFACE" -j MASQUERADE
sudo iptables -A FORWARD -i "$INTERFACE" -o "$FWD_INTERFACE" -j ACCEPT
sudo iptables -A FORWARD -i "$FWD_INTERFACE" -o "$INTERFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT

# ─── Start Local Services ───
start_dns_service
start_ntp_service
start_http_server