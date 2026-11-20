---
description: Sprint 3: checklist rows 1-5 (joint order, action/obs scaling, frequency, inputs)
---

Read CLAUDE.md. Sprint 3: checklist rows 1 to 5, on paper. Policy run: $ARGUMENTS
Write tools/check_deploy_cfg.py that loads the run's env.yaml and the deploy.yaml the controller will use, and prints a PASS/FAIL table for:
1. Joint ordering: Isaac Lab joint order vs joint_ids_map vs Unitree SDK motor order (all three side by side, 12 rows).
2. Action scaling: action scale, default joint positions, action clip.
3. Observation scaling: every policy input term, its scale and clip, in order; total input size.
4. Control frequency: sim dt x decimation vs controller policy period; Kp and Kd per joint.
5. Policy inputs: order and dimensions vs the exported policy's input size; last-action buffer initial value; command ranges.
Run it, save the output to experiments/deploy_check.md, and explain every FAIL in plain words.
