# Quick Start Guide - Platform Leveling System

## 🚀 Launching the One-Click Application

### Option 1: Double-Click in Finder (Recommended)
1. Navigate to the `dist/` folder
2. Double-click `PlatformLeveling.app`
3. A terminal window will open with the interactive menu

### Option 2: Command Line
```bash
# From the project directory
open dist/PlatformLeveling.app
```

## 📱 Interactive Menu

When you launch the app, you'll see:

```
============================================================
Platform Leveling Application
============================================================
Current platform: tripod

Select an option:
  1) Launch graphical interface (GUI)
  2) Launch 3D visualizer
  3) Launch leveling system CLI
  4) Change platform type
  5) Quit
Enter choice [1-5]:
```

### Menu Options

**Option 1: Graphical Interface (GUI)**
- Opens a Tkinter-based GUI with real-time 3D visualization
- Shows IMU data (roll, pitch, yaw, tilt)
- Displays actuator positions
- Interactive 3D platform view
- Enable/disable leveling with a button

**Option 2: 3D Visualizer**
- Opens matplotlib-based 3D platform visualizer
- Real-time platform orientation display
- Keyboard controls:
  - `Space`: Toggle leveling ON/OFF
  - `c`: Calibrate (set current angle as zero)
  - `q`: Quit

**Option 3: Leveling System CLI**
- Command-line interface for the leveling system
- Commands:
  - `c`: Calibrate IMU
  - `a`: Calibrate actuators
  - `e`: Enable/disable leveling
  - `l`: Level once (manual trigger)
  - `auto`: Enable/disable auto-leveling
  - `s`: Show status
  - `q`: Quit

**Option 4: Change Platform Type**
- Switch between configurations:
  - `tripod`: 3-actuator tripod platform
  - `stewart_3dof`: 6-actuator Stewart platform (3 DOF)
  - `stewart_6dof`: 6-actuator Stewart platform (6 DOF)

**Option 5: Quit**
- Exit the application

## 🔧 Rebuilding the Application

If you make code changes, rebuild the app:

```bash
# Clean old builds
rm -rf build dist

# Rebuild
pyinstaller PlatformLeveling.spec --clean
```

The new app will be in `dist/PlatformLeveling.app`.

## 🐛 Bug Fixes Applied

### Threading Issue (Fixed)
**Problem**: GUI crashed with GIL (Global Interpreter Lock) error when closing
**Solution**: Changed from background thread to Tkinter's `after()` method for thread-safe GUI updates

**Error was:**
```
Fatal Python error: PyEval_RestoreThread: the function must be called with the GIL held
```

**Fix applied in:** `platform_leveling_gui.py`
- Removed background thread that directly modified GUI widgets
- Implemented `_schedule_update()` using `root.after(50, _update_loop)`
- All GUI updates now happen on the main thread

## 📍 iPhone IMU Setup

All three options use iPhone as IMU source (for testing):

1. **Install IMU app on iPhone:**
   - Download "Sensor Logger" or similar IMU streaming app
   
2. **Configure the app:**
   - Set target IP to your Mac's IP address
   - Set target port to `5555`
   - Enable accelerometer and gyroscope streaming

3. **Start streaming:**
   - Launch the streaming app on iPhone
   - Start the Platform Leveling app on Mac
   - Data should connect automatically

## ✅ Verification

Test all features work:
- [x] Menu launches and accepts input
- [x] GUI opens without crashing
- [x] 3D visualizer displays
- [x] CLI system accepts commands
- [x] Platform type switching works
- [x] Closing windows doesn't crash

## 📦 Distribution

To share the app:
1. Copy `dist/PlatformLeveling.app` to another Mac
2. Recipients don't need Python installed
3. Works on macOS 11.0+ (same architecture)

## 🆘 Troubleshooting

### App Won't Open
```bash
# Remove quarantine attribute if macOS blocks it
xattr -cr dist/PlatformLeveling.app
```

### See Error Messages
```bash
# Run from terminal to see console output
./dist/PlatformLeveling.app/Contents/MacOS/PlatformLeveling
```

### GUI Crashes
- **Fixed in latest build** - rebuild if using old version
- The threading fix prevents GIL errors on window close

### IMU Not Connecting
- Verify iPhone and Mac are on same network
- Check iPhone streaming app is running
- Confirm port 5555 is not blocked by firewall

## 📚 More Information

- Full documentation: `README.md`
- Packaging details: `PACKAGING.md`
- Calibration procedures: `docs/CALIBRATION.md`
- Hardware specs: `docs/HARDWARE_SPEC.md`
- ESP32 firmware: `docs/ESP32_FIRMWARE.md`
