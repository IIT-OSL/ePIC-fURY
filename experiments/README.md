# Experiments

One folder per run. Versions below, then one table per sprint.
Errors and fixes are in `NOTES.md`, decisions in `DECISIONS.md`, and the audit of the own-policy task in `policy_inputs.md`.

## Versions

| Item | Value |
| --- | --- |
| Date recorded | 2026-11-20 (unitree_rl_lab rows added 2026-11-27) |
| GPU / driver / CUDA | NVIDIA GeForce RTX 5090 32 GB / 580.173.02 / CUDA 13.0 (torch 2.7.0+cu128) |
| Isaac Sim | 5.1.0 (pip, conda env `env_isaaclab`) |
| Isaac Lab (tag, commit) | 2.3.2, `v2.3.2-32-g858234d06e`, 858234d06e6845d75420d2558e236526282e5da6 (main) |
| rsl_rl | rsl-rl-lib 5.0.1 |
| unitree_rl_lab (commit) | 4960b84732b0c2ec593dccbfe963fda1bcd7b1e3 (package 0.2.1, same env `env_isaaclab`; Go2 USD from HF `unitreerobotics/unitree_model`; only local edit: `UNITREE_MODEL_DIR`) |
| Python | 3.11.15 (env `env_isaaclab`) |
| Run method, Isaac Lab tasks | `conda activate env_isaaclab`, then `./isaaclab.sh -p ...` from `/home/root-daham/isaac-installations/IsaacLab` |
| Run method, unitree_rl_lab tasks | our wrappers `scripts/unitree_rl_lab/url_train.py` / `url_play.py`, run from `external/unitree_rl_lab` (see CLAUDE.md); 4 own runs via `scripts/run_own.sh` |
| Sprint 1 tasks (built-in) | `Isaac-Velocity-Flat-Unitree-Go2-v0`, `Isaac-Velocity-Flat-Unitree-Go2-Play-v0` |
| Sprint 2 task (own policy) | `Unitree-Go2-Velocity-FullCmd`: unitree_rl_lab `Unitree-Go2-Velocity` with the full command range and no command curriculum (`scripts/unitree_rl_lab/epic_tasks/`, approved 2026-11-27) |

## Sprint 1: built-in Isaac Lab baseline (done)

| Run folder | Task | Seed | Iterations | Wall time | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| baseline_flat_seed42_20261120-0930 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 42 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-30-45_baseline_seed42_20261120-0930; video checked by Daham 2026-11-25 |
| baseline_flat_seed43_20261120-0932 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 43 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-32-48_baseline_seed43_20261120-0932; video checked by Daham 2026-11-25 |
| baseline_flat_seed44_20261120-0934 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 44 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-34-57_baseline_seed44_20261120-0934; video checked by Daham 2026-11-25 |

Results: `results/baseline_flat/summary.md`. Sprint 1 smoke run: `_smoke/`.

## Sprint 2: smoke tests

| Run folder | Task | Seed | Iterations | Wall time | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| _smoke_url_go2_20261127 | Unitree-Go2-Velocity | 42 | 10 | ~1 min | ok (smoke) | install check; ~2.05 s/iteration at 4096 envs; play/export + deploy.yaml checked |
| _smoke_fullcmd_20261127 | Unitree-Go2-Velocity-FullCmd | 42 | 5 | ~1 min | ok (smoke) | new task variant check; resolved env/agent/deploy.yaml diffed against the audited task: only command ranges + curriculum differ |

## Sprint 2: archived starts (not part of the 4 runs; kept per rule 7)

All in `experiments/_archive/`. Logs under `external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity/`.

| Run folder | Task | Seed | Last checkpoint | Wall time | Why stopped |
| --- | --- | --- | --- | --- | --- |
| own_flat_seed42_20261127-1029_aborted_headless | Unitree-Go2-Velocity | 42 | none (0 it) | ~1 min | stopped to relaunch with the GUI (Daham's request) |
| own_flat_seed42_20261127-1036_stopped_gui | Unitree-Go2-Velocity | 42 | model_100 (184 it) | 25 min | GUI run froze twice when the sim got paused; switched to headless |
| own_flat_seed42_20261127-1104_accidental_start | Unitree-Go2-Velocity | 42 | model_0 (51 it) | <2 min | started by mistake while testing the GPU check (my error), killed at once |
| own_flat_seed42_20261127-1108_curriculum_stuck | Unitree-Go2-Velocity | 42 | model_800 (824 it) | 28 min | command curriculum stuck at ±0.1 m/s for 824 iterations; restarted on `-FullCmd` (evidence for the report) |

## Sprint 2: own deployable policy, 4 runs (seeds 42, 43, 44, then 42 again), 3,000 iterations, headless

Started 2026-11-27 11:42 with `scripts/run_own.sh` (tmux `epic:own`, log `experiments/run_own_20261127-1142.log`).
Logs under `external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity_fullcmd/`. Rows are appended by `run_own.sh` when each run finishes.

| Run folder | Task | Seed | Iterations | Wall time | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| own_flat_seed42_20261127-1142 | Unitree-Go2-Velocity-FullCmd | 42 | 3000 | 101 min | ok (headless) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity_fullcmd/2026-11-27_11-42-57_own_seed42_20261127-1142 |
| own_flat_seed43_20261127-1324 | Unitree-Go2-Velocity-FullCmd | 43 | 3000 | 101 min | ok (headless) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity_fullcmd/2026-11-27_13-24-25_own_seed43_20261127-1324 |
| own_flat_seed44_20261127-1505 | Unitree-Go2-Velocity-FullCmd | 44 | 3000 | 98 min | ok (headless) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity_fullcmd/2026-11-27_15-05-51_own_seed44_20261127-1505 |
| own_flat_seed42_repeat_20261127-1644 | Unitree-Go2-Velocity-FullCmd | 42 (repeat) | 3000 | 94 min | ok (headless) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity_fullcmd/2026-11-27_16-44-50_own_seed42_repeat_20261127-1644 |

All 4 finished 2026-11-27 18:19. Results: `results/own_flat/summary.md` (final reward 30.39 ± 0.16 over seeds 42/43/44; the seed-42 repeat is bit-identical to the first seed-42 run).
