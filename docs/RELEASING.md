# Releasing Email Signature Generator

This guide explains the complete release process for the Email Signature Generator, including version management, building binaries, creating GitHub releases, and Docker image distribution.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Version Management](#version-management)
- [Release Workflow](#release-workflow)
- [Manual Release Process](#manual-release-process)
- [Automated Release with Make](#automated-release-with-make)
- [GitHub Release](#github-release)
- [Docker Release](#docker-release)
- [Post-Release Tasks](#post-release-tasks)
- [Troubleshooting](#troubleshooting)

## Overview

The release process follows these steps:

1. **Version Bump**: Update version number following semantic versioning
2. **Update Changelog**: Document changes in CHANGELOG.md
3. **Build Binaries**: Create executables for all platforms
4. **Create Git Tag**: Tag the release in Git
5. **GitHub Release**: Create release with binaries and notes
6. **Docker Release**: Build and push Docker image
7. **Verify**: Test the release artifacts

## Prerequisites

### Required Tools

- **Git**: For version control and tagging
- **Python 3.13+**: For running scripts
- **PyInstaller**: For building binaries
- **GitHub CLI** (optional): For easier GitHub operations
- **Docker** (optional): For Docker image releases
- **Make**: For using automated release targets

### Required Access

- **GitHub**: Write access to the repository
- **GitHub Token**: Personal access token with `repo` scope
  - Create at: https://github.com/settings/tokens
  - Set as environment variable: `export GITHUB_TOKEN=your_token_here`
- **Docker Hub** (optional): Account for pushing Docker images

### Environment Setup

```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token_here

# Verify tools are installed
python --version
git --version
pyinstaller --version
docker --version  # If using Docker
```

## Version Management

The project uses **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

### Version Format

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.0 → 1.0.1)

### Pre-release Versions

For pre-releases, append a suffix:
- **Alpha**: `1.0.0-alpha.1`
- **Beta**: `1.0.0-beta.1`
- **Release Candidate**: `1.0.0-rc.1`

### Bumping the Version

#### Using Make (Recommended)

```bash
# Display current version
make version

# Bump patch version (1.0.0 → 1.0.1)
make version-bump-patch

# Bump minor version (1.0.0 → 1.1.0)
make version-bump-minor

# Bump major version (1.0.0 → 2.0.0)
make version-bump-major
```

#### Using the Script Directly

```bash
# Bump version
python scripts/bump_version.py patch   # or minor, or major

# Verify the new version
python -c "from src.email_signature.__version__ import __version__; print(__version__)"
```

#### Manual Version Update

Edit `src/email_signature/__version__.py`:

```python
"""Version information for email-signature-generator."""

__version__ = "1.0.1"  # Update this
__version_info__ = tuple(int(x) for x in __version__.split("."))
```

### Version Consistency

The version is stored in a single location (`src/email_signature/__version__.py`) and automatically propagated to:
- `pyproject.toml` (dynamic version)
- CLI `--version` output
- GUI window title
- Binary metadata
- Docker image tags
- Git tags

## Release Workflow

### Quick Release (Using Make)

For a complete release with all steps automated:

```bash
# 1. Bump version
make version-bump-patch  # or minor/major

# 2. Update CHANGELOG.md manually (see below)

# 3. Commit changes
git add src/email_signature/__version__.py CHANGELOG.md
git commit -m "Bump version to $(make version)"

# 4. Run full release process
make release
```

This will:
- Validate the version bump
- Run all tests
- Build binaries for all platforms
- Create Git tag
- Create GitHub release
- Upload binary assets

### Step-by-Step Release

For more control, follow the manual process below.

## Manual Release Process

### Step 1: Prepare the Release

#### 1.1 Create a Release Branch (Optional)

```bash
# Create release branch
git checkout -b release/v1.0.1
```

#### 1.2 Bump the Version

```bash
# Bump version
make version-bump-patch  # or minor/major

# Verify
make version
```

#### 1.3 Update CHANGELOG.md

Add a new section for the release:

```markdown
## [1.0.1] - 2024-01-15

### Added
- New feature X
- New feature Y

### Changed
- Improved performance of Z
- Updated dependency A to version B

### Fixed
- Fixed bug #123: Description
- Fixed issue with feature X

### Security
- Fixed security vulnerability in dependency Y
```

#### 1.4 Run Tests

```bash
# Run all tests
make test

# Run quality checks
make check
```

#### 1.5 Commit Changes

```bash
git add src/email_signature/__version__.py CHANGELOG.md
git commit -m "Bump version to $(make version)"
git push origin release/v1.0.1  # If using release branch
```

### Step 2: Build Binaries

#### 2.1 Build for All Platforms

You need to build on each platform separately (see [Cross-Compilation Limitations](BUILDING.md#cross-compilation-limitations)).

**On Windows:**
```powershell
make build-windows
```

**On macOS:**
```bash
make build-macos
```

**On Linux:**
```bash
make build-linux
```

#### 2.2 Test the Binaries

Test each binary on its target platform:

```bash
# Test CLI
./dist/email-signature --version

# Test GUI
./dist/email-signature-gui
```

#### 2.3 Rename Binaries for Release

```bash
# Get version
VERSION=$(make version)

# Rename binaries with version
# Windows
mv dist/email-signature.exe dist/email-signature-${VERSION}-windows.exe
mv dist/email-signature-gui.exe dist/email-signature-gui-${VERSION}-windows.exe

# macOS
zip -r dist/email-signature-${VERSION}-macos.zip dist/email-signature-gui.app
mv dist/email-signature dist/email-signature-${VERSION}-macos

# Linux
mv dist/email-signature dist/email-signature-${VERSION}-linux-amd64
mv email-signature-generator_*.deb email-signature-generator-${VERSION}-amd64.deb
```

### Step 3: Create Git Tag

```bash
# Get version
VERSION=$(make version)

# Create annotated tag
git tag -a "v${VERSION}" -m "Release version ${VERSION}"

# Push tag to GitHub
git push origin "v${VERSION}"
```

### Step 4: Create GitHub Release

#### Using GitHub CLI (Recommended)

```bash
VERSION=$(make version)

# Create release with binaries
gh release create "v${VERSION}" \
    --title "Release v${VERSION}" \
    --notes-file <(sed -n "/## \[${VERSION}\]/,/## \[/p" CHANGELOG.md | head -n -1) \
    dist/email-signature-${VERSION}-windows.exe \
    dist/email-signature-gui-${VERSION}-windows.exe \
    dist/email-signature-${VERSION}-macos.zip \
    dist/email-signature-${VERSION}-macos \
    dist/email-signature-${VERSION}-linux-amd64 \
    dist/email-signature-generator-${VERSION}-amd64.deb
```

#### Using the Release Script

```bash
# Set GitHub token
export GITHUB_TOKEN=your_token_here

# Run release script
python scripts/create_github_release.py
```

#### Using GitHub Web Interface

1. Go to https://github.com/yourusername/email-signature-generator/releases/new
2. Select the tag you created
3. Set release title: `Release v1.0.1`
4. Copy release notes from CHANGELOG.md
5. Upload binary files
6. Check "This is a pre-release" if applicable
7. Click "Publish release"

### Step 5: Verify the Release

1. **Check GitHub Release**: Visit the releases page and verify:
   - All binaries are attached
   - Release notes are correct
   - Tag is correct

2. **Test Downloads**: Download and test each binary:
   ```bash
   # Download from GitHub
   wget https://github.com/yourusername/email-signature-generator/releases/download/v1.0.1/email-signature-1.0.1-linux-amd64
   
   # Test
   chmod +x email-signature-1.0.1-linux-amd64
   ./email-signature-1.0.1-linux-amd64 --version
   ```

3. **Verify Version**: Ensure version is correct in all artifacts

## Automated Release with Make

The Makefile provides targets for automated releases.

### Available Targets

```bash
# Display current version
make version

# Bump version
make version-bump-patch
make version-bump-minor
make version-bump-major

# Build binaries for all platforms
make build-all

# Prepare release (validate, test, build)
make release-prepare

# Create GitHub release
make release-github

# Full release workflow
make release
```

### Full Automated Release

```bash
# 1. Bump version
make version-bump-patch

# 2. Update CHANGELOG.md manually

# 3. Commit
git add src/email_signature/__version__.py CHANGELOG.md
git commit -m "Release $(make version)"

# 4. Run release
make release
```

This will:
1. Validate version increment
2. Run all tests
3. Build binaries for current platform
4. Create Git tag
5. Push tag to GitHub
6. Create GitHub release
7. Upload binaries

### Platform-Specific Builds

```bash
# Build for specific platform
make build-windows  # On Windows
make build-macos    # On macOS
make build-linux    # On Linux
```

## GitHub Release

### Release Notes Format

Use this template for release notes:

```markdown
## What's New in v1.0.1

### ✨ New Features
- Feature description

### 🐛 Bug Fixes
- Bug fix description

### 🔧 Improvements
- Improvement description

### 📦 Downloads

**Windows**
- [email-signature-1.0.1-windows.exe](link) - CLI version
- [email-signature-gui-1.0.1-windows.exe](link) - GUI version

**macOS**
- [email-signature-1.0.1-macos.zip](link) - GUI application bundle
- [email-signature-1.0.1-macos](link) - CLI version

**Linux**
- [email-signature-1.0.1-linux-amd64](link) - CLI/GUI binary
- [email-signature-generator-1.0.1-amd64.deb](link) - Debian package

**Docker**
```bash
docker pull yourusername/email-signature-generator:1.0.1
```

### 📝 Installation

See the [README](https://github.com/yourusername/email-signature-generator#installation) for installation instructions.

### 🔄 Upgrading

If upgrading from a previous version, simply download and replace the executable.

### 📋 Full Changelog

See [CHANGELOG.md](https://github.com/yourusername/email-signature-generator/blob/main/CHANGELOG.md) for complete details.
```

### Pre-release vs Stable Release

**Pre-release** (alpha, beta, rc):
- Check "This is a pre-release" on GitHub
- Use version suffix: `1.0.0-beta.1`
- Clearly mark in release notes

**Stable Release**:
- Leave "This is a pre-release" unchecked
- Use standard version: `1.0.0`
- Mark as "Latest release"

## Docker Release

### Building Docker Image

```bash
# Build with version tag
make docker-build

# This creates:
# - email-signature-generator:1.0.1
# - email-signature-generator:latest
```

### Testing Docker Image

```bash
# Test the image
docker run --rm email-signature-generator:$(make version) --version

# Test with docker-compose
make docker-run
```

### Pushing to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag for Docker Hub
VERSION=$(make version)
docker tag email-signature-generator:${VERSION} yourusername/email-signature-generator:${VERSION}
docker tag email-signature-generator:latest yourusername/email-signature-generator:latest

# Push
docker push yourusername/email-signature-generator:${VERSION}
docker push yourusername/email-signature-generator:latest
```

### Using Make for Docker Release

```bash
# Build and push
make docker-build
make docker-push
```

## Post-Release Tasks

### 1. Merge Release Branch

If you used a release branch:

```bash
# Merge to main
git checkout main
git merge release/v1.0.1
git push origin main

# Delete release branch
git branch -d release/v1.0.1
git push origin --delete release/v1.0.1
```

### 2. Update Documentation

- Update README.md if needed
- Update any version references in docs
- Update installation instructions if changed

### 3. Announce the Release

- Post on GitHub Discussions
- Update project website
- Notify users via email/social media
- Update package managers (if applicable)

### 4. Monitor for Issues

- Watch for bug reports
- Monitor GitHub issues
- Check download statistics
- Gather user feedback

### 5. Plan Next Release

- Review roadmap
- Prioritize features for next version
- Update project board

## Troubleshooting

### Version Validation Fails

**Problem**: `scripts/validate_version.py` reports version not incremented

**Solution**:
1. Ensure version in `__version__.py` is higher than the last Git tag
2. Check that you've bumped the version correctly
3. Verify no typos in version string

### GitHub Release Creation Fails

**Problem**: Script fails to create GitHub release

**Solution**:
1. Check `GITHUB_TOKEN` is set and valid
2. Verify token has `repo` scope
3. Ensure you have write access to the repository
4. Check network connectivity

### Binary Upload Fails

**Problem**: Binaries fail to upload to GitHub release

**Solution**:
1. Check file sizes (GitHub has a 2GB limit per file)
2. Verify file paths are correct
3. Ensure files exist before upload
4. Check network stability

### Docker Push Fails

**Problem**: Cannot push Docker image

**Solution**:
1. Verify you're logged in: `docker login`
2. Check image name and tag
3. Ensure you have push access to the repository
4. Verify network connectivity

### Missing Binaries

**Problem**: Not all platform binaries are available

**Solution**:
1. Build on each platform separately (no cross-compilation)
2. Use CI/CD with multiple runners
3. Use VMs or cloud services for other platforms

### Tag Already Exists

**Problem**: Git tag already exists

**Solution**:
```bash
# Delete local tag
git tag -d v1.0.1

# Delete remote tag
git push origin :refs/tags/v1.0.1

# Create new tag
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

## Best Practices

### Before Release

- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version is bumped correctly
- [ ] Binaries are tested on target platforms

### During Release

- [ ] Use semantic versioning
- [ ] Create annotated Git tags
- [ ] Write clear release notes
- [ ] Include all platform binaries
- [ ] Test downloads work

### After Release

- [ ] Verify all artifacts are accessible
- [ ] Announce the release
- [ ] Monitor for issues
- [ ] Update documentation
- [ ] Plan next release

## Release Checklist

Use this checklist for each release:

```markdown
## Release Checklist for v1.0.1

### Pre-Release
- [ ] All tests passing
- [ ] Code quality checks passing
- [ ] Version bumped in __version__.py
- [ ] CHANGELOG.md updated
- [ ] Documentation reviewed
- [ ] Changes committed

### Build
- [ ] Windows binary built and tested
- [ ] macOS binary built and tested
- [ ] Linux binary built and tested
- [ ] Docker image built and tested
- [ ] All binaries renamed with version

### Release
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Release notes added
- [ ] All binaries uploaded
- [ ] Docker image pushed
- [ ] Release verified

### Post-Release
- [ ] Release branch merged (if used)
- [ ] Documentation updated
- [ ] Release announced
- [ ] Issues monitored
- [ ] Next release planned
```

## Getting Help

If you encounter issues during the release process:

1. Check this documentation
2. Review [BUILDING.md](BUILDING.md) for build issues
3. Check the [GitHub Issues](https://github.com/yourusername/email-signature-generator/issues)
4. Ask in [GitHub Discussions](https://github.com/yourusername/email-signature-generator/discussions)

---

For information about building binaries, see [BUILDING.md](BUILDING.md).
