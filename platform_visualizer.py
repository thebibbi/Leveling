"""
3D Visualization of Platform Leveling
Real-time visualization using matplotlib with iPhone IMU data
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches
from typing import Optional
import time

from imu_streamer import IMUStreamer, IMUData
from inverse_kinematics import TripodIK, StewartPlatformIK, PlatformConfig


class PlatformVisualizer:
    """
    Real-time 3D visualization of platform leveling
    """
    
    def __init__(self, platform_type: str = 'tripod', config: Optional[PlatformConfig] = None):
        """
        Args:
            platform_type: 'tripod' or 'stewart_3dof' or 'stewart_6dof'
            config: Platform configuration
        """
        if config is None:
            # Default configuration: 4'x6' platform
            config = PlatformConfig(
                length=1.83,  # 6 feet
                width=1.22,   # 4 feet
                min_height=0.3,
                max_height=0.7,
                actuator_stroke=0.4
            )
        
        self.config = config
        self.platform_type = platform_type
        
        # Initialize inverse kinematics solver
        if platform_type == 'tripod':
            self.ik_solver = TripodIK(config)
        elif platform_type == 'stewart_3dof':
            self.ik_solver = StewartPlatformIK(config, dof_mode='3DOF')
        elif platform_type == 'stewart_6dof':
            self.ik_solver = StewartPlatformIK(config, dof_mode='6DOF')
        else:
            raise ValueError(f"Unknown platform type: {platform_type}")
        
        # IMU streamer
        self.imu_streamer = IMUStreamer()
        
        # Leveling control
        self.leveling_enabled = False
        self.last_imu_data: Optional[IMUData] = None
        
        # Setup visualization
        self.fig = plt.figure(figsize=(14, 8))
        self.ax_3d = self.fig.add_subplot(121, projection='3d')
        self.ax_info = self.fig.add_subplot(122)
        
        # Storage for animation data
        self.actuator_lengths = None
        self.current_orientation = [0, 0, 0]  # roll, pitch, yaw
        
        self._setup_plot()
        
        print(f"\n{'='*60}")
        print(f"Platform Visualizer - {platform_type.upper()}")
        print(f"{'='*60}")
        print("\nControls:")
        print("  Space: Toggle leveling ON/OFF")
        print("  'c': Calibrate (set current angle as zero)")
        print("  'q': Quit")
        print(f"{'='*60}\n")
    
    def _setup_plot(self):
        """Setup 3D plot axes and styling"""
        # 3D view setup
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        self.ax_3d.set_title(f'{self.platform_type.upper()} Platform')
        
        # Set axis limits
        max_dim = max(self.config.length, self.config.width) / 2 * 1.5
        self.ax_3d.set_xlim([-max_dim, max_dim])
        self.ax_3d.set_ylim([-max_dim, max_dim])
        self.ax_3d.set_zlim([0, self.config.max_height * 1.5])
        
        # Equal aspect ratio
        self.ax_3d.set_box_aspect([1, 1, 0.7])
        
        # Info panel setup
        self.ax_info.axis('off')
        
        # Key bindings
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
    
    def _on_key_press(self, event):
        """Handle keyboard input"""
        if event.key == ' ':
            self.leveling_enabled = not self.leveling_enabled
            status = "ENABLED" if self.leveling_enabled else "DISABLED"
            print(f"\nLeveling: {status}")
        elif event.key == 'c':
            self.imu_streamer.calibrate()
        elif event.key == 'q':
            plt.close()
    
    def _draw_platform(self, roll: float, pitch: float, yaw: float,
                       actuator_lengths: np.ndarray):
        """Draw the platform and actuators in 3D"""
        self.ax_3d.clear()
        
        # Reconfigure axis (clearing removes settings)
        self.ax_3d.set_xlabel('X (m)')
        self.ax_3d.set_ylabel('Y (m)')
        self.ax_3d.set_zlabel('Z (m)')
        self.ax_3d.set_title(f'{self.platform_type.upper()} Platform')
        
        max_dim = max(self.config.length, self.config.width) / 2 * 1.5
        self.ax_3d.set_xlim([-max_dim, max_dim])
        self.ax_3d.set_ylim([-max_dim, max_dim])
        self.ax_3d.set_zlim([0, self.config.max_height * 1.5])
        self.ax_3d.set_box_aspect([1, 1, 0.7])
        
        # Get rotation matrix
        R = self.ik_solver.rotation_matrix(roll, pitch, yaw)
        
        # Get actuator attachment points
        base_points, platform_points_init = self.ik_solver.get_actuator_positions()
        
        # Calculate center and rotated platform points
        if self.leveling_enabled:
            # When leveling, use opposite angles
            R = self.ik_solver.rotation_matrix(-roll, -pitch, -yaw if hasattr(self, 'platform_type') and 'stewart' in self.platform_type else 0)
        
        center = np.array([0, 0, self.config.min_height])
        
        # Rotate platform points
        platform_points = []
        for point in platform_points_init:
            local_point = point - center
            rotated_point = R @ local_point + center
            platform_points.append(rotated_point)
        platform_points = np.array(platform_points)
        
        # Draw base plate (ground)
        base_corners = np.array([
            [-self.config.length/2, -self.config.width/2, 0],
            [self.config.length/2, -self.config.width/2, 0],
            [self.config.length/2, self.config.width/2, 0],
            [-self.config.length/2, self.config.width/2, 0]
        ])
        
        base_poly = Poly3DCollection([base_corners], alpha=0.2, facecolor='gray', edgecolor='black')
        self.ax_3d.add_collection3d(base_poly)
        
        # Draw platform (top plate)
        platform_corners = []
        for corner in base_corners:
            corner_local = corner - np.array([0, 0, self.config.min_height])
            corner_rotated = R @ corner_local + center
            platform_corners.append(corner_rotated)
        platform_corners = np.array(platform_corners)
        
        platform_poly = Poly3DCollection([platform_corners], alpha=0.5, 
                                        facecolor='lightblue', edgecolor='blue', linewidth=2)
        self.ax_3d.add_collection3d(platform_poly)
        
        # Draw actuators
        for i, (base_pt, plat_pt) in enumerate(zip(base_points, platform_points)):
            # Actuator line
            self.ax_3d.plot([base_pt[0], plat_pt[0]],
                           [base_pt[1], plat_pt[1]],
                           [base_pt[2], plat_pt[2]],
                           'r-', linewidth=3, alpha=0.7)
            
            # Base attachment point
            self.ax_3d.scatter(*base_pt, color='darkred', s=100, marker='o')
            
            # Platform attachment point
            self.ax_3d.scatter(*plat_pt, color='blue', s=100, marker='o')
            
            # Length label
            length_mm = actuator_lengths[i] * 1000
            mid_point = (base_pt + plat_pt) / 2
            self.ax_3d.text(mid_point[0], mid_point[1], mid_point[2],
                          f'{length_mm:.0f}mm', fontsize=8)
        
        # Draw coordinate frame at platform center
        frame_length = 0.2
        platform_center = np.mean(platform_corners, axis=0)
        
        # X axis (red)
        x_axis = R @ np.array([frame_length, 0, 0])
        self.ax_3d.quiver(*platform_center, *x_axis, color='red', 
                         arrow_length_ratio=0.2, linewidth=2, label='X')
        
        # Y axis (green)
        y_axis = R @ np.array([0, frame_length, 0])
        self.ax_3d.quiver(*platform_center, *y_axis, color='green',
                         arrow_length_ratio=0.2, linewidth=2, label='Y')
        
        # Z axis (blue)
        z_axis = R @ np.array([0, 0, frame_length])
        self.ax_3d.quiver(*platform_center, *z_axis, color='blue',
                         arrow_length_ratio=0.2, linewidth=2, label='Z')
        
        # Set view angle
        self.ax_3d.view_init(elev=25, azim=45)
    
    def _draw_info_panel(self):
        """Draw information panel with current state."""

        self.ax_info.clear()
        self.ax_info.axis('off')

        # Get IMU data
        imu_data = self.imu_streamer.get_latest()

        # Build info text
        info_lines = [
            f"PLATFORM: {self.platform_type.upper()}",
            f"Dimensions: {self.config.length*1000:.0f} × {self.config.width*1000:.0f} mm",
            "",
        ]

        # IMU status
        if imu_data:
            info_lines.extend(
                [
                    "IMU DATA:",
                    f"  Roll:  {imu_data.roll:7.2f}°",
                    f"  Pitch: {imu_data.pitch:7.2f}°",
                    f"  Yaw:   {imu_data.yaw:7.2f}°",
                ]
            )

            # Tilt magnitude
            tilt_mag = np.sqrt(imu_data.roll**2 + imu_data.pitch**2)
            info_lines.append(f"  Tilt:  {tilt_mag:7.2f}°")
        else:
            info_lines.append("IMU DATA: Waiting...")

        info_lines.append("")

        # Leveling status
        status_color = 'green' if self.leveling_enabled else 'red'
        status_text = 'ENABLED' if self.leveling_enabled else 'DISABLED'
        info_lines.append(f"LEVELING: {status_text}")

        info_lines.append("")

        # Actuator lengths
        if self.actuator_lengths is not None:
            info_lines.append("ACTUATOR LENGTHS:")
            for i, length in enumerate(self.actuator_lengths):
                length_mm = length * 1000
                min_mm = self.config.min_height * 1000
                max_mm = (self.config.min_height + self.config.actuator_stroke) * 1000

                # Check if within limits
                status = "✓" if min_mm <= length_mm <= max_mm else "✗"
                info_lines.append(f"  [{i+1}] {length_mm:6.1f} mm {status}")

        info_lines.extend(
            [
                "",
                "CONTROLS:",
                "  [Space] Toggle leveling",
                "  [C] Calibrate",
                "  [Q] Quit",
            ]
        )

        # Draw text
        y_pos = 0.95
        for line in info_lines:
            if "ENABLED" in line:
                self.ax_info.text(
                    0.05,
                    y_pos,
                    line,
                    fontsize=11,
                    color=status_color,
                    weight='bold',
                    transform=self.ax_info.transAxes,
                )
            elif (
                line.startswith("PLATFORM:")
                or line.startswith("IMU DATA:")
                or line.startswith("LEVELING:")
                or line.startswith("ACTUATOR")
                or line.startswith("CONTROLS:")
            ):
                self.ax_info.text(
                    0.05,
                    y_pos,
                    line,
                    fontsize=11,
                    weight='bold',
                    transform=self.ax_info.transAxes,
                )
            else:
                self.ax_info.text(
                    0.05,
                    y_pos,
                    line,
                    fontsize=10,
                    transform=self.ax_info.transAxes,
                    family='monospace',
                )
            y_pos -= 0.05
    
    def _animation_update(self, frame):
        """Animation update function"""
        # Get latest IMU data
        imu_data = self.imu_streamer.get_latest()
        
        if imu_data:
            self.last_imu_data = imu_data
            
            # Convert to radians
            roll_rad = np.deg2rad(imu_data.roll)
            pitch_rad = np.deg2rad(imu_data.pitch)
            yaw_rad = np.deg2rad(imu_data.yaw)
            
            # Calculate actuator lengths
            if self.leveling_enabled:
                # Calculate lengths needed to level the platform
                if self.platform_type == 'tripod':
                    lengths, valid = self.ik_solver.level_platform(roll_rad, pitch_rad)
                else:
                    lengths, valid = self.ik_solver.level_platform(roll_rad, pitch_rad, yaw_rad)
                
                # Display platform level (correcting for measured tilt)
                display_roll = 0
                display_pitch = 0
                display_yaw = 0
            else:
                # Calculate lengths for current orientation (not leveling)
                if self.platform_type == 'tripod':
                    lengths, valid = self.ik_solver.solve(roll_rad, pitch_rad, 0)
                else:
                    lengths, valid = self.ik_solver.solve(roll_rad, pitch_rad, yaw_rad)
                
                # Display actual orientation
                display_roll = roll_rad
                display_pitch = pitch_rad
                display_yaw = yaw_rad
            
            self.actuator_lengths = lengths
            self.current_orientation = [display_roll, display_pitch, display_yaw]
            
            # Draw 3D platform
            self._draw_platform(display_roll, display_pitch, display_yaw, lengths)
        else:
            # No IMU data yet, draw level platform
            if self.platform_type == 'tripod':
                lengths, _ = self.ik_solver.solve(0, 0, 0)
            else:
                lengths, _ = self.ik_solver.solve(0, 0, 0)
            self.actuator_lengths = lengths
            self._draw_platform(0, 0, 0, lengths)
        
        # Draw info panel
        self._draw_info_panel()
    
    def run(self):
        """Start the visualization"""
        # Start IMU streamer
        self.imu_streamer.start()
        
        # Start animation
        anim = FuncAnimation(self.fig, self._animation_update,
                           interval=50,  # 20 FPS
                           cache_frame_data=False)
        
        plt.tight_layout()
        plt.show()
        
        # Cleanup
        self.imu_streamer.stop()


def run_visualizer(platform_type: str = "tripod") -> None:
    """Launch the 3D platform visualizer for the selected platform type.

    Args:
        platform_type: Platform configuration to visualize. Supported values
            are ``"tripod"``, ``"stewart_3dof"``, and ``"stewart_6dof"``.
    """

    viz = PlatformVisualizer(platform_type=platform_type)
    viz.run()


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    platform_type = 'tripod'
    if len(sys.argv) > 1:
        platform_type = sys.argv[1].lower()
        if platform_type not in ['tripod', 'stewart_3dof', 'stewart_6dof']:
            print(f"Unknown platform type: {platform_type}")
            print("Valid options: tripod, stewart_3dof, stewart_6dof")
            sys.exit(1)

    # Create and run visualizer
    run_visualizer(platform_type=platform_type)
