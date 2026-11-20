# 5 ICRA/IROS RL Locomotion Papers with Public Code

Peer-reviewed papers with author-released (or, where noted, well-maintained community) code, picked for relevance to quadruped RL locomotion. One important caveat up front: only #1 is native to Isaac Lab. The other four were built on **Isaac Gym** (NVIDIA's older, now-deprecated standalone RL simulator, separate from Isaac Sim/Isaac Lab). They won't drop into your existing Isaac Lab install as-is — you'd either install Isaac Gym Preview 4 separately alongside it, or port the reward/env config into Isaac Lab's `ManagerBasedRLEnv`/`DirectRLEnv` structure. I've flagged this per entry.

---

## 1. Leveraging Symmetry in RL-based Legged Locomotion Control — IROS 2024 ⭐ runs on your stack today

**Authors:** Su, Huang, Ordoñez-Apraez, Li, Zhongyu, Liao, Turrisi, Pontil, Semini, Wu, Sreenath (IIT / Berkeley / UC San Diego)
**Paper:** https://arxiv.org/pdf/2403.17320 · DOI 10.1109/IROS58592.2024.10802439
**Code:** https://github.com/iit-DLSLab/basic-locomotion-isaaclab (110 stars, actively maintained)

This is the one directly usable on the exact stack you already installed: it's a **native Isaac Lab extension** (tested against Isaac Lab v2.3.2) with **Go2 explicitly supported** (`tested_policies/go2` folder included), plus Aliengo, B2, and HyQReal2. It exploits the robot's morphological symmetry (mirror the left/right legs) to cut training time and improve generalization, and ships sim-to-sim (MuJoCo) and sim-to-real (ROS2) pipelines. It also includes working implementations of adversarial motion priors, rapid motor adaptation, and a concurrent state estimator as optional features — so it's a good hub for trying several techniques at once.

Run it:
```bash
git clone https://github.com/iit-DLSLab/basic-locomotion-isaaclab.git
cd basic-locomotion-isaaclab
python -m pip install -e source/basic_locomotion_isaaclab
python scripts/reinforcement_learning/rsl_rl/train.py --task=Locomotion-Go2-Flat-Blind --headless
```
Follow `README_train.md` in the repo for the full task list (Flat-Blind / Rough-Blind / Rough-Vision).

---

## 2. Extreme Parkour with Legged Robots — ICRA 2024

**Authors:** Cheng, Shi, Agarwal, Pathak (CMU)
**Paper:** https://arxiv.org/pdf/2309.14341
**Code:** https://github.com/chengxuxin/extreme-parkour (well over 1k stars, one of the most cited RL-locomotion repos of 2024)

A single depth-camera-driven policy that long-jumps 2x the robot's body length, high-jumps 2x its height, runs tilted ramps, and walks on its front two legs — all from one neural network. Built on the Unitree A1 in `legged_gym`/Isaac Gym. Training is claimed to take under 20 hours on a single GPU. Extremely well documented (the repo subtitle literally promises "train your parkour robot in less than 20 hours"), which makes it a good second project once you're comfortable with the basics — swapping the A1 URDF for the Go2 one is a common community exercise (search "extreme-parkour go2" on GitHub issues/forks for others who've done it).

Requires Isaac Gym Preview 4 (separate install from Isaac Sim/Isaac Lab) — see the repo's install section.

---

## 3. Robust RL-Based Locomotion for Resource-Constrained Quadrupeds with Exteroceptive Sensing — ICRA 2025

**Authors:** Plozza, Apostol, Joseph, Schläpfer, Magno (ETH Zurich, PBL group)
**Paper:** https://arxiv.org/abs/2505.12537 · DOI 10.1109/ICRA55743.2025.11128474
**Code:** https://github.com/ETH-PBL/elmap-rl-controller (108 stars)

Trains a locomotion policy that consumes an onboard elevation map so a small, compute-constrained quadruped (built on Go1 + Jetson-class hardware) can step cleanly over obstacles up to 17.5 cm and handle 22.5 cm steps 80% of the time, even with noisy visual-inertial odometry. Ships a pretrained checkpoint (`runs/exteroceptive_robust_icra_proposed`) so you can evaluate before you train. Built on `legged_gym`/Isaac Gym via the "Walk These Ways" codebase — same porting caveat as #2.

---

## 4. Adversarial Motion Priors Make Good Substitutes for Complex Reward Functions — IROS 2022

**Authors:** Escontrela, Peng, Yu, Zhang, Iscen, Goldberg, Abbeel (UC Berkeley / Google)
**Paper:** https://arxiv.org/pdf/2203.15103
**Code:** https://github.com/escontra/AMP_for_hardware (810 stars, official author repo)

Rather than hand-engineering a reward function for natural-looking gaits, this trains a discriminator on ~4.5 seconds of real dog motion-capture data (a German Shepherd) and uses that as a learned "style reward," combined with a task reward. Produces natural gait transitions and energy-efficient locomotion on a real Unitree A1 with far less reward-shaping effort than usual. This is the paper the field's "AMP" technique (referenced inside project #1's feature list) traces back to. Also `legged_gym`/Isaac Gym-based.

---

## 5. DreamWaQ: Learning Robust Quadrupedal Locomotion With Implicit Terrain Imagination via Deep RL — ICRA 2023

**Authors:** Nahrendra, Yu, Myung (KAIST)
**Paper:** https://arxiv.org/abs/2301.10602
**Code (community reimplementation, not the original authors' release):** https://github.com/Manaro-Alpha/DreamWaQ (259 stars, Go1-configured, `legged_gym`/Isaac Gym)

Trains a blind quadruped (no exteroceptive terrain sensing) to infer an implicit "terrain imagination" belief state from proprioception alone via a context-aided estimator network, letting it handle stairs and rough terrain without any camera or LiDAR. Influential paper — the authors have since extended it into DreamWaQ++, DreamFLEX, and DreamRiser. Flagging clearly: the official authors never released code publicly, so what's linked here is a community reimplementation — treat it as a reference/starting point rather than a guaranteed reproduction of the paper's exact numbers.

---

## Practical note on Isaac Gym vs. Isaac Lab

Projects #2–#5 all predate Isaac Lab's dominance and were built on Isaac Gym Preview 4, which NVIDIA has since deprecated in favor of Isaac Sim/Isaac Lab (the stack you just installed). Two ways to actually run them:

1. **Install Isaac Gym Preview 4 side-by-side** (separate conda env, separate from your `env_isaaclab`) — the fastest path to just seeing the paper's results reproduced, but you're working in a dead-end framework NVIDIA no longer updates.
2. **Port the environment into Isaac Lab** — take the reward terms, curriculum, and network architecture from the paper's `legged_gym` config and rebuild them as an Isaac Lab `ManagerBasedRLEnv` task (similar to what project #1 already did for the symmetry paper). More work, but the result runs natively on your installed stack and stays maintained.

If your goal is genuinely to *train on Isaac Sim/Isaac Lab specifically*, start with #1 — it's the only one of the five that's already there.
