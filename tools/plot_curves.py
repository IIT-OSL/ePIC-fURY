#!/usr/bin/env python
"""Mean +/- std training curves across seeds (grayscale, white bg, 1600x900 PNG + CSV per plot).

Usage:
  python tools/plot_curves.py <run_dir> [<run_dir> ...] -o results/baseline_flat [--label "Go2 flat baseline"]
  python tools/plot_curves.py <run_dir> ... -o results/own_flat --preset url   # unitree_rl_lab runs (Sprint 2)

Each run_dir is an experiments/<run>/ folder (isaaclab_log symlink followed) or an Isaac Lab log dir.
Curves are aligned on the iteration steps common to all runs.
"""
import argparse
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tb_to_csv import load_scalars  # noqa: E402

# (file stem, TensorBoard tag, y label) -- tag names as written by Isaac Lab 2.3.2 / rsl-rl-lib 5.0.1
PLOTS_ISAACLAB = [
    ("mean_reward", "Train/mean_reward", "Mean episode reward"),
    ("mean_episode_length", "Train/mean_episode_length", "Mean episode length (steps)"),
    ("track_lin_vel_xy", "Episode_Reward/track_lin_vel_xy_exp", "Reward term: track_lin_vel_xy_exp"),
    ("track_ang_vel_z", "Episode_Reward/track_ang_vel_z_exp", "Reward term: track_ang_vel_z_exp"),
    ("base_contact_termination", "Episode_Termination/base_contact", "Base-contact termination rate"),
]

# unitree_rl_lab Unitree-Go2-Velocity(-FullCmd): different reward-term names; falls end via bad_orientation
PLOTS_URL = [
    ("mean_reward", "Train/mean_reward", "Mean episode reward"),
    ("mean_episode_length", "Train/mean_episode_length", "Mean episode length (steps)"),
    ("track_lin_vel_xy", "Episode_Reward/track_lin_vel_xy", "Reward term: track_lin_vel_xy"),
    ("track_ang_vel_z", "Episode_Reward/track_ang_vel_z", "Reward term: track_ang_vel_z"),
    ("error_vel_xy", "Metrics/base_velocity/error_vel_xy", "Velocity tracking error xy (m/s)"),
    ("error_vel_yaw", "Metrics/base_velocity/error_vel_yaw", "Yaw-rate tracking error (rad/s)"),
    ("bad_orientation_termination", "Episode_Termination/bad_orientation", "Bad-orientation termination rate"),
]
PRESETS = {"isaaclab": PLOTS_ISAACLAB, "url": PLOTS_URL}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="isaaclab", help="tag set (default: Isaac Lab tasks)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    data = [load_scalars(r) for r in a.runs]
    names = [os.path.basename(os.path.normpath(r)) for r in a.runs]

    plt.rcParams.update({"font.size": 20, "axes.linewidth": 1.2})
    for stem, tag, ylabel in PRESETS[a.preset]:
        series = []
        for d, n in zip(data, names):
            if tag not in d:
                sys.exit(f"tag {tag} missing in {n}")
            series.append(dict(d[tag]))
        steps = sorted(set.intersection(*[set(s) for s in series]))
        vals = np.array([[s[k] for k in steps] for s in series])  # (runs, steps)
        mean, std = vals.mean(0), vals.std(0)  # population std across seeds

        with open(os.path.join(a.out, f"{stem}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["iteration", "mean", "std"] + names)
            for i, k in enumerate(steps):
                w.writerow([k, mean[i], std[i]] + list(vals[:, i]))

        fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        x = np.array(steps)
        ax.fill_between(x, mean - std, mean + std, color="0.75", linewidth=0, label="± 1 std")
        ax.plot(x, mean, color="black", linewidth=2.5, label=f"mean of {len(a.runs)} seeds")
        ax.set_xlabel("Iteration")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{a.label}: {ylabel}" if a.label else ylabel)
        ax.grid(True, color="0.85")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(os.path.join(a.out, f"{stem}.png"), facecolor="white")
        plt.close(fig)
        print(f"wrote {stem}.png/.csv ({len(steps)} points)")


if __name__ == "__main__":
    main()
