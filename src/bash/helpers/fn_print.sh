#!/bin/bash

# ─── Standardise Output Formatting ───
# These functions provide consistent, prefixed status messages.
# They use printf for better portability and safe handling of arguments.

print_section() {
    printf "\033[1m[ %s ]\033[0m\n" "$1"
}

print_info() {
    printf "[*] %s\n" "$1"
}

print_success() {
    printf "[+] %s\n" "$1"
}

print_fail() {
    printf "[x] %s\n" "$1"
}

print_warn() {
    printf "[!] %s\n" "$1"
}

print_action() {
    printf "[>] %s\n" "$1"
}

print_waiting() {
    printf "[~] %s\n" "$1"
}

print_prompt() {
    printf "[?] %s" "$1"
}

print_none() {
    printf "%s\n" "$1"
}

print_blank() {
    printf "\n"
}