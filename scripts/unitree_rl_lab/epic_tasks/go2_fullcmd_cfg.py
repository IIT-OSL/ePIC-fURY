"""Unitree-Go2-Velocity-FullCmd: unitree_rl_lab Go2 velocity task, full command range, no command curriculum.

Only the command ranges and the command curriculum differ from upstream
(external/unitree_rl_lab/.../tasks/locomotion/robots/go2/velocity_env_cfg.py, commit 4960b84). See __init__.py.
"""

from isaaclab.utils import configclass

from unitree_rl_lab.tasks.locomotion.robots.go2.velocity_env_cfg import RobotEnvCfg, RobotPlayEnvCfg


def _full_command_range(cfg) -> None:
    """Train on the full command limits from the start and drop the command-level curriculum."""
    cmd = cfg.commands.base_velocity
    lim = cmd.limit_ranges
    cmd.ranges.lin_vel_x = tuple(lim.lin_vel_x)  # (-1.0, 1.0)
    cmd.ranges.lin_vel_y = tuple(lim.lin_vel_y)  # (-0.4, 0.4)
    cmd.ranges.ang_vel_z = tuple(lim.ang_vel_z)  # (-1.0, 1.0)
    cfg.curriculum.lin_vel_cmd_levels = None


@configclass
class RobotEnvCfgFullCmd(RobotEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        _full_command_range(self)


@configclass
class RobotPlayEnvCfgFullCmd(RobotPlayEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        _full_command_range(self)
