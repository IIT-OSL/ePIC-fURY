---
description: Sprint 2: read-only audit of the Go2 task (inputs, actions, timing, gains, randomisation, rewards)
---

Read CLAUDE.md. Sprint 2: audit the unitree_rl_lab Go2 velocity task before any real training. Read-only, change nothing.
Write experiments/policy_inputs.md with:
1. Policy observation group: every term in order, its dimension, scale, noise, clip. Total input size.
2. Critic observation group: same.
3. Actions: joint names in policy order, action scale, default joint positions, clip.
4. Control timing: sim dt, decimation, resulting policy rate in Hz.
5. Actuator model and PD gains (Kp, Kd) per joint group.
6. Every randomisation event (friction, mass, pushes, motor gains, noise, delays) with its range and when it fires.
7. Rewards: every term with its weight (for the report, not to change).
8. A flagged list: any policy input the real robot cannot measure (base linear velocity, height scan, privileged terms).
Then stop and wait for my sign-off.
