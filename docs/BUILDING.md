# Building Email Signature Generator

This guide explains how to build standalone executables for the Email Signature Generator on Windows, macOS, and Linux.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building on Windows](#building-on-windows)
- [Building on macOS](#building-on-macos)
- [Building on Linux](#building-on-linux)
- [Cross-Compilation Limitations](#cross-compilation-limitations)
- [Build Configuration](#build-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### All Platforms

Before building, ensure you have:

1. **Python 3.13 or higher** installed
2. **Git** for cloning the repository
3. **uv** package manager (recommended) or pip
4. **PyInstaller** for creating executables

### Install PyInstaller

```bash
# Using uv (recommended)
uv add --dev pyinstaller

# Or using pip
pip install pyinstaller
```

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/email-signature-generator.git
cd email-signature-generator

# Install dependencies
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Building on Windows

### Windows-Specific Prerequisites

- **Windows 10 or later** (64-bit recommended)
- **Visual C++ Redistributable** (usually already installed)
- **PyInstaller** 6.0 or later

### Build Commands

#### Using Make (if you have Make installed)

```powershell
# Build both CLI and GUI executables
make build-windows
```

#### Using PyInstaller Directly

```powershell
# Build CLI executable
pyinstaller build/pyinstaller/email-signature.spec

# Build GUI executable
pyinstaller build/pyinstaller/email-signature-gui.spec
```

### Output Location

Built executables will be in:
- `dist/email-signature.exe` - CLI version
- `dist/email-signature-gui.exe` - GUI version

### Windows Build Notes

- **Console Window**: The CLI version shows a console window; the GUI version hides it
- **Icon**: The build process embeds `logo.png` as the executable icon
- **Size**: Expect executables around 30-50 MB each
- **Dependencies**: All Python dependencies and DLLs are bundled
- **Antivirus**: Some antivirus software may flag PyInstaller executables as suspicious (false positive)

### Testing the Windows Build

```powershell
# Test CLI version
.\dist\email-signature.exe --version

# Test GUI version (double-click or run from command line)
.\dist\email-signature-gui.exe
```

## Building on macOS

### macOS-Specific Prerequisites

- **macOS 10.15 (Catalina) or later**
- **Xcode Command Line Tools**: `xcode-select --install`
- **PyInstaller** 6.0 or later
- **Python-tk**: `brew install python-tk@3.13` (if using Homebrew Python)

### Build Commands

#### Using Make

```bash
# Build both CLI and GUI executables
make build-macos
```

#### Using PyInstaller Directly

```bash
# Build CLI executable
pyinstaller build/pyinstaller/email-signature.spec

# Build GUI executable
pyinstaller build/pyinstaller/email-signature-gui.spec
```

### Output Location

Built executables will be in:
- `dist/email-signature` - CLI version (Unix executable)
- `dist/email-signature-gui.app` - GUI version (macOS application bundle)

### macOS Build Notes

- **Application Bundle**: The GUI version is packaged as a `.app` bundle
- **Code Signing**: Unsigned by default; see [Code Signing](#code-signing-macos) for distribution
- **Gatekeeper**: Users may need to right-click and select "Open" the first time
- **Universal Binary**: By default, builds for the current architecture (Intel or Apple Silicon)
- **Size**: Expect executables around 35-55 MB

### Code Signing (macOS)

For distribution outside the App Store, you should sign your application:

```bash
# Sign the application
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/email-signature-gui.app

# Verify signature
codesign --verify --verbose dist/email-signature-gui.app

# Notarize for Gatekeeper (requires Apple Developer account)
xcrun notarytool submit dist/email-signature-gui.app.zip --apple-id developer@example.com --team-id TEAMID --password app-specific-password
```

### Testing the macOS Build

```bash
# Test CLI version
./dist/email-signature --version

# Test GUI version
open dist/email-signature-gui.app
```

## Building on Linux

### Linux-Specific Prerequisites

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    python3.13 \
    python3.13-venv \
    python3-tk \
    fonts-dejavu \
    fonts-liberation \
    ruby \
    ruby-dev \
    build-essential

# Install fpm for .deb package creation
sudo gem install fpm
```

#### Fedora/RHEL

```bash
sudo dnf install -y \
    python3.13 \
    python3-tkinter \
    dejavu-sans-fonts \
    liberation-fonts \
    ruby \
    ruby-devel \
    gcc \
    rpm-build

# Install fpm
sudo gem install fpm
```

#### Arch Linux

```bash
sudo pacman -S \
    python \
    tk \
    ttf-dejavu \
    ttf-liberation \
    ruby \
    base-devel

# Install fpm
sudo gem install fpm
```

### Build Commands

#### Using Make

```bash
# Build both CLI and GUI executables plus .deb package
make build-linux
```

#### Using PyInstaller Directly

```bash
# Build CLI executable
pyinstaller build/pyinstaller/email-signature.spec

# Build GUI executable
pyinstaller build/pyinstaller/email-signature-gui.spec

# Create .deb package (requires fpm)
fpm -s dir -t deb \
    -n email-signature-generator \
    -v $(python -c "from src.email_signature.__version__ import __version__; print(__version__)") \
    --prefix /opt/email-signature-generator \
    --description "Professional email signature generator" \
    --url "https://github.com/yourusername/email-signature-generator" \
    --license MIT \
    dist/email-signature=/opt/email-signature-generator/bin/email-signature \
    dist/email-signature-gui=/opt/email-signature-generator/bin/email-signature-gui
```

### Output Location

Built executables will be in:
- `dist/email-signature` - CLI version
- `dist/email-signature-gui` - GUI version
- `email-signature-generator_*.deb` - Debian package (if fpm is used)

### Linux Build Notes

- **Shared Libraries**: All required shared libraries are bundled
- **Display Server**: GUI requires X11 or Wayland
- **Fonts**: Include DejaVu or Liberation fonts for best results
- **Permissions**: Make executables executable: `chmod +x dist/email-signature*`
- **Size**: Expect executables around 30-50 MB

### Creating Distribution Packages

#### Debian/Ubuntu (.deb)

The Makefile target `build-linux` automatically creates a `.deb` package using fpm.

To install the package:

```bash
sudo dpkg -i email-signature-generator_*.deb
```

#### RPM-based Distributions

```bash
# Create RPM package
fpm -s dir -t rpm \
    -n email-signature-generator \
    -v $(python -c "from src.email_signature.__version__ import __version__; print(__version__)") \
    --prefix /opt/email-signature-generator \
    dist/email-signature=/opt/email-signature-generator/bin/email-signature \
    dist/email-signature-gui=/opt/email-signature-generator/bin/email-signature-gui
```

### Testing the Linux Build

```bash
# Make executable
chmod +x dist/email-signature dist/email-signature-gui

# Test CLI version
./dist/email-signature --version

# Test GUI version
./dist/email-signature-gui
```

## Cross-Compilation Limitations

**Important**: PyInstaller does not support cross-compilation. You must build on the target platform.

### What This Means

- **Windows binaries** must be built on Windows
- **macOS binaries** must be built on macOS
- **Linux binaries** must be built on Linux

### Workarounds

If you need to build for multiple platforms, you have several options:

#### 1. Use Multiple Machines

Build on separate machines for each platform:
- Windows PC for Windows builds
- Mac for macOS builds
- Linux machine for Linux builds

#### 2. Use Virtual Machines

Set up VMs for each platform:
- **Windows**: Use VirtualBox or VMware
- **macOS**: Use VMware Fusion (on Mac) or cloud services
- **Linux**: Use VirtualBox, VMware, or WSL2

#### 3. Use CI/CD Services

Use GitHub Actions or similar services that provide runners for all platforms:

```yaml
# .github/workflows/build.yml
name: Build Binaries

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install pyinstaller
          pip install -e .
      - name: Build
        run: make build-${{ matrix.os }}
```

#### 4. Use Docker for Linux Builds

You can build Linux binaries on macOS or Windows using Docker:

```bash
# Build Linux binary in Docker container
docker run --rm -v $(pwd):/app python:3.13-slim bash -c "
    cd /app && \
    apt-get update && \
    apt-get install -y python3-tk fonts-dejavu && \
    pip install pyinstaller && \
    pip install -e . && \
    pyinstaller build/pyinstaller/email-signature.spec
"
```

### Architecture Considerations

- **Intel vs ARM**: Builds are architecture-specific
- **macOS**: Build on Apple Silicon for ARM, Intel for x86_64
- **Linux**: Build on the target architecture (amd64, arm64, etc.)
- **Windows**: Typically x86_64 (64-bit)

## Build Configuration

### PyInstaller Spec Files

The build process uses spec files located in `build/pyinstaller/`:

- `email-signature.spec` - CLI version configuration
- `email-signature-gui.spec` - GUI version configuration

### Customizing the Build

You can modify the spec files to customize the build:

#### Adding Data Files

```python
datas=[
    ('../../config', 'config'),
    ('../../logo.png', '.'),
    ('../../fonts', 'fonts'),  # Add custom fonts
],
```

#### Adding Hidden Imports

```python
hiddenimports=[
    'PIL._tkinter_finder',
    'email.mime.text',  # Add if needed
],
```

#### Excluding Modules

```python
excludes=[
    'matplotlib',  # Exclude unused modules
    'numpy',
],
```

#### One-File vs One-Folder

By default, builds use one-file mode. To use one-folder:

```python
# In the EXE() section
exe = EXE(
    # ... other parameters ...
    onefile=False,  # Change to False for one-folder
)
```

### Build Optimization

#### Reduce Binary Size

1. **Exclude unused modules**:
   ```python
   excludes=['matplotlib', 'numpy', 'pandas']
   ```

2. **Use UPX compression** (already enabled):
   ```python
   upx=True
   ```

3. **Strip debug symbols** (Linux/macOS):
   ```bash
   strip dist/email-signature
   ```

#### Improve Startup Time

1. Use one-folder mode instead of one-file
2. Exclude unnecessary modules
3. Optimize imports in your code

## Troubleshooting

### Common Build Issues

#### "Module not found" errors

**Problem**: PyInstaller can't find a module

**Solution**: Add to `hiddenimports` in the spec file:
```python
hiddenimports=['missing_module_name'],
```

#### "Failed to execute script" errors

**Problem**: Runtime error in the built executable

**Solution**: 
1. Test with `--debug` flag: `pyinstaller --debug all your.spec`
2. Check for hardcoded paths in your code
3. Ensure all data files are included in `datas`

#### Tkinter not found

**Problem**: GUI won't start due to missing Tkinter

**Solution**:
- **Windows**: Reinstall Python with Tkinter enabled
- **macOS**: `brew install python-tk@3.13`
- **Linux**: `sudo apt install python3-tk`

#### Large executable size

**Problem**: Executable is larger than expected

**Solution**:
1. Exclude unused modules in spec file
2. Use UPX compression
3. Consider one-folder mode
4. Remove unnecessary dependencies from `pyproject.toml`

#### Antivirus false positives (Windows)

**Problem**: Antivirus flags the executable

**Solution**:
1. This is common with PyInstaller executables
2. Submit to antivirus vendors as false positive
3. Consider code signing the executable
4. Use VirusTotal to verify it's a false positive

### Platform-Specific Issues

#### Windows: Missing DLL errors

**Solution**: Install Visual C++ Redistributable

#### macOS: "App is damaged" message

**Solution**: 
```bash
# Remove quarantine attribute
xattr -cr dist/email-signature-gui.app
```

#### Linux: Missing shared libraries

**Solution**:
```bash
# Check missing libraries
ldd dist/email-signature

# Install missing libraries
sudo apt install <missing-library>
```

### Getting Help

If you encounter issues not covered here:

1. Check the [PyInstaller documentation](https://pyinstaller.org/en/stable/)
2. Search [PyInstaller issues](https://github.com/pyinstaller/pyinstaller/issues)
3. Open an issue in this repository with:
   - Your platform and Python version
   - Complete error message
   - Steps to reproduce

## Next Steps

After building successfully:

1. **Test the executable** thoroughly on the target platform
2. **Create a release** - see [RELEASING.md](RELEASING.md)
3. **Distribute** - upload to GitHub releases or your distribution channel

---

For information about creating releases, see [RELEASING.md](RELEASING.md).
