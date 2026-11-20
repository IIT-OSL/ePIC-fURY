#!/usr/bin/env bash
# Sprint 1: reproduce the built-in Isaac Lab Go2 flat PPO baseline (RSL-RL), stock settings.
# Seeds run strictly one after another. Usage: scripts/run_baseline.sh [seed ...]   (default: 42 43 44)
# Only --task, --headless, --seed and --run_name are passed; --run_name only names the log folder.
set -uo pipefail

WORK=/home/root-daham/ePICfURY/ePIC-fURY
ISAACLAB=/home/root-daham/isaac-installations/IsaacLab
TASK=Isaac-Velocity-Flat-Unitree-Go2-v0
LOG_ROOT=$ISAACLAB/logs/rsl_rl/unitree_go2_flat
README=$WORK/experiments/README.md
SEEDS=("$@"); [ ${#SEEDS[@]} -eq 0 ] && SEEDS=(42 43 44)

source /home/root-daham/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONUNBUFFERED=1

gpu_busy() {  # any compute process on the GPU other than the desktop streamer
  nvidia-smi --query-compute-apps=process_name --format=csv,noheader | grep -v -e sunshine -e '^$' | grep -q .
}

for SEED in "${SEEDS[@]}"; do
  while gpu_busy; do
    echo "[run_baseline] $(date '+%F %T') GPU busy, waiting 5 min before seed $SEED:"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
    sleep 300
  done

  STAMP=$(date +%Y%m%d-%H%M)
  RUN=$WORK/experiments/baseline_flat_seed${SEED}_${STAMP}
  RUN_NAME=baseline_seed${SEED}_${STAMP}
  mkdir -p "$RUN"
  CMD="./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task $TASK --headless --seed $SEED --run_name $RUN_NAME"
  echo "cd $ISAACLAB && PYTHONUNBUFFERED=1 $CMD" > "$RUN/cmd.txt"
  {
    echo "isaaclab: $(git -C "$ISAACLAB" describe --tags --match "v*" --always) $(git -C "$ISAACLAB" rev-parse HEAD)"
    echo "isaaclab dirty files: $(git -C "$ISAACLAB" status --porcelain | wc -l)"
    echo "work: $(git -C "$WORK" rev-parse HEAD) (dirty files: $(git -C "$WORK" status --porcelain | wc -l))"
    echo "rsl-rl-lib: $(pip show rsl-rl-lib 2>/dev/null | awk '/^Version/{print $2}')"
  } > "$RUN/git.txt"

  echo "[run_baseline] $(date '+%F %T') start seed $SEED -> $RUN"
  T0=$(date +%s)
  (cd "$ISAACLAB" && $CMD) 2>&1 | tee "$RUN/train.log"
  RC=${PIPESTATUS[0]}
  T1=$(date +%s)
  WALL=$(( (T1 - T0) / 60 ))

  LOGDIR=$(ls -d "$LOG_ROOT"/*_"$RUN_NAME" 2>/dev/null | tail -n 1)
  ITERS=?
  if [ -n "$LOGDIR" ]; then
    ln -sfn "$LOGDIR" "$RUN/isaaclab_log"
    cp "$LOGDIR/params/env.yaml" "$LOGDIR/params/agent.yaml" "$RUN/" 2>/dev/null
    LAST=$(ls "$LOGDIR"/model_*.pt 2>/dev/null | sed 's/.*model_\([0-9]*\)\.pt/\1/' | sort -n | tail -n 1)
    [ -n "$LAST" ] && ITERS=$((LAST + 1))
  fi
  STATUS=ok; [ "$RC" -ne 0 ] && STATUS="failed (exit $RC)"; [ -z "$LOGDIR" ] && STATUS="$STATUS, no log dir"
  echo "| $(basename "$RUN") | $TASK | $SEED | $ITERS | ${WALL} min | $STATUS | log: ${LOGDIR#$ISAACLAB/} |" >> "$README"
  echo "[run_baseline] $(date '+%F %T') seed $SEED done: $STATUS, ${WALL} min, iterations $ITERS"
done
echo "[run_baseline] all seeds finished"
