---
description: Sprint 1: train the built-in Isaac Lab Go2 flat PPO baseline, 3 seeds
---

Read CLAUDE.md. Sprint 1: reproduce the built-in Isaac Lab Go2 flat PPO baseline. Do not change any env or agent settings.

1. Write scripts/run_baseline.sh that trains the built-in Go2 flat velocity task headless with rsl_rl for seeds 42, 43, 44, one after another (never in parallel). For each seed: create experiments/baseline_flat_seed<N>_<timestamp>/, save cmd.txt and git.txt, tee output to train.log, and after training copy (or symlink) the Isaac Lab log dir including params/env.yaml and params/agent.yaml.
2. Check nvidia-smi is idle, then launch the script in tmux window `baseline`.
3. Tell me the expected time per seed (estimate from the first ~50 iterations) and how to watch progress (tmux attach, TensorBoard command and port).
4. Log any error and fix in experiments/NOTES.md.
