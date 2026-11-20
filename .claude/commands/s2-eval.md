---
description: Sprint 2: write eval.py and run the fixed 6-command protocol plus push test
---

Read CLAUDE.md. Sprint 2: evaluation.
1. Write tools/eval.py: load a checkpoint for a given task, override commands to each fixed eval command in CLAUDE.md (stand, 0.5, 1.0, -0.5 m/s, sidestep 0.3 m/s, turn 0.8 rad/s), 64 envs for 20 s each with command resampling off, then once more at 0.5 m/s with random pushes on. Per command compute: linear velocity tracking RMSE, yaw rate RMSE, fall rate (base-contact terminations / envs), mean mechanical power sum |tau * qdot|. Write eval.csv into the run folder and print a markdown table.
2. Run it on every finished own_flat run, and on the baseline_flat runs for comparison.
3. Write results/eval_summary.md: mean +/- std across seeds per command for both tasks, plus which seed scores best overall. I pick the policy to deploy.
