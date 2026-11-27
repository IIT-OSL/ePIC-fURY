#!/usr/bin/env bash
# Sprint 2: train the deployable flat-ground Go2 policy (unitree_rl_lab task, settings as audited 2026-11-27).
# Runs strictly one after another: seeds 42 43 44, then 42 again (reproducibility run).
# Usage: scripts/run_own.sh [seed ...]       env: ITERS (default 3000, decided by Daham 2026-11-27)
#        GUI_FIRST=1 GUI_DISPLAY=:2  -> the FIRST run opens the Isaac Sim window (no --headless) on that X display;
#        all later runs stay headless (Daham, 2026-11-27). Rendering does not change the physics or the training settings.
# Only --task, --headless (not for a GUI run), --seed, --max_iterations and --run_name are passed; --run_name only names the log folder.
set -uo pipefail

WORK=/home/root-daham/ePICfURY/ePIC-fURY
URL=$WORK/external/unitree_rl_lab
ISAACLAB=/home/root-daham/isaac-installations/IsaacLab
TASK=Unitree-Go2-Velocity
ITERS=${ITERS:-3000}
GUI_FIRST=${GUI_FIRST:-0}
GUI_DISPLAY=${GUI_DISPLAY:-:2}
LOG_ROOT=$URL/logs/rsl_rl/unitree_go2_velocity
README=$WORK/experiments/README.md
SEEDS=("$@"); [ ${#SEEDS[@]} -eq 0 ] && SEEDS=(42 43 44 42)

source /home/root-daham/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONUNBUFFERED=1

gpu_busy() {  # any compute process on the GPU except the desktop streamer / terminal / X server / our checkpoint viewer
  local pid cmd
  for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader); do
    cmd=$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null)
    [ -z "$cmd" ] && continue
    echo "$cmd" | grep -q -e sunshine -e ptyxis -e Xwayland -e watch_ckpt.py && continue
    return 0
  done
  return 1
}

declare -A SEEN=()
IDX=0
for SEED in "${SEEDS[@]}"; do
  if [ "$GUI_FIRST" = 1 ] && [ $IDX -eq 0 ]; then MODE_FLAG=""; ENVPFX="DISPLAY=$GUI_DISPLAY "; MODE=gui; else MODE_FLAG="--headless"; ENVPFX=""; MODE=headless; fi
  IDX=$((IDX + 1))
  VARIANT=""
  [ -n "${SEEN[$SEED]:-}" ] && VARIANT="_repeat"
  SEEN[$SEED]=1

  while gpu_busy; do
    echo "[run_own] $(date '+%F %T') GPU busy, waiting 5 min before seed $SEED:"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
    sleep 300
  done

  STAMP=$(date +%Y%m%d-%H%M)
  RUN=$WORK/experiments/own_flat_seed${SEED}${VARIANT}_${STAMP}
  RUN_NAME=own_seed${SEED}${VARIANT}_${STAMP}
  mkdir -p "$RUN"
  CMD="python $WORK/scripts/unitree_rl_lab/url_train.py $MODE_FLAG --task $TASK --seed $SEED --max_iterations $ITERS --run_name $RUN_NAME"
  echo "cd $URL && ${ENVPFX}PYTHONUNBUFFERED=1 $CMD" > "$RUN/cmd.txt"
  {
    echo "work: $(git -C "$WORK" rev-parse HEAD) (dirty files: $(git -C "$WORK" status --porcelain | wc -l))"
    echo "unitree_rl_lab: $(git -C "$URL" rev-parse HEAD) (local edits: $(git -C "$URL" diff --name-only | tr '\n' ' '))"
    echo "isaaclab: $(git -C "$ISAACLAB" describe --tags --match "v*" --always) $(git -C "$ISAACLAB" rev-parse HEAD)"
    echo "rsl-rl-lib: $(pip show rsl-rl-lib 2>/dev/null | awk '/^Version/{print $2}')"
  } > "$RUN/git.txt"

  echo "[run_own] $(date '+%F %T') start seed $SEED$VARIANT ($ITERS it, $MODE) -> $RUN"
  T0=$(date +%s)
  (cd "$URL" && if [ "$MODE" = gui ]; then DISPLAY=$GUI_DISPLAY $CMD; else $CMD; fi) 2>&1 | tee "$RUN/train.log"
  RC=${PIPESTATUS[0]}
  WALL=$(( ($(date +%s) - T0) / 60 ))

  LOGDIR=$(ls -d "$LOG_ROOT"/*_"$RUN_NAME" 2>/dev/null | tail -n 1)
  DONE=?
  if [ -n "$LOGDIR" ]; then
    ln -sfn "$LOGDIR" "$RUN/url_log"
    cp "$LOGDIR"/params/{env,agent,deploy}.yaml "$RUN/" 2>/dev/null
    LAST=$(cd "$LOGDIR" && ls model_*.pt 2>/dev/null | sort -V | tail -n 1 | sed 's/model_\([0-9]*\)\.pt/\1/')
    [ -n "$LAST" ] && DONE=$((LAST + 1))
  fi
  STATUS=ok; [ "$DONE" != "$ITERS" ] && STATUS="incomplete ($DONE/$ITERS)"; [ "$RC" -ne 0 ] && STATUS="failed (exit $RC)"; [ -z "$LOGDIR" ] && STATUS="$STATUS, no log dir"
  echo "| $(basename "$RUN") | $TASK (unitree_rl_lab) | $SEED${VARIANT:+ (repeat)} | $DONE | ${WALL} min | $STATUS ($MODE) | log: ${LOGDIR#$WORK/} |" >> "$README"
  echo "[run_own] $(date '+%F %T') seed $SEED$VARIANT done: $STATUS, ${WALL} min, iterations $DONE"
done
echo "[run_own] all runs finished"
