# Calibration Procedures

This document describes the calibration workflows for the vehicle-mounted platform leveling system. Perform these steps after assembling the hardware and before running the leveling routines in production.

## IMU Calibration

1. Power on the leveling control system and the IMU sensor (BNO055 or iPhone test source).
2. Place the platform on a surface known to be level.
3. Launch the leveling system CLI (`leveling_app system --platform tripod` or your preferred platform).
4. Issue the `c` command to trigger IMU calibration.
5. Wait for confirmation that offsets have been stored.

### Troubleshooting
- If the IMU output appears unstable, verify power and wiring.
- For the BNO055, ensure that the sensor has reached full calibration status (system/gyro/acc/mag = 3).

## Actuator Calibration

1. Ensure the actuators have unobstructed travel over their full stroke.
2. From the leveling CLI, issue the `a` command to start calibration.
3. The actuators will retract to their minimum length and set that position as the zero reference.
4. Wait for the calibration routine to complete (the CLI shows "Actuators calibrated").

### Notes
- Each actuator should have functional limit switches; the calibration routine assumes they will stop travel at mechanical limits.
- If the actuators do not move, confirm that power and the ESP32 controller are enabled.

## Platform Zeroing

1. After calibrating the IMU and actuators, keep the platform on the level surface.
2. Enable leveling (`e` command) and run a manual leveling cycle (`l` command) to confirm zero offsets.
3. Inspect the IMU readings (`s` command) to verify roll/pitch are near 0°.

## Periodic Recalibration

- Re-run IMU calibration whenever the sensor is remounted or subjected to large temperature swings.
- Re-run actuator calibration if mechanical components are serviced or replaced.
- Store logs in the `logs/` directory created by `setup.sh` for maintenance history.
