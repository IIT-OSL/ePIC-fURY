---
description: Sprint 2: train the deployable policy, 3 seeds plus a repeat run
---

Read CLAUDE.md. Sprint 2: train the deployable flat policy. Task name: $ARGUMENTS (use the one recorded in CLAUDE.md if empty).
1. Write scripts/run_own.sh: seeds 42, 43, 44, then 42 again as the reproducibility run, one after another, headless. Each run in experiments/own_flat_seed<N>_<timestamp>/ with cmd.txt, git.txt, train.log, env.yaml, agent.yaml, and deploy.yaml if unitree_rl_lab exports one.
2. Check the GPU is idle, launch in tmux window `own`.
3. When all four finish: run tools/plot_curves.py on seeds 42/43/44 into results/own_flat/, and overlay the two seed-42 runs in results/own_flat/repro_seed42.png.
4. Report final reward per seed and how closely the two seed-42 curves overlap. GPU physics is not bit-exact; say so if they differ slightly.
