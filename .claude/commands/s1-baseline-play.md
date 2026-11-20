---
description: Sprint 1: playback videos and exported policies for the baseline runs
---

Read CLAUDE.md. Sprint 1: playback for the baseline runs.
For each experiments/baseline_flat_seed*/ run that finished:
1. Run the Go2 flat Play task on the final checkpoint with --video (about 500 steps, 16 envs) and copy the mp4 into the run folder as play.mp4.
2. Find the exported policy files (exported/policy.pt, policy.onnx) and copy them into the run folder.
3. List the videos for me to watch. Do not judge the gait yourself beyond "it ran / it crashed".
