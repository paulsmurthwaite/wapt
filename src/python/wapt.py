#!/usr/bin/env python3
"""watt.py

Main entry point for the Wireless Attack Testing Toolkit (WATT) menu interface.

This script provides a simple, operator-friendly CLI for accessing key toolkit functions such as scanning, capturing, and detection.  It is designed to offer a clear and low-complexity user experience, suitable for field use in SME environments.

The menu system acts as the central launcher for Bash and Python-based components of the toolkit, with screen clearing and section redrawing used to improve usability without introducing graphical complexity.

Author:      Paul Smurthwaite
Date:        2025-05-16
Module:      TM470-25B
"""

import os
import pyfiglet
import re
import subprocess
import time

# ─── UI Helpers ───
# UI Colour Dictionary
COLOURS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "grey":   "\033[90m",
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "magenta": "\033[95m",
    "warn":   "\033[38;5;226m",  # amber
}

# UI Colour
def colour(text, style):
    """
    Apply ANSI colour styling to text.
    """
    return f"{COLOURS.get(style, '')}{text}{COLOURS['reset']}"

# UI Banner
def ui_banner():
    """
    Display ASCII banner.
    """
    ascii_banner = pyfiglet.figlet_format("WAPT", font="ansi_shadow")
    print(colour(ascii_banner, "magenta"))

# UI Header
def ui_header(title="Wireless Access Point Toolkit"):
    """
    Display section header.
    """
    styled = f"{COLOURS['bold']}{COLOURS['magenta']}[ {title} ]{COLOURS['reset']}"
    print(styled)

# UI Divider
def ui_divider():
    """
    Display divider.
    """
    print(colour("-----------------------------------", "grey"))
    print()

# UI Subtitle
def ui_subtitle():
    """
    Display combined subtitle.
    """
    ui_divider()
    print_interface_status()
    print_service_status()
    ui_divider()

# UI Standard Header
def ui_standard_header(menu_title=None):
    """
    Render standard UI header block: banner, main title, subtitle.
    Optionally takes a menu title to display immediately after.
    """
    ui_banner()       # ASCII banner
    ui_header()       # Toolkit title
    print()
    ui_subtitle()     # Divider + interface + service info

    if menu_title:
        ui_header(menu_title)  # Current menu title
        print()

# UI Clear Screen
def ui_clear_screen():
    """
    Clear terminal screen.
    """
    os.system("cls" if os.name == "nt" else "clear")

# UI Invalid Option
def ui_pause_on_invalid():
    """
    Display invalid input message and pause.
    """
    print(colour("\n[!] Invalid option. Please try again.", "red"))
    input("[Press Enter to continue]")

# ─── Display Interface ───
# 
def print_interface_status():
    """
    Print the current interface, state, and mode.
    """
    interface, state_raw, mode_raw = get_interface_details()

    state = state_raw.title()
    mode = "AP" if mode_raw.lower() == "ap" else mode_raw.title()

    # Determine colours
    interface_display = colour(interface, "warn")
    state_display = colour(state, "green" if state.lower() == "up" else "red")

    if mode_raw.lower() == "managed":
        mode_display = colour(mode, "green")
    elif mode_raw.lower() == "monitor":
        mode_display = colour(mode, "red")
    elif mode_raw.lower() == "ap":
        mode_display = colour(mode, "yellow")
    else:
        mode_display = colour(mode, "reset")

    # Output
    print(f"[ Interface       ] {interface_display}")
    print(f"[ Interface State ] {state_display}")
    print(f"[ Interface Mode  ] {mode_display}")
    print()

# ─── Display Service ───
# 
def print_service_status():
    """
    Display Access Point status with time-based expiry, NAT state, and BSSID.
    """
    ap_file = "/tmp/wapt_ap_active"
    ap_raw = "Stopped"

    # Expiry threshold
    expiry_seconds = 900

    if os.path.exists(ap_file):
        try:
            with open(ap_file, "r") as f:
                content = f.read().strip()
                parts = content.split("|")

                if len(parts) >= 3:
                    ssid = parts[0]
                    timestamp = int(parts[1])
                    nat_flag = parts[2]
                    bssid = parts[3] if len(parts) > 3 else "default"

                    age = time.time() - timestamp

                    if age <= expiry_seconds:
                        nat_status = "NAT" if nat_flag == "nat" else "No NAT"
                        bssid_display = f", BSSID {bssid}" if bssid != "default" else ""
                        ap_raw = f"Running ({ssid}, {nat_status}{bssid_display})"
        except Exception:
            pass  # Keep ap_raw as "Stopped"

    style = "green" if ap_raw == "Stopped" else "yellow"
    print(f"[ Access Point ] {colour(ap_raw, style)}")
    print()

# ─── Interface Helpers ───
#
def get_interface_details():
    """
    Returns (interface, state, mode) from get-current-interface.sh.
    """
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bash", "get-current-interface.sh")
    )

    if not os.path.exists(script_path):
        return ("[!] Not found", "[!] Not found", "[!] Not found")

    try:
        result = subprocess.run(["bash", script_path], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        interface = lines[0].split(":")[1].strip().upper() if len(lines) > 0 else "?"
        state     = lines[1].split(":")[1].strip().upper() if len(lines) > 1 else "?"
        mode      = lines[2].split(":")[1].strip().upper() if len(lines) > 2 else "?"
        return (interface, state, mode)
    except subprocess.CalledProcessError:
        return ("[!] Script error", "[!] Script error", "[!] Script error")

def get_current_interface():
    """
    Returns interface, state, mode.
    """
    return get_interface_details()[0]

def get_interface_state():
    """
    Returns state from get_interface_details.
    """
    return f"State:     {get_interface_details()[1]}"

def get_interface_mode():
    """
    Returns mode from get_interface_details.
    """
    return f"Mode:      {get_interface_details()[2]}"

# ─── Display Main Menu ───
# 
def show_menu():
    """
    Display main menu.
    """
    ui_clear_screen()
    
    # Header block
    ui_standard_header("Main Menu")

    # Menu block
    ui_header("Standalone Tools")
    print("[1] Access Points")
    print()
    ui_header("Utilities")
    print("[2] Service Control")
    print("[3] Help | About")

    # Exit option
    print("\n[0] Exit")

def run_bash_script(script_name, pause=True, capture=True, title=None, args=None, clear=True):
    """
    Executes a Bash script located under /src/bash.
    
    Args:
        script_name (str): Script name without extension (no .sh)
        args (list): List of arguments to pass to the script
        ...
    """
    if clear:
        ui_clear_screen()

    if title:
        ui_header(title)
        print()

    # Script full path
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bash", f"{script_name}.sh")
    )

    if not os.path.exists(script_path):
        print(f"[!] Script not found: {script_name}.sh")
        return

    cmd = ["bash", script_path]
    if args:
        cmd.extend(args)

    try:
        if capture:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout.strip())
        else:
            subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(colour(f"[x] Script failed: {script_name}.sh", "red"))
        if e.stderr:
            print(e.stderr.strip())

    if pause:
        input("\n[Press Enter to return to menu]")

def prompt_nat():
    """
    Prompt user to enable NAT.
    """
    response = input("\n[+] Enable NAT forwarding for this profile? [y/N]: ").strip().lower()
    return ["nat"] if response == "y" else []

def generate_bssid(profile_number: int) -> str:
    """
    Generate a locally administered MAC address with profile-specific last octet.
    """
    # First byte 0x02 = locally administered
    base = [0x02, 0x00, 0x00, 0x00, 0x00, profile_number]
    return ":".join(f"{octet:02X}" for octet in base)

def ap_profiles():
    """
    Access Points submenu.
    """
    def ap_open(args):
        run_bash_script("start-ap", args=["ap_open"] + args, capture=False, pause=True, clear=False, title="Open Access Point")

    def ap_wpa2(args):
        run_bash_script("start-ap", args=["ap_wpa2"] + args, capture=False, pause=True, clear=False, title="WPA2 Access Point")

    def ap_hidden(args):
        run_bash_script("start-ap", args=["ap_wpa2-hidden"] + args, capture=False, pause=True, clear=False, title="Hidden SSID Access Point")

    def ap_spoofed(args):
        run_bash_script("start-ap", args=["ap_spoofed"] + args, capture=False, pause=True, clear=False, title="Spoofed SSID Access Point")

    def ap_misconfig(args):
        run_bash_script("start-ap", args=["ap_misconfig"] + args, capture=False, pause=True, clear=False, title="Misconfigured Access Point")

    def ap_wpa3(args):
        run_bash_script("start-ap", args=["ap_wpa3"] + args, capture=False, pause=True, clear=False, title="WPA3 Access Point")

    def stop_ap():
        run_bash_script("stop-ap", pause=True, capture=False, clear=False, title="Stop Access Point")

    actions = {
        "1": ap_open,
        "2": ap_wpa2,
        "3": ap_hidden,
        "4": ap_spoofed,
        "5": ap_misconfig,
        "6": ap_wpa3,
        "S": stop_ap
    }

    while True:
        ui_clear_screen()

        # Header block
        ui_standard_header("Standalone Access Point Profiles")

        # Menu block
        print("[1] Launch OPN Access Point (Unencrypted)")
        print("[2] Launch WPA2 Personal Access Point (WPA2-PSK)")
        print("[3] Launch Hidden SSID Access Point (WPA2-PSK)")
        print("[4] Launch Spoofed SSID Access Point (OPN)")
        print("[5] Launch Misconfigured Access Point (WPA1-TKIP)")
        print("[6] Launch WPA3 Access Point (WPA3-SAE)")
        print("\n[S] Stop Access Point")
        print("\n[0] Return to Main Menu")

        # Input
        choice = input("\n[+] Select an option: ").strip().upper()

        if choice == "0":
            break

        if choice in actions:
            if choice in {"1", "2", "3", "4", "5", "6"}:
                if os.path.exists("/tmp/wapt_ap_active"):
                    print(colour("\n[!] An access point is already running.", "red"))
                    input("\n[Press Enter to return to menu]")
                    continue  # Return to submenu without prompting for NAT

                # NAT prompt
                nat_args = prompt_nat()

                # BSSID prompt
                use_bssid = input("[+] Use a custom (locally administered) BSSID? [y/N]: ").strip().lower()
                if use_bssid == "y":
                    profile_map = {
                        "1": 1,
                        "2": 2,
                        "3": 3,
                        "4": 4,
                        "5": 5,
                        "6": 6
                    }
                    profile_number = profile_map.get(choice, 0)
                    generated_bssid = generate_bssid(profile_number)
                    print(colour(f"[+] Custom BSSID selected: {generated_bssid}", "green"))
                    print(colour("[*] You can verify BSSID assignment in the Service Status panel.", "grey"))
                    os.environ["BSSID"] = generated_bssid
                else:
                    os.environ.pop("BSSID", None)

                print()
                actions[choice](nat_args)  # Call AP launcher with args

            else:
                print()
                actions[choice]()  # Stop AP or other non-arg actions
        else:
            ui_pause_on_invalid()

def service_control():
    """
    Service Control menu.
    """

    def interface_state():
        """
        Interface State submenu.
        """

        def set_interface_down():
            run_bash_script("set-interface-down", pause=False, capture=False, clear=False, title="Change Interface State")

        def set_interface_up():
            run_bash_script("set-interface-up", pause=False, capture=False, clear=False, title="Change Interface State")

        actions = {
            "1": set_interface_down,
            "2": set_interface_up
        }

        while True:
            ui_clear_screen()

            # Header block
            ui_standard_header("Set Interface State")

            # Menu block                    
            print("[1] Set interface state DOWN")
            print("[2] Set interface state UP")
            print("\n[0] Return to Service Control Menu")

            # Input
            choice = input("\n[+] Select an option: ")

            if choice == "0":
                break

            action = actions.get(choice)
            if action:
                print()
                action()
            else:
                ui_pause_on_invalid()

    def interface_mode():
        """
        Interface mode submenu.
        """

        def switch_to_managed():
            run_bash_script("set-mode-managed", pause=False, capture=False, clear=False, title="Change Interface Mode")

        def switch_to_monitor():
            run_bash_script("set-mode-monitor", pause=False, capture=False, clear=False, title="Change Interface Mode")

        actions = {
            "1": switch_to_managed,
            "2": switch_to_monitor
        }

        while True:
            ui_clear_screen()

            # Header block
            ui_standard_header("Set Interface Mode")
            
            # Menu block
            print("[1] Set interface mode MANAGED")
            print("[2] Set interface mode MONITOR")
            print("\n[0] Return to Service Control Menu")

            # Input
            choice = input("\n[+] Select an option: ")

            if choice == "0":
                break

            action = actions.get(choice)
            if action:
                print()
                action()
            else:
                ui_pause_on_invalid()

    def interface_reset():
        """
        Reset interface submenu.
        """

        def perform_soft_reset():
            run_bash_script("reset-interface-soft", pause=False, capture=False, clear=False, title="Reset Interface (Soft)")

        def perform_hard_reset():
            run_bash_script("reset-interface-hard", pause=False, capture=False, clear=False, title="Reset Interface (Hard)")

        actions = {
            "1": perform_soft_reset,
            "2": perform_hard_reset
        }

        while True:
            ui_clear_screen()

            # Header block
            ui_standard_header("Reset Interface")
            
            # Menu block
            print("[1] Interface soft reset (Down/Up)")
            print("[2] Interface hard reset (Unload/Reload)")
            print("\n[0] Return to Service Control Menu")

            # Input
            choice = input("\n[+] Select an option: ")

            if choice == "0":
                break

            action = actions.get(choice)
            if action:
                print()
                action()
            else:
                ui_pause_on_invalid()

    actions = {
        "1": interface_state,
        "2": interface_mode,
        "3": interface_reset
    }

    while True:
        ui_clear_screen()

        # Header block
        ui_standard_header("Service Control")

        # Menu block
        print("[1] Interface State")
        print("[2] Interface Mode")
        print("[3] Reset Interface")
        print("\n[0] Return to Main Menu")

        # Input
        choice = input("\n[+] Select an option: ")

        if choice == "0":
            break

        action = actions.get(choice)
        if action:
            ui_clear_screen()
            action()
        else:
            ui_pause_on_invalid()

def help_about():
    """
    Help | About submenu.
    """

    ui_clear_screen()

    # Header block
    ui_standard_header("Help | About")

    print("This tool provides a command-line interface for managing")
    print("wireless access point profiles in a structured testbed environment.")
    print()
    print("Functions include:")
    print("  • Launching access points with varied encryption and visibility modes")
    print("  • Applying optional NAT and custom BSSID configurations")
    print("  • Stopping services and restoring network state")
    print("  • Monitoring interface and AP status via the Service Status panel")
    print()
    print("All operations are driven by modular Bash scripts, coordinated")
    print("through a unified Python menu for SME-friendly field usage.")
    print()
    print("Author : Paul Smurthwaite")
    print("Module : TM470-25B")
    print("Date   : May 2025")

    # Input
    input("\n[Press Enter to return to menu]")

def main():
    """
    User input handler.
    """

    while True:
        show_menu()
        choice = input("\n[+] Select an option: ")
        
        if choice == "1":
            ap_profiles()
        elif choice == "2":
            service_control()
        elif choice == "3":
            help_about()
        elif choice == "0":
            if os.path.exists("/tmp/wapt_ap_active"):
                print(colour("\n[!] Stopping running access point", "red"))
                run_bash_script("stop-ap", pause=False, capture=False, clear=False)

            print(colour("\n[+] Exiting to shell.", "green"))
            break

        else:
            ui_pause_on_invalid()

if __name__ == "__main__":
    main()
