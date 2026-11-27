# Decision log

One row per decision: what was decided, by whom, why, and where it shows. Newest at the bottom.
Daham decides; Claude Code proposes and records.

| Date | Decision | Decided by | Why | Where it shows |
| --- | --- | --- | --- | --- |
| 2026-11-19 | Train the deployable policy in unitree_rl_lab, not basic-locomotion-isaaclab | Plan (accepted by Daham) | Unitree's own Isaac Lab + RSL-RL repo, exports deploy.yaml (joint map, gains, action scale, timestep), same repo covers sim-to-sim and sim-to-real | Plan doc, CLAUDE.md |
| 2026-11-19 | Flat-ground, blind (proprioception-only) task | Plan (accepted by Daham) | WSO2 floor is flat; real Go2 has no height scan feeding the policy; novelty not required | Plan doc, CLAUDE.md Goal |
| 2026-11-20 | Sprint 1 baseline with fully stock settings (300 iterations, 4096 envs) | Plan | Prove the install reproduces before changing anything | results/baseline_flat/summary.md |
| 2026-11-25 | Sprint 1 closed; playback videos checked by Daham | Daham | Videos watched, gait OK | results/baseline_flat/summary.md (sign-off) |
| 2026-11-25 | 5-paper task deferred (not part of Sprint 1 sign-off) | Daham | His call; still needed for the report's literature section | experiments/sprint1_summary.md |
| 2026-11-26 | WSO2 booking message and supervisor deadline question sent | Daham | Robot time is the bottleneck | (outside repo) |
| 2026-11-27 | unitree_rl_lab in the SAME conda env (`env_isaaclab`), not a separate env | Daham ("go with the same env plan") | Isaac Sim 5.1.0 matches; Isaac Lab 2.3.0 vs 2.3.2 is a minor gap; a new env costs a multi-GB download and ~half a day; keeps Sprint 1 reproducible | CLAUDE.md Environment |
| 2026-11-27 | Do not downgrade rsl-rl (keep 5.0.1); bridge the API gap with our own wrapper scripts | Daham (same approval) | Downgrade would break the Sprint 1 setup; wrappers change only API glue, not task/rewards/gains | scripts/unitree_rl_lab/url_train.py, url_play.py; NOTES.md |
| 2026-11-27 | Install with `pip install -e` only, skip `./unitree_rl_lab.sh -i` | Daham (same approval) | The script needs git-lfs, writes a conda activate script with an empty ISAACLAB_PATH and changes global shell completion | NOTES.md |
| 2026-11-27 | Robot files: Go2 USD only from HF `unitreerobotics/unitree_model` (19 MB), not the URDF route | Daham (same approval) | Matches the code's default spawn, so the only edit is UNITREE_MODEL_DIR; URDF route needs a 334 MB clone and a spawn-code change | external/unitree_model/Go2/ |
| 2026-11-27 | Set `UNITREE_MODEL_DIR` in external/unitree_rl_lab/.../assets/robots/unitree.py (only edit to an upstream file) | Daham (task step approved) | Required by unitree_rl_lab's install instructions | `git -C external/unitree_rl_lab diff` |
| 2026-11-27 | unitree_rl_lab runs log to `external/unitree_rl_lab/logs/` (run from its root, its default) and run folders symlink there | Claude Code (convention) | Keeps unitree's relative paths working (deploy tools expect them). Note: `external/` is git-ignored, so never re-clone or delete that folder without first moving logs to experiments/_archive/ | experiments/*/url_log symlinks |
| 2026-11-27 | Audit of `Unitree-Go2-Velocity` signed off: policy inputs deployable as is, randomisation and rewards unchanged, `/s2-deployable-cfg` not needed | Daham ("approved") | All 45 policy inputs are measurable on the real Go2; base_lin_vel and joint_effort are critic-only | experiments/policy_inputs.md |

## Open decisions

| Needed by | Decision | Options / recommendation |
| --- | --- | --- |
| before /s2-train | Training length for unitree_rl_lab Go2 | Its default `max_iterations` is 50,000; at ~2.05 s/iteration (4096 envs) that is ~28 h per seed, ~4.7 days for 4 runs. Needs a decision after the audit. |
| after /s2-eval | Which run to deploy | From the eval table |
| before /s3-build-deploy | Deploy machine (Ubuntu laptop vs Go2 onboard computer) | Depends on WSO2's answer |
