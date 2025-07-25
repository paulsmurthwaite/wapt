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
import datetime

LOG_FILE = "logs/wapt_session.log"

# Define version and date at the top for easy update
APP_VERSION = "v1.0"
APP_DATE = "May 2025"

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
    Apply ANSI colour styling to text based on the current theme.

    Args:
        text (str): The text to style.
        style (str): The style key (e.g., 'header', 'info', 'success').

    Returns:
        str: The styled text with ANSI codes.
    """
    return f"{COLOURS.get(style, '')}{text}{COLOURS['reset']}"

# UI Banner
def ui_banner():
    """
    Display the ASCII art banner for the application using the current theme's header colour.
    """
    ascii_banner = pyfiglet.figlet_format("WAPT", font="ansi_shadow")
    print(colour(ascii_banner, "header"))

# UI Header
def ui_header(title="Wireless Access Point Toolkit"):
    """
    Display a section header. If the main title, includes version and date.

    Args:
        title (str): The header text to display. Defaults to the main app title.
    """
    if title == "Wireless Access Point Toolkit":
        styled = f"{COLOURS['bold']}{COLOURS['header']}[ {title} {APP_VERSION} – {APP_DATE} ]{COLOURS['reset']}"
    else:
        styled = f"{COLOURS['bold']}{COLOURS['header']}[ {title} ]{COLOURS['reset']}"
    print(styled)

# UI Divider
def ui_divider():
    """
    Print a horizontal divider line in the UI using the neutral colour.
    """
    print(colour("-----------------------------------", "neutral"))
    print()

# UI Subtitle
def ui_subtitle():
    """
    Display a subtitle block: divider, interface status, service status, divider.
    """
    ui_divider()
    print_interface_status()
    print_service_status()
    ui_divider()

# UI Standard Header
def ui_standard_header(menu_title=None):
    """
    Render the standard UI header block: banner, main title, subtitle, and optional menu title.

    Args:
        menu_title (str, optional): If provided, displays this as a section header after the main title.
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
    Clear the terminal screen using the appropriate command for the OS.
    """
    os.system("cls" if os.name == "nt" else "clear")

# UI Invalid Option
def ui_pause_on_invalid():
    """
    Display an invalid input warning and pause for user acknowledgment.
    """
    print(colour("\n[!] Invalid option. Please try again.", "warning"))
    input("[Press Enter to continue]")

# ─── Display Interface ───
# 
def print_interface_status():
    """
    Print the current wireless interface, its state, and mode, with colour coding.
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
    Display the current Access Point status, including expiry, NAT state, and BSSID.
    Reads from /tmp/ap_active and shows 'Running' or 'Stopped' with details.
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
    Get the current wireless interface details by running a helper bash script.

    Returns:
        tuple: (interface, state, mode) as strings.
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
    Get the current wireless interface name.

    Returns:
        str: The interface name.
    """
    return get_interface_details()[0]

def get_interface_state():
    """
    Get the current wireless interface state.

    Returns:
        str: The interface state.
    """
    return f"State:     {get_interface_details()[1]}"

def get_interface_mode():
    """
    Get the current wireless interface mode.

    Returns:
        str: The interface mode.
    """
    return f"Mode:      {get_interface_details()[2]}"

# ─── Theme Management ───
def set_theme(mode):
    """
    Set the global theme mode and update the COLOURS dictionary.

    Args:
        mode (str): The theme mode to set ('dark', 'light', 'high-contrast', 'monochrome').
    """
    global THEME_MODE, COLOURS
    THEME_MODE = mode
    if mode == "dark":
        COLOURS = COLOURS_DARK
    elif mode == "light":
        COLOURS = COLOURS_LIGHT
    elif mode == "high-contrast":
        COLOURS = COLOURS_HIGH_CONTRAST
    elif mode == "monochrome":
        COLOURS = COLOURS_MONOCHROME
    else:
        COLOURS = COLOURS_DARK

# Initialize theme from CLI args (moved from top-level)
if __name__ == "__main__":
    # Only parse CLI args on first run
    if "--light" in sys.argv:
        set_theme("light")
    elif "--high-contrast" in sys.argv:
        set_theme("high-contrast")
    elif "--monochrome" in sys.argv:
        set_theme("monochrome")
    else:
        set_theme("dark")

# ─── Display Main Menu ───
# 
def show_menu():
    """
    Display the main menu, including current theme, and handle no user input.
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
    # Show current theme in the menu
    theme_label = THEME_MODE.replace("-", " ").title()
    print(f"[3] Change Theme [{theme_label}]")
    print("[4] Help | About")

    # Exit option
    print("\n[0] Exit")

# ─── Bash Script Handler ───
#
def run_bash_script(script_name, pause=True, capture=True, args=None, clear=True, title=None):
    """
    Executes a Bash script located under /src/bash. Handles errors and logs events.

    Args:
        script_name (str): Script name without extension (no .sh).
        pause (bool): If True, pauses after execution.
        capture (bool): If True, captures and prints script output.
        args (list, optional): Arguments to pass to the script.
        clear (bool): If True, clears the screen before running.
        title (str, optional): Title to display before running.

    Returns:
        None

    Side Effects:
        Prints output to terminal. Logs errors to session log.
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
        error_msg = f"[x] Script not found: {script_name}.sh"
        print(error_msg)
        log_event(f"ERROR: {error_msg}")
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
        error_msg = f"[x] Script failed: {script_name}.sh"
        print(colour(error_msg, "warning"))
        if e.stderr:
            print(e.stderr.strip())
        log_event(f"ERROR: {error_msg} | {e.stderr.strip() if e.stderr else ''}")
    except Exception as e:
        error_msg = f"[x] Unexpected error running script: {script_name}.sh"
        print(colour(error_msg, "warning"))
        print(e)
        log_event(f"UNEXPECTED ERROR: {error_msg} | {str(e)}")

    if pause:
        input("\n[Press Enter to return to menu]")

def prompt_nat():
    """
    Prompt the user to enable NAT forwarding for the selected AP profile.

    Returns:
        list: ["nat"] if enabled, otherwise an empty list.
    """
    response = input(f"\n[{colour('?', 'header')}] Enable NAT forwarding for this profile? [y/N]: ").strip().lower()
    return ["nat"] if response == "y" else []

def generate_bssid(profile_number: int) -> str:
    """
    Generate a locally administered MAC address with a profile-specific last octet.

    Args:
        profile_number (int): The AP profile number to encode in the MAC address.

    Returns:
        str: The generated MAC address as a string.
    """
    # First byte 0x02 = locally administered
    base = [0x02, 0x00, 0x00, 0x00, 0x00, profile_number]
    return ":".join(f"{octet:02X}" for octet in base)

def log_event(message):
    """
    Append a timestamped event to the session log file. Ensures the logs directory exists.
    Logs file write errors to stderr.

    Args:
        message (str): The event message to log.
    """
    # Ensure logs directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} | {message}\n")
    except Exception as e:
        print(colour("[x] Failed to write to log file.", "warning"))
        print(e)

def ap_profiles():
    """
    Display the Access Points submenu, allowing the user to launch or stop AP profiles.
    Handles user input and logs AP launches.
    """
    def ap_t001(_):
        log_event("Launched AP profile: T001")
        run_bash_script("utilities/start-ap", args=["ap_t001", "nat"], capture=False, pause=False, clear=False, title="T001: Open")

    def ap_t003_1(_):
        log_event("Launched AP profile: T003_1")
        run_bash_script("utilities/start-ap", args=["ap_t003_1", "nat"], capture=False, pause=True, clear=False, title="T003: Open")

    def ap_t003_2(_):
        log_event("Launched AP profile: T003_2")
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
        choice = input(f"\n[{colour('?', 'header')}] Select an option: ").strip().upper()

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
    Display the Service Control menu, providing access to interface and service management.
    Handles user input and calls relevant submenus.
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
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

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
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

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
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

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
        choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

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
    Display the Help | About submenu, including inclusivity features and project info.
    """
    ui_clear_screen()
    # Header block
    ui_standard_header("Help | About")
    print(colour("Inclusivity & Accessibility Features:", "header"))
    print("  • Multiple colour themes: Dark, Light, High Contrast, Monochrome")
    print("  • High-contrast and monochrome modes for low vision and colourblind users")
    print("  • Fully keyboard-navigable menu system")
    print("  • Clear, consistent prompts and colour cues throughout the UI")
    print("  • Accessible to users with limited command-line experience")
    print()
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
    print(f"Author : Paul Smurthwaite")
    print(f"Module : TM470-25B")
    print(f"Version: {APP_VERSION}")
    print(f"Date   : {APP_DATE}")
    # Input
    input("\n[Press Enter to return to menu]")

def theme_menu():
    """
    Display the theme selection submenu, allowing the user to change the colour theme.
    Handles user input and logs theme changes.
    """
    while True:
        ui_clear_screen()
        ui_standard_header("Change Theme")
        print("Select a theme:\n")
        print("[1] Dark (default)")
        print("[2] Light")
        print("[3] High Contrast")
        print("[4] Monochrome")
        print("\n[0] Return to Main Menu")
        choice = input(f"\n[{colour('?', 'header')}] Select a theme: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            set_theme("dark")
            log_event("Theme changed to 'Dark'")
            print(colour("\n[+] Theme changed to Dark.", "success"))
            input("[Press Enter to continue]")
            break
        elif choice == "2":
            set_theme("light")
            log_event("Theme changed to 'Light'")
            print(colour("\n[+] Theme changed to Light.", "success"))
            input("[Press Enter to continue]")
            break
        elif choice == "3":
            set_theme("high-contrast")
            log_event("Theme changed to 'High Contrast'")
            print(colour("\n[+] Theme changed to High Contrast.", "success"))
            input("[Press Enter to continue]")
            break
        elif choice == "4":
            set_theme("monochrome")
            log_event("Theme changed to 'Monochrome'")
            print(colour("\n[+] Theme changed to Monochrome.", "success"))
            input("[Press Enter to continue]")
            break
        else:
            log_event(f"Theme menu: Invalid option '{choice}'")
            ui_pause_on_invalid()

def main():
    """
    Main user input handler and application loop. Handles menu navigation, logging, and error handling.
    """
    log_event("Session started")
    try:
        while True:
            show_menu()
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ").strip()
            if choice == "1":
                log_event("Main menu: Selected 'Access Points'")
                ap_profiles()
            elif choice == "2":
                log_event("Main menu: Selected 'Service Control'")
                service_control()
            elif choice == "3":
                log_event(f"Main menu: Selected 'Change Theme' (current: {THEME_MODE})")
                theme_menu()
            elif choice == "4":
                log_event("Main menu: Selected 'Help | About'")
                help_about()
            elif choice == "0":
                if os.path.exists("/tmp/wapt_ap_active"):
                    print(colour("\n[!] Stopping running access point", "warning"))
                    run_bash_script("stop-ap", pause=False, capture=False, clear=False)
                print(colour("\n[+] Exiting to shell.", "warning"))
                log_event("Session ended")
                break
            else:
                log_event(f"Main menu: Invalid option '{choice}'")
                ui_pause_on_invalid()
    except KeyboardInterrupt:
        print(colour("\n[!] Session interrupted by user.", "warning"))
        log_event("Session interrupted by user (KeyboardInterrupt)")
    except Exception as e:
        print(colour("[x] An unexpected error occurred. See log for details.", "warning"))
        log_event(f"UNEXPECTED ERROR: {str(e)}")

if __name__ == "__main__":
    main()
