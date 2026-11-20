# Errors and fixes

One entry per problem. Newest at the bottom.

<!--
## YYYY-MM-DD: short title
- What I was doing:
- Error (exact line):
- Cause:
- Fix:
-->

## 2026-11-20: list_envs.py rejects --headless
- What I was doing: Sprint 0 smoke test, `./isaaclab.sh -p scripts/environments/list_envs.py --headless`
- Error (exact line): `list_envs.py: error: unrecognized arguments: --headless`
- Cause: in Isaac Lab 2.3.2 list_envs.py hard-codes `AppLauncher(headless=True)` and only accepts `--keyword`.
- Fix: run without the flag: `./isaaclab.sh -p scripts/environments/list_envs.py --keyword Go2`

## 2026-11-20: list_envs.py prints no table when output goes to a file
- What I was doing: same command, stdout redirected to a log file
- Error (exact line): none; exit code 0 but the environment table is missing from the log
- Cause: stdout is block-buffered when redirected, and `simulation_app.close()` exits the process before the buffer is flushed.
- Fix: set `PYTHONUNBUFFERED=1` (or pass `python -u`) whenever an Isaac Lab script's output is tee'd/redirected.

## 2026-11-20: GPU in use by another user's job before Sprint 1 launch
- What I was doing: pre-launch `nvidia-smi` check before the Sprint 1 smoke test.
- Error (exact line): none; `nvidia-smi` showed `/shared/miniforge3/bin/python3.13 ... neuralbench eeg image ...` (user `yenuli`) at 91% util, 574 W.
- Cause: the workstation is shared; other users train on the same RTX 5090.
- Fix: did not launch until the GPU was idle (the job ended a few minutes later). `scripts/run_baseline.sh` now checks
  `nvidia-smi --query-compute-apps` before each seed and waits (5 min polls) while any compute process other than `sunshine` is on the GPU.

## 2026-11-20: pandas not installed in env_isaaclab
- What I was doing: planning tools/tb_to_csv.py and tools/plot_curves.py.
- Error (exact line): `ModuleNotFoundError: No module named 'pandas'`
- Cause: Isaac Lab's env does not ship pandas.
- Fix: tools use only the csv module, numpy, matplotlib and tensorboard (all present). No install needed.

## 2026-11-20: playback loaded model_50.pt instead of the final model_299.pt
- What I was doing: Sprint 1 Step 4, `scripts/run_play.sh` on the three baseline runs.
- Error (exact line): `[run_play] ... baseline_flat_seed42_20261120-0930 <- model_50.pt` (no crash; wrong checkpoint picked silently)
- Cause: the script picked the latest checkpoint with `ls $LOGDIR/model_*.pt | sort -t_ -k2 -n`. The full path contains other
  underscores (`unitree_go2_flat`, `baseline_seed42_...`), so field 2 was not the iteration number and the numeric sort was meaningless.
- Fix: sort on the file name only: `ls model_*.pt | sort -V | tail -n 1` inside the log dir. Wrong videos/exports (from model_50)
  moved to `experiments/_archive/play_wrong_ckpt_model50/` (not deleted), playback re-run on model_299.pt.
  Lesson: always print and check which checkpoint a play/eval script loaded.

## 2026-11-20: git.txt shows a different Isaac Lab tag name than README
- What I was doing: checking git.txt of the baseline runs.
- Error (exact line): `isaaclab: training-checkpoints-develop-17-g858234d06e 858234d06e...` (README says `v2.3.2-32-g858234d06e`)
- Cause: `git describe --tags` picks the nearest tag of any name; Isaac Lab has a non-release tag `training-checkpoints-develop` closer to HEAD.
- Fix: none needed for the recorded runs (same commit 858234d06e, which is what matters). run_baseline.sh now uses
  `git describe --tags --match "v*"` so future git.txt files show the release tag.
