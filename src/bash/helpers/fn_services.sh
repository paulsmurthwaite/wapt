#!/bin/bash

# ─── Internal Service Helpers for AP Profiles ───
# This file is sourced by start-ap.sh and stop-ap.sh

# ─── HTTP Server ───
start_http_server() {
    print_action "Starting HTTP server on port 80"
    
    local WEB_ROOT="/srv/wapt/www"

    # Create target web root
    sudo mkdir -p "$WEB_ROOT"

    # Deploy captive portal files
    if [[ -f "$UTILITIES_DIR/index.html" && -f "$UTILITIES_DIR/submit" ]]; then
        sudo cp "$UTILITIES_DIR/index.html" "$WEB_ROOT/"
        sudo cp "$UTILITIES_DIR/submit" "$WEB_ROOT/"
        print_success "Captive portal files deployed"
    else
        print_fail "Captive portal files missing in $UTILITIES_DIR"
        return 1
    fi

    # Launch HTTP server in background
    cd "$WEB_ROOT" || exit 1
    sudo setsid python3 -m http.server 80 > /dev/null 2>&1 &
    
    sleep 1
    HTTP_PID=$(pgrep -n -f "http.server 80")
    echo "$HTTP_PID" > /tmp/wapt_http_server.pid

    sleep 1  # allow server time to bind

    if ps -p "$HTTP_PID" > /dev/null; then
        print_success "HTTP server started (PID: $HTTP_PID)"
    else
        print_fail "Failed to start HTTP server"
    fi
}

stop_http_server() {
    print_action "Stopping HTTP server"

    if [[ -f /tmp/wapt_http_server.pid ]]; then
        HTTP_PID=$(cat /tmp/wapt_http_server.pid)
        sudo kill "$HTTP_PID" > /dev/null 2>&1
        rm -f /tmp/wapt_http_server.pid
        print_success "HTTP server stopped"
    else
        print_fail "No HTTP server PID file found — nothing to stop"
    fi

    # Clean up captive portal files
    local WEB_ROOT="/srv/watt/www"
    sudo rm -f "$WEB_ROOT/index.html" "$WEB_ROOT/submit"
    print_success "Captive portal files removed"
}

# ─── DNS Server Wrapper ───
start_dns_service() {
    print_action "Disabling systemd-resolved"
    sudo systemctl stop systemd-resolved

    print_action "Overriding resolv.conf with 9.9.9.9"
    sudo rm -f /etc/resolv.conf
    echo "nameserver 9.9.9.9" | sudo tee /etc/resolv.conf > /dev/null

    print_action "Starting dnsmasq (DHCP + DNS)"
    sudo dnsmasq -C "$CONFIG_DIR/dnsmasq.conf"
}

stop_dns_service() {
    print_action "Stopping dnsmasq"
    if pgrep dnsmasq > /dev/null; then
        sudo pkill dnsmasq
    else
        print_warn "dnsmasq not running"
    fi

    print_action "Restoring systemd-resolved"
    sudo systemctl start systemd-resolved

    print_action "Relinking /etc/resolv.conf"
    sudo rm -f /etc/resolv.conf
    sudo ln -s /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
}

# ─── NTP Server ───
start_ntp_service() {
    print_action "Starting local NTP server"
    sudo systemctl start ntp.service
    if systemctl is-active --quiet ntp.service; then
        print_success "Local NTP server started"
    else
        print_fail "Failed to start local NTP server"
    fi
}

stop_ntp_service() {
    print_action "Stopping local NTP server"
    sudo systemctl stop ntp.service
    if ! systemctl is-active --quiet ntp.service; then
        print_success "Local NTP server stopped"
    else
        print_fail "Failed to stop local NTP server"
    fi
}