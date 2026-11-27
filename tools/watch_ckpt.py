"""Live checkpoint viewer for the own-policy training (Sprint 2). VIEWING ONLY: never writes into training runs.

Opens an Isaac Sim window with a few Go2s (play config), plays the newest checkpoint of the newest run under --log_root,
and hot-reloads whenever training saves a newer model_*.pt (every 100 iterations) or moves on to the next seed.
Pausing, moving or closing this window has no effect on training (it is a separate process).

Viewer-only changes to the play config (training config untouched):
  - plain floor (terrain_type "plane") with env_spacing 2.5 m, so robots stand apart instead of stacked on 2 terrain tiles
  - terrain-level and command curricula off (play config already uses the full command limit ranges)
  - camera aimed at the robot grid

Run (from the unitree_rl_lab root, GUI on the Xwayland display):
  cd external/unitree_rl_lab && DISPLAY=:2 PYTHONUNBUFFERED=1 python ../../tools/watch_ckpt.py --num_envs 16
"""

import argparse
import glob
import os
import sys
import time

_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "external", "unitree_rl_lab")
sys.path.insert(0, os.path.join(_URL, "scripts", "rsl_rl"))  # for unitree_rl_lab's cli_args

from isaaclab.app import AppLauncher  # noqa: E402

import cli_args  # noqa: E402  isort: skip

parser = argparse.ArgumentParser(description="Live viewer of the newest training checkpoint (view only).")
parser.add_argument("--task", default="Unitree-Go2-Velocity")
parser.add_argument("--num_envs", type=int, default=16)
parser.add_argument(
    "--log_root",
    default=os.path.abspath(os.path.join(_URL, "logs", "rsl_rl", "unitree_go2_velocity")),
    help="folder holding the training run folders; the newest run is followed",
)
parser.add_argument("--run_glob", default="*_own_seed*", help="which run folders to follow")
parser.add_argument("--reload_s", type=float, default=30.0, help="how often to look for a newer checkpoint (s)")
cli_args.add_rsl_rl_args(parser)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402
from importlib.metadata import version  # noqa: E402

from rsl_rl.runners import OnPolicyRunner  # noqa: E402

import isaaclab_tasks  # noqa: E402,F401
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg  # noqa: E402

import unitree_rl_lab.tasks  # noqa: E402,F401
from unitree_rl_lab.utils.parser_cfg import parse_env_cfg  # noqa: E402


def newest_checkpoint():
    runs = sorted(glob.glob(os.path.join(args_cli.log_root, args_cli.run_glob)), key=os.path.getmtime)
    for run in reversed(runs):
        models = glob.glob(os.path.join(run, "model_*.pt"))
        if models:
            best = max(models, key=lambda p: int(os.path.basename(p)[6:-3]))
            return best
    return None


def main():
    env_cfg = parse_env_cfg(
        args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=True,
        entry_point_key="play_env_cfg_entry_point",
    )
    # --- viewer-only scene changes (see module docstring) ---
    env_cfg.scene.terrain.terrain_type = "plane"
    env_cfg.scene.terrain.terrain_generator = None
    env_cfg.scene.env_spacing = 2.5
    env_cfg.curriculum.terrain_levels = None
    env_cfg.curriculum.lin_vel_cmd_levels = None
    env_cfg.viewer.origin_type = "world"
    env_cfg.viewer.eye = (9.0, 9.0, 6.0)
    env_cfg.viewer.lookat = (0.0, 0.0, 0.0)

    agent_cfg = cli_args.parse_rsl_rl_cfg(args_cli.task, args_cli)
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, version("rsl-rl-lib"))

    ckpt = None
    while ckpt is None and simulation_app.is_running():
        ckpt = newest_checkpoint()
        if ckpt is None:
            print("[watch_ckpt] no checkpoint yet, waiting...", flush=True)
            time.sleep(10)

    env = gym.make(args_cli.task, cfg=env_cfg)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(ckpt)
    policy = runner.get_inference_policy(device=env.unwrapped.device)
    print(f"[watch_ckpt] {time.strftime('%H:%M:%S')} showing {ckpt}", flush=True)

    dt = env.unwrapped.step_dt
    obs = env.get_observations()
    last_check = time.time()
    while simulation_app.is_running():
        t0 = time.time()
        with torch.inference_mode():
            obs, _, _, _ = env.step(policy(obs))
        if time.time() - last_check > args_cli.reload_s:
            last_check = time.time()
            new = newest_checkpoint()
            if new and new != ckpt:
                ckpt = new
                runner.load(ckpt)
                policy = runner.get_inference_policy(device=env.unwrapped.device)
                print(f"[watch_ckpt] {time.strftime('%H:%M:%S')} reloaded {ckpt}", flush=True)
        sleep = dt - (time.time() - t0)
        if sleep > 0:
            time.sleep(sleep)  # real time
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
