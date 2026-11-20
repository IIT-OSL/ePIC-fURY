# Unitree Go2 RL Walking — 5 Isaac Sim / Isaac Lab Projects

Curated list of hands-on projects for training a Unitree Go2 quadruped to walk using reinforcement learning in NVIDIA Isaac Sim / Isaac Lab. Ordered roughly from "learn the fundamentals" to "production-grade multi-robot framework."

Before any of these: install Isaac Sim and Isaac Lab following NVIDIA's official guide at https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html (conda install recommended). You'll need an NVIDIA RTX GPU (6 GB VRAM is enough for smaller env counts, 24 GB+ recommended for large-scale training) and Ubuntu 22.04 (Windows is also supported by Isaac Lab, but most of these repos assume Linux).

---

## 1. Isaac Lab built-in Go2 task (start here)

The Go2 velocity-tracking task ships inside Isaac Lab itself — no extra repo needed. This is the fastest way to see a Go2 walk and understand the manager-based RL environment structure before touching custom code.

Repo: https://github.com/isaac-sim/IsaacLab

Install:
```
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab
./isaaclab.sh -i          # installs Isaac Lab + rsl_rl
```

Train and watch it play:
```
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-Unitree-Go2-v0 --headless

./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=Isaac-Velocity-Flat-Unitree-Go2-v0
```
Swap `Flat` for `Rough` for uneven-terrain training. Discussion thread with tips specific to Go2: https://github.com/isaac-sim/IsaacLab/discussions/4105

---

## 2. Lab-of-AI-and-Robotics/IsaacLab-Tutorial (best for actually learning)

A 10-chapter, hands-on tutorial that walks you from running the baseline Go2 example to building your own custom RL environment from scratch — reward shaping, curriculum learning, sim-to-real gap closing with ActuatorNet, and finally scaling up to humanoid (H1) locomotion. This is the one to work through if your goal is understanding *how* Isaac Lab RL environments are built, not just running someone else's policy.

Repo: https://github.com/Lab-of-AI-and-Robotics/IsaacLab-Tutorial
Full written tutorial (Notion): https://marble-resistance-175.notion.site/A-Tutorial-on-Developing-Reinforcement-Learning-Environments-for-Legged-Robots-in-Isaac-Lab-25e59724dbdf80b5b6c6c2dbd9ea6b66

Each chapter is its own git branch:
```
git clone https://github.com/Lab-of-AI-and-Robotics/IsaacLab-Tutorial.git
cd IsaacLab-Tutorial
git checkout chapter2_3   # project scaffolding
git checkout chapter7     # reward shaping
git checkout chapter9     # sim-to-real (ActuatorNet)
```
Follow the Notion doc chapter-by-chapter alongside the corresponding branch. Requires Isaac Lab already installed (see #1).

---

## 3. unitreerobotics/unitree_rl_lab (official Unitree repo)

Unitree's own RL environments for Go2, H1, and G1-29dof, built as a standalone Isaac Lab extension. Includes the full pipeline through to real-robot deployment (sim2sim in MuJoCo, then sim2real on hardware), so it's the most complete reference if you eventually want to run a trained policy on a physical Go2.

Repo: https://github.com/unitreerobotics/unitree_rl_lab

Install:
```
git clone https://github.com/unitreerobotics/unitree_rl_lab.git
cd unitree_rl_lab
conda activate env_isaaclab
./unitree_rl_lab.sh -i
# restart shell after this

# get robot description files
git clone https://github.com/unitreerobotics/unitree_ros.git
# then set UNITREE_ROS_DIR in source/unitree_rl_lab/unitree_rl_lab/assets/robots/unitree.py
```

Train / play:
```
./unitree_rl_lab.sh -l                       # list available tasks
./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity
./unitree_rl_lab.sh -p --task Unitree-Go2-Velocity
```
Deploy section in the README covers MuJoCo sim2sim and real Go2 sim2real via `unitree_sdk2`.

---

## 4. BrandoUlissi/isaaclab-go2-locomotion (best for a laptop / small GPU)

A clean, well-documented portfolio-style project specifically built and validated on a 6 GB VRAM laptop GPU (RTX 4050). Good pick if your machine isn't a 24 GB workstation. It trains a baseline velocity-tracking policy, then extends it with a push-recovery (disturbance-rejection) behavior — a nice second milestone once basic walking works. Per-run training logs and hyperparameters are documented in detail, useful for comparing your own results.

Repo: https://github.com/BrandoUlissi/isaaclab-go2-locomotion

Requires Isaac Sim 4.5 + Isaac Lab 2.1 installed separately (see #1). Then, baseline reproduction from the IsaacLab repo directly:
```
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-Unitree-Go2-v0 \
    --num_envs=3072 --max_iterations=2000 --seed=42 --headless
```
Push-recovery extension (registers a custom task from this repo):
```
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-Unitree-Go2-PushRecovery-v0 \
    --num_envs=3072 --max_iterations=2500 --seed=42 --headless
```
Full setup and per-session run notes are in the repo's `docs/` folder.

---

## 5. fan-ziqi/robot_lab (most robots, most actively maintained)

The most feature-complete community extension — 1.7k stars, supports Go2 plus ~20 other quadruped/wheeled/humanoid robots through one consistent framework, with rough and flat terrain variants, symmetry-augmented training, teacher-student distillation, and multi-GPU/multi-node training support. Worth using once you're past the basics and want a serious, extensible codebase.

Repo: https://github.com/fan-ziqi/robot_lab

Install:
```
git clone https://github.com/fan-ziqi/robot_lab.git
cd robot_lab
python -m pip install -e source/robot_lab
python scripts/tools/list_envs.py   # confirms install, lists all tasks
```

Train / play Go2:
```
python scripts/reinforcement_learning/rsl_rl/train.py \
    --task=RobotLab-Isaac-Velocity-Rough-Unitree-Go2-v0 --headless

python scripts/reinforcement_learning/rsl_rl/play.py \
    --task=RobotLab-Isaac-Velocity-Rough-Unitree-Go2-v0
```
Swap `Rough` for `Flat`. Docker setup and multi-GPU commands are in the README if you want to scale up later.

---

## YouTube walkthroughs

- "Training Isaac Lab, Unitree Go2 walking on Flat Surface" — Lens Lab: https://www.youtube.com/watch?v=IMSxQ4OaoIs (RTX 4070, Isaac Sim 4.5)
- "Training unitree go2 robot dog with Isaac Lab": https://www.youtube.com/watch?v=clODrsJObLA
- "Unitree Go2 Isaac Sim/Isaac Lab ROS2 Simulator": https://www.youtube.com/watch?v=TM4DpYzmoQw (navigation/ROS2 side rather than RL training, but useful once you have a walking policy and want to deploy it)

## Suggested order

Start with #1 to confirm your install works and see a Go2 walk in minutes. Work through #2 if you want to actually understand the RL environment code rather than just run it. Use #4 if your GPU is modest. Move to #3 or #5 once you want deployment-ready policies or want to experiment with other robots/terrains.
