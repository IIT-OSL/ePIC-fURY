# Sprint 2 evaluation: fixed protocol, 3 own seeds vs 3 baseline seeds

Generated 2026-11-27 20:25 by `tools/eval_summary.py` from each run's `eval.csv` (made by `tools/eval.py`, launched with `scripts/run_eval.sh`). Protocol and eval settings: docstring of `tools/eval.py`.

64 envs × 20 s per condition, commands fixed, flat plane, same env seed (0) for every policy. RMSE and power after a 1 s warm-up; fall = base contact or tilt > 0.8 rad. Values: mean ± std over seeds (population std).

## own (Unitree-Go2-Velocity-FullCmd)

Runs: `own_flat_seed42_20261127-1142`, `own_flat_seed43_20261127-1324`, `own_flat_seed44_20261127-1505`

| Condition | Command (vx, vy, wz) | Lin. vel RMSE (m/s) | Yaw RMSE (rad/s) | Fall rate | Power (W) |
| --- | --- | --- | --- | --- | --- |
| stand | (0.0, 0.0, 0.0) | 0.022 ± 0.001 | 0.045 ± 0.001 | 0.000 ± 0.000 | 2.7 ± 0.2 |
| walk_0.5 | (0.5, 0.0, 0.0) | 0.051 ± 0.005 | 0.051 ± 0.002 | 0.000 ± 0.000 | 23.2 ± 0.2 |
| walk_1.0 | (1.0, 0.0, 0.0) | 0.067 ± 0.006 | 0.057 ± 0.004 | 0.000 ± 0.000 | 47.5 ± 0.4 |
| backward_-0.5 | (-0.5, 0.0, 0.0) | 0.060 ± 0.010 | 0.053 ± 0.001 | 0.000 ± 0.000 | 25.7 ± 0.5 |
| sidestep_0.3 | (0.0, 0.3, 0.0) | 0.056 ± 0.006 | 0.058 ± 0.004 | 0.000 ± 0.000 | 22.0 ± 0.1 |
| turn_0.8 | (0.0, 0.0, 0.8) | 0.027 ± 0.001 | 0.066 ± 0.007 | 0.000 ± 0.000 | 16.6 ± 0.3 |
| walk_0.5_push | (0.5, 0.0, 0.0) + pushes | 0.076 ± 0.004 | 0.052 ± 0.001 | 0.000 ± 0.000 | 23.7 ± 0.2 |

## baseline (Isaac-Velocity-Flat-Unitree-Go2-v0)

Runs: `baseline_flat_seed42_20261120-0930`, `baseline_flat_seed43_20261120-0932`, `baseline_flat_seed44_20261120-0934`

| Condition | Command (vx, vy, wz) | Lin. vel RMSE (m/s) | Yaw RMSE (rad/s) | Fall rate | Power (W) |
| --- | --- | --- | --- | --- | --- |
| stand | (0.0, 0.0, 0.0) | 0.036 ± 0.003 | 0.098 ± 0.002 | 0.000 ± 0.000 | 8.1 ± 0.3 |
| walk_0.5 | (0.5, 0.0, 0.0) | 0.118 ± 0.021 | 0.109 ± 0.010 | 0.000 ± 0.000 | 70.0 ± 9.5 |
| walk_1.0 | (1.0, 0.0, 0.0) | 0.091 ± 0.010 | 0.113 ± 0.014 | 0.000 ± 0.000 | 135.0 ± 22.6 |
| backward_-0.5 | (-0.5, 0.0, 0.0) | 0.063 ± 0.010 | 0.100 ± 0.003 | 0.000 ± 0.000 | 64.6 ± 7.2 |
| sidestep_0.3 | (0.0, 0.3, 0.0) | 0.068 ± 0.015 | 0.113 ± 0.006 | 0.000 ± 0.000 | 54.1 ± 1.6 |
| turn_0.8 | (0.0, 0.0, 0.8) | 0.070 ± 0.009 | 0.740 ± 0.049 | 0.161 ± 0.228 | 23.5 ± 4.3 |
| walk_0.5_push | (0.5, 0.0, 0.0) + pushes | 0.122 ± 0.020 | 0.109 ± 0.010 | 0.000 ± 0.000 | 70.3 ± 9.8 |

## Own vs baseline (means over seeds)

| Condition | Lin. RMSE own | Lin. RMSE baseline | Yaw RMSE own | Yaw RMSE baseline | Falls own | Falls baseline | Power own (W) | Power baseline (W) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stand | 0.022 | 0.036 | 0.045 | 0.098 | 0.000 | 0.000 | 2.7 | 8.1 |
| walk_0.5 | 0.051 | 0.118 | 0.051 | 0.109 | 0.000 | 0.000 | 23.2 | 70.0 |
| walk_1.0 | 0.067 | 0.091 | 0.057 | 0.113 | 0.000 | 0.000 | 47.5 | 135.0 |
| backward_-0.5 | 0.060 | 0.063 | 0.053 | 0.100 | 0.000 | 0.000 | 25.7 | 64.6 |
| sidestep_0.3 | 0.056 | 0.068 | 0.058 | 0.113 | 0.000 | 0.000 | 22.0 | 54.1 |
| turn_0.8 | 0.027 | 0.070 | 0.066 | 0.740 | 0.000 | 0.161 | 16.6 | 23.5 |
| walk_0.5_push | 0.076 | 0.122 | 0.052 | 0.109 | 0.000 | 0.000 | 23.7 | 70.3 |

The baseline policy reads base linear velocity, which the real robot cannot measure, and was trained without pushes; it is a sim-only reference. It also had only 300 iterations (own: 3,000), and it was trained with heading commands (`heading_command=True`: yaw rate comes from a heading controller, so a constant 0.8 rad/s yaw command is rarely seen in training). That explains its poor turn_0.8 result (it barely turns; one seed tips over in 48 % of envs). The comparison is therefore not like-for-like; it shows the own policy is at least as good as the Sprint 1 reference on every condition.

## Per-seed overall (mean over the 7 conditions)

| Run | Falls (total envs, 7 × 64) | Mean lin. RMSE (m/s) | Mean yaw RMSE (rad/s) | Mean power (W) |
| --- | --- | --- | --- | --- |
| own_flat_seed42_20261127-1142 | 0 | 0.0549 | 0.0541 | 23.0 |
| own_flat_seed43_20261127-1324 | 0 | 0.0510 | 0.0556 | 23.0 |
| own_flat_seed44_20261127-1505 | 0 | 0.0480 | 0.0541 | 23.1 |
| own_flat_seed42_repeat_20261127-1644 | 0 | 0.0549 | 0.0541 | 23.0 |
| baseline_flat_seed42_20261120-0930 | 0 | 0.0866 | 0.1975 | 56.2 |
| baseline_flat_seed43_20261120-0932 | 31 | 0.0839 | 0.2042 | 70.3 |
| baseline_flat_seed44_20261120-0934 | 0 | 0.0728 | 0.1912 | 55.9 |

Ranking rule: fewest falls, then lowest mean linear-velocity RMSE, then lowest mean yaw RMSE (own seeds only; the repeat run is listed for reference).

**Best own seed by this rule: `own_flat_seed44_20261127-1505`.** Daham picks the policy to deploy.

Decision 2026-11-27: Daham picked seed 44 (`own_flat_seed44_20261127-1505`, `model_2999.pt`) for deployment (experiments/DECISIONS.md).
