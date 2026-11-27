"""Record one video clip per eval command (Sprint 2 video material). Read-only for the run; clips go to --out.

Usage (from the unitree_rl_lab root):
  cd external/unitree_rl_lab
  PYTHONUNBUFFERED=1 python ../../tools/record_clips.py --headless --enable_cameras \
      --task Unitree-Go2-Velocity-FullCmd --run ../../experiments/own_flat_seed44_20261127-1505 --out ../../results/video

Same conditions as tools/eval.py (fixed commands, flat plane, no time-out, env seed 0), with these VIDEO-ONLY changes:
  - 9 robots (3 x 3 grid, 2.5 m apart), all starting at their grid point facing +x (no random start pose/yaw),
    so they move in formation
  - camera follows the centre robot (Isaac Lab viewer origin "asset_root"), 1920x1080, 50 fps (policy rate)
  - push clip: same push as the eval (+-0.5 m/s in x and y) but every 3-5 s instead of 5-10 s, so it shows on screen
  - 1 s settle before recording, then --clip_s seconds (default 10)
Output: <out>/<NN>_<condition>.mp4 and <out>/clips.txt (list for ffmpeg concat).
"""

import argparse
import glob
import os
import sys
import time

from isaaclab.app import AppLauncher

CLIPS = [
    # file name, vx, vy, wz, pushes, caption
    ("01_stand", 0.0, 0.0, 0.0, False),
    ("02_walk_0.5", 0.5, 0.0, 0.0, False),
    ("03_walk_1.0", 1.0, 0.0, 0.0, False),
    ("04_backward_-0.5", -0.5, 0.0, 0.0, False),
    ("05_sidestep_0.3", 0.0, 0.3, 0.0, False),
    ("06_turn_0.8", 0.0, 0.0, 0.8, False),
    ("07_walk_0.5_push", 0.5, 0.0, 0.0, True),
]

parser = argparse.ArgumentParser(description="Record one clip per eval command.")
parser.add_argument("--task", required=True)
parser.add_argument("--run", required=True)
parser.add_argument("--checkpoint", default=None)
parser.add_argument("--out", required=True)
parser.add_argument("--clip_s", type=float, default=10.0)
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
args_cli.enable_cameras = True
simulation_app = AppLauncher(args_cli).app

import gymnasium as gym  # noqa: E402
import imageio.v2 as imageio  # noqa: E402
import torch  # noqa: E402
from importlib.metadata import version  # noqa: E402

from rsl_rl.runners import OnPolicyRunner  # noqa: E402

import isaaclab.envs.mdp as base_mdp  # noqa: E402
import isaaclab_tasks  # noqa: E402,F401
from isaaclab.managers import EventTermCfg, TerminationTermCfg  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg  # noqa: E402
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg  # noqa: E402

import unitree_rl_lab.tasks  # noqa: E402,F401

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "unitree_rl_lab"))
import epic_tasks  # noqa: E402,F401

PUSH_RANGE = (3.0, 5.0)
NO_PUSH_RANGE = (1.0e6, 1.0e6)


def find_checkpoint(run):
    for link in ("url_log", "isaaclab_log"):
        models = glob.glob(os.path.join(run, link, "model_*.pt"))
        if models:
            return max(models, key=lambda p: int(os.path.basename(p)[6:-3]))
    sys.exit(f"no model_*.pt in {run}")


def make_env_cfg():
    cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=9)
    cfg.seed = args_cli.seed
    cfg.episode_length_s = 1.0e4
    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None
    cfg.scene.env_spacing = 2.5
    for name in ("terrain_levels", "lin_vel_cmd_levels"):
        if hasattr(cfg.curriculum, name):
            setattr(cfg.curriculum, name, None)
    cmd = cfg.commands.base_velocity
    cmd.resampling_time_range = (1.0e6, 1.0e6)
    cmd.rel_standing_envs = 0.0
    cmd.heading_command = False
    cmd.rel_heading_envs = 0.0
    cmd.debug_vis = False
    cfg.events.push_robot = EventTermCfg(
        func=base_mdp.push_by_setting_velocity, mode="interval", interval_range_s=NO_PUSH_RANGE,
        params={"velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}},
    )
    cfg.terminations.time_out = None
    cfg.terminations.bad_orientation = TerminationTermCfg(func=base_mdp.bad_orientation, params={"limit_angle": 0.8})
    # video only: start at the grid point, facing +x
    cfg.events.reset_base.params["pose_range"] = {"x": (0.0, 0.0), "y": (0.0, 0.0), "yaw": (0.0, 0.0)}
    # camera follows the centre robot (env 4 of the 3x3 grid)
    cfg.viewer.origin_type = "asset_root"
    cfg.viewer.asset_name = "robot"
    cfg.viewer.env_index = 4
    cfg.viewer.eye = (-6.5, -7.5, 5.0)
    cfg.viewer.lookat = (0.3, 0.0, 0.0)
    cfg.viewer.resolution = (1920, 1080)
    return cfg


def set_condition(uenv, vx, vy, wz, pushes):
    r = uenv.command_manager.get_term("base_velocity").cfg.ranges
    r.lin_vel_x, r.lin_vel_y, r.ang_vel_z = (vx, vx), (vy, vy), (wz, wz)
    for term_cfg in uenv.event_manager._mode_term_cfgs.get("interval", []):
        if term_cfg.func is base_mdp.push_by_setting_velocity:
            term_cfg.interval_range_s = PUSH_RANGE if pushes else NO_PUSH_RANGE


def main():
    ckpt = args_cli.checkpoint or find_checkpoint(args_cli.run)
    os.makedirs(args_cli.out, exist_ok=True)
    env_cfg = make_env_cfg()
    agent_cfg = load_cfg_from_registry(args_cli.task, "rsl_rl_cfg_entry_point")
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, version("rsl-rl-lib"))
    agent_cfg.device = args_cli.device or agent_cfg.device

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array")
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    uenv = env.unwrapped
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(ckpt)
    policy = runner.get_inference_policy(device=uenv.device)
    print(f"[clips] {time.strftime('%H:%M:%S')} {ckpt}", flush=True)

    fps = int(round(1.0 / uenv.step_dt))
    n_settle, n_rec = fps, int(round(args_cli.clip_s * fps))
    listing = []
    with torch.inference_mode():
        for name, vx, vy, wz, pushes in CLIPS:
            set_condition(uenv, vx, vy, wz, pushes)
            obs, _ = env.reset()
            path = os.path.join(args_cli.out, f"{name}.mp4")
            falls = 0
            with imageio.get_writer(path, fps=fps, codec="libx264", quality=8, macro_block_size=8,
                                    ffmpeg_params=["-pix_fmt", "yuv420p"]) as w:
                for step in range(n_settle + n_rec):
                    obs, _, _, _ = env.step(policy(obs))
                    falls += int(uenv.termination_manager.terminated.sum())
                    if step >= n_settle:
                        w.append_data(uenv.render())
            listing.append(f"file '{name}.mp4'")
            print(f"[clips] {name}: {n_rec} frames, falls {falls} -> {path}", flush=True)
    with open(os.path.join(args_cli.out, "clips.txt"), "w") as f:
        f.write("\n".join(listing) + "\n")
    with open(os.path.join(args_cli.out, "record_cmd.txt"), "w") as f:
        f.write(" ".join(sys.argv) + f"\n# checkpoint: {os.path.realpath(ckpt)}\n# {time.strftime('%Y-%m-%d %H:%M')}\n")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
