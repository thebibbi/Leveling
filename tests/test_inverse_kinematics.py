import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inverse_kinematics import PlatformConfig, TripodIK, StewartPlatformIK


def _default_config() -> PlatformConfig:
    return PlatformConfig(
        length=1.83,
        width=1.22,
        min_height=0.3,
        max_height=0.7,
        actuator_stroke=0.4,
    )


def test_tripod_levels_to_min_height():
    config = _default_config()
    tripod = TripodIK(config)

    lengths, valid = tripod.level_platform(0.0, 0.0)

    assert valid
    assert lengths.shape == (3,)
    assert np.allclose(lengths, config.min_height)


def test_stewart_3dof_levels_orientation():
    config = _default_config()
    platform = StewartPlatformIK(config, dof_mode="3DOF")

    lengths, valid = platform.level_platform(np.deg2rad(6), np.deg2rad(-3))

    assert valid
    assert lengths.shape == (6,)
    assert np.all(lengths >= config.min_height)
    assert np.all(lengths <= config.min_height + config.actuator_stroke)


def test_stewart_6dof_handles_yaw():
    config = _default_config()
    platform = StewartPlatformIK(config, dof_mode="6DOF")

    lengths, valid = platform.level_platform(
        np.deg2rad(2), np.deg2rad(-2), np.deg2rad(10)
    )

    assert valid
    assert lengths.shape == (6,)
    assert np.all(lengths >= config.min_height)
    assert np.all(lengths <= config.min_height + config.actuator_stroke)
