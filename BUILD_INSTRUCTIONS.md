# CDST Desktop Application - Build Instructions

## Overview

This document explains how to build the CDST (CoDing Sequence Typer) desktop application for Windows and macOS.

## Quick Start

### Using GitHub Actions (Recommended)

The easiest way to build for multiple platforms is using GitHub Actions:

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for release"
   git push origin main
   ```

2. **Create a release tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Download builds**
   - Go to the repository's "Actions" tab
   - Wait for the build workflow to complete
   - Download artifacts from the release page

## Manual Build Instructions

### Prerequisites

All platforms require:
- Python 3.8 or higher
- pip package manager

### Windows Build

1. **Install Python** (if not already installed)
   - Download from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install dependencies**
   ```cmd
   python -m pip install --upgrade pip
   pip install customtkinter pyinstaller pandas
   ```

3. **Build the executable**
   ```cmd
   python -m PyInstaller --name CDST --windowed --onefile --add-data "src/cdst;cdst" --hidden-import=tkinter --hidden-import=pandas cdst_gui.py
   ```

4. **Find your executable**
   - The built application will be in `dist/CDST.exe`

### macOS Build

1. **Install Python** (if not already installed)
   ```bash
   brew install python@3.11
   ```

2. **Install dependencies**
   ```bash
   python3 -m pip install --upgrade pip
   pip3 install customtkinter pyinstaller pandas
   ```

3. **Build the executable**
   
   For Intel Macs:
   ```bash
   python3 -m PyInstaller --name CDST --windowed --onefile --add-data "src/cdst:cdst" --hidden-import=tkinter --hidden-import=pandas --osx-bundle-identifier=com.cdst.app cdst_gui.py
   ```
   
   For Apple Silicon (M1/M2/M3):
   ```bash
   python3 -m PyInstaller --name CDST --windowed --onefile --add-data "src/cdst:cdst" --hidden-import=tkinter --hidden-import=pandas --osx-bundle-identifier=com.cdst.app cdst_gui.py
   ```

4. **Find your application**
   - The built application will be in `dist/CDST`

### Linux Build

1. **Install Python and dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-tk
   pip3 install customtkinter pyinstaller pandas
   ```

2. **Build the executable**
   ```bash
   python3 -m PyInstaller --name CDST --windowed --onefile --add-data "src/cdst:cdst" --hidden-import=tkinter --hidden-import=pandas cdst_gui.py
   ```

3. **Find your executable**
   - The built application will be in `dist/CDST`

## Using the Build Script

A helper script `build.sh` is included:

```bash
# Show cross-platform build instructions
./build.sh

# Build for current platform only
./build.sh --current

# Show help
./build.sh --help
```

## Distribution

### Windows
- Distribute `CDST.exe` directly
- Users can run it without installing Python

### macOS
- Distribute the `CDST` executable
- Users may need to right-click and select "Open" the first time due to Gatekeeper
- To bypass Gatekeeper warnings, you can sign the app with an Apple Developer certificate

### Linux
- Distribute the `CDST` executable
- Make sure it has execute permissions: `chmod +x CDST`

## Troubleshooting

### Common Issues

**1. Module not found errors**
```bash
# Add hidden imports
--hidden-import=pandas
--hidden-import=tkinter
```

**2. Data files not included**
```bash
# Windows (use semicolon)
--add-data "src/cdst;cdst"

# macOS/Linux (use colon)
--add-data "src/cdst:cdst"
```

**3. App won't start on macOS**
- Right-click the app and select "Open"
- Or run: `xattr -d com.apple.quarantine dist/CDST`

**4. Missing tkinter**
```bash
# Windows
py -m tkinter

# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk
```

## Building for Multiple Platforms from One Machine

Unfortunately, PyInstaller cannot cross-compile. You have these options:

1. **GitHub Actions** (Recommended) - Automatically builds for all platforms
2. **Virtual Machines** - Set up VMs for each target OS
3. **CI/CD Services** - Use Azure Pipelines, CircleCI, etc.
4. **Multiple Physical Machines** - Build on actual hardware

## Version Information

- CDST GUI uses CustomTkinter for modern UI
- PyInstaller creates standalone executables
- Built applications include all dependencies

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review PyInstaller documentation: https://pyinstaller.org
3. Check CustomTkinter documentation: https://customtkinter.tomschimansky.com
