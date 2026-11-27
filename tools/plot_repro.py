#!/usr/bin/env python
"""Overlay two runs of the same seed (reproducibility check). Grayscale, white bg, 1600x900 PNG + CSV.

Usage:
  python tools/plot_repro.py <run_a> <run_b> -o results/own_flat/repro_seed42.png [--tag Train/mean_reward]

Also prints, for the main tags, the largest absolute difference between the two runs and the first iteration where
they differ (GPU physics is not guaranteed bit-exact, so small differences are possible).
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

CHECK_TAGS = [
    "Train/mean_reward",
    "Train/mean_episode_length",
    "Episode_Reward/track_lin_vel_xy",
    "Metrics/base_velocity/error_vel_xy",
    "Episode_Termination/bad_orientation",
    "Loss/value_function",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_a")
    ap.add_argument("run_b")
    ap.add_argument("-o", "--out", required=True, help="output PNG; the CSV goes next to it")
    ap.add_argument("--tag", default="Train/mean_reward")
    ap.add_argument("--ylabel", default="Mean episode reward")
    a = ap.parse_args()
    da, db = load_scalars(a.run_a), load_scalars(a.run_b)
    na, nb = (os.path.basename(os.path.normpath(r)) for r in (a.run_a, a.run_b))

    for tag in CHECK_TAGS:
        if tag not in da or tag not in db:
            continue
        sa, sb = dict(da[tag]), dict(db[tag])
        steps = sorted(set(sa) & set(sb))
        diff = np.abs(np.array([sa[k] for k in steps]) - np.array([sb[k] for k in steps]))
        first = next((k for k, d in zip(steps, diff) if d != 0.0), None)
        print(f"{tag:42s} max|diff| {diff.max():.6g}  first differing iteration: {first}")

    sa, sb = dict(da[a.tag]), dict(db[a.tag])
    steps = sorted(set(sa) & set(sb))
    ya, yb = np.array([sa[k] for k in steps]), np.array([sb[k] for k in steps])
    base = os.path.splitext(a.out)[0]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(base + ".csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iteration", na, nb, "abs_diff"])
        for k, x, y in zip(steps, ya, yb):
            w.writerow([k, x, y, abs(x - y)])

    plt.rcParams.update({"font.size": 20, "axes.linewidth": 1.2})
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.plot(steps, ya, color="black", linewidth=4.0, label=na)
    ax.plot(steps, yb, color="0.6", linewidth=1.8, linestyle="--", label=nb)
    ax.set_xlabel("Iteration")
    ax.set_ylabel(a.ylabel)
    ax.set_title(f"Reproducibility, same seed: {a.ylabel}")
    ax.grid(True, color="0.85")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(a.out, facecolor="white")
    plt.close(fig)
    print(f"wrote {a.out} and {base}.csv ({len(steps)} points)")


if __name__ == "__main__":
    main()
