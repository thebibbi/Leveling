# Vehicle-Mounted Platform Leveling System

Complete leveling system for roof-mounted and truck-bed mounted platforms (pop-up tents, RTTs) using automatic leveling with inverse kinematics.

## 🎯 Features

- **Two MVP Configurations:**
  - 3-actuator tripod (simpler, lower cost)
  - Stewart platform 3-DOF/6-DOF (higher precision, yaw control)

- **Real-time Leveling:**
  - iPhone IMU streaming for simulation
  - BNO055 sensor for production
  - ±2° accuracy
  - Up to 15-16° compensation

- **ESP32 Control:**
  - 12V DC linear actuators
  - Position feedback
  - Limit switch protection
  - H-bridge motor control

- **3D Visualization:**
  - Real-time simulation
  - Visual feedback
  - Actuator position display

## 📋 System Requirements

### Software
- Python 3.8+
- Libraries: numpy, matplotlib, pyserial
- Optional (hardware IMU): adafruit-circuitpython-bno055, adafruit-blinka
- iOS device with IMU streaming app (for testing)

### Hardware (Production)
- ESP32 microcontroller
- BNO055 9-DOF IMU sensor
- 3 or 6 linear actuators (12V DC)
- H-bridge motor drivers (L298N or similar)
- 12V power supply (vehicle power)
- Position feedback sensors (potentiometer or hall effect)
- Limit switches

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
git clone <repository-url>
cd platform-leveling

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the packaged application (recommended)

Install the project as a Python package to get a single entrypoint that launches
all of the simulation tools:

```bash
# From the project root
pip install .

# Start the guided menu
leveling-app

# Launch the desktop GUI directly (optional)
leveling-app gui

# The same menu can be launched without installing globally
python -m leveling_app
```

Inside the menu you can:

- launch the Tkinter-based GUI,
- launch the 3D visualizer,
- start the interactive leveling-system CLI, or
- switch between platform configurations (tripod, Stewart 3-DOF, Stewart 6-DOF)
  without touching any source files.

For automation you can also run individual tools directly:

```bash
# Open the GUI preconfigured for the tripod platform
leveling-app gui --platform tripod

# Launch the visualizer immediately for a 6-DOF Stewart platform
leveling-app visualizer --platform stewart_6dof

# Start the interactive leveling shell for the tripod configuration
leveling-app system --platform tripod
```

### 3. iPhone IMU Setup (For Testing)

**Option A: Using Sensor Logger App**
1. Download "Sensor Logger" from App Store
2. Configure settings:
   - Enable Gyroscope + Accelerometer
   - Set output format to JSON
   - Set target IP to your computer's IP
   - Set target port to 5555
3. Start streaming

**Option B: Using UDP Sender App**
1. Download "UDP Sender" from App Store
2. Configure to send IMU data as JSON
3. Target your computer's IP:5555

**Find your computer's IP:**
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

### 4. Run Simulation

**3-Actuator Tripod:**
```bash
python platform_visualizer.py tripod
```

**Stewart Platform (3-DOF):**
```bash
python platform_visualizer.py stewart_3dof
```

**Stewart Platform (6-DOF):**
```bash
python platform_visualizer.py stewart_6dof
```

### 5. Controls

In the visualization:
- **[Space]** - Toggle leveling ON/OFF
- **[C]** - Calibrate IMU (set current angle as zero)
- **[Q]** - Quit

### 6. Integrated System (CLI)

Run the complete leveling system with command interface:

```bash
python leveling_system.py tripod
```

Commands:
- `c` - Calibrate IMU
- `a` - Calibrate actuators
- `e` - Enable/disable leveling
- `l` - Level once (manual trigger)
- `auto` - Enable/disable auto-leveling
- `s` - Show status
- `q` - Quit

See `docs/CALIBRATION.md` for detailed calibration procedures.

## 📁 Project Structure

```
platform-leveling/
├── imu_streamer.py          # IMU data receiver (UDP)
├── inverse_kinematics.py    # IK solvers for both configurations
├── esp32_controller.py      # ESP32 controller simulator
├── platform_visualizer.py   # 3D visualization
├── leveling_system.py       # Integrated system
├── platform_leveling_gui.py # Tkinter GUI interface
├── leveling_app/            # CLI launcher package
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py               # Interactive menu
├── requirements.txt         # Python dependencies
├── PlatformLeveling.spec    # PyInstaller build configuration
├── README.md                # This file
├── QUICK_START.md          # Quick start guide for packaged app
├── PACKAGING.md            # Detailed packaging documentation
├── LICENSE                 # MIT license
├── tests/                  # Unit tests
│   └── test_inverse_kinematics.py
└── docs/
    ├── ESP32_FIRMWARE.md    # ESP32 firmware guide
    ├── HARDWARE_SPEC.md     # Hardware specifications
    └── CALIBRATION.md       # Calibration procedures
```

## 🔧 Configuration

Edit `PlatformConfig` in your script:

```python
config = PlatformConfig(
    length=1.83,           # 6 feet in meters
    width=1.22,            # 4 feet in meters
    min_height=0.3,        # 300mm minimum height
    max_height=0.7,        # 700mm maximum height
    actuator_stroke=0.4    # 400mm stroke
)
```

## 📊 Testing the IK Solvers

Test inverse kinematics calculations:

```bash
python inverse_kinematics.py
```

This will output actuator lengths for various orientations.

## 🎮 ESP32 Controller Test

Test the controller simulation:

```bash
python esp32_controller.py
```

## 🔍 Monitoring IMU Data

Monitor raw IMU stream:

```bash
python imu_streamer.py
```

## 📐 Mathematics

### Inverse Kinematics

**3-Actuator Tripod:**
- Define plane with 3 points
- Calculate rotation matrix from roll/pitch
- Solve for actuator lengths using geometry

**Stewart Platform:**
- 6 actuators in hexagonal pattern
- Full 6-DOF capability (position + orientation)
- Rotation matrix: R = Rz · Ry · Rx

For each actuator:
```
L_i = ||P_i - B_i||
```
Where:
- `L_i` = actuator length
- `P_i` = platform attachment point (rotated)
- `B_i` = base attachment point (fixed)

Platform point transformation:
```
P_i = R · (P_i0 - center) + center
```

## 🛠️ Troubleshooting

### IMU not receiving data
1. Check firewall settings (allow UDP port 5555)
2. Verify computer IP address
3. Ensure iPhone and computer on same network
4. Check iPhone app settings

### Visualization not updating
1. Ensure IMU app is actively streaming
2. Check console for error messages
3. Try recalibrating with 'c' key

### Actuators not moving
1. Check if leveling is enabled (press 'e')
2. Verify targets are within limits
3. Check emergency stop status

## 📝 Next Steps

### For Production Deployment:

1. **Hardware Assembly:**
   - Mount actuators at calculated positions
   - Install BNO055 IMU on platform
   - Wire ESP32 and H-bridges
   - Connect limit switches

2. **ESP32 Firmware:**
   - Port controller logic to C++
   - Implement serial protocol
   - Add safety features
   - Test with real hardware

3. **Calibration:**
   - Run actuator calibration routine
   - Set IMU offsets
   - Test full range of motion
   - Verify safety limits

4. **User Interface:**
   - Add physical button for leveling
   - Optional: Bluetooth app control
   - Status LED indicators

## 🔐 Safety Features

- Emergency stop function
- Actuator limit switches (hardware + software)
- Current monitoring
- Position validation before movement
- Tilt angle limits

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review hardware specifications
3. Test individual components
4. Consult the calibration guide in `docs/CALIBRATION.md`

## 🗂️ Packaging into a One-Click Application

Create a standalone macOS app launcher that bundles all simulation tools into a single application.

> **✅ Threading Issue Fixed:** The GUI now uses Tkinter's `after()` method for thread-safe updates, preventing GIL-related crashes when closing windows.

### Building the Application

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Clean previous builds (optional)
rm -rf build dist

# Build the application
pyinstaller PlatformLeveling.spec
```

### Using the Packaged Application

After the build completes, you can launch the application in two ways:

**Option 1: Double-click in Finder**
- Navigate to `dist/PlatformLeveling.app` in Finder
- Double-click to launch the application
- A terminal window will open with an interactive menu

**Option 2: Command Line**
```bash
open dist/PlatformLeveling.app
```

### Interactive Menu Options

The packaged app provides a guided menu interface with the following options:

1. **Launch graphical interface (GUI)** - Opens the Tkinter-based GUI with real-time 3D visualization
2. **Launch 3D visualizer** - Opens the matplotlib-based 3D platform visualizer
3. **Launch leveling system CLI** - Opens the interactive leveling system command-line interface
4. **Change platform type** - Switch between tripod, stewart_3dof, and stewart_6dof configurations
5. **Quit** - Exit the application

### Distribution

The `dist/PlatformLeveling.app` bundle is self-contained and can be:
- Copied to other macOS machines (same architecture)
- Distributed to users without Python installed
- Placed in the Applications folder

**Note:** The build warnings about missing Windows modules (e.g., `winreg`, `nt`) are expected and can be ignored on macOS. Optional BNO055 IMU libraries are also listed as warnings but don't prevent the app from functioning with the iPhone IMU fallback.

## 📄 License

Licensed under the MIT License. See `LICENSE` for details.

## 🙏 Acknowledgments

Built with:
- NumPy for mathematical operations
- Matplotlib for visualization
- PySerial for ESP32 communication
