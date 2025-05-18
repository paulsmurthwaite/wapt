#!/bin/bash
# Usage:
# ./stop-ap.sh

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

set -e

# Stop hostapd
echo "{+] Stopping hostapd ... "
sudo pkill hostapd
rm -f /tmp/wapt_ap_active

# Stop dnsmasq
echo "{+] Stopping dnsmasq ... "
sudo pkill dnsmasq

# Restore systemd-resolved
echo "{+] Restoring systemd-resolved ... "
sudo systemctl start systemd-resolved

# Relink /etc/resolv.conf
echo "{+] Relinking /etc/resolv.conf ... "
sudo rm -f /etc/resolv.conf
sudo ln -s /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# Flush iptables
echo "{+] Flushing iptables ... "
sudo iptables -F
sudo iptables -t nat -F

# Disable IP Forwarding
echo 0 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# Reset Wi-Fi Interface
echo "{+] Resetting interface $INTERFACE ... "
sudo ip link set $INTERFACE down
sudo ip addr flush dev $INTERFACE
sudo ip link set $INTERFACE up

# Reenable NetworkManager
echo "{+] Starting NetworkManager ... "
sudo systemctl start NetworkManager

echo "{+] Access Point DISABLED ... "