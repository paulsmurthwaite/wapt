#!/bin/bash
# Usage:
# ./start-ap.sh <profile> [nat]
# Example:
# ./start-ap.sh ap_wpa2            ← no internet for clients
# ./start-ap.sh ap_open nat        ← clients get internet access

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

# ─── Validate arguments ───
PROFILE="$1"
if [[ -z "$PROFILE" ]]; then
    print_fail "No profile specified. Usage: ./start-ap.sh <profile> [nat]"
    exit 1
fi
PROFILE_PATH="$CONFIG_DIR/${PROFILE}.cfg"
if [[ ! -f "$PROFILE_PATH" ]]; then
    print_fail "Profile config '$PROFILE_PATH' not found"
    exit 1
fi

# ─── Load profile variables ───
source "$PROFILE_PATH"

# ─── Export for envsubst and BSSID support ───
export INTERFACE SSID CHANNEL HIDDEN WPA_MODE PASSPHRASE WPA3 BSSID

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

# ─── WPA3 enhancement (append SAE options if requested) ───
if [[ "$WPA3" == "1" ]]; then
    print_action "WPA3 - SAE enhancements enabled"
    {
        echo "ieee80211w=2"
        echo "sae_require_mfp=1"
        echo "wpa_key_mgmt=SAE WPA-PSK"
    } >> /tmp/hostapd.conf
fi

# ─── Apply custom BSSID if passed ───
if [[ -n "$BSSID" ]]; then
    print_action "Applying custom BSSID: $BSSID"
    echo "bssid=$BSSID" >> /tmp/hostapd.conf
fi

# ─── Stop NetworkManager ───
print_action "Stopping NetworkManager"
sudo systemctl stop NetworkManager

# ─── Configure interface ───
print_action "Configuring interface $INTERFACE"
bash "$SERVICES_DIR/set-interface-down.sh"
sudo ip addr add "${GATEWAY}/24" dev "$INTERFACE"
bash "$SERVICES_DIR/set-interface-up.sh"

# ─── IP forwarding ───
print_action "Enabling IP forwarding"
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# ─── Launch hostapd ───
print_action "Starting hostapd"
sudo hostapd /tmp/hostapd.conf -B

# ─── NAT ───
NAT_STATE="nonat"
if [[ "$2" == "nat" ]]; then
    NAT_STATE="nat"
fi

# ─── DNS ───
print_action "Stopping systemd-resolved"
sudo systemctl stop systemd-resolved
print_action "Configuring resolv.conf"
sudo rm -f /etc/resolv.conf
echo "nameserver 9.9.9.9" | sudo tee /etc/resolv.conf > /dev/null

# ─── Launch dnsmasq ───
print_action "Starting dnsmasq"
sudo dnsmasq -C "$CONFIG_DIR/dnsmasq.conf"

# ─── Apply NAT rules ───
if [[ "$NAT_STATE" == "nat" ]]; then
    print_action "NAT enabled - client Internet access AVAILABLE"
    sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o $FWD_INTERFACE -j MASQUERADE
    sudo iptables -A FORWARD -i "$INTERFACE" -o $FWD_INTERFACE -j ACCEPT
    sudo iptables -A FORWARD -i $FWD_INTERFACE -o "$INTERFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT
else
    print_warn "NAT disabled - client Internet access BLOCKED"
fi

# ─── Retrieve BSSID from hostapd ───
ACTUAL_BSSID=$(iw dev "$INTERFACE" info | awk '/addr/ {print toupper($2)}')

# ─── Write AP status to file ───
echo "$SSID|$(date +%s)|$NAT_STATE|$ACTUAL_BSSID" > /tmp/wapt_ap_active

# ─── Display Status ───
print_success "Access point '$SSID' is now running on $INTERFACE"
if [[ -n "$BSSID" ]]; then
    print_info "Custom BSSID applied - view details in the Service Status panel"
fi