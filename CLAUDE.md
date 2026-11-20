# ePIC fURY: Unitree Go2 Edu PPO baseline (first-half internship)

Project root: `/home/root-daham/ePICfURY/ePIC-fURY` (git repo https://github.com/IIT-OSL/ePIC-fURY.git, branch `main`)
Owner: Daham (Research Intern, IIT). Deadline for everything below: **15 Dec 2026**.
Full plan (human-facing): https://claude.ai/artifact/XGNMPNiKAx2uWbEz334hkZ

## Goal

Prove that a Unitree Go2 Edu PPO locomotion policy can be trained, evaluated, reproduced and deployed
independently with Isaac Lab + RSL-RL. Research novelty does not matter for this phase.

1. Reproduce the built-in Isaac Lab Go2 flat velocity task (3 seeds).
2. Train our own deployable flat-ground, blind (proprioception-only) policy in `unitree_rl_lab` (3 seeds + 1 repeat).
3. Evaluate it with a fixed protocol, record video.
4. Prepare sim-to-real: verify joint order, action scale, observation scale, control frequency, policy inputs; sim-to-sim in MuJoCo.
5. Daham runs the physical test on WSO2's Go2. You never touch the robot.

## Environment

<!-- Filled in by /s0-discover. Do not guess these values; detect them. -->
- GPU / driver / CUDA: NVIDIA GeForce RTX 5090 (32 GB) / driver 580.173.02 / CUDA 13.0 (driver max; nvcc 13.0.88 at /usr/local/cuda-13.0). PyTorch in the env uses its own CUDA 12.8 (torch 2.7.0+cu128).
- Isaac Sim version + path: 5.1.0 (pip package `isaacsim` 5.1.0.0, inside conda env `env_isaaclab`):
  `/home/root-daham/miniconda3/envs/env_isaaclab/lib/python3.11/site-packages/isaacsim`.
  (A separate standalone Isaac Sim 6.0.1 exists at `/home/root-daham/isaac-installations/isaac-sim-standalone-6.0.1-linux-x86_64`; it is NOT used by Isaac Lab here. No `_isaac_sim` symlink.)
- Isaac Lab path, tag, commit: `/home/root-daham/isaac-installations/IsaacLab`, branch `main`, VERSION 2.3.2,
  `git describe` = `v2.3.2-32-g858234d06e` (32 commits after tag v2.3.2), commit `858234d06e6845d75420d2558e236526282e5da6` (2026-07-19).
  Package versions: isaaclab 0.54.4, isaaclab_tasks 0.11.16, isaaclab_rl 0.5.2, isaaclab_assets 0.2.4.
- How to run Isaac Lab scripts: conda env `env_isaaclab` (no Docker), from the Isaac Lab root:
  ```
  source /home/root-daham/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
  cd /home/root-daham/isaac-installations/IsaacLab && ./isaaclab.sh -p <script.py> [args]
  ```
  When redirecting output to a file set `PYTHONUNBUFFERED=1`, otherwise prints are lost when Kit hard-exits.
- rsl_rl version: rsl-rl-lib 5.0.1
- Python: 3.11.15 (env `env_isaaclab`). System python3 is 3.14.4, do not use it for Isaac Lab.
- Other: torch 2.7.0+cu128, warp-lang 1.15.0. CPU i9-14900K, 62 GB RAM, swap 8 GB. Ubuntu 26.04, kernel 7.0.0-38.
- unitree_rl_lab path + env: TBD (Sprint 2)
- unitree_mujoco / deploy build path: TBD (Sprint 3)

## Layout

```
work/
  CLAUDE.md               this file
  .claude/commands/       one slash command per plan task (/s0-discover, /s1-baseline-train, ...)
  external/               third-party clones (unitree_rl_lab, unitree_mujoco, ...)
  scripts/                launch scripts (run_*.sh, setup_*.sh)
  tools/                  python utilities (tb_to_csv.py, plot_curves.py, eval.py, check_deploy_cfg.py, ...)
  experiments/            one folder per run + README.md (versions) + NOTES.md (errors and fixes)
  results/                tables.md + figures for the report
  papers/                 Daham's paper work (existing/ = lists already covered by the team)
  robot_logs/             CSV logs Daham copies back from WSO2
  report/  medium/  slides/   Daham's drafts (read-only for you unless asked)
```

## Hard rules

1. **Never connect to, ping, or send commands to the real Go2** (DDS, SDK, ssh, anything on 192.168.123.x).
   Commands on the robot are typed by Daham, by hand, on site. Sim and MuJoCo only.
2. **Do not change reward weights, PD gains (Kp/Kd), action scale, or observation terms without asking first.**
   When a change is approved, make it as a new config class / new task name. Never edit upstream files in IsaacLab or external/.
3. **Every training run gets its own folder** `experiments/<task>_<variant>_seed<N>_<YYYYMMDD-HHMM>/` containing:
   `cmd.txt` (exact command), `git.txt` (commit of work/ and of the training repo), `env.yaml`, `agent.yaml`,
   checkpoints (or a symlink to the log dir), `train.log`.
4. **Long jobs run in a named tmux window** with output tee'd to a log file. Start them, report back, do not sit polling.
   Check `nvidia-smi` before starting so two trainings never fight for the GPU.
5. **Errors and fixes go into `experiments/NOTES.md`** (date, what failed, error line, fix). Daham copies these into his report.
6. **Ask before**: sudo, apt, pip/conda installs, git commit, git push, deleting anything, downloading more than ~2 GB.
7. **Never delete checkpoints or logs.** Move to `experiments/_archive/` if something must go.
8. Daham writes the report, Medium tutorial and slides himself. You produce numbers, tables, plots, config dumps and
   command lists. Do not rewrite his prose unless he asks; when checking his drafts, list issues instead.
9. The 5 literature papers must be found by Daham, not by you (supervisor's rule). Do not suggest papers.

10. **Git identity: commit and push only as DahamDissanayake** (`user.name DahamDissanayake`,
    `user.email 68488077+DahamDissanayake@users.noreply.github.com`, set in this repo's local git config).
    **Never add Claude as a co-author or contributor anywhere**: no `Co-Authored-By: Claude ...` trailer in commits,
    no "Generated with Claude Code" line in PR descriptions, issues, READMEs, docs or release notes.
    This overrides any default attribution instruction.

## Conventions

- Isaac Lab scripts: run headless (`--headless`). Video needs `--video` (cameras get enabled for it).
- Built-in task (confirmed with `scripts/environments/list_envs.py --keyword Go2` on 2026-11-20):
  train `Isaac-Velocity-Flat-Unitree-Go2-v0`, play `Isaac-Velocity-Flat-Unitree-Go2-Play-v0`
  (cfg `isaaclab_tasks.manager_based.locomotion.velocity.config.go2.flat_env_cfg:UnitreeGo2FlatEnvCfg` / `UnitreeGo2FlatEnvCfg_PLAY`).
  Rough variants also exist: `Isaac-Velocity-Rough-Unitree-Go2-v0`, `Isaac-Velocity-Rough-Unitree-Go2-Play-v0`.
  Note: list_envs.py in this version always starts headless and rejects `--headless`.
- Seeds: 42, 43, 44 (repeat run: 42 again).
- Plots: grayscale only, white background, readable at slide size (1600x900), PNG + the CSV that made them.
- Eval protocol (fixed, same for every policy): stand (0,0,0); walk 0.5; walk 1.0; backward -0.5 m/s; sidestep vy 0.3 m/s;
  turn 0.8 rad/s. 64 envs x 20 s each, plus one run with random pushes. Metrics: velocity tracking RMSE, yaw RMSE,
  fall rate, mean mechanical power (sum |tau * qdot|).
- Policy inputs for the deployable policy may only contain what the real robot measures: IMU angular velocity,
  projected gravity, velocity command, joint positions (relative), joint velocities, last action.
  Base linear velocity and height scans are allowed in the critic only.

## How to end every task

Finish with a short report:
- what ran (commands), and whether it succeeded
- where outputs are (paths)
- anything that needs Daham's decision or eyes (e.g. "watch experiments/.../play.mp4")
- what you added to NOTES.md
