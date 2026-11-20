---
description: Sprint 3: checklist row 7, run the real deploy controller against unitree_mujoco
---

Read CLAUDE.md. Sprint 3: checklist row 7, sim-to-sim. Never connect to the real robot.
1. Run the actual deploy controller against unitree_mujoco with the chosen policy and its deploy.yaml.
2. Go through the controller states (passive, stand, policy) and drive each eval command from the controller's command input. Record a screen video per command into results/sim2sim/.
3. Log the controller loop period and report its mean and jitter.
4. Report: does it stand, walk at 0.5 m/s and turn without shaking. Daham watches the videos to confirm.
