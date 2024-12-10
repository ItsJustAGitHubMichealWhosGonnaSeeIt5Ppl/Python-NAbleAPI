# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
 