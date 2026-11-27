"""Fixed evaluation protocol (Sprint 2), same for every policy. Read-only for training runs except for writing eval.csv.

Usage (from the unitree_rl_lab root, so unitree tasks resolve):
  cd external/unitree_rl_lab
  PYTHONUNBUFFERED=1 python ../../tools/eval.py --headless --task <task> --run ../../experiments/<run_folder>

Protocol (CLAUDE.md): 7 conditions, each 64 envs x 20 s (1000 policy steps at 50 Hz), commands fixed (no resampling):
  stand (0,0,0) | walk 0.5 | walk 1.0 | backward -0.5 | sidestep vy 0.3 | turn wz 0.8 | walk 0.5 with random pushes

Eval settings applied to the task's TRAINING config (identical for both tasks; training configs themselves untouched):
  - 64 envs, flat plane, env_spacing 2.5 m, all curricula off, fixed env seed (--seed, default 0) so every policy
    sees the same friction/mass randomisation and start poses
  - commands: fixed value, resampling off, no standing envs, no heading control
  - observation noise and startup randomisation (friction, base mass) kept as in training
  - no time-out (episode_length_s = 1e4); terminations = base contact OR tilt > 0.8 rad (the unitree task's
    bad_orientation limit). The built-in task only has base contact, so the tilt check is added there for an
    identical fall definition
  - pushes: off, except in the push condition, where both tasks get the SAME push term
    (push_by_setting_velocity, +-0.5 m/s in x and y, every 5-10 s; the unitree training push). The built-in task
    was trained without pushes.

Metrics per condition (after a 1 s warm-up; samples of an env are dropped from its first fall onward):
  lin_vel_rmse  sqrt(mean((vx - cmd_vx)^2 + (vy - cmd_vy)^2)), body frame, m/s
  yaw_rmse      sqrt(mean((wz - cmd_wz)^2)), rad/s
  fall_rate     envs with >= 1 fall in the 20 s / 64 (falls counted over the full 20 s)
  power_w       mean over envs and steps of sum_j |tau_j * qdot_j| (applied torque), W
  push_events   number of pushes actually applied in the condition (all 64 envs), as a check
"""

import argparse
import csv
import glob
import math
import os
import sys
import time

from isaaclab.app import AppLauncher

CONDITIONS = [
    # name, vx, vy, wz, pushes
    ("stand", 0.0, 0.0, 0.0, False),
    ("walk_0.5", 0.5, 0.0, 0.0, False),
    ("walk_1.0", 1.0, 0.0, 0.0, False),
    ("backward_-0.5", -0.5, 0.0, 0.0, False),
    ("sidestep_0.3", 0.0, 0.3, 0.0, False),
    ("turn_0.8", 0.0, 0.0, 0.8, False),
    ("walk_0.5_push", 0.5, 0.0, 0.0, True),
]

parser = argparse.ArgumentParser(description="Fixed 7-condition eval of one checkpoint.")
parser.add_argument("--task", required=True, help="training task id (e.g. Unitree-Go2-Velocity-FullCmd)")
parser.add_argument("--run", required=True, help="experiments/<run_folder>; eval.csv is written here")
parser.add_argument("--checkpoint", default=None, help="model .pt (default: newest model_*.pt in the run's log link)")
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--duration_s", type=float, default=20.0)
parser.add_argument("--warmup_s", type=float, default=1.0)
parser.add_argument("--seed", type=int, default=0, help="env seed (same for every policy)")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
simulation_app = AppLauncher(args_cli).app

import gymnasium as gym  # noqa: E402
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

PUSH_RANGE = (5.0, 10.0)
NO_PUSH_RANGE = (1.0e6, 1.0e6)


def find_checkpoint(run):
    for link in ("url_log", "isaaclab_log"):
        models = glob.glob(os.path.join(run, link, "model_*.pt"))
        if models:
            return max(models, key=lambda p: int(os.path.basename(p)[6:-3]))
    sys.exit(f"no model_*.pt in {run}/url_log or {run}/isaaclab_log")


def make_env_cfg():
    cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    cfg.seed = args_cli.seed
    cfg.episode_length_s = 1.0e4
    # flat plane, no curricula
    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None
    cfg.scene.env_spacing = 2.5
    for name in ("terrain_levels", "lin_vel_cmd_levels"):
        if hasattr(cfg.curriculum, name):
            setattr(cfg.curriculum, name, None)
    # fixed commands
    cmd = cfg.commands.base_velocity
    cmd.resampling_time_range = (1.0e6, 1.0e6)
    cmd.rel_standing_envs = 0.0
    cmd.heading_command = False
    cmd.rel_heading_envs = 0.0
    cmd.debug_vis = False
    # one push term for both tasks (interval switched per condition)
    cfg.events.push_robot = EventTermCfg(
        func=base_mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=NO_PUSH_RANGE,
        params={"velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}},
    )
    # same fall definition for both tasks
    cfg.terminations.time_out = None
    cfg.terminations.bad_orientation = TerminationTermCfg(func=base_mdp.bad_orientation, params={"limit_angle": 0.8})
    return cfg


def set_condition(uenv, vx, vy, wz, pushes):
    r = uenv.command_manager.get_term("base_velocity").cfg.ranges
    r.lin_vel_x, r.lin_vel_y, r.ang_vel_z = (vx, vx), (vy, vy), (wz, wz)
    for term_cfg in uenv.event_manager._mode_term_cfgs.get("interval", []):
        if term_cfg.func is base_mdp.push_by_setting_velocity:
            term_cfg.interval_range_s = PUSH_RANGE if pushes else NO_PUSH_RANGE


def main():
    ckpt = args_cli.checkpoint or find_checkpoint(args_cli.run)
    env_cfg = make_env_cfg()
    agent_cfg = load_cfg_from_registry(args_cli.task, "rsl_rl_cfg_entry_point")
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, version("rsl-rl-lib"))
    agent_cfg.device = args_cli.device or agent_cfg.device

    env = gym.make(args_cli.task, cfg=env_cfg)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    uenv = env.unwrapped
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(ckpt)
    policy = runner.get_inference_policy(device=uenv.device)
    robot = uenv.scene["robot"]
    push_idx = next(i for i, c in enumerate(uenv.event_manager._mode_term_cfgs["interval"])
                    if c.func is base_mdp.push_by_setting_velocity)
    push_left = uenv.event_manager._interval_term_time_left[push_idx]
    print(f"[eval] {time.strftime('%H:%M:%S')} task {args_cli.task}, checkpoint {ckpt}", flush=True)

    n_steps = int(round(args_cli.duration_s / uenv.step_dt))
    n_warm = int(round(args_cli.warmup_s / uenv.step_dt))
    rows = []
    for name, vx, vy, wz, pushes in CONDITIONS:
        set_condition(uenv, vx, vy, wz, pushes)
        with torch.inference_mode():
            obs, _ = env.reset()
        fallen = torch.zeros(uenv.num_envs, dtype=torch.bool, device=uenv.device)
        se_lin = se_yaw = power = 0.0
        n = pushes_done = 0
        with torch.inference_mode():
            for step in range(n_steps):
                before = push_left.clone()
                obs, _, _, _ = env.step(policy(obs))
                pushes_done += int((push_left > before).sum())  # timer restarted = push applied
                fallen |= uenv.termination_manager.terminated
                if step < n_warm:
                    continue
                valid = ~fallen
                k = int(valid.sum())
                if k == 0:
                    continue
                c = uenv.command_manager.get_command("base_velocity")[valid]
                v = robot.data.root_lin_vel_b[valid]
                w = robot.data.root_ang_vel_b[valid]
                se_lin += float(((v[:, 0] - c[:, 0]) ** 2 + (v[:, 1] - c[:, 1]) ** 2).sum())
                se_yaw += float(((w[:, 2] - c[:, 2]) ** 2).sum())
                power += float((robot.data.applied_torque[valid] * robot.data.joint_vel[valid]).abs().sum())
                n += k
        row = {
            "condition": name, "cmd_vx": vx, "cmd_vy": vy, "cmd_wz": wz, "pushes": int(pushes),
            "lin_vel_rmse": math.sqrt(se_lin / n) if n else float("nan"),
            "yaw_rmse": math.sqrt(se_yaw / n) if n else float("nan"),
            "fall_rate": float(fallen.float().mean()),
            "falls": int(fallen.sum()),
            "power_w": power / n if n else float("nan"),
            "push_events": pushes_done,
            "samples": n,
        }
        rows.append(row)
        print(f"[eval] {name:14s} lin {row['lin_vel_rmse']:.3f}  yaw {row['yaw_rmse']:.3f}  "
              f"fall {row['fall_rate']:.3f}  power {row['power_w']:.1f} W  pushes {pushes_done}", flush=True)

    out = os.path.join(args_cli.run, "eval.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(args_cli.run, "eval_cmd.txt"), "w") as f:
        f.write(" ".join(sys.argv) + f"\n# checkpoint: {os.path.realpath(ckpt)}\n# {time.strftime('%Y-%m-%d %H:%M')}\n")

    print(f"\nEval: {os.path.basename(os.path.normpath(args_cli.run))} ({os.path.basename(ckpt)})\n")
    print("| Condition | Command (vx, vy, wz) | Lin. vel RMSE (m/s) | Yaw RMSE (rad/s) | Fall rate | Power (W) |")
    print("| --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print(f"| {r['condition']} | ({r['cmd_vx']}, {r['cmd_vy']}, {r['cmd_wz']}){' + pushes' if r['pushes'] else ''} | "
              f"{r['lin_vel_rmse']:.3f} | {r['yaw_rmse']:.3f} | {r['fall_rate']:.3f} | {r['power_w']:.1f} |")
    print(f"\nwrote {out}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
