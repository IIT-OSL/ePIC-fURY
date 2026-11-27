# Sprint 2: Go2 own deployable policy (unitree_rl_lab), 3 seeds + 1 repeat

Recorded 2026-11-27. Task `Unitree-Go2-Velocity-FullCmd` (unitree_rl_lab `Unitree-Go2-Velocity` with the full command
range and no command curriculum; audit in `experiments/policy_inputs.md`, decision in `experiments/DECISIONS.md`).

## Setup

| Item | Value |
| --- | --- |
| Train task | `Unitree-Go2-Velocity-FullCmd` |
| Iterations | 3,000 per run (unitree default 50,000) |
| num_envs | 4096 |
| Policy inputs | 45 (all measurable on the real robot); critic 60 |
| Control | Kp 25, Kd 0.5, action scale 0.25, 50 Hz |
| Seeds | 42, 43, 44, then 42 again (reproducibility run) |
| Launch | `ITERS=3000 scripts/run_own.sh` (headless), log `experiments/run_own_20261127-1142.log` |
| Wall time | 101, 101, 98, 94 min |

## Per-seed results (final iteration, 2999)

Values are the training-log values at the last iteration (episodes that ended in that iteration, random commands).
This is not the fixed eval protocol; that comes from `/s2-eval`.

| Run | Mean reward | Mean reward, last 100 it. | Episode length | track_lin_vel_xy | track_ang_vel_z | error_vel_xy (m/s) | error_vel_yaw (rad/s) | bad_orientation rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| own_flat_seed42_20261127-1142 | 30.54 | 30.31 | 1000.0 | 1.429 | 0.709 | 0.178 | 0.194 | 0.0048 |
| own_flat_seed43_20261127-1324 | 30.46 | 30.45 | 1000.0 | 1.427 | 0.708 | 0.183 | 0.194 | 0.0078 |
| own_flat_seed44_20261127-1505 | 30.17 | 30.39 | 995.5 | 1.420 | 0.704 | 0.187 | 0.198 | 0.0072 |
| **mean ± std (42/43/44)** | **30.39 ± 0.16** | 30.38 ± 0.06 | **998.5 ± 2.1** | 1.425 ± 0.004 | 0.707 ± 0.002 | **0.182 ± 0.004** | **0.195 ± 0.002** | 0.0066 ± 0.0013 |
| own_flat_seed42_repeat_20261127-1644 | 30.54 | 30.31 | 1000.0 | 1.429 | 0.709 | 0.178 | 0.194 | 0.0048 |

std is the population std over the 3 seeds (same as the plots). Max episode length is 1000 steps (20 s).

## Plateau

Mean reward (3-seed mean) at iteration 1500: 29.33; at 2000: 30.01; at 3000: 30.39.
About +1.1 over the last 1,500 iterations, against +29 in the first 1,500. See `mean_reward.png`.

## Reproducibility (seed 42 run twice)

`repro_seed42.png` / `.csv`, made with `tools/plot_repro.py`.
The two seed-42 runs are **bit-identical**: every logged value (reward, episode length, tracking terms, errors,
terminations) has a max absolute difference of 0 over all 3,000 iterations, and the final checkpoints
`model_2999.pt` have identical actor and critic weights (checked with `torch.equal`; seed 42 vs 43 differ, as expected).
GPU physics is not guaranteed bit-exact in general; on this machine, with the same software versions and the GPU
used by one job at a time, it was. Only the wall time differed (101 vs 94 min).

## Figures (grayscale, 1600x900, each with its CSV)

| File | Content |
| --- | --- |
| mean_reward.png | mean episode reward, mean ± std over seeds 42/43/44 |
| mean_episode_length.png | mean episode length |
| track_lin_vel_xy.png, track_ang_vel_z.png | velocity-tracking reward terms |
| error_vel_xy.png, error_vel_yaw.png | velocity / yaw-rate tracking error |
| bad_orientation_termination.png | fall (bad orientation) termination rate |
| repro_seed42.png | seed 42 vs seed 42 repeat, mean reward |

Commands:

```bash
python tools/plot_curves.py experiments/own_flat_seed42_20261127-1142 experiments/own_flat_seed43_20261127-1324 \
    experiments/own_flat_seed44_20261127-1505 -o results/own_flat --preset url --label "Go2 own policy (FullCmd)"
python tools/plot_repro.py experiments/own_flat_seed42_20261127-1142 experiments/own_flat_seed42_repeat_20261127-1644 \
    -o results/own_flat/repro_seed42.png
```

The Sprint 1 reward (33.87) is not comparable: different reward terms and a harder task (deployable inputs, motor model,
pushes, mass and friction randomisation).
