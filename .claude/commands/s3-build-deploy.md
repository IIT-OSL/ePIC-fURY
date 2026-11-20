---
description: Sprint 3: build unitree_sdk2 deploy controller + unitree_mujoco, write setup_deploy.sh
---

Read CLAUDE.md. Sprint 3: build the sim-to-real stack. Never connect to the real robot.
1. Follow unitree_rl_lab's deploy instructions for Go2: install unitree_sdk2 and build the Go2 deploy controller. Clone and build unitree_mujoco in external/.
2. Write scripts/setup_deploy.sh that reproduces the whole build on a fresh Ubuntu machine (it will run on the laptop Daham takes to WSO2). State the Ubuntu version and packages it assumes.
3. Record paths, build commands, the controller's state machine and its joystick bindings (from its config) in CLAUDE.md and in experiments/deploy_notes.md.
