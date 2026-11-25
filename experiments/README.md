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
| unitree_rl_lab (commit) | TBD |
| Python | 3.11.15 (env `env_isaaclab`) |
| Run method | `conda activate env_isaaclab` then `./isaaclab.sh -p ...` from `/home/root-daham/isaac-installations/IsaacLab` |
| Go2 flat tasks | `Isaac-Velocity-Flat-Unitree-Go2-v0`, `Isaac-Velocity-Flat-Unitree-Go2-Play-v0` |

## Runs

| Run folder | Task | Seed | Iterations | Wall time | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| baseline_flat_seed42_20261120-0930 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 42 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-30-45_baseline_seed42_20261120-0930; video checked by Daham 2026-11-25 |
| baseline_flat_seed43_20261120-0932 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 43 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-32-48_baseline_seed43_20261120-0932; video checked by Daham 2026-11-25 |
| baseline_flat_seed44_20261120-0934 | Isaac-Velocity-Flat-Unitree-Go2-v0 | 44 | 300 | 2 min | ok | log: logs/rsl_rl/unitree_go2_flat/2026-11-20_09-34-57_baseline_seed44_20261120-0934; video checked by Daham 2026-11-25 |
