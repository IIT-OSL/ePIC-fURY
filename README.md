# ePIC-fURY

Unitree Go2 Edu PPO locomotion with Isaac Lab and RSL-RL, first half of the IIT internship (deadline 15 Dec 2026).

The goal of this phase is to show that a Go2 walking policy can be **trained, evaluated, reproduced and deployed** independently. Research novelty is not the goal yet; this is the groundwork for the later TAPS research problem.

1. Reproduce the built-in Isaac Lab Go2 flat-ground velocity task (3 seeds).
2. Train our own deployable flat-ground, blind (proprioception-only) policy in `unitree_rl_lab` (3 seeds plus a repeat run).
3. Evaluate it with a fixed protocol and record video.
4. Prepare sim-to-real: verify joint order, action and observation scaling, control rate and policy inputs; sim-to-sim in MuJoCo.
5. Test on the real Go2 at WSO2.

## Status (27 Nov 2026)

| Sprint | Dates | Content | Status |
| --- | --- | --- | --- |
| 0 | 19–20 Nov | Environment setup, version record, project rules | done |
| 1 | 19–22 Nov | Built-in Isaac Lab Go2 flat baseline, 3 seeds, curves, playback | done: final reward 33.87 ± 0.49, episode length 996.9 ± 5.4 / 1000 |
| 2 | 23–29 Nov | Own deployable policy in unitree_rl_lab: install, input audit, 4 training runs, eval, video | in progress: install, audit and 4 training runs done (final reward 30.39 ± 0.16, episode length 998.5 / 1000, repeat run bit-identical); eval and video next |
| 3 | 30 Nov – 6 Dec | Sim-to-real checklist, golden test, MuJoCo sim-to-sim, WSO2 robot test (3 Dec, backup 8 Dec) | not started |
| 4 | 7–15 Dec | Fixes, second robot session, results, report, Medium tutorial, presentation | not started |

## Software

| Item | Version |
| --- | --- |
| GPU | NVIDIA RTX 5090 32 GB, driver 580.173.02, CUDA 13.0 (PyTorch 2.7.0+cu128) |
| Isaac Sim | 5.1.0 (pip, conda env `env_isaaclab`) |
| Isaac Lab | 2.3.2 (`v2.3.2-32-g858234d06e`) |
| RSL-RL | rsl-rl-lib 5.0.1 |
| unitree_rl_lab | commit `4960b84` |
| Python | 3.11.15 |
| OS | Ubuntu 26.04 |

Full version table: [`experiments/README.md`](experiments/README.md).

## Folders

| Folder / file | What it holds |
| --- | --- |
| [`experiments/`](experiments/) | **One folder per training run.** Each has `cmd.txt` (exact command), `git.txt` (code versions), `train.log`, `env.yaml` / `agent.yaml` (full configuration) and, for unitree_rl_lab runs, `deploy.yaml`, plus a link to the checkpoints. Also holds the project logs listed below this table. |
| [`experiments/_archive/`](experiments/_archive/) | Runs that were stopped or replaced. Nothing is ever deleted; stopped runs are moved here with the reason in the folder name. |
| [`results/`](results/) | Figures and tables for the report. Every figure is a grayscale 1600×900 PNG with the CSV that made it. `baseline_flat/` holds Sprint 1; `own_flat/` holds the Sprint 2 training curves and the reproducibility check. |
| [`scripts/`](scripts/) | Launch scripts. `run_baseline.sh`: Sprint 1 training, 3 seeds. `run_play.sh`: playback video and policy export. `run_own.sh`: Sprint 2 training, 4 runs. |
| [`scripts/unitree_rl_lab/`](scripts/unitree_rl_lab/) | Our wrappers around unitree_rl_lab's train and play scripts (`url_train.py`, `url_play.py`), which make them work with rsl-rl 5 and Isaac Lab 2.3.2, and [`epic_tasks/`](scripts/unitree_rl_lab/epic_tasks/), our task variants. |
| [`tools/`](tools/) | Python utilities. `tb_to_csv.py`: TensorBoard to CSV. `plot_curves.py`: mean ± std curves across seeds (`--preset url` for unitree_rl_lab runs). `plot_repro.py`: overlay of two runs of the same seed. `watch_ckpt.py`: live viewer of the newest checkpoint. `x_fit_window.py`: display helper. Later: `eval.py`, `check_deploy_cfg.py`. |
| `external/` | Third-party clones (unitree_rl_lab, Go2 robot model; later unitree_mujoco and the deploy SDK). **Not in git**: re-create it with the steps in `CLAUDE.md`. Training logs and checkpoints for unitree_rl_lab runs live in `external/unitree_rl_lab/logs/`. |
| [`papers/`](papers/) | Literature work. `existing/` holds the paper lists the team has already covered; `my_titles.txt` is for new papers (duplicate check). |
| [`robot_logs/`](robot_logs/) | CSV logs copied back from the WSO2 robot sessions (Sprint 3–4). |
| [`report/`](report/), [`medium/`](medium/), [`slides/`](slides/) | Drafts of the internship report, the Medium tutorial and the presentation. |
| [`Project-Documentation/`](Project-Documentation/) | Learning notes (Obsidian vault): Isaac Sim / Isaac Lab learning progress, chapters 1–3. |
| [`CLAUDE.md`](CLAUDE.md) | Project rules, environment and run commands for the workstation. |
| [`SETUP_KIT.md`](SETUP_KIT.md) | How the workstation kit was installed, and the list of task commands per sprint. |
| `.claude/` | Workstation task commands (one per plan task) and settings. |
| [`LICENSE`](LICENSE) | Apache 2.0 |

### Project logs in `experiments/`

| File | Content |
| --- | --- |
| [`README.md`](experiments/README.md) | Versions table and a table of every run, per sprint |
| [`NOTES.md`](experiments/NOTES.md) | Every error hit, with the exact error line, the cause and the fix |
| [`DECISIONS.md`](experiments/DECISIONS.md) | Every decision: what, who decided, why, where it shows; plus the open decisions |
| [`policy_inputs.md`](experiments/policy_inputs.md) | Sprint 2 audit of the training task: policy and critic inputs, actions, timing, motor model and gains, randomisation, rewards |
| [`sprint1_summary.md`](experiments/sprint1_summary.md) | Sprint 1 problems and fixes in plain words |

## Tasks

| Task | Used for | Notes |
| --- | --- | --- |
| `Isaac-Velocity-Flat-Unitree-Go2-v0` | Sprint 1 baseline | Built into Isaac Lab, stock settings, 300 iterations. Not deployable as is: its policy uses base linear velocity, which the real robot cannot measure. |
| `Unitree-Go2-Velocity` | Audited reference | unitree_rl_lab's Go2 task. 45 policy inputs, all measurable on the robot; exports `deploy.yaml`. |
| `Unitree-Go2-Velocity-FullCmd` | **Sprint 2 training** | `Unitree-Go2-Velocity` with the full command range from the start (vx ±1.0, vy ±0.4, yaw ±1.0) and no command curriculum. The upstream curriculum stayed at ±0.1 m/s. Everything else is identical (diff-checked). 3,000 iterations, 4,096 envs. |

## How to run

All commands use the conda env `env_isaaclab`:

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
```

**Sprint 1: built-in baseline**

```bash
scripts/run_baseline.sh                 # trains seeds 42 43 44, one after another
scripts/run_play.sh experiments/baseline_flat_seed42_*   # playback video + policy export
python tools/tb_to_csv.py <run_folder>
python tools/plot_curves.py <run_folders...> -o results/baseline_flat
```

**Sprint 2: own deployable policy**

```bash
ITERS=3000 scripts/run_own.sh           # seeds 42 43 44, then 42 again, headless
python tools/plot_curves.py experiments/own_flat_seed4{2,3,4}_2026* -o results/own_flat --preset url
python tools/plot_repro.py <seed42 run> <seed42 repeat run> -o results/own_flat/repro_seed42.png
```

Single run, by hand:

```bash
cd external/unitree_rl_lab
python ../../scripts/unitree_rl_lab/url_train.py --headless --task Unitree-Go2-Velocity-FullCmd --seed 42 --max_iterations 3000
python ../../scripts/unitree_rl_lab/url_play.py --headless --task Unitree-Go2-Velocity-FullCmd --checkpoint <model.pt> --video --video_length 500
```

Run long jobs in tmux. When saving output to a file, set `PYTHONUNBUFFERED=1`. Setting up `external/` and the display for a GUI is described in [`CLAUDE.md`](CLAUDE.md).

## Evaluation protocol (fixed for every policy)

Six commands, 64 robots × 20 s each:
- stand (0, 0, 0)
- walk 0.5 m/s
- walk 1.0 m/s
- backward −0.5 m/s
- sidestep 0.3 m/s
- turn 0.8 rad/s

Plus one run with random pushes.

Metrics: velocity-tracking RMSE, yaw-rate RMSE, fall rate, and mean mechanical power (Σ|τ·q̇|).

## Safety

Nothing in this repository connects to the real robot. Every command on the physical Go2 is typed by hand, on site, during the WSO2 sessions.

## License

Apache 2.0, see [`LICENSE`](LICENSE).
