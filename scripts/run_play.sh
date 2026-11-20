#!/usr/bin/env bash
# Sprint 1: play the final checkpoint of a baseline run with video, and collect the exported policy.
# Usage: scripts/run_play.sh experiments/baseline_flat_seed<N>_<stamp> [more run folders ...]
# Stock Play task; only --num_envs 16 and --video_length 500 are set (playback only, no training settings).
set -uo pipefail

ISAACLAB=/home/root-daham/isaac-installations/IsaacLab
TASK=Isaac-Velocity-Flat-Unitree-Go2-Play-v0
source /home/root-daham/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONUNBUFFERED=1

for RUN in "$@"; do
  RUN=$(realpath "$RUN")
  LOGDIR=$(realpath "$RUN/isaaclab_log")
  # highest iteration number; sort on the file name only (the log path itself contains underscores)
  CKPT="$LOGDIR/$(cd "$LOGDIR" && ls model_*.pt | sort -V | tail -n 1)"
  CMD="./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task $TASK --headless --video --video_length 500 --num_envs 16 --checkpoint $CKPT"
  echo "cd $ISAACLAB && PYTHONUNBUFFERED=1 $CMD" > "$RUN/play_cmd.txt"
  echo "[run_play] $(date '+%F %T') $RUN <- $(basename "$CKPT")"
  (cd "$ISAACLAB" && timeout 1800 $CMD) 2>&1 | tee "$RUN/play.log"
  RC=${PIPESTATUS[0]}
  MP4=$(ls -t "$LOGDIR"/videos/play/*.mp4 2>/dev/null | head -n 1)
  [ -n "$MP4" ] && cp "$MP4" "$RUN/play.mp4"
  mkdir -p "$RUN/exported"
  cp "$LOGDIR"/exported/* "$RUN/exported/" 2>/dev/null
  echo "[run_play] exit $RC, video: ${MP4:-MISSING}, exported: $(ls "$RUN/exported" | tr '\n' ' ')"
done
