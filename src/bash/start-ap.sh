#!/bin/bash
# Usage:
# ./start-ap.sh <profile> [nat]
# Example:
# ./start-ap.sh ap_wpa2            ← no internet for clients
# ./start-ap.sh ap_open nat        ← clients get internet access

set -e

# Resolve base directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Validate arguments
PROFILE="$1"
if [[ -z "$PROFILE" ]]; then
    echo "[ERROR] No profile specified. Usage: ./start-ap.sh <profile> [nat]"
    exit 1
fi

PROFILE_PATH="$SCRIPT_DIR/ap-profiles/${PROFILE}.cfg"
if [[ ! -f "$PROFILE_PATH" ]]; then
    echo "[ERROR] Profile config '$PROFILE_PATH' not found."
    exit 1
fi

# Load profile variables
source "$PROFILE_PATH"

# Export for envsubst and BSSID support
export INTERFACE SSID CHANNEL HIDDEN WPA_MODE PASSPHRASE WPA3 BSSID

# Generate hostapd.conf
if [[ -z "$WPA_MODE" ]]; then
    echo "[INFO] Launching open AP. Skipping WPA config..."
    grep -v '^wpa=' "$SCRIPT_DIR/hostapd.conf.template" \
    | grep -v '^wpa_passphrase=' \
    | grep -v '^wpa_key_mgmt=' \
    | grep -v '^rsn_pairwise=' \
    | grep -v '^wpa_pairwise=' \
    | envsubst > /tmp/hostapd.conf
else
    echo "[INFO] Launching secured AP. Applying WPA config..."
    envsubst < "$SCRIPT_DIR/hostapd.conf.template" > /tmp/hostapd.conf
fi

# WPA3 enhancement (append SAE options if requested)
if [[ "$WPA3" == "1" ]]; then
    echo "[INFO] WPA3-SAE enhancements enabled"
    {
        echo "ieee80211w=2"
        echo "sae_require_mfp=1"
        echo "wpa_key_mgmt=SAE WPA-PSK"
    } >> /tmp/hostapd.conf
fi

# Apply custom BSSID if passed
if [[ -n "$BSSID" ]]; then
    echo "[INFO] Applying custom BSSID: $BSSID"
    echo "bssid=$BSSID" >> /tmp/hostapd.conf
fi

# Stop NetworkManager
echo "[+] Stopping NetworkManager ..."
sudo systemctl stop NetworkManager

# Configure interface
echo "[+] Configuring interface $INTERFACE ..."
bash "$SCRIPT_DIR/set-interface-down.sh"
sudo ip addr add "${GATEWAY}/24" dev "$INTERFACE"
bash "$SCRIPT_DIR/set-interface-up.sh"

# Enable IP forwarding
echo "[+] Enabling IP forwarding ..."
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# Launch hostapd
echo "[+] Starting hostapd ..."
sudo hostapd /tmp/hostapd.conf -B

# NAT handling
NAT_STATE="nonat"
if [[ "$2" == "nat" ]]; then
    NAT_STATE="nat"
fi

# DNS setup
echo "[+] Stopping systemd-resolved ..."
sudo systemctl stop systemd-resolved

echo "[+] Configuring resolv.conf ..."
sudo rm -f /etc/resolv.conf
echo "nameserver 9.9.9.9" | sudo tee /etc/resolv.conf > /dev/null

# Launch dnsmasq
echo "[+] Starting dnsmasq ..."
sudo dnsmasq -C "$SCRIPT_DIR/dnsmasq.conf"

# Optional NAT support
if [[ "$NAT_STATE" == "nat" ]]; then
    echo "[+] NAT enabled. Applying forwarding rules ..."
    sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o ens33 -j MASQUERADE
    sudo iptables -A FORWARD -i "$INTERFACE" -o ens33 -j ACCEPT
    sudo iptables -A FORWARD -i ens33 -o "$INTERFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT
else
    echo "[+] NAT disabled. Internet access blocked for clients."
fi

# Final status file
echo "$SSID|$(date +%s)|$NAT_STATE|${BSSID:-default}" > /tmp/wapt_ap_active

# Inform user of launch success
echo "[+] Access point '$SSID' is now running on $INTERFACE."
if [[ -n "$BSSID" ]]; then
    echo "[+] Verify BSSID assignment using: iw dev $INTERFACE info"
fi
