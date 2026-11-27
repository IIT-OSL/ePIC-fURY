# Experiments

Filled in by /s0-discover, then one line per run.

## Versions

| Item | Value |
| --- | --- |
| Date recorded | 2026-11-20 |
| GPU / driver / CUDA | NVIDIA GeForce RTX 5090 32 GB / 580.173.02 / CUDA 13.0 (torch 2.7.0+cu128) |
| Isaac Sim | 5.1.0 (pip, conda env `env_isaaclab`) |
| Isaac Lab (tag, commit) | 2.3.2, `v2.3.2-32-g858234d06e`, 858234d06e6845d75420d2558e236526282e5da6 (main) |
| rsl_rl | rsl-rl-lib 5.0.1 |
| unitree_rl_lab (commit) | 4960b84732b0c2ec593dccbfe963fda1bcd7b1e3 (package 0.2.1, same env `env_isaaclab`; Go2 USD from HF `unitreerobotics/unitree_model`) |
| Python | 3.11.15 (env `env_isaaclab`) |
| Run method | `conda activate env_isaaclab` then `./isaaclab.sh -p ...` from `/home/root-daham/isaac-installations/IsaacLab` |
| Go2 flat tasks | `Isaac-Velocity-Flat-Unitree-Go2-v0`, `Isaac-Velocity-Flat-Unitree-Go2-Play-v0` |

## Runs

| Run folder | Task | Seed | Iterations | Wall time | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| baseline_flat_seed42_20261120-0930 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 42 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-30-45_baseline_seed42_20261120-0930; video checked by Daham 2026-11-25 |
| baseline_flat_seed43_20261120-0932 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 43 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-32-48_baseline_seed43_20261120-0932; video checked by Daham 2026-11-25 |
| baseline_flat_seed44_20261120-0934 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 44 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-34-57_baseline_seed44_20261120-0934; video checked by Daham 2026-11-25 |
| _smoke_url_go2_20261127 | Unitree-Go2-Velocity (unitree_rl_lab) | 42 | 10 | ~1 min | ok (smoke) | install check; ~2.05 s/iteration at 4096 envs; play/export + deploy.yaml checked |
| _archive/own_flat_seed42_20261127-1029_aborted_headless | Unitree-Go2-Velocity (unitree_rl_lab) | 42 | ? | 0 min | aborted (stopped by request to relaunch with GUI) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity/2026-11-27_10-29-35_own_seed42_20261127-1029 |
| _archive/own_flat_seed42_20261127-1036_stopped_gui | Unitree-Go2-Velocity (unitree_rl_lab) | 42 | 101 | 25 min | stopped at iteration 184 (GUI run kept pausing; restarted headless, Daham 2026-11-27) (gui) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity/2026-11-27_10-36-28_own_seed42_20261127-1036 |
| _archive/own_flat_seed42_20261127-1104_accidental_start | Unitree-Go2-Velocity (unitree_rl_lab) | 42 | 0 | <2 min | aborted (started by mistake, killed at once) | log: external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity/2026-11-27_11-04-48_own_seed42_20261127-1104 |
