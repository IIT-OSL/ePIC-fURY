---
description: Sprint 1: TensorBoard to CSV and mean/std training curves across seeds
---

Read CLAUDE.md. Sprint 1: training curves for the baseline.
1. Write tools/tb_to_csv.py: read TensorBoard event files from a run folder, export all scalars to CSV (step, tag, value).
2. Write tools/plot_curves.py: given several run folders, plot mean +/- std across seeds for mean reward, mean episode length, the linear and angular velocity tracking reward terms, and the base-contact termination rate. Grayscale, white background, 1600x900 PNG, plus the CSV behind each plot.
3. Run both on the 3 baseline seeds, save to results/baseline_flat/.
4. Give me a 5-line summary: final mean reward per seed, spread across seeds, iteration where reward plateaus.
