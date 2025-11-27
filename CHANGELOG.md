# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## How to Maintain This Changelog

### Guidelines

- **Add entries under "Unreleased"** for changes that haven't been released yet
- **Move entries to a version section** when creating a new release
- **Use the following categories** for organizing changes:
  - `Added` for new features
  - `Changed` for changes in existing functionality
  - `Deprecated` for soon-to-be removed features
  - `Removed` for now removed features
  - `Fixed` for any bug fixes
  - `Security` for vulnerability fixes

### Version Numbering

Follow Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes or breaking changes
- **MINOR**: New functionality in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

### Example Entry Format

```markdown
## [1.2.3] - 2025-01-15

### Added
- New feature description (#123)

### Fixed
- Bug fix description (#124)
```

---

## [Unreleased]

### Changed
- Replaced proprietary company logo with generic placeholder logo
- Sanitized all documentation to use generic example data (example.com emails, 555-xxxx phone numbers)
- Updated configuration files to use generic English confidentiality text
- Sanitized test data to use fictional/reserved values only

### Security
- Removed proprietary logo from git history using git-filter-repo
- Removed all personally identifiable information (PII) from repository
- Ensured repository is safe for open-source distribution

### Added
- Version management system with semantic versioning support
- PyInstaller build configurations for Windows, macOS, and Linux
- Makefile targets for building platform-specific binaries
- Docker and Docker Compose configurations for containerized deployment
- Release automation scripts for GitHub releases
- Version display in CLI (--version flag) and GUI (window title)
- Automated version bumping scripts (patch, minor, major)

### Changed
- Centralized version management in `src/email_signature/__version__.py`
- Enhanced Makefile with build, Docker, and release targets

---

## [0.1.0] - 2025-11-27

### Added
- Initial release of Email Signature Generator
- GUI interface with Tkinter for interactive signature creation
- CLI interface for command-line signature generation
- Profile management system for saving and loading user configurations
- HTML signature generation with customizable templates
- Logo support with automatic resizing and embedding
- Font customization with fallback support
- Cross-platform compatibility (Windows, macOS, Linux)
- Configuration file support (YAML)
- Comprehensive test suite with unit and property-based tests
- Domain model with clean architecture separation
- Input validation for email addresses, phone numbers, and URLs

### Features
- **Profile Management**: Save, load, and manage multiple signature profiles
- **Logo Integration**: Embed company logos with automatic optimization
- **Customization**: Configurable fonts, colors, and layout options
- **Validation**: Robust input validation for all user data
- **Testing**: Extensive test coverage with Hypothesis property-based testing

---

## Release Links

- [Unreleased]: https://github.com/yourusername/email-signature-generator/compare/v0.1.0...HEAD
- [0.1.0]: https://github.com/yourusername/email-signature-generator/releases/tag/v0.1.0
