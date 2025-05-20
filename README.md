# Wireless Access Point Toolkit (WAPT)

WAPT is a modular command-line toolkit for deploying standalone wireless access points for security testing and demonstration. It supports a range of profiles including open, WPA2, WPA3, hidden, spoofed, and misconfigured access points. The toolkit is structured for reliability, maintainability, and ease of use in SME or lab environments.

## Features

- Profile-based access point deployment using Bash and Python
- Optional NAT forwarding for client internet access
- Optional custom BSSID assignment using locally administered MACs
- Displays active BSSID in Service Status panel (default or custom)
- Automatic status tracking and time-based expiry of active AP flags
- Clean service shutdown and interface state restoration
- Menu-driven interface with clear operator prompts and validation
- Symbol-based CLI output format for clear operator feedback
- Standardised menu layout with persistent interface/service status display

## Repository Structure

The key files and directories are as follows:

```
/src/
├── bash/
│   ├── config.sh
│   ├── print.sh
│   ├── start-ap.sh
│   ├── stop-ap.sh
│   ├── set-interface-down.sh
│   ├── set-interface-up.sh
│   ├── reset-interface-soft.sh
│   ├── hostapd.conf.template
│   ├── dnsmasq.conf
│   └── ap-profiles/
│       ├── ap_open.cfg
│       ├── ap_wpa2.cfg
│       ├── ap_wpa3.cfg
│       ├── ap_spoofed.cfg
│       ├── ap_misconfig.cfg
│       └── ap_wpa2-hidden.cfg
├── python/
│   └── wapt.py
```

## Usage

To launch WAPT:

```
cd src/python
python3 wapt.py
```

The main menu allows the user to launch access point profiles, stop a running AP, or configure interface settings.

When launching a profile, the user is prompted to:

1. Enable or disable NAT forwarding
2. Use a custom BSSID (auto-generated if enabled)

Once launched, the access point runs on the configured wireless interface. Runtime status (SSID, NAT, BSSID) is shown in the Service Status panel and stored in `/tmp/wapt_ap_active`.

## Access Point Profiles

| Profile         | Description                                   | Security   |
|-----------------|-----------------------------------------------|------------|
| Open            | No encryption                                 | None       |
| WPA2            | Standard WPA2 Personal                        | WPA2-PSK   |
| Hidden SSID     | WPA2 with hidden SSID broadcast               | WPA2-PSK   |
| Spoofed SSID    | Fake SSID for impersonation testing           | None       |
| Misconfigured   | WPA1/TKIP legacy setup                        | WPA1-TKIP  |
| WPA3            | Secure SAE-based modern AP                    | WPA3-SAE   |

Each profile is defined via a configuration file in `bash/ap-profiles/`.

## Shutdown & Recovery

- Active access points can be stopped from the menu or automatically when exiting WAPT.
- `stop-ap.sh` fully resets interface state, DNS resolver settings, IP forwarding, and firewall rules.
- The system is returned to a stable post-launch condition.

## Requirements

- Linux system with `hostapd`, `dnsmasq`, `iptables`, `mac80211` driver stack
- Wireless interface that supports AP mode (e.g., `iw list` should show `AP` under supported interface modes)
- Python 3.x for the menu interface

## Notes

- WPA3 functionality depends on `hostapd` compiled with SAE support.
- Custom BSSIDs are generated using the 02:00:00:00:00:XX range to ensure locally administered uniqueness.
- This project is designed for controlled environments only and should not be used in production networks.
