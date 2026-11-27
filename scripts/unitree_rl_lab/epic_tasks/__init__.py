"""ePIC fURY task variants built on unitree_rl_lab (upstream files untouched).

Registered tasks:
  Unitree-Go2-Velocity-FullCmd
      = unitree_rl_lab `Unitree-Go2-Velocity` with ONE change, approved by Daham on 2026-11-27:
        the velocity commands use the full limit ranges from the start (vx +-1.0, vy +-0.4, yaw +-1.0)
        and the `lin_vel_cmd_levels` command curriculum is removed.
      Reason: the upstream curriculum only widens when the ~4 envs that reset exactly on every 1000th step track well,
      and it stayed at +-0.1 m/s for 824 iterations (see experiments/NOTES.md, 2026-11-27).
      Rewards, PD gains, action scale, observations, randomisation, terrain and PPO settings are unchanged.

Registration only uses string entry points, so importing this package does not import Isaac Lab.
"""

import gymnasium as gym

gym.register(
    id="Unitree-Go2-Velocity-FullCmd",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "epic_tasks.go2_fullcmd_cfg:RobotEnvCfgFullCmd",
        "play_env_cfg_entry_point": "epic_tasks.go2_fullcmd_cfg:RobotPlayEnvCfgFullCmd",
        "rsl_rl_cfg_entry_point": "unitree_rl_lab.tasks.locomotion.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",
    },
)
