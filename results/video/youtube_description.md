# YouTube description (DRAFT, Daham edits and uploads)

Policy: `experiments/own_flat_seed44_20261127-1505`, `model_2999.pt` (the seed chosen for deployment, 2026-11-27).
Clips: `01_stand.mp4` … `07_walk_0.5_push.mp4` (10 s each, 1920x1080, 50 fps), `rough_cut.mp4` (70 s, same order),
title card `title_card_training_curve.png`. Made with `tools/record_clips.py` (command in `record_cmd.txt`).

---

**Title idea:** Unitree Go2 learns to walk with PPO in Isaac Lab (blind, deployable policy)

A Unitree Go2 quadruped walking policy trained from scratch with reinforcement learning (PPO) in NVIDIA Isaac Lab
with RSL-RL. The policy is blind: it only uses what the real robot can measure (IMU angular velocity, gravity
direction, joint positions and velocities, the velocity command and its last action), so it can be deployed on the
real Go2. 4,096 robots train in parallel on one GPU with randomised friction, body mass and random pushes. This video
shows the trained policy following fixed velocity commands: standing, walking at 0.5 and 1.0 m/s, walking backward,
sidestepping, turning in place, and walking while being pushed. Part of the ePIC fURY project (IIT internship).

**Setup**
- Task: `Unitree-Go2-Velocity-FullCmd` (unitree_rl_lab `Unitree-Go2-Velocity`, full command range, no command curriculum)
- Isaac Sim 5.1.0, Isaac Lab 2.3.2, rsl-rl-lib 5.0.1, unitree_rl_lab (commit 4960b84)
- PPO, 3,000 iterations, 4,096 parallel environments, policy at 50 Hz (45 inputs, 12 joint position targets)
- Training time: 98 min on one NVIDIA RTX 5090 (this seed); 3 seeds trained, final reward 30.39 ± 0.16

**Evaluation of this policy (64 robots × 20 s per command, flat ground)**

| Command | Velocity error (RMSE, m/s) | Yaw-rate error (RMSE, rad/s) | Falls | Mech. power (W) |
| --- | --- | --- | --- | --- |
| Stand | 0.021 | 0.044 | 0 / 64 | 2.8 |
| Walk 0.5 m/s | 0.044 | 0.050 | 0 / 64 | 23.5 |
| Walk 1.0 m/s | 0.061 | 0.052 | 0 / 64 | 47.9 |
| Backward 0.5 m/s | 0.064 | 0.053 | 0 / 64 | 25.5 |
| Sidestep 0.3 m/s | 0.048 | 0.053 | 0 / 64 | 22.1 |
| Turn 0.8 rad/s | 0.027 | 0.074 | 0 / 64 | 16.2 |
| Walk 0.5 m/s + random pushes | 0.071 | 0.052 | 0 / 64 | 24.0 |

**Chapters** (rough cut, 10 s each)
0:00 Stand · 0:10 Walk 0.5 m/s · 0:20 Walk 1.0 m/s · 0:30 Backward · 0:40 Sidestep · 0:50 Turn · 1:00 Pushes

(Shift the chapter times by the title card length in the final cut.)

**Code:** <REPO LINK>
**Medium tutorial:** <MEDIUM LINK>

#reinforcementlearning #robotics #IsaacLab #UnitreeGo2 #PPO #legged #simtoreal
