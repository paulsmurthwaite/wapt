# Wireless Access Point Toolkit (WAPT)

WAPT is a modular command-line toolkit for launching simulated wireless access points to support wireless threat simulations. It provides a set of predefined AP profiles corresponding to specific threat scenarios (T001–T016 subset) used in WATT (Wireless Attack Toolkit). The toolkit is optimised for reliability and consistency in controlled lab environments.

## Features

- Scenario-aligned AP profiles for 13 WATT threats (e.g. Evil Twin, Open Rogue, Misconfigured)
- Fixed parameters for each profile: SSID, BSSID, encryption, channel
- NAT forwarding always enabled for client traffic routing
- Custom BSSID generation for local admin testing (used in legacy versions only)
- Service Status panel displays live SSID, BSSID, channel, and start time
- Time-based status expiry and consistent cleanup via stop-ap.sh
- Fully automated AP launch with no operator input required
- Clean Bash/Python CLI integration with consistent symbol-based output

## Repository Structure

The key files and directories are as follows:

```
/src/
├── bash/
│   ├── config.sh
│   ├── start-ap.sh
│   ├── stop-ap.sh
│   ├── set-interface-up.sh
│   ├── set-interface-down.sh
│   ├── fn_print.sh
│   ├── fn_services.sh
│   ├── hostapd.conf.template
│   ├── dnsmasq.conf
│   └── ap-profiles/
│       ├── ap_t001.cfg
│       ├── ap_t003_1.cfg
│       ├── ap_t003_2.cfg
│       ├── ap_t003_3.cfg
│       ├── ap_t003_4.cfg
│       ├── ap_t004.cfg
│       ├── ap_t005.cfg
│       ├── ap_t006.cfg
│       ├── ap_t007.cfg
│       ├── ap_t009.cfg
│       ├── ap_t014.cfg
│       ├── ap_t015.cfg
│       └── ap_t016.cfg
├── python/
│   └── wapt.py
```

## Usage

To launch WAPT:

```
cd src/python
python3 wapt.py
```

From the menu:
- Select a scenario-specific access point (T001–T016 subset)
- AP is launched with fixed config (NAT and MAC defaults included)
- Service Status reflects real-time AP state
- Stop AP at any time from the menu

## Access Point Profiles

| Profile         | Description                                   | Security   |
|-----------------|-----------------------------------------------|------------|
| T001            | Open Access Point                             | None       |
| T003            | Open, WPA2, Hidden, Misconfig                 | Mixed      |
| T004            | WPA2 Evil Twin                                | WPA2-PSK   |
| T005            | WPA2 + Open Rogue                             | WPA2/Open  |
| T006            | Misconfigured WPA1/TKIP                       | WPA1-TKIP  |
| T007, T009      | WPA2 for client targeting                     | WPA2-PSK   |
| T014–T016       | Open + Client for spoofing/MiTM               | None       |

Each profile launches with L7 services (DNS, NTP, HTTP) and consistent interface configuration.

## Requirements

- Linux host with support for hostapd, dnsmasq, iptables
- Wireless interface supporting AP mode (e.g. Alfa AWUS036ACM)
- Python 3.x for CLI interface

## Notes

- All APs use NAT routing by default via iptables
- BSSID defaults to hardware MAC unless overridden (custom BSSID disabled by default)
- Status is logged in /tmp/ap_active and auto-expires after 15 mins
