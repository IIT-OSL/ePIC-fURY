#!/usr/bin/env python
"""Title-card figure for the YouTube video: training curve (mean +/- std over seeds) as a 1920x1080 grayscale PNG.

Usage:
  python tools/plot_title_card.py results/own_flat/mean_reward.csv -o results/video/title_card_training_curve.png
Input is the CSV written by tools/plot_curves.py (iteration, mean, std, per-run columns).
"""
import argparse
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("csv")
ap.add_argument("-o", "--out", required=True)
ap.add_argument("--title", default="Unitree Go2: PPO walking policy, Isaac Lab + RSL-RL")
ap.add_argument("--subtitle", default="Blind, deployable inputs only · 3 seeds · 3,000 iterations · 4,096 parallel robots")
a = ap.parse_args()

with open(a.csv) as f:
    rows = list(csv.DictReader(f))
x = np.array([float(r["iteration"]) for r in rows])
m = np.array([float(r["mean"]) for r in rows])
s = np.array([float(r["std"]) for r in rows])

plt.rcParams.update({"font.size": 26, "axes.linewidth": 1.5})
fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.fill_between(x, m - s, m + s, color="0.75", linewidth=0, label="± 1 std over seeds")
ax.plot(x, m, color="black", linewidth=3.0, label="mean episode reward")
ax.set_xlabel("Training iteration")
ax.set_ylabel("Mean episode reward")
ax.grid(True, color="0.85")
ax.legend(frameon=False, loc="lower right")
fig.suptitle(a.title, fontsize=44, fontweight="bold", y=0.965)
ax.set_title(a.subtitle, fontsize=26, color="0.3", pad=18)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(a.out, facecolor="white")
print(f"wrote {a.out}")
