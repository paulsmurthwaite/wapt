# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [v1.0] - 2025-05-16
### Added
- Initial release of WAPT.
- Modular CLI for launching simulated wireless access points.
- 13 scenario-aligned AP profiles.
- NAT forwarding and custom BSSID support.
- Live Service Status panel.
- Accessibility features: multiple colour themes, high-contrast and monochrome modes, keyboard navigation.
- Robust error handling and session logging.
- Comprehensive in-code documentation and Sphinx-ready docstrings.

### Changed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## [v1.1] - 2025-05-17
### Added
- The Access Point status panel now displays whether NAT is enabled.
- Automatic dependency check on startup to ensure required tools are installed.
- A new menu option in "Service Control" to view the session log.

### Changed
- Refactored the Access Point Profiles menu to be data-driven, improving maintainability.
- Activated dynamic launch options, allowing the operator to enable/disable NAT and use a custom BSSID for each AP launch, with sensible defaults.
- The `start-ap.sh` script now conditionally applies NAT rules based on user selection.
- The `run_bash_script` and `get_interface_details` functions now use `pathlib` for more secure and consistent path handling.

### Fixed
- The `show-ap-stations.sh` and `show-ap-dhcp.sh` scripts now gracefully handle cases where no clients are connected or no leases exist, preventing script errors.
- Corrected a bug in the main exit logic that checked for an incorrect status file path (`/tmp/wapt_ap_active`).
- The screen now clears correctly before stopping an access point for a more consistent UI.
- Improved error logging for the AP status file to prevent silent failures.
- Enhanced error logging in `run_bash_script` to include the full command that failed.

### Security
- Hardened script execution path handling in `run_bash_script` and `get_interface_details` to prevent path traversal issues.

## [Unreleased]
- (Future changes will go here)

## [v1.2] - 2025-05-17
### Added
- A new menu option in "Service Control" to archive the session log.
- A final cleanup routine to remove all temporary files on application exit.

### Changed
- Consolidated seven separate interface management scripts into a single, more robust `interface-ctl.sh` utility.
- Improved logging in the "Service Control" menu to provide a more detailed audit trail of operator actions.

### Fixed
- Resolved a series of complex race conditions in `interface-ctl.sh` to make soft and hard interface resets reliable, especially when `NetworkManager` is active.
- Fixed a bug where `start-ap.sh` was calling old, deleted interface management scripts.
- Fixed a bug in `fn_services.sh` where the `$WEB_ROOT` variable was undefined, preventing the HTTP server from starting.
- The `show-ap-stations.sh` script now gracefully handles cases where the AP is not running, preventing a script failure error.
- Corrected a bug where the "Show DHCP Leases" menu option was calling the wrong script.
