---
description: Sprint 0: detect the environment, fill CLAUDE.md, set up folders and git
---

Read CLAUDE.md first. Task: get this workspace ready. Do not install or change anything outside work/ in this task.

1. Detect and write into the "Environment" section of CLAUDE.md (replace the TBD lines): GPU model, NVIDIA driver, CUDA; Isaac Sim version and install path; Isaac Lab path, git tag and commit; how Isaac Lab scripts are run on this machine (isaaclab.sh -p, conda env name, or Docker container); rsl_rl (rsl-rl-lib) version; Python version.
2. Create the folders listed under "Layout" in CLAUDE.md if missing.
3. Write experiments/README.md with the same version table plus today's date.
4. If work/ is not a git repo, git init it with a .gitignore that excludes checkpoints (*.pt, *.onnx), videos (*.mp4), TensorBoard event files and external/. Ask before the first commit.
5. Smoke test: run Isaac Lab's list_envs.py headless and confirm the Go2 flat velocity tasks exist. Write their exact names into CLAUDE.md under Conventions.
6. Report back as described in "How to end every task".
