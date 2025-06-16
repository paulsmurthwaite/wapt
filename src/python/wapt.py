#!/usr/bin/env python3
"""wapt.py

Main entry point for the Wireless Access Point Toolkit (WAPT) menu interface.

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
import sys
import time

# ─── UI Helpers ───
# Theme Config
COLOURS_DARK = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "header": "\033[93m",  # yellow
    "info":   "\033[96m",  # cyan
    "success":"\033[92m",  # green
    "warning":"\033[91m",  # red
    "neutral":"\033[90m"   # grey
}

COLOURS_LIGHT = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "header": "\033[94m",  # blue
    "info":   "\033[36m",  # teal
    "success":"\033[32m",  # dark green
    "warning":"\033[31m",  # red/maroon
    "neutral":"\033[30m"   # black/grey
}

COLOURS_HIGH_CONTRAST = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "header": "\033[97m",  # Bright white
    "info":   "\033[96m",  # Cyan
    "success":"\033[92m",  # Bright green
    "warning":"\033[91m",  # Bright red
    "neutral":"\033[97m"   # Bright white again
}

COLOURS_MONOCHROME = {
    "reset":  "",
    "bold":   "",
    "header": "",
    "info":   "",
    "success":"",
    "warning":"",
    "neutral":""
}

THEME_MODE = "dark"
if "--light" in sys.argv:
    THEME_MODE = "light"
elif "--high-contrast" in sys.argv:
    THEME_MODE = "high-contrast"
elif "--monochrome" in sys.argv:
    THEME_MODE = "monochrome"

if THEME_MODE == "dark":
    COLOURS = COLOURS_DARK
elif THEME_MODE == "light":
    COLOURS = COLOURS_LIGHT
elif THEME_MODE == "high-contrast":
    COLOURS = COLOURS_HIGH_CONTRAST
elif THEME_MODE == "monochrome":
    COLOURS = COLOURS_MONOCHROME
else:
    COLOURS = COLOURS_DARK  # Fallback default

# UI Colour
def colour(text, style):
    """
    Apply ANSI colour styling to text based on theme.
    """
    return f"{COLOURS.get(style, '')}{text}{COLOURS['reset']}"

# UI Banner
def ui_banner():
    """
    Display ASCII banner.
    """
    ascii_banner = pyfiglet.figlet_format("WAPT", font="ansi_shadow")
    print(colour(ascii_banner, "header"))

# UI Header
def ui_header(title="Wireless Access Point Toolkit"):
    """
    Display section header.
    """
    styled = f"{COLOURS['bold']}{COLOURS['header']}[ {title} ]{COLOURS['reset']}"
    print(styled)

# UI Divider
def ui_divider():
    """
    Display divider.
    """
    print(colour("-----------------------------------", "neutral"))
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
    print(colour("\n[!] Invalid option. Please try again.", "warning"))
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
    interface_display = colour(interface, "info")
    state_display = colour(state, "success" if state.lower() == "up" else "warning")

    if mode_raw.lower() == "managed":
        mode_display = colour(mode, "success")
    elif mode_raw.lower() == "monitor":
        mode_display = colour(mode, "warning")
    elif mode_raw.lower() == "ap":
        mode_display = colour(mode, "warning")
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
    ap_file = "/tmp/ap_active"
    ap_raw = "Stopped"

    # Expiry threshold
    expiry_seconds = 900

    if os.path.exists(ap_file):
        try:
            with open(ap_file, "r") as f:
                content = f.read().strip()
                parts = content.split("|")

                if len(parts) >= 4:
                    timestamp = int(parts[0])
                    ssid = parts[1]
                    bssid = parts[2]
                    channel = parts[3]

                    age = time.time() - timestamp

                    if age <= expiry_seconds:
                        start_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        ap_raw = f"Running ({start_time}, {ssid}, CH {channel}, BSSID {bssid})"
        except Exception:
            pass  # Keep ap_raw as "Stopped"

    style = "success" if ap_raw == "Stopped" else "warning"
    print(f"[ Access Point ] {colour(ap_raw, style)}")
    print()

# ─── Interface Helpers ───
#
def get_interface_details():
    """
    Returns (interface, state, mode) from get-current-interface.sh.
    """
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bash", "services", "get-current-interface.sh")
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
    ui_header("Utilities")
    print("[1] Access Points")
    print()
    ui_header("Services")
    print("[2] Service Control")
    print()
    print("[3] Help | About")

    # Exit option
    print("\n[0] Exit")

# ─── Bash Script Handler ───
#
def run_bash_script(script_name, pause=True, capture=True, args=None, clear=True, title=None):
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
        print(f"[x] Script not found: {script_name}.sh")
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
        print(colour(f"[x] Script failed: {script_name}.sh", "warning"))
        if e.stderr:
            print(e.stderr.strip())

    if pause:
        input("\n[Press Enter to return to menu]")

def prompt_nat():
    """
    Prompt user to enable NAT.
    """
    response = input("\n[?] Enable NAT forwarding for this profile? [y/N]: ").strip().lower()
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
    def ap_t001(_):
        run_bash_script("utilities/start-ap", args=["ap_t001", "nat"], capture=False, pause=False, clear=False, title="T001: Open")

    def ap_t003_1(_):
        run_bash_script("utilities/start-ap", args=["ap_t003_1", "nat"], capture=False, pause=True, clear=False, title="T003: Open")

    def ap_t003_2(_):
        run_bash_script("utilities/start-ap", args=["ap_t003_2", "nat"], capture=False, pause=True, clear=False, title="T003: WPA2")

    def ap_t003_3(_):
        run_bash_script("utilities/start-ap", args=["ap_t003_3", "nat"], capture=False, pause=True, clear=False, title="T003: WPA2 Hidden SSID")

    def ap_t003_4(_):
        run_bash_script("utilities/start-ap", args=["ap_t003_4", "nat"], capture=False, pause=True, clear=False, title="T003: Misconfigured")

    def ap_t004(_):
        run_bash_script("utilities/start-ap", args=["ap_t004", "nat"], capture=False, pause=False, clear=False, title="T004: WPA2")

    def ap_t005(_):
        run_bash_script("utilities/start-ap", args=["ap_t005", "nat"], capture=False, pause=False, clear=False, title="T005: WPA2")

    def ap_t006(_):
        run_bash_script("utilities/start-ap", args=["ap_t006", "nat"], capture=False, pause=False, clear=False, title="T006: Misconfigured")

    def ap_t007(_):
        run_bash_script("utilities/start-ap", args=["ap_t007", "nat"], capture=False, pause=False, clear=False, title="T007: WPA2")

    def ap_t009(_):
        run_bash_script("utilities/start-ap", args=["ap_t009", "nat"], capture=False, pause=False, clear=False, title="T009: WPA2")

    def ap_t014(_):
        run_bash_script("utilities/start-ap", args=["ap_t014", "nat"], capture=False, pause=False, clear=False, title="T014: Open")

    def ap_t015(_):
        run_bash_script("utilities/start-ap", args=["ap_t015", "nat"], capture=False, pause=False, clear=False, title="T015: Open")

    def ap_t016(_):
        run_bash_script("utilities/start-ap", args=["ap_t016", "nat"], capture=False, pause=False, clear=False, title="T016: Open")

    def stop_ap():
        run_bash_script("utilities/stop-ap", pause=True, capture=False, clear=False, title="Stop Access Point")

    actions = {
        "1": ap_t001,
        "2": ap_t003_1,
        "3": ap_t003_2,
        "4": ap_t003_3,
        "5": ap_t003_4,
        "6": ap_t004,
        "7": ap_t005,
        "8": ap_t006,
        "9": ap_t007,
        "10": ap_t009,
        "11": ap_t014,
        "12": ap_t015,
        "13": ap_t016,
        "S": stop_ap
    }

    while True:
        ui_clear_screen()

        # Header block
        ui_standard_header("Standalone Access Point Profiles")

        # Menu block
        print("[1] Launch T001: Open")
        print("[2] Launch T003: Open")
        print("[3] Launch T003: WPA2")
        print("[4] Launch T003: WPA2 Hidden SSID")
        print("[5] Launch T003: Misconfigured")
        print("[6] Launch T004: WPA2")
        print("[7] Launch T005: WPA2")
        print("[8] Launch T006: Misconfigured")
        print("[9] Launch T007: WPA2")
        print("[10] Launch T009: WPA2")
        print("[11] Launch T014: Open")
        print("[12] Launch T015: Open")
        print("[13] Launch T016: Open")
        print("\n[S] Stop Access Point")
        print("\n[0] Return to Main Menu")

        # Input
        choice = input("\n[?] Select an option: ").strip().upper()

        if choice == "0":
            break

        if choice in actions:
            if choice == "S":
                print()
                actions[choice]()  # Stop AP
            else:
                # Preconfigured profiles (1–13)
                if os.path.exists("/tmp/ap_active"):
                    print(colour("\n[!] An access point is already running.", "warning"))
                    input("\n[Press Enter to return to menu]")
                    continue

                os.environ.pop("BSSID", None)  # Ensure no leftover override
                print()
                actions[choice](None)
        else:
            ui_pause_on_invalid()

def service_control():
    """
    Service Control menu.
    """

    def show_dhcp_leases():
        run_bash_script("services/show-ap-dhcp", pause=True, capture=True, clear=False, title="DHCP Lease Table")

    def show_connected_stations():
        run_bash_script("services/show-ap-stations", pause=True, capture=True, clear=False, title="Connected Stations")

    def interface_state():
        """
        Interface State submenu.
        """

        def set_interface_down():
            run_bash_script("services/set-interface-down", pause=False, capture=False, clear=False, title="Change Interface State")

        def set_interface_up():
            run_bash_script("services/set-interface-up", pause=False, capture=False, clear=False, title="Change Interface State")

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
            choice = input("\n[?] Select an option: ")

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
            run_bash_script("services/set-mode-managed", pause=False, capture=False, clear=False, title="Change Interface Mode")

        def switch_to_monitor():
            run_bash_script("services/set-mode-monitor", pause=False, capture=False, clear=False, title="Change Interface Mode")

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
            choice = input("\n[?] Select an option: ")

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
            run_bash_script("services/reset-interface-soft", pause=False, capture=False, clear=False, title="Reset Interface (Soft)")

        def perform_hard_reset():
            run_bash_script("services/reset-interface-hard", pause=False, capture=False, clear=False, title="Reset Interface (Hard)")

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
            choice = input("\n[?] Select an option: ")

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
        "3": interface_reset,
        "4": show_dhcp_leases,
        "5": show_connected_stations
    }

    while True:
        ui_clear_screen()

        # Header block
        ui_standard_header("Service Control")

        # Menu block
        print("[1] Interface State")
        print("[2] Interface Mode")
        print("[3] Reset Interface")
        print("[4] Show DHCP Leases")
        print("[5] Show Connected Stations")
        print("\n[0] Return to Main Menu")

        # Input
        choice = input("\n[?] Select an option: ")

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
        choice = input("\n[?] Select an option: ")
        
        if choice == "1":
            ap_profiles()
        elif choice == "2":
            service_control()
        elif choice == "3":
            help_about()
        elif choice == "0":
            if os.path.exists("/tmp/wapt_ap_active"):
                print(colour("\n[!] Stopping running access point", "warning"))
                run_bash_script("stop-ap", pause=False, capture=False, clear=False)

            print(colour("\n[+] Exiting to shell.", "success"))
            break

        else:
            ui_pause_on_invalid()

if __name__ == "__main__":
    main()
