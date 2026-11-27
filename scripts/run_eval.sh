#!/usr/bin/env bash
# Sprint 2 eval: tools/eval.py (fixed 7-condition protocol) on every finished own_flat run and the 3 baseline_flat runs.
# Writes eval.csv + eval.log + eval_cmd.txt into each run folder. Headless, one run after another.
# Usage: scripts/run_eval.sh
set -u
WORK=/home/root-daham/ePICfURY/ePIC-fURY
URL=$WORK/external/unitree_rl_lab
source /home/root-daham/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
cd "$URL"
export PYTHONUNBUFFERED=1

declare -a JOBS=()
for d in "$WORK"/experiments/own_flat_seed4[234]_2026* "$WORK"/experiments/own_flat_seed42_repeat_2026*; do
  JOBS+=("Unitree-Go2-Velocity-FullCmd|$d")
done
for d in "$WORK"/experiments/baseline_flat_seed4[234]_2026*; do
  JOBS+=("Isaac-Velocity-Flat-Unitree-Go2-v0|$d")
done

for job in "${JOBS[@]}"; do
  task=${job%%|*}; run=${job#*|}
  echo "[run_eval] $(date '+%F %T') $task  $(basename "$run")"
  python "$WORK/tools/eval.py" --headless --task "$task" --run "$run" 2>&1 | tee "$run/eval.log" | grep -E "^\[eval\]|^\||^Eval:|Traceback|Error"
  [ -f "$run/eval.csv" ] || echo "[run_eval] FAILED: $run"
done
echo "[run_eval] $(date '+%F %T') all evals finished"
