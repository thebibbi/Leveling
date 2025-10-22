# Packaging Guide for Platform Leveling System

This document provides detailed instructions for packaging the Platform Leveling System as a standalone macOS application.

## Overview

The Platform Leveling System can be packaged into a single-click `.app` bundle using PyInstaller. This bundle includes:
- Interactive CLI menu launcher
- Tkinter-based GUI with 3D visualization
- Matplotlib-based 3D visualizer
- Leveling system command-line interface
- All Python dependencies and libraries

## Prerequisites

- macOS operating system (tested on macOS 15.6.1 arm64)
- Python 3.8 or later
- PyInstaller 6.0 or later
- All project dependencies installed

## Building the Application

### Step 1: Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### Step 2: Clean Previous Builds (Optional)

```bash
# Remove old build artifacts
rm -rf build dist
```

### Step 3: Build the Package

```bash
# Run PyInstaller with the spec file
pyinstaller PlatformLeveling.spec --clean
```

The build process will:
- Analyze all Python dependencies
- Bundle required libraries
- Create a standalone executable
- Package everything into a macOS `.app` bundle

### Step 4: Verify the Build

The completed application will be located at:
```
dist/PlatformLeveling.app
```

## Understanding the Build Output

### Expected Warnings

The build process will generate warnings in `build/PlatformLeveling/warn-PlatformLeveling.txt`. Most warnings are harmless:

**Windows-specific modules** (safe to ignore on macOS):
- `winreg`, `nt`, `_winapi`, `msvcrt`
- These are Windows-only modules that aren't needed on macOS

**Optional hardware libraries** (safe to ignore if not using BNO055):
- `board`, `busio`, `adafruit_bno055`
- The system falls back to iPhone IMU streaming if these aren't available

**Platform-specific imports**:
- `vms_lib`, `java.lang`, `_wmi`
- Optional modules for other operating systems

### Build Statistics

A successful build will show:
- **Analysis time**: ~10-15 seconds
- **Build time**: ~30-40 seconds
- **Output size**: ~150-200 MB (includes Python runtime and all dependencies)

## Running the Packaged Application

### Method 1: Finder (Double-Click)

1. Open Finder
2. Navigate to `dist/`
3. Double-click `PlatformLeveling.app`
4. A terminal window opens with the interactive menu

### Method 2: Command Line

```bash
# Open the application
open dist/PlatformLeveling.app

# Or run the executable directly
./dist/PlatformLeveling.app/Contents/MacOS/PlatformLeveling
```

## Distribution

### Sharing the Application

The packaged `.app` can be distributed by:
1. Copying the entire `PlatformLeveling.app` folder
2. Creating a DMG disk image
3. Compressing to a ZIP archive

### System Requirements

Recipients will need:
- macOS 11.0 or later (Big Sur or newer)
- Same CPU architecture (arm64 for Apple Silicon, x86_64 for Intel)
- No Python installation required!

### Installation on User Machines

Users can:
1. Copy `PlatformLeveling.app` to `/Applications` folder
2. Launch from Spotlight or Launchpad
3. Run directly from any folder

## Troubleshooting

### Build Fails with Missing Module

**Problem**: PyInstaller can't find a required module

**Solution**:
1. Install the missing module: `pip install <module-name>`
2. Add it to `hiddenimports` in `PlatformLeveling.spec` if needed
3. Rebuild with `--clean` flag

### App Won't Open / Crashes on Launch

**Problem**: The app crashes immediately when opened

**Solution**:
1. Run from terminal to see error messages:
   ```bash
   ./dist/PlatformLeveling.app/Contents/MacOS/PlatformLeveling
   ```
2. Check for missing dependencies in the error output
3. Verify all project modules are properly bundled

### "App is Damaged" Message

**Problem**: macOS says the app is damaged or can't be verified

**Solution**:
```bash
# Remove quarantine attribute
xattr -cr dist/PlatformLeveling.app
```

### GUI/Visualizer Doesn't Open

**Problem**: Menu launches but GUI options fail

**Solution**:
1. Verify matplotlib backend in `PlatformLeveling.spec`:
   ```python
   hiddenimports=[
       'matplotlib.backends.backend_tkagg',
       'matplotlib.backends.backend_qt5agg',
   ]
   ```
2. Rebuild the package

## Advanced Customization

### Adding an Icon

1. Create or obtain an `.icns` file
2. Update `PlatformLeveling.spec`:
   ```python
   app = BUNDLE(
       exe,
       name='PlatformLeveling.app',
       icon='path/to/icon.icns',
       bundle_identifier=None,
   )
   ```

### Reducing App Size

Add to `excludes` in `PlatformLeveling.spec`:
```python
excludes=[
    'tkinter.test',
    'test',
    'unittest',
    'distutils',
],
```

### Creating a Universal Binary (arm64 + x86_64)

This requires building on both architectures and using `lipo` to merge:
```bash
# Build on arm64 Mac
pyinstaller PlatformLeveling.spec

# Build on x86_64 Mac
pyinstaller PlatformLeveling.spec

# Merge binaries (advanced)
lipo -create arm64/PlatformLeveling x86_64/PlatformLeveling \
     -output universal/PlatformLeveling
```

## Packaging Spec File Details

The `PlatformLeveling.spec` file configures the build:

- **Entry point**: `leveling_app/cli.py` - the main menu interface
- **Path**: `.` - adds project root to Python path
- **Data files**: Includes `inverse_kinematics.py` and `imu_streamer_http.py`
- **Hidden imports**: matplotlib backends for GUI support
- **Console**: `True` - enables terminal output for the menu
- **Bundle**: Creates macOS `.app` package

## Testing the Package

Before distribution, test all functionality:

1. **Menu navigation**: Verify all menu options work
2. **GUI launch**: Test the Tkinter interface opens
3. **Visualizer**: Check matplotlib 3D view launches
4. **CLI system**: Verify leveling system commands work
5. **Platform switching**: Test changing between platform types

## Maintenance

### Updating the Package

After code changes:
```bash
# Rebuild with clean flag
pyinstaller PlatformLeveling.spec --clean
```

### Version Management

Update version in:
- `pyproject.toml` - package version
- `PlatformLeveling.spec` - can add version to name

### Automated Builds

Consider using CI/CD (GitHub Actions) for automated packaging:
- Build on push/tag
- Generate release artifacts
- Create DMG images automatically

## Support

For packaging issues:
1. Check `build/PlatformLeveling/warn-PlatformLeveling.txt` for warnings
2. Review `build/PlatformLeveling/xref-PlatformLeveling.html` for dependencies
3. Run with `--debug all` flag for verbose output
4. Consult PyInstaller documentation: https://pyinstaller.org/

## References

- PyInstaller Documentation: https://pyinstaller.org/en/stable/
- macOS App Bundle Structure: https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/
- Code Signing Guide: https://developer.apple.com/support/code-signing/
