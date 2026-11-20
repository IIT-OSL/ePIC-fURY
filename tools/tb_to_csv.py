#!/usr/bin/env python
"""Export every TensorBoard scalar of a run to CSV (columns: step, tag, value).

Usage:
  python tools/tb_to_csv.py <run_dir_or_logdir> [-o out.csv] [--list]

<run_dir> may be an experiments/<run>/ folder (its isaaclab_log symlink is followed)
or an Isaac Lab log dir containing events.out.tfevents.* files.
Default output: <run_dir>/scalars.csv. --list prints the tags and their point counts.
"""
import argparse
import csv
import glob
import os
import sys

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def find_event_dir(path):
    for cand in (os.path.join(path, "isaaclab_log"), path):
        if glob.glob(os.path.join(cand, "events.out.tfevents.*")):
            return cand
    sys.exit(f"no events.out.tfevents.* in {path} or {path}/isaaclab_log")


def load_scalars(path):
    """Return {tag: [(step, value), ...]} merged over all event files in the run (sorted by step)."""
    ev_dir = find_event_dir(path)
    acc = EventAccumulator(ev_dir, size_guidance={"scalars": 0})
    acc.Reload()
    out = {}
    for tag in acc.Tags()["scalars"]:
        pts = {}
        for e in acc.Scalars(tag):
            pts[e.step] = e.value  # last write per step wins
        out[tag] = sorted(pts.items())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("-o", "--out")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    scalars = load_scalars(a.run)
    if a.list:
        for tag in sorted(scalars):
            print(f"{tag}\t{len(scalars[tag])}")
        return
    out = a.out or os.path.join(a.run, "scalars.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "tag", "value"])
        for tag in sorted(scalars):
            for step, val in scalars[tag]:
                w.writerow([step, tag, val])
    print(f"wrote {out}: {len(scalars)} tags, {sum(len(v) for v in scalars.values())} rows")


if __name__ == "__main__":
    main()
