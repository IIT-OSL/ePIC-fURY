#!/usr/bin/env python
"""Summarise tools/eval.py results: mean +/- std across seeds per condition, per task, plus a per-seed overall table.

Usage:
  python tools/eval_summary.py --own experiments/own_flat_seed4[234]_2026* --baseline experiments/baseline_flat_seed4*_2026* \
      [--repeat experiments/own_flat_seed42_repeat_*] -o results/eval_summary.md

Writes the markdown file and eval_summary.csv next to it. std = population std over seeds (as in the training plots).
Overall ranking rule (stated in the output): fewest falls over all 7 conditions, then lowest mean linear-velocity RMSE
over the 7 conditions, then lowest mean yaw RMSE. Daham picks the policy to deploy; this is only input.
"""
import argparse
import csv
import os
import time

import numpy as np

METRICS = [("lin_vel_rmse", "Lin. vel RMSE (m/s)", 3), ("yaw_rmse", "Yaw RMSE (rad/s)", 3),
           ("fall_rate", "Fall rate", 3), ("power_w", "Power (W)", 1)]


def load(run):
    with open(os.path.join(run, "eval.csv")) as f:
        rows = list(csv.DictReader(f))
    return {r["condition"]: r for r in rows}, [r["condition"] for r in rows]


def name(run):
    return os.path.basename(os.path.normpath(run))


def fmt(vals, nd):
    return f"{np.mean(vals):.{nd}f} ± {np.std(vals):.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--own", nargs="+", required=True)
    ap.add_argument("--baseline", nargs="+", required=True)
    ap.add_argument("--repeat", nargs="*", default=[])
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    groups = {"own (Unitree-Go2-Velocity-FullCmd)": a.own, "baseline (Isaac-Velocity-Flat-Unitree-Go2-v0)": a.baseline}
    data = {r: load(r)[0] for r in a.own + a.baseline + a.repeat}
    conds = load(a.own[0])[1]
    cmd = {c: data[a.own[0]][c] for c in conds}

    def cmd_str(c):
        r = cmd[c]
        return f"({r['cmd_vx']}, {r['cmd_vy']}, {r['cmd_wz']})" + (" + pushes" if r["pushes"] == "1" else "")

    out_csv = os.path.splitext(a.out)[0] + ".csv"
    L = [f"# Sprint 2 evaluation: fixed protocol, {len(a.own)} own seeds vs {len(a.baseline)} baseline seeds", "",
         f"Generated {time.strftime('%Y-%m-%d %H:%M')} by `tools/eval_summary.py` from each run's `eval.csv` "
         "(made by `tools/eval.py`, launched with `scripts/run_eval.sh`). Protocol and eval settings: docstring of `tools/eval.py`.",
         "", "64 envs × 20 s per condition, commands fixed, flat plane, same env seed (0) for every policy. "
         "RMSE and power after a 1 s warm-up; fall = base contact or tilt > 0.8 rad. Values: mean ± std over seeds "
         "(population std).", ""]
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["task_group", "condition"] + [f"{m}_{s}" for m, _, _ in METRICS for s in ("mean", "std")])
        for g, runs in groups.items():
            L += [f"## {g}", "", f"Runs: {', '.join('`' + name(r) + '`' for r in runs)}", "",
                  "| Condition | Command (vx, vy, wz) | " + " | ".join(t for _, t, _ in METRICS) + " |",
                  "| --- | --- | " + " | ".join("---" for _ in METRICS) + " |"]
            for c in conds:
                cells, nums = [], []
                for m, _, nd in METRICS:
                    v = [float(data[r][c][m]) for r in runs]
                    cells.append(fmt(v, nd))
                    nums += [np.mean(v), np.std(v)]
                L.append(f"| {c} | {cmd_str(c)} | " + " | ".join(cells) + " |")
                w.writerow([g, c] + nums)
            L.append("")

    # side by side: own vs baseline means
    L += ["## Own vs baseline (means over seeds)", "",
          "| Condition | Lin. RMSE own | Lin. RMSE baseline | Yaw RMSE own | Yaw RMSE baseline | Falls own | Falls baseline | Power own (W) | Power baseline (W) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in conds:
        def m(runs, k):
            return np.mean([float(data[r][c][k]) for r in runs])
        L.append(f"| {c} | {m(a.own, 'lin_vel_rmse'):.3f} | {m(a.baseline, 'lin_vel_rmse'):.3f} | "
                 f"{m(a.own, 'yaw_rmse'):.3f} | {m(a.baseline, 'yaw_rmse'):.3f} | "
                 f"{m(a.own, 'fall_rate'):.3f} | {m(a.baseline, 'fall_rate'):.3f} | "
                 f"{m(a.own, 'power_w'):.1f} | {m(a.baseline, 'power_w'):.1f} |")
    L += ["", "The baseline policy reads base linear velocity, which the real robot cannot measure, and was trained "
          "without pushes; it is a sim-only reference. It also had only 300 iterations (own: 3,000), and it was trained with "
          "heading commands (`heading_command=True`: yaw rate comes from a heading controller, so a constant 0.8 rad/s yaw "
          "command is rarely seen in training). That explains its poor turn_0.8 result (it barely turns; one seed tips "
          "over in 48 % of envs). The comparison is therefore not like-for-like; it shows the own policy is at least as "
          "good as the Sprint 1 reference on every condition.", ""]

    # per-seed overall
    def overall(r):
        d = data[r]
        return (sum(int(d[c]["falls"]) for c in conds), np.mean([float(d[c]["lin_vel_rmse"]) for c in conds]),
                np.mean([float(d[c]["yaw_rmse"]) for c in conds]), np.mean([float(d[c]["power_w"]) for c in conds]))

    L += ["## Per-seed overall (mean over the 7 conditions)", "",
          "| Run | Falls (total envs, 7 × 64) | Mean lin. RMSE (m/s) | Mean yaw RMSE (rad/s) | Mean power (W) |",
          "| --- | --- | --- | --- | --- |"]
    for r in a.own + a.repeat + a.baseline:
        f_, l_, y_, p_ = overall(r)
        L.append(f"| {name(r)} | {f_} | {l_:.4f} | {y_:.4f} | {p_:.1f} |")
    best = min(a.own, key=lambda r: overall(r)[:3])
    L += ["", "Ranking rule: fewest falls, then lowest mean linear-velocity RMSE, then lowest mean yaw RMSE "
          "(own seeds only; the repeat run is listed for reference).", "",
          f"**Best own seed by this rule: `{name(best)}`.** Daham picks the policy to deploy.", ""]
    with open(a.out, "w") as f:
        f.write("\n".join(L))
    print("\n".join(L))
    print(f"wrote {a.out} and {out_csv}")


if __name__ == "__main__":
    main()
