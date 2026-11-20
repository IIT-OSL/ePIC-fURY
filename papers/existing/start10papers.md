# Start 10 Papers — Locomotion, Controlled Environments, RL

Ten seed papers selected to anchor a research problem search across the three topics the project is scoping in on: **locomotion**, **controlled (simulated) training environments**, and **reinforcement learning (RL)**. Each entry gives full citation info, a detailed description of the method and findings, and why it matters for narrowing toward a researchable question on the Unitree Go2 Edu.

---

## 1. Sim-to-Real: Learning Agile Locomotion for Quadruped Robots

**Authors:** Jie Tan, Tingnan Zhang, Erwin Coumans, Atil Iscen, Yunfei Bai, Danijar Hafner, Steven Bohez, Vincent Vanhoucke
**Venue:** Robotics: Science and Systems (RSS), 2018
**Link:** arxiv.org/abs/1804.10332

### Description
This is the foundational sim-to-real paper for legged robots. The authors train locomotion policies entirely in a physics simulator using dynamics randomization — varying mass, friction, motor strength, and latency across training episodes — so that the learned policy is robust to the mismatch between simulation and the real world. The trained policy was deployed directly on a real quadruped (Minitaur) with no additional fine-tuning and successfully produced agile, natural-looking gaits.

A key empirical finding: dynamics randomization decreases peak performance in simulation but substantially increases the policy's stability and robustness once transferred to hardware. This trade-off — simulation performance vs. real-world robustness — is a recurring tension that shows up in nearly every subsequent locomotion paper.

### Why it matters here
This is the paper that established "train in a controlled/simulated environment, transfer to real hardware" as the standard locomotion research pipeline. Any Go2 Edu project inherits this pipeline and its central open question: how much simulation robustness is needed, and at what cost to nominal performance.

---

## 2. Learning to Walk in Minutes Using Massively Parallel Deep Reinforcement Learning

**Authors:** Nikita Rudin, David Hoeller, Philipp Reist, Marco Hutter
**Venue:** Conference on Robot Learning (CoRL), 2022
**Link:** arxiv.org/abs/2109.11978

### Description
This paper introduced the now-standard "legged_gym" training setup: thousands of simulated robot instances run in parallel on a single GPU using NVIDIA's IsaacGym. Instead of one simulated robot generating experience sequentially, thousands run simultaneously, collapsing training time from days to minutes. The paper also introduces a game-inspired terrain curriculum that gradually increases difficulty as the policy improves, and studies which PPO implementation details matter most when scaling to massive parallelism.

The resulting policies were transferred to a real ANYmal quadruped and walked confidently across rough, uneven terrain after only ~20 minutes of simulated training time.

### Why it matters here
This is the controlled-environment backbone almost every subsequent quadruped RL paper builds on (including Walk These Ways and Rapid Locomotion, both used with Unitree hardware). If the Go2 Edu project trains any policy from scratch, it will almost certainly run on this exact simulated-environment architecture (IsaacGym / Isaac Lab + legged_gym).

---

## 3. Rapid Locomotion via Reinforcement Learning

**Authors:** Gabriel B. Margolis, Ge Yang, Kartik Paigwar, Tao Chen, Pulkit Agrawal
**Venue:** Robotics: Science and Systems (RSS), 2022
**Link:** arxiv.org/abs/2205.02824

### Description
Trains a quadruped (Unitree A1) to run at high speed (up to 3.9 m/s) using RL in a controlled simulated environment with aggressive dynamics randomization. The paper's key contribution is a multiplicity-of-behaviors training scheme: the policy is trained to reach a wide range of target speeds and behaviors rather than a single optimal gait, which turns out to make the final policy more robust when deployed on hardware.

Extensive ablations study which components of the simulated environment (contact modeling, actuator lag modeling, terrain variation) are necessary for successful transfer to the physical robot.

### Why it matters here
Directly relevant to the "locomotion" and "controlled environment" axes on Unitree hardware. Establishes a strong single-objective (speed) baseline any multi-objective extension would need to beat or explain a trade-off against.

---

## 4. Learning Quadrupedal Locomotion over Challenging Terrain

**Authors:** Joonho Lee, Jemin Hwangbo, Lorenz Wellhausen, Vladlen Koltun, Marco Hutter
**Venue:** Science Robotics, 2020
**Link:** DOI: 10.1126/scirobotics.abc5986

### Description
One of the first papers to show that a single RL-trained policy (on ANYmal) can generalize across a wide range of natural, unstructured terrain — slippery slopes, mud, snow, rubble — without any explicit terrain classification. The controlled training environment models a broad terrain library, and the policy learns implicit terrain-adaptive behavior purely from proprioceptive feedback (joint angles, contact forces), without needing vision.

The paper carefully analyzes failure cases and shows that policies trained on a sufficiently diverse simulated terrain set transfer with very high reliability to terrain never seen in simulation.

### Why it matters here
Provides a template for how to define and structure a "controlled environment" (terrain library design, curriculum) as a research variable in its own right, rather than an implementation detail — relevant if the Go2 project studies environment design as part of its contribution.

---

## 5. Learning Robust Perceptive Locomotion for Quadrupedal Robots in the Wild

**Authors:** Takahiro Miki, Joonho Lee, Jemin Hwangbo, Lorenz Wellhausen, Vladlen Koltun, Marco Hutter
**Venue:** Science Robotics, 2022
**Link:** DOI: 10.1126/scirobotics.abk2822

### Description
Extends blind proprioceptive locomotion (Paper 4) by adding visual perception. Uses a teacher-student training scheme: a "teacher" policy is first trained in simulation with privileged information (perfect terrain maps), then a "student" policy learns to imitate the teacher using only realistic, noisy sensor inputs (depth camera + proprioception) that would be available on the real robot. This lets the controlled simulated environment do the heavy lifting of exploration while the deployable policy only has to learn to reconstruct the teacher's behavior from noisy real-world-like inputs.

Deployed on ANYmal in numerous real outdoor environments (forests, construction sites, stairs) with high reliability.

### Why it matters here
Teacher-student distillation is the standard architecture for combining a controlled/privileged simulated environment with real-world sensor constraints. Directly informative if the Go2 project incorporates any perception (camera/RGB) alongside locomotion — a natural next axis after RL and controlled environment.

---

## 6. Walk These Ways: Tuning Robot Control for Generalization with Multiplicity of Behavior

**Authors:** Gabriel B. Margolis, Pulkit Agrawal
**Venue:** Conference on Robot Learning (CoRL), 2023
**Link:** github.com/Improbable-AI/walk-these-ways

### Description
Trains a single policy on the Unitree Go1 conditioned on a low-dimensional "behavior descriptor" (gait frequency, body height, footswing height, etc.) inside a controlled IsaacGym environment. Rather than training one policy per behavior, the network learns to interpolate across the whole behavior space, so a single trained policy can produce trotting, bounding, pronking, or crouching gaits just by changing the conditioning vector at test time — with no retraining.

The paper shows this multiplicity of behavior also improves robustness: when one behavior fails on a given terrain, the operator (or an outer-loop controller) can query a different behavior from the same policy instantly.

### Why it matters here
This is the closest existing analogue in the literature to a "preference-conditioned" policy, and it already runs on Unitree hardware (Go1, easily portable to Go2 Edu). It is the most directly reusable codebase and methodology for any project combining locomotion + controlled environment + RL on this specific robot family.

---

## 7. Advanced Skills through Multiple Adversarial Motion Priors in Reinforcement Learning

**Authors:** Eric Vollenweider, Marko Bjelonic, Victor Klemm, Nikita Rudin, Joonho Lee, Marco Hutter
**Venue:** IEEE International Conference on Robotics and Automation (ICRA), 2023
**Link:** arxiv.org/abs/2203.14912

### Description
Addresses a known weakness of pure RL in controlled simulated environments: reward-only training tends to produce robotic, non-natural, or degenerate gaits when the reward function isn't perfectly specified. This paper introduces adversarial motion priors — a discriminator network trained to distinguish "natural" reference motions (collected from real quadruped/animal data) from the policy's current behavior — as an auxiliary training signal inside the simulated environment. Multiple priors are blended to allow the robot to learn a diverse skill set (walking, jumping, backflipping) without hand-designing a reward term for each one.

### Why it matters here
Relevant to the "controlled environment" axis specifically: it demonstrates that what goes into the simulated training environment (reference motion data, discriminator rewards) is itself a research lever, not just the RL algorithm or the robot morphology. A useful comparison point if reward-design difficulty becomes a bottleneck in the Go2 project.

---

## 8. Benchmarking Model Predictive Control and Reinforcement Learning for Legged Robot Locomotion in MuJoCo Simulation

**Authors:** (2025 preprint)
**Venue:** arXiv preprint, 2025
**Link:** arxiv.org/abs/2501.16590

### Description
A head-to-head benchmark comparing classical Model Predictive Control (MPC) against RL-trained controllers on a Unitree Go1 inside a standardized MuJoCo simulation environment, using a shared evaluation protocol: constant-velocity walking under external disturbances, energy consumption, and terrain adaptability. The paper finds RL controllers handle disturbances and energy efficiency better, but generalize worse to terrain not seen during training, while MPC generalizes better to novel terrain but responds more conservatively to disturbances.

### Why it matters here
Directly useful as an evaluation-protocol template: it defines exactly what "controlled environment" benchmarking should measure (disturbance rejection, energy, terrain generalization) and provides a non-RL baseline (MPC) worth citing as a comparison point, which strengthens the "significance" criterion for publishability.

---

## 9. LocoMuJoCo: A Comprehensive Imitation Learning Benchmark for Locomotion

**Authors:** Firas Al-Hafez, Guoping Zhao, Jan Peters, Davide Tateo
**Venue:** NeurIPS Workshop / arXiv, 2023
**Link:** github.com/robfiras/loco-mujoco

### Description
A standardized benchmark suite built on MuJoCo covering quadrupeds, humanoids, and musculoskeletal human models, each shipped with reference motion datasets (22,000+ samples per humanoid) for imitation learning. While primarily framed around imitation learning, it explicitly supports custom reward functions, making it usable as a pure RL benchmark as well. Its main value is standardization: it gives the field a shared, reproducible controlled environment so that results across different labs' locomotion papers can be fairly compared.

### Why it matters here
Directly relevant to publishability (Week 1 doc, Section 2 — validity/reproducibility). If the Go2 project needs a controlled benchmark environment that reviewers will recognize and trust rather than a bespoke one, LocoMuJoCo is a candidate off-the-shelf option, and its design is a model for building a Go2-specific benchmark if none exists.

---

## 10. Learning-Based Legged Locomotion: State of the Art and Future Perspectives

**Authors:** Sehoon Ha, Joonho Lee, Michiel van de Panne, Zhaoming Xie, Wenhao Yu, Majid Khadiv
**Venue:** International Journal of Robotics Research (IJRR) / arXiv, 2024
**Link:** arxiv.org/abs/2406.01152

### Description
A comprehensive, recent survey covering the entire learning-based legged locomotion field: RL algorithms used (PPO dominant), controlled simulated environment design (domain randomization, terrain curricula, parallel simulation), sim-to-real transfer strategies (teacher-student, system identification), and open challenges. The survey explicitly maps out where the field is heading, including multi-task and multi-objective locomotion, and calls out real-hardware evaluation and sample efficiency as persistent open problems.

### Why it matters here
This is the single best "map of the field" paper for the three topics combined (locomotion + controlled environment + RL). It functions like a second seed paper (alongside the MORL survey from Week 1) — reading its reference list and "future perspectives" section is the fastest way to identify where a Go2 Edu-specific contribution could fit.

---

## Summary Table

| # | Paper | Year | Robot / Platform | Core Contribution |
|---|-------|------|-------------------|--------------------|
| 1 | Sim-to-Real: Learning Agile Locomotion | 2018 | Minitaur | Dynamics randomization for sim-to-real |
| 2 | Learning to Walk in Minutes | 2022 | ANYmal | Massively parallel GPU training (legged_gym) |
| 3 | Rapid Locomotion via RL | 2022 | Unitree A1 | High-speed locomotion, multiplicity of behaviors |
| 4 | Learning Quadrupedal Locomotion over Challenging Terrain | 2020 | ANYmal | Blind terrain-adaptive locomotion |
| 5 | Learning Robust Perceptive Locomotion | 2022 | ANYmal | Teacher-student + vision perception |
| 6 | Walk These Ways | 2023 | Unitree Go1 | Behavior-conditioned single policy |
| 7 | Advanced Skills through Adversarial Motion Priors | 2023 | ANYmal | Motion-prior-guided reward design |
| 8 | Benchmarking MPC vs RL in MuJoCo | 2025 | Unitree Go1 | Standardized controlled-environment benchmark |
| 9 | LocoMuJoCo | 2023 | Multiple | Reproducible benchmark suite |
| 10 | Learning-Based Legged Locomotion Survey | 2024 | Survey | Field map + open problems |

## Next Step

Use this set alongside the Week 2 seed papers (MORL-focused) to identify where the Go2 Edu project's contribution sits: most of these 10 papers use a single-objective reward and a controlled simulated environment on Unitree or ANYmal hardware, but none combine multi-objective reward structures with the Go2 Edu specifically — that intersection remains the clearest opening.
