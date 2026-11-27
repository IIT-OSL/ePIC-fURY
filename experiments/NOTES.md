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

## 2026-11-27: unitree_rl_lab scripts are written for an older rsl-rl
- What I was doing: Sprint 2 install, reading unitree_rl_lab (commit 4960b84) before training.
- Error (exact line): none run yet; found by reading the code. Its `BasePPORunnerCfg` uses the legacy `policy=RslRlPpoActorCriticCfg(...)`,
  and its `scripts/rsl_rl/train.py` builds `OnPolicyRunner` without converting it. rsl-rl 5.0.1 reads `cfg["actor"]` (ppo.py:477), so it would fail.
  Its `play.py` exports via `runner.alg.policy` / `runner.alg.actor_critic`, which do not exist in rsl-rl >= 4.
- Cause: unitree_rl_lab targets Isaac Lab 2.3.0 with rsl-rl 2.x/3.x; we have Isaac Lab 2.3.2 with rsl-rl-lib 5.0.1.
- Fix: our own copies `scripts/unitree_rl_lab/url_train.py` and `url_play.py` that call Isaac Lab's `handle_deprecated_rsl_rl_cfg`
  (and `handle_deprecated_rsl_rl_checkpoint` in play) and export with `runner.export_policy_to_jit/onnx`. Upstream files untouched.
  Verified: 10-iteration train and play/export both exit 0 (`experiments/_smoke_url_go2_20261127/`).

## 2026-11-27: url_play.py import error (pretrained_checkpoint moved)
- What I was doing: play/export test of the smoke checkpoint with the new play wrapper.
- Error (exact line): `ModuleNotFoundError: No module named 'isaaclab.utils.pretrained_checkpoint'`
- Cause: in Isaac Lab 2.3.2 the module lives in `isaaclab_rl.utils.pretrained_checkpoint` (unitree_rl_lab was written for 2.3.0).
- Fix: import from `isaaclab_rl.utils.pretrained_checkpoint` in `scripts/unitree_rl_lab/url_play.py`. Failed log kept as `play_fail1.log`.

## 2026-11-27: unitree_rl_lab.sh -i not used
- What I was doing: installing unitree_rl_lab.
- Error (exact line): none (not run). `git-lfs` is not installed, `ISAACLAB_PATH` is unset, and the script overwrites
  `$CONDA_PREFIX/etc/conda/activate.d/setenv.sh` and runs `activate-global-python-argcomplete` (changes the user's shell setup).
- Fix: installed with `pip install -e external/unitree_rl_lab/source/unitree_rl_lab` only (pulled in `argcomplete 3.8.0`, the package's one
  dependency). Go2 USD downloaded with `huggingface_hub.snapshot_download(..., allow_patterns=["Go2/*"])` (19 MB), no git-lfs needed.

## 2026-11-27: no X display for the Isaac Sim GUI (Wayland-only desktop)
- What I was doing: relaunching the seed-42 own-policy run with the GUI (Daham asked to watch it in the sim instead of headless).
- Error (exact line): none yet; `DISPLAY` was empty, `XDG_SESSION_TYPE=wayland`, gnome-shell runs with `--no-x11`, and `/tmp/.X11-unix/` held only GDM's
  sockets (X1024, X1025). Isaac Sim's Kit window needs X11.
- Cause: Ubuntu 26.04 GNOME session without Xwayland; the old TurboVNC display `:1` (Docker-era setup) was not running.
- Fix: start a windowed (rootful) Xwayland on the desktop, in tmux window `epic:display`:
  `XDG_RUNTIME_DIR=/run/user/1001 WAYLAND_DISPLAY=wayland-0 Xwayland :2 -decorate -geometry 1900x1000 -noreset`,
  then run Isaac Sim with `DISPLAY=:2`. The "Isaac Sim 5.1.0" window opened on the DP-1 monitor; training speed with the GUI is ~2.95 s/iteration
  (vs ~2.05 s headless). `run_own.sh` ignores Xwayland in its GPU-busy check.
- Also: the first headless launch (stopped with Ctrl-C after ~1 min, 0 iterations) was logged by run_own.sh as "ok". Folder moved to
  `experiments/_archive/own_flat_seed42_20261127-1029_aborted_headless`, README row corrected, and run_own.sh now marks a run
  "incomplete (N/3000)" when the last checkpoint is short of the target.

## 2026-11-27: Isaac Sim window does not scale inside the Xwayland frame
- What I was doing: seed-42 GUI run on Xwayland `:2`; Daham full-screened the outer window.
- Error (exact line): none; the X screen followed the outer window (xrandr showed 1717x900), but the "Isaac Sim 5.1.0" window stayed 1440x900 at 0,0.
- Cause: a rootful Xwayland has no window manager inside it, so nothing resizes, maximises or focuses client windows.
- Fix: started xfwm4 inside the display, in tmux window `epic:wm`: `DISPLAY=:2 xfwm4 --compositor=off` (no restart of Isaac Sim, training unaffected).
  Isaac Sim then has a normal title bar and can be maximised. Fallback without a WM: `DISPLAY=:2 python3 tools/x_fit_window.py` (resizes the
  window to the screen once a second). Cleaner long-term option: log into an X11 session (Xfce/MATE are installed); GNOME 50 here runs `--no-x11`.

## 2026-11-27: seed-42 GUI training froze at iteration 178
- What I was doing: seed-42 GUI run, while Daham moved the camera in the viewport.
- Error (exact line): none; the log stopped at `Learning iteration 178/3000` at 10:50:36, GPU at 6%, process alive (state R, ~244% CPU). The last log lines
  were `[carb.windowing-glfw.gamepad] Joystick with unknown remapping detected ... Pen passthrough / Touch passthrough` (remote-desktop input devices appearing).
- Cause: the simulation timeline was paused (Space bar or the pause button toggles Play/Pause in Isaac Sim). While paused, Isaac Lab keeps rendering and waits,
  so training stalls without an error.
- Fix: Daham pressed Play; training resumed (iteration 184 at 10:56), no data lost. Lesson: in a GUI training run do not press Space / Pause / Stop.

## 2026-11-27: GUI training froze a second time; switched to headless + live checkpoint viewer
- What I was doing: seed-42 GUI run, after the first pause had been cleared.
- Error (exact line): none; stuck at `Learning iteration 184/3000` from 10:55:35, GPU ~8%.
- Cause: the sim was paused again (Space / pause button); a GUI training run stalls whenever its timeline is paused.
- Fix: stopped the GUI run (archived as `_archive/own_flat_seed42_20261127-1036_stopped_gui`, checkpoints model_0/model_100 kept), restarted
  all 4 runs headless (`run_own_20261127-1108.log`), and added `tools/watch_ckpt.py`: a separate Isaac Sim window that plays the newest checkpoint
  (16 robots, plain floor, 2.5 m apart) and reloads every time training saves one. `run_own.sh`'s GPU check ignores this viewer.

## 2026-11-27: training script started by mistake (my error)
- What I was doing: testing the new `gpu_busy()` function in `run_own.sh`.
- Error (exact line): none; the check command `source scripts/run_own.sh` ran the whole script, which started a headless seed-42 run.
- Cause: sourcing the script executes it; only the function should have been loaded.
- Fix: stopped it within ~2 min (51 iterations), folder archived as `_archive/own_flat_seed42_20261127-1104_accidental_start`, README row added.
  Function then tested by extracting it with `sed -n '/^gpu_busy()/,/^}/p'` into a scratch file.

## 2026-11-27: Xwayland :2 window closed, viewer had no display
- What I was doing: starting `tools/watch_ckpt.py` on `DISPLAY=:2`.
- Error (exact line): `xwininfo: error: unable to open display ":2"`
- Cause: the Xwayland process ended cleanly at ~11:11 (socket /tmp/.X11-unix/X2 gone, no error in its log), which is what happens when its outer
  window is closed; xfwm4 exited with it. Headless training was not affected.
- Fix: restarted Xwayland (`epic:display`), xfwm4 (`epic:wm`) and the viewer (`epic:watch`). Closing the Xwayland window again only stops the viewer.
