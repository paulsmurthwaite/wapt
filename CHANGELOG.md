# CHANGELOG

All notable changes to the Wireless Access Point Toolkit (WAPT) will be documented in this file.

## [v1.0.1] – 2025-05-20

### Changed
- Reworked start-ap.sh to always report the actual runtime BSSID, using iw dev for accuracy
- Reset wireless interface MAC address to factory default in set-interface-down.sh (unless custom BSSID is applied)
- Improved BSSID messaging in wapt.py to direct users to the Service Status panel
- Expanded help_about() content with clearer description of toolkit functions
- Corrected menu label typo in WPA2 access point entry
- Updated exit message formatting and script failure output to match symbol-based UI style

### UI
- Finalised standardised output format using [+], [x], [>], [!], etc. across all Bash scripts
- Applied consistent UI presentation across all screens: ASCII banner, headers, subtitle, menu, input

## [v1.0.0] – 2025-05-19

### Added
- Initial release of the WAPT system, including:
  - `wapt.py` Python CLI interface with colour-coded status display and menu navigation
  - Access point launch profiles:
    - Open AP (`ap_open`)
    - WPA2-PSK (`ap_wpa2`)
    - Hidden SSID (`ap_wpa2-hidden`)
    - Spoofed SSID (`ap_spoofed`)
    - Misconfigured WPA1/TKIP AP (`ap_misconfig`)
    - WPA3-SAE (`ap_wpa3`)
  - NAT toggle support (enabled per launch)
  - Custom BSSID generation (locally administered MACs by profile)
  - Time-based AP status expiry (auto-clears stale status files after 15 mins)

### Changed
- Refactored interface configuration logic into dedicated helper scripts:
  - `set-interface-up.sh`
  - `set-interface-down.sh`
  - `reset-interface-soft.sh`
- `start-ap.sh` and `stop-ap.sh` simplified to rely on helpers and central `config.sh`

### Fixed
- Prevented launching multiple APs simultaneously using `/tmp/wapt_ap_active` lock
- Ensured AP is automatically shut down when exiting main menu
- Removed redundant double interface resets caused by unnecessary internal `stop-ap` call in `start-ap.sh`

### Notes
- WPA3 functionality requires compatible `hostapd` with SAE support
- All custom BSSIDs are assigned from `02:00:00:00:00:XX` range (locally administered)
- `wapt.py` is ready for future extension with additional services or reporting functionality
