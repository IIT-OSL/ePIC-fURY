# Sprint 1: Go2 flat PPO baseline (Isaac Lab built-in task), 3 seeds

Recorded 2026-11-20. Stock settings, nothing changed in env, rewards, gains, observations, actions or PPO.

## Versions

| Item | Value |
| --- | --- |
| GPU / driver / CUDA | NVIDIA GeForce RTX 5090 32 GB / 580.173.02 / CUDA 13.0 (torch 2.7.0+cu128) |
| Isaac Sim | 5.1.0 (pip, conda env `env_isaaclab`) |
| Isaac Lab | 2.3.2, `v2.3.2-32-g858234d06e`, commit 858234d06e6845d75420d2558e236526282e5da6 |
| rsl_rl | rsl-rl-lib 5.0.1 |
| Python | 3.11.15 |
| Run method | `conda activate env_isaaclab`, `./isaaclab.sh -p ...` from the Isaac Lab root |

## Setup

| Item | Value |
| --- | --- |
| Train task | `Isaac-Velocity-Flat-Unitree-Go2-v0` |
| Play task | `Isaac-Velocity-Flat-Unitree-Go2-Play-v0` (16 envs, 500 steps, video) |
| Iterations | 300 (default `max_iterations` of `UnitreeGo2FlatPPORunnerCfg`) |
| num_envs | 4096 |
| Steps per env per iteration | 24 (98,304 transitions per iteration, about 29.5 M env steps per run) |
| Sim dt / decimation | 0.005 s / 4 (policy at 50 Hz) |
| Networks | actor and critic MLP 128-128-128, ELU |
| Seeds | 42, 43, 44 |

## Per-seed results

"Final" = value logged at the last iteration (299). "Last 10" = mean over iterations 290-299 (less noisy).
Std across seeds is the sample std (n-1).

| Seed | Run folder | Training time | Wall time (incl. startup) | Final reward | Final ep. length | Last-10 reward | Last-10 ep. length |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | `experiments/baseline_flat_seed42_20261120-0930` | 110.3 s | 2 min 03 s | 33.34 | 1000.0 | 33.18 | 994.5 |
| 43 | `experiments/baseline_flat_seed43_20261120-0932` | 110.4 s | 2 min 06 s | 34.31 | 1000.0 | 34.00 | 998.8 |
| 44 | `experiments/baseline_flat_seed44_20261120-0934` | 111.3 s | 2 min 05 s | 33.95 | 990.6 | 34.12 | 994.0 |
| **mean ± std** | | 110.7 ± 0.5 s | | **33.87 ± 0.49** | **996.9 ± 5.4** | **33.76 ± 0.51** | **995.8 ± 2.7** |

Episode length is capped at 1000 steps (20 s at 50 Hz), so ~1000 means almost no robot falls.

Other final values (mean of 3 seeds, iteration 299): `track_lin_vel_xy_exp` 1.418, `track_ang_vel_z_exp` 0.636,
base-contact termination rate 0.0043.

## Plateau

- Mean episode length passes 950 at iteration **40** and stays near 1000 from then on.
- Mean reward has no hard plateau within 300 iterations. It rises fast until ~200 (29.3), then flattens:
  32.2 at 250, 33.3 at 275, 33.9 at 299. The 20-iteration smoothed curve reaches 90% of its total gain at iteration
  **222** and 95% at iteration **249**. So it is levelling off from about iteration 250 but still creeping up (+1.6 over the
  last 50 iterations). This matches the stock 300-iteration budget; we did not train longer because settings stay default.

## Figures (1600x900 PNG, grayscale; CSV beside each, columns iteration, mean, std, one per seed)

Band = ±1 population std across the 3 seeds.

- `results/baseline_flat/mean_reward.png` (+ `.csv`), tag `Train/mean_reward`
- `results/baseline_flat/mean_episode_length.png` (+ `.csv`), tag `Train/mean_episode_length`
- `results/baseline_flat/track_lin_vel_xy.png` (+ `.csv`), tag `Episode_Reward/track_lin_vel_xy_exp`
- `results/baseline_flat/track_ang_vel_z.png` (+ `.csv`), tag `Episode_Reward/track_ang_vel_z_exp`
- `results/baseline_flat/base_contact_termination.png` (+ `.csv`), tag `Episode_Termination/base_contact`
  (fraction of envs whose last episode ended by base contact)

All raw scalars per run: `experiments/baseline_flat_seed<N>_*/scalars.csv` (step, tag, value; 26 tags).

## Videos and exported policies (from the final checkpoint `model_299.pt`)

- `experiments/baseline_flat_seed42_20261120-0930/play.mp4`, `exported/policy.pt`, `exported/policy.onnx`
- `experiments/baseline_flat_seed43_20261120-0932/play.mp4`, `exported/policy.pt`, `exported/policy.onnx`
- `experiments/baseline_flat_seed44_20261120-0934/play.mp4`, `exported/policy.pt`, `exported/policy.onnx`

## Run-to-run spread

The three seeds land within about 1 reward point of each other (33.3 to 34.3 final, std 0.49, about 1.5% of the mean),
and the ±1 std band in the curves stays narrow over the whole run, widest around iterations 120-180 while the reward
is climbing fastest. Some spread is expected even with fixed seeds: PhysX on the GPU is not bit-exact between runs
(parallel reductions, contact ordering), so two runs with the same seed would also differ slightly. A repeat of seed 42
was not part of Sprint 1. The spread here is small enough to treat the pipeline as reproducing on this machine.

## How to reproduce

```
scripts/run_baseline.sh            # seeds 42 43 44, one after another
scripts/run_play.sh experiments/baseline_flat_seed42_* ...
python tools/tb_to_csv.py <run_folder>
python tools/plot_curves.py <run_folders...> -o results/baseline_flat --label "Go2 flat baseline (3 seeds)"
```
Exact per-run commands are in each run folder's `cmd.txt` and `play_cmd.txt`.
