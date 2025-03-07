# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.9] - 2025-01-10

### Added

### Fixed

- Experimental EDR check causing error if no checks are present on device.

### Changed

### Removed

## [0.0.8] 2025-01-06
 
### Added

- Response formatter, allowing more consistent responses in data
- Toggle to init for using new response data
- Session for requests

### Fixed

- EDRPresent not detecting devices with EDR checks.

### Changed

- Response line for all methods
- Reponse for clientDevice when include details is enabled

### Removed

## [0.0.7] - 2024-12-19

### Added

### Fixed

- Issue with experimental EDR check when software was returned as None

### Changed

### Removed

## [0.0.6] - 2024-12-17

### Added

- Format handling for guids (mav), details (mav), and av type (mav)
- MAV Endpoints and docstrings
- Missing endpoints to Readme.md

### Fixed

- Status handling for MAV responses, as some use FAIL
- Missing describe param in docstrings for a few endpoints

### Changed

### Removed

## [0.0.5] - 2024-12-16

### Added

- Link to documentation in workstations docstring.
- assetHardware, assetSoftware, licenseGroups, licenseGroupItems, clientLicenseCount, assetDetails, edrPresent methods
- docstring for addSite, assetHardware, assetSoftware, licenseGroups, licenseGroupItems, clientLicenseCount, assetDetails, edrPresent
- experimentalChecks toggle for clientDevices and deviceDetails
- Experimental checks section under device details in documentation.

### Fixed

- Missing and incorrect information documentation for sites, clients, and workstations.
- Issue with clients response if describe was set to True and a name was still sent.

### Changed

- Tested addSite method.
- docstring for listPatches to include more IDs


### Removed


## [0.0.4] - 2024-12-13

### Added

- Windows Patch Management endpoints
- docstring for all Windows Patch Management endpoints
- ReadTheDocs page for Windows Patch Management

### Fixed

### Changed

- Formatter can now handle patch IDs sent as a list, or a string.

### Removed


## [0.0.3] - 2024-12-10

### Added

- Changelog
- Basic client search function
- addClient function.
- Docstring for addClient, wallchartSettings, generalSettings, listPatches

### Fixed

- Possible error when response content does not contain 'result' key.
- listPatches response formatting
 
### Changed

- Updated docstring for _formatter, clients, workstations, templates, backupHistory
- index.RST to add home page
- Updated readme.md with new working endpoints (incomplete)
 
### Removed

- searchClient placeholder (integrating into clients)
 
## [0.0.0] - Template

### Added

### Fixed

### Changed

### Removed