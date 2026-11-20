# Sprint 1: problems hit and how they were fixed (2026-11-20)

Plain-words version of the Sprint 1 entries in `experiments/NOTES.md`, for the install log.
Sprint 0 problems (list_envs.py and `--headless`, missing output when redirected) are in NOTES.md too.

1. **The GPU was busy when I wanted to start.**
   Another user on the shared workstation was training a different model on the same RTX 5090 (91% load).
   Starting our training at the same time would have slowed both jobs down and made our timings meaningless.
   Fix: waited until the GPU was free (a few minutes). The training script now checks `nvidia-smi` before every seed
   and waits if anyone else is using the GPU.

2. **pandas is not installed in the Isaac Lab environment.**
   The tools for turning TensorBoard logs into CSV files and plots were going to use pandas.
   Fix: wrote them using only Python's built-in `csv` module plus numpy and matplotlib, which are already installed.
   Nothing new had to be installed.

3. **The first playback used an early checkpoint instead of the final one.**
   The playback script was supposed to pick the newest checkpoint (`model_299.pt`) but picked `model_50.pt`.
   It did not crash, so the mistake was only visible in the log line that names the checkpoint.
   Cause: the script sorted the checkpoint file names by splitting the full path at underscores, and the folder names
   themselves contain underscores (`unitree_go2_flat`), so it sorted on the wrong part of the path.
   Fix: sort on the file name only, with version-aware sorting (`sort -V`). The wrong videos and exported policies were
   moved to `experiments/_archive/play_wrong_ckpt_model50/` (kept, not deleted) and playback was run again on `model_299.pt`.
   Lesson: always check which checkpoint a play or eval script actually loaded.

4. **The Isaac Lab version label in git.txt did not match the README.**
   `git describe --tags` printed `training-checkpoints-develop-17-g858234d06e` instead of `v2.3.2-32-g858234d06e`.
   Both point to the same commit (858234d06e), so the recorded runs are correct. Isaac Lab simply has an extra,
   non-release tag closer to the current commit.
   Fix: the script now asks git for release tags only (`--match "v*"`), so future runs show `v2.3.2-...`.

No problems with the training itself: all three seeds trained to 300 iterations with stock settings on the first try,
about 2 minutes each.
