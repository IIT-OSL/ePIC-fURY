# MORL for Unitree Go2 Locomotion: Literature and Implementation Review, Gap Analysis, and Refined Research Problems

**Bottom line:** The team's core idea, a single preference-conditioned MORL policy for quadruped locomotion on the Unitree Go2 trained in Isaac Lab, is no longer novel. PROMO (Amr Mousa, Rifny Rachman, Neil Karavis, Michele Caprio and Richard Allmendinger; University of Manchester / BAE Systems; arXiv:2610.01260, submitted 1 October 2026) has already done it, with hardware validation and released code. The work is still publishable, but only if the team moves the contribution to what PROMO explicitly leaves open: **rough terrain, automatic (terrain-aware) preference selection, and safety constraints**. The current "MORL gait optimisation for any terrain" framing needs to become a narrow, testable claim before the IROS 2027 deadline (1 March 2027, Florence), which is roughly 4 months away, not 6-7.

## TL;DR

- **Novelty has moved.** PROMO (arXiv:2610.01260) trains one PPO policy in Isaac Lab conditioned on preferences over tracking, stability and efficiency. It transfers zero-shot to a Go2, and preference changes alone cut specific energy by up to 30.4%. But it was trained only on flat terrain, the preference is set by an operator, and it uses linear scalarisation. AMOR (arXiv:2505.23708) already pairs a weight-conditioned MO-PPO policy with a high-level policy that predicts weights, but for humanoid characters and motion tracking, not quadruped terrain traversal. The open gap is **terrain-adaptive, constraint-aware preference selection on rough terrain with real-Go2 energy and success measurements**.
- **Recommended problem (ranked #1):** "Does the utility-optimal trade-off between command tracking, energy (cost of transport) and robustness shift with terrain? If so, can a lightweight selector that infers terrain from proprioception choose preferences online and beat every fixed-weight policy on a mission-level metric?" Build it on the multi-head-critic PPO pattern (PROMO, GCR-PPO), enforce safety with Constraints-as-Terminations (CaT) instead of exposing safety as a preference axis, and validate on real Go2 terrains like those used in the Legged Robot Challenge.
- **Fix the plan now:** use IROS 2027 (Florence, deadline 1 March 2027), not "IROS 2028". Drop SAC and LeWorldModel from the critical path: LeWM is a reward-free, pixel-based JEPA planner and does not fit proprioceptive Pareto-front approximation. Replace the withdrawn Ding et al. arXiv:2510.10455 citation with arXiv:2403.10723. Add PROMO, MOPPO, CaT, Walk These Ways and fixed-weight sweeps as mandatory baselines. Note that the ICRA 2027 Legged Robot Challenge is not yet confirmed: competition acceptances are announced 31 October 2026.

## Key Findings

1. **Direct prior art now exists on the exact platform and simulator.** PROMO trains on a 12-DoF Go2 in Isaac Sim/Isaac Lab with 4096 parallel flat-terrain environments. It uses three semantic objectives (tracking, stability, efficiency) plus fixed "locomotion priors", a three-head semantic critic, and preference-scalarised PPO. Across 100 sampled preferences in simulation, 67 behaviours are non-dominated, with a mean preference-objective correlation of 0.843. On hardware (Vicon, five trials per condition, four anchor preferences), preference changes alone reduce specific energy by up to 30.4%, position error by up to 38.7%, and peak attitude deviation by up to 59.0% relative to the balanced preference. PROMO's own limitations section names what it leaves open: changing dynamics and online adaptation, non-convex Pareto regions (because of linear scalarisation), dense hardware controllability, and statistical significance.
2. **The "reward terms as objectives" approach is empirically a bad idea.** PROMO's ablations show that exposing locomotion priors as objectives, or folding them into the semantic objectives, raises the fall rate from 6% to as much as 21.8% and degrades controllability. The team's proposal lists velocity, smoothness, symmetry and energy as the objectives. It should instead pick 2-3 semantic objectives and keep shaping terms fixed, or turn them into constraints.
3. **Objective conflict is real but asymmetric.** In PROMO, tracking and efficiency form the clearest conflict, while stability is partly complementary to both. An efficiency-only specialist converges much later (1700-1900 steps to reach the episode horizon, against 550-650 for PROMO), because effort minimisation is a weak gait-discovery signal. Separately, adaptive energy regularisation (Liang et al., UC Berkeley, arXiv:2403.20001), validated "through simulations and on a real Unitree Go1 robot", shows that energy weighting alone produces "four-beat walking at lower speeds and trotting at higher speeds" without explicit gait regularisation. With the energy weight set to 0.0, the robot "exhibits a bouncing gait across the whole velocity domain", so the energy weight changes gait qualitatively, not just quantitatively.
4. **Multi-head critics are the established way to get vector rewards into massively parallel PPO.** GCR-PPO (Munn, Tidd, Böhm, Gallagher and Howard, arXiv:2509.14816, ICRA 2026) splits the actor update into per-objective gradients using a multi-headed critic, resolves conflicts by priority, and runs inside Isaac Lab/RSL-RL. It reports an average 9.5% improvement over large-scale PPO across 13 Isaac Lab tasks, with "superior scalability compared to parallel PPO (p = 0.04), without significant computational overhead", and code at github.com/humphreymunn/GCR-PPO. Multi-critic PPO with per-group GAE and per-group advantage normalisation is also used in APEX (arXiv:2505.10022) and in multi-critic loco-manipulation work (arXiv:2608.28140). This removes most of the engineering risk in the team's "modify Isaac Lab for vector rewards" step.
5. **"LeWorldModel" is real but does not fit the plan.** LeWM (Maes, Le Lidec, Scieur, LeCun, Balestriero; Mila/Université de Montréal, NYU, Samsung SAIL, Brown; arXiv:2603.19312) is a 15M-parameter JEPA world model "trainable on a single GPU in a few hours", trained end-to-end from raw pixels with only two loss terms and no reward, that plans "up to 48× faster" than foundation-model world models. It addresses visual latent planning, not proprioceptive locomotion, and has no reward or objective heads. The relevant locomotion world models are ETH's Robotic World Model (RWM, arXiv:2501.10100, MBPO-PPO) and its uncertainty-aware offline variant (RWM-U, arXiv:2504.16680). Even there, the authors report that "the policy often exploits minor world model errors".
6. **Competition alignment is partial.** The Legged Robot Challenge (LRC), formerly the Quadruped Robot Challenges (QRC), rewards autonomous traversal of terrain lanes and inspection tasks. Autonomy multiplies scores: 4× for autonomous mobility at ICRA 2024. Winners combined robust RL locomotion with a strong navigation stack. The ICRA 2024 winner (fuRo, Chiba Institute of Technology) used a Go2 EDU with an added Livox Mid-360 and a Jetson Orin NX, three switched RL policies, and a stuck-escape strategy. A MORL locomotion policy helps the mobility score only if it improves reliability or energy on the specific lane types.

## 1. State of the Art Map: RL Quadruped Locomotion (2019-2026)

Legend: † = well-established work listed from the reviewer's domain knowledge and not re-verified in this review session. Check venue details before citing.

| Work | Year / Venue | Robot | Method | Objectives / reward focus | Code |
|---|---|---|---|---|---|
| Hwangbo et al., Learning agile and dynamic motor skills | 2019, Science Robotics | ANYmal | Actuator network + sim-to-real RL | Velocity tracking + regularisers | No |
| Lee et al., Learning quadrupedal locomotion over challenging terrain † | 2020, Science Robotics | ANYmal | Teacher-student, blind, proprioceptive history | Tracking + robustness | No |
| Miki et al., Robust perceptive locomotion in the wild | 2022, Science Robotics | ANYmal | Attention-based fusion of exteroception + proprioception | Tracking + terrain robustness | No |
| Rudin et al., Learning to walk in minutes | 2021/2022, CoRL (PMLR 164) | ANYmal, Unitree A1 | Massively parallel PPO, game-inspired terrain curriculum (legged_gym) | Weighted-sum reward | github.com/leggedrobotics/legged_gym † |
| Kumar et al., RMA | 2021, RSS | A1 | Privileged teacher + adaptation module | Tracking + energy terms | No public training code † |
| Fu et al., Minimizing energy leads to emergence of gaits | 2021, CoRL (arXiv:2111.01674) | A1 | Energy-minimising RL | Energy vs speed; gaits emerge | No † |
| Margolis & Agrawal, Walk These Ways | 2022/2023, CoRL (PMLR 205) | Go1 | Behaviour-conditioned policy (gait frequency, phase, foot clearance, body height) | Fixed reward + commanded behaviour parameters | github.com/Improbable-AI/walk-these-ways † |
| Bellegarda et al., CPG-RL † | 2022, RA-L | A1 / Go1 | RL modulates CPG oscillators | Tracking, gait regularity | Partial † |
| Nahrendra et al., DreamWaQ | 2023, ICRA | A1 | Asymmetric actor-critic, implicit terrain imagination (context-aided estimator) | Blind rough-terrain robustness | Community re-implementations † |
| Zhuang et al., Robot Parkour Learning | 2023, CoRL (PMLR 229) | A1, Go1 | Specialist skills distilled to vision policy | Agility | github.com/ZiwenZhuang/parkour † |
| Long et al., Hybrid Internal Model (HIMLoco) | 2024, ICLR | Go1 / Aliengo † | Internal model from simulated robot response | Robustness | github.com/OpenRobotLab/HIMLoco † |
| Long et al., H-Infinity locomotion | 2024/2025, CoRL (PMLR 270) | Unitree quadrupeds † | Adversarial disturbance learning | Robustness | † |
| Chane-Sane et al., CaT: Constraints as Terminations | 2024, IROS | Solo-12 | Constraints as stochastic terminations on top of PPO | Tracking reward + 60+ constraints | github.com/Gepetto/constraints-as-terminations (Isaac Lab) |
| Lee et al., Not only rewards but also constraints | 2023 arXiv:2308.12517 / T-RO | Several legged robots | Constrained RL with multi-head cost value | 3 rewards + generalisable constraints | No † |
| Adaptive energy regularisation (Liang et al., UC Berkeley, arXiv:2403.20001) | 2024, arXiv | Unitree Go1 (hardware); ANYmal-C (sim) | Velocity-adaptive energy weight | Energy / CoT vs speed; automatic gait transitions | † |
| Mousa et al., TAR | 2025, IROS | Go2 † | Teacher-aligned representations via contrastive learning | Single-objective | † |
| Irie et al., Rough terrain navigation (fuRo) | 2025, Advanced Robotics 39(18):1182-1198 | **Go2 EDU** | Blind deep-RL locomotion (legged_gym, asymmetric actor-critic), three switched policies, stuck-escape | Mobility + recovery | Paper: furo.org |
| Ding et al., Symmetry-guided RL hierarchy (arXiv:2510.10455) | 2025, arXiv, **WITHDRAWN** | Quadruped | Symmetry-guided rewards, gait transitions | Temporal / morphological / time-reversal symmetry | Cite arXiv:2403.10723 instead |
| Munn et al., GCR-PPO | 2025 arXiv / ICRA 2026 | Isaac Lab suite, humanoid | Multi-head critic + priority PCGrad | Many reward terms | github.com/humphreymunn/GCR-PPO |
| Li, Krause, Hutter, Robotic World Model | 2025, arXiv:2501.10100 (NeurIPS 2025 EWM workshop, Outstanding Paper) | ANYmal, others | Learned neural simulator + MBPO-PPO | Model-based policy learning | Project page |
| wty-yy, go2_rl_lab (MoE robust locomotion) | 2026, RSS (per repo) | **Go2** | MoE policy, Isaac Lab 3.0 EA | Robust high-speed tracking | github.com/wty-yy/go2_rl_lab |
| Mousa et al., **PROMO** | 2026, arXiv:2610.01260 (submitted to IEEE) | **Go2** | Preference-conditioned PPO, 3-head semantic critic, fixed priors, action-diversity regulariser | Tracking, stability, efficiency | amrmousa.com/promo |

**What this map means for the team:**

- Go2-specific work with open code is plentiful at the infrastructure level (unitree_rl_lab, robot_lab, go2_rl_lab, Genesis-based go2_sim2real, osudrl quadruped_locomotion) and now includes PROMO for MORL specifically.
- The dominant recipe is fixed: PPO, 4096 parallel environments, terrain curriculum, domain randomisation, asymmetric or teacher-student critics, and an MLP policy at about 50 Hz. The team should adopt it wholesale and not innovate on it.
- Gait emergence from energy (Fu et al.; adaptive energy regularisation) is the scientific hook connecting "gait optimisation" with "Pareto trade-offs": different trade-off points produce different gaits.

## 2. MORL in Robotics and Legged Locomotion

| Work | Year / Venue | Domain | MORL type | Relevance |
|---|---|---|---|---|
| Xu et al., PGMORL | 2020, ICML (PMLR 119) | MO-MuJoCo incl. quadruped-like tasks (speed vs energy) | Multi-policy, evolutionary + prediction model | Found that Pareto sets form distinct "policy families", which maps onto gait families |
| Huang et al., Constrained MORL framework | 2022, CoRL | Robot control (DeepMind) | Constrained MO | Constraint + objective separation |
| Basaklar et al., PD-MORL | 2023, ICLR | MO-MuJoCo | Single universal preference-conditioned network | Off-policy (TD3-based †) |
| Lu et al., CAPQL (Convexity, stationarity and Pareto optimality) | 2023, ICLR | MO-MuJoCo | Preference-conditioned off-policy actor-critic | Off-policy |
| Cai et al., DPMORL | 2023, NeurIPS | MO-MuJoCo | Distributional multi-policy | PROMO baseline; 26.6% fall rate on Go2 sim |
| Terekhov & Gulcehre, MOPPO | 2024, arXiv:2407.16807 | Benchmarks | Preference-conditioned PPO | PROMO baseline; the obvious on-policy starting point |
| Hyper-MORL (Learning Pareto set for continuous robot control) | 2024, IJCAI | MO-MuJoCo | Hypernetwork maps preference to policy parameters | Found Pareto set lies on a low-dimensional manifold in parameter space |
| PSL-MORL | 2025, AAAI | MO benchmarks | Hypernetwork Pareto set learning | Alternative to input-conditioning |
| C-MORL | 2025, ICLR | MO-MuJoCo up to many objectives | Constrained Pareto extension | Multi-policy, better coverage |
| Ambadkar et al., decomposed diversity-driven PC-MORL | 2026, arXiv:2602.07764 | MO-MuJoCo, Building-9d | Late vs early scalarisation | Opposing gradients in 30-55% of steps under early scalarisation |
| Munn et al., GCR-PPO | 2025/2026, ICRA 2026 | Isaac Lab locomotion + humanoid | Multi-head critic, priority gradient surgery | Not preference-conditioned; a fixed-priority MO optimiser |
| Multi-Objective Learning for open-ended robotic problems (arXiv:2411.08070) | 2024, arXiv | Quadruped in MuJoCo | MO curriculum over commands | Command-space coverage, not objective trade-offs |
| Stage-wise reward shaping, constrained MORL (arXiv:2409.15755) | 2024, arXiv | Acrobatic robots | Constrained MO | Constraint handling |
| Preference-conditioned MORL for humanoid force compliance (arXiv:2510.10851) | 2025, arXiv | Humanoid, hardware | Preference-conditioned PPO | Tracking vs compliance |
| PCHC (arXiv:2603.24047) | 2026, arXiv | Humanoid | Multi-expert module + preference-parameterised Beta distribution | Stride length vs disturbance resistance |
| AMOR (arXiv:2505.23708) | 2025 | Humanoid characters / robots, motion tracking | Weight-conditioned MO-PPO + high-level policy predicting weights | **Closest prior art for terrain-adaptive preference selection** |
| **PROMO (arXiv:2610.01260)** | 2026 | **Go2, flat terrain, hardware** | Preference-conditioned PPO, semantic objectives + fixed priors | **Direct prior art** |

**Novelty assessment:** "MORL for quadruped gait on Go2" is now **low novelty** as a headline. What remains open, with evidence:

- **Rough and diverse terrain.** PROMO trains and tests only on flat terrain ("lightweight architecture for preference-conditioned flat-terrain locomotion").
- **Who chooses the preference.** PROMO assumes "a human operator, planner, or supervisory controller supplies w" but does not build or evaluate an automatic selector. AMOR does build one, but for humanoid motion tracking in a different setting.
- **Constraints versus objectives.** PROMO keeps safety-relevant terms as fixed priors. CaT shows constraints can be enforced cheaply in PPO. Nobody has combined constrained safety with preference-conditioned locomotion on terrain.
- **Non-convex fronts.** PROMO's linear scalarisation "does not recover unsupported non-convex regions."
- **Statistical hardware evidence.** PROMO used five trials per condition and four anchors.

**Reviewer risk:** "This is reward-weight conditioning plus Walk These Ways." To defuse it, the paper must show a result that weight conditioning alone cannot explain: a terrain-dependent optimal preference, plus a selector that exploits it under constraints, with real-robot success-rate and energy gains.

## 3. MORL Algorithms: Suitability for Isaac Lab + rsl_rl

| Algorithm | Type | On/off-policy | Fits 4096-env PPO in Isaac Lab? | Notes |
|---|---|---|---|---|
| Fixed weighted-sum PPO sweep | Multi-policy (outer loop) | On | Yes, trivially | Mandatory baseline; each policy is cheap |
| MOPPO / preference-conditioned PPO (PROMO style) | Single-policy conditioned | On | **Yes, best fit** | Sample w per environment per episode; K-head critic; scalarise values / advantages |
| GCR-PPO | Fixed-priority MO | On | Yes (Isaac Lab code exists) | Combine with preference conditioning as an ablation |
| AMOR-style MO-PPO + high-level weight policy | Conditioned + selector | On | Yes | Template for the recommended problem |
| PGMORL | Multi-policy evolutionary | On (PPO-based) | Partially; population of PPO runs | Expensive but parallelisable across the IIT cluster |
| Hyper-MORL / PSL-MORL (hypernetwork) | Pareto set model | Either | Possible; adds complexity | Good ablation: input-conditioning vs hypernetwork |
| C-MORL | Multi-policy constrained extension | On/Off | Possible | Coverage-oriented, more runs |
| Envelope Q-learning † | Conditioned | Off (value-based) | No | Discrete actions in its original form |
| PD-MORL, CAPQL | Conditioned | Off | Poor fit | Need replay; do not exploit massive on-policy parallelism |
| GPI-LS / GPI-PD † | Multi-policy (successor-feature style) | Off | Poor fit | Designed for sample-efficient off-policy settings |
| PCN (Pareto Conditioned Networks) | Return-conditioned supervised | Off / offline | Poor fit | Mostly discrete / low-dimensional |
| DPMORL | Distributional multi-policy | Off/On | Feasible but weak | 26.6% fall rate in PROMO's Go2 sim comparison |

**Libraries:** MO-Gymnasium and MORL-Baselines (Felten et al., NeurIPS 2023 Datasets and Benchmarks Track) are the reference implementations and metric code. They are CPU or Gymnasium-centric, so use them for metrics and algorithm references, not for training on Isaac Lab.

**Metrics:**

- **Hypervolume (HV).** Use a common, range-normalised reference point across methods, as PROMO does.
- **Expected utility (EU)** over a preference distribution.
- **Sparsity.**
- **IGD**, if a reference front can be estimated from the union of all methods.
- **Preference controllability**, the Spearman correlation between w_i and J_i (PROMO).
- Locomotion metrics: fall rate, success rate per terrain, and CVaR of tilt.

**Decision:** Use on-policy, preference-conditioned PPO with a K-head critic as the core. Drop SAC: legged robotics practice and the RWM-U authors note that on-policy PPO gives "significantly more robust and reliable performance".

## 4. Implementation Landscape

**Simulation stack:**

- **unitree_rl_lab** (github.com/unitreerobotics/unitree_rl_lab) is Unitree's official Isaac Lab extension for Go2, H1 and G1-29dof. Its badge targets Isaac Sim 5.1 / Isaac Lab 2.3. It includes C++ deployment via unitree_sdk2 and MuJoCo sim2sim. Lock versions early. RTX 50-series (Blackwell) GPUs need a matching driver / Isaac Sim version, so confirm on the RTX 5090 before anything else.
- **Alternatives:** fan-ziqi/robot_lab (Isaac Lab, Go2 rough-terrain tasks), wty-yy/go2_rl_lab (Isaac Lab 3.0 EA), abizovnuralem/go2_omniverse (ROS 2 digital twin), GaganBhusal/go2_sim2real (Genesis + rsl_rl, zero-shot to hardware via low-level DDS), and legged_gym (Isaac Gym, legacy).
- **About the MuJoCo finding:** the hand-tuned gaits the team saw come from Unitree's example controllers, not from MuJoCo itself. MuJoCo-based RL training (for example MJX / MuJoCo Playground †) is possible. The proposal's sentence about "touch-down and lift-off events and holonomic constraints for each leg" closely matches wording in Ding et al.'s abstract, so rephrase it and attribute it.

**Getting vector rewards out of Isaac Lab (concrete design):**

1. Subclass the manager-based RewardManager. Return a (num_envs, K) tensor by summing configured terms into K groups (for example tracking, efficiency, robustness), plus a separate "prior" group that is always on.
2. Add the preference w (sampled per environment at reset from a truncated Dirichlet, as in PROMO: w_i = 0.1 + 0.7·x_i) to both actor and critic observations through an observation term.
3. In rsl_rl: change RolloutStorage rewards to shape (T, N, K), give the critic K outputs, compute GAE per head, then scalarise advantages with each environment's w. Decide between scalarising raw advantages (PROMO style) or per-head-normalised advantages (APEX style), and treat this as an ablation, because per-head normalisation changes the effective trade-off.
4. Start from code that already does steps 1-3: PROMO's release or GCR-PPO's Isaac Lab/RSL-RL fork. Do not write it from scratch.
5. Add CaT constraints (Gepetto repo, Isaac Lab implementation) for torque limits, joint limits and base/knee collisions.

**Go2 EDU hardware constraints that shape objectives:**

- Peak joint torque about 45 N·m. Per Unitree's spec table (reproduced by UK reseller RoboSavvy), this "refers to the maximum torque of the largest joint motor; the actual maximum torque varies for the 12 joint motors".
- Mass "About 15kg" with battery.
- Battery 8000 mAh standard or 15000 mAh long-endurance, at 28.8 V nominal (28-33.6 V).
- Peak power "About 3000W"; the fast charger is 33.6 V 9 A.
- Speed 0-3.7 m/s (about 5 m/s peak in lab).
- Obstacle height about 16 cm; climbing angle 40°.
- Compute: EDU has a Jetson Orin Nano (40 TOPS), EDU Plus an Orin NX (100 TOPS). Either can run an MLP policy at 50 Hz.
- Sensors: L1 4D LiDAR, foot force sensors, IMU. fuRo found the L1 inadequate for competition navigation and added a Livox Mid-360.
- Vendor spec pages disagree on some numbers (for example one lists 46.4 V), so treat Unitree's datasheet as the authority.

**Measuring objectives on the real Go2:**

- Electrical power from battery voltage and current in the low-level state stream (unitree_sdk2 LowState / BMS fields †).
- Mechanical power from Σ|τ_est·q̇| using motor torque estimates.
- Cost of transport: CoT = P / (m·g·v), with v from motion capture or LiDAR odometry. PROMO reports CoT and J/m on Go2 with Vicon.
- Stability from IMU roll/pitch rates and peak attitude deviation.
- Foot slip from foot-contact flags combined with leg kinematics.
- Smoothness from action-rate and torque-rate RMS.
- Success and falls from trial logs.

## 5. World Models: Is "Pareto Front via World Model" Realistic?

- **LeWM (arXiv:2603.19312, code github.com/lucas-maes/le-wm)** is trained "solely from unannotated trajectories of observations and actions, without access to reward signals". It targets pixel-based planning on 2D/3D control tasks. Using it to approximate a locomotion Pareto front would require adding reward or objective predictors, a proprioceptive encoder, and a contact-rich dynamics model accurate enough for policy optimisation. That is a separate research project.
- **The better-matched route is RWM / RWM-U (ETH)**: a learned neural simulator from observation-action history, used with MBPO-PPO or uncertainty-penalised MOPO-PPO. A realistic world-model contribution would be to **evaluate candidate preferences cheaply** (screening w on recorded real-robot data) rather than to train the front inside the model.
- **Verdict:** Within the November 2026 to February 2027 window, a world-model Pareto approximation is not realistic as a core contribution. Isaac Lab already makes evaluating a preference policy cheap (PROMO evaluates 100 preferences × 1024 environments × 20 s). The world model's compute-saving rationale is weak when simulation is massively parallel. Move it to future work or a post-IROS extension (for example for ICRA 2028).

## 6. Defining "Optimal": Objectives That Are Measurable and Genuinely Conflict

| Objective | Sim measure | Real Go2 measure | Conflict evidence |
|---|---|---|---|
| Command tracking | exp-kernel velocity / yaw error | Vicon or LiDAR odometry RMSE, position MAE | Strong conflict with efficiency (PROMO) |
| Energy / CoT | Σ τ², Σ\|τ·q̇\|, CoT | Battery V·I, CoT, J/m | Efficiency preference: −17.9% to −30.4% specific energy on hardware (PROMO) |
| Stability / robustness | roll/pitch rates, tilt, CVaR tilt | IMU peak attitude | Partly complementary with others (PROMO) |
| Terrain success / falls | terrain level reached, fall rate | Success per lane, falls | Robustness gaits (higher clearance) cost energy |
| Hardware stress | torque, torque rate, joint limits | τ_est, motor temperature | Better as **constraints** (CaT) |
| Smoothness | action rate, jerk | Action / torque-rate RMS | Tracking preference raised action and torque-rate RMS by about 24-49% on hardware (PROMO) |
| Symmetry, foot clearance, air time | gait regularisers | foot contact timing | Better as **fixed priors**, not objectives |

**Recommendation:** Define "optimal" as **Pareto-optimal over 3 objectives (tracking, CoT, robustness/success), subject to hardware-safety constraints**. Report mission-level utility per terrain class. Terrain changes the optimum in a plausible but untested way: low-friction and step fields should favour robustness-heavy preferences (higher clearance, lower speed), and flat or gentle slopes should favour efficiency. Testing this terrain dependence is the scientific core of Problem 1.

## 7. Competition and Venue Alignment

- **ICRA 2027:** Seoul, COEX, 24-28 May 2027. Competitions run 25-27 May 2027. The call for competition proposals has closed, and acceptance results are announced **31 October 2026**. An LRC edition is likely, given that it has run at every ICRA since 2023, but it is **not yet confirmed**. The ICRA 2027 paper deadline (16 September 2026, extended) has passed.
- **LRC/QRC history:**
  - Started at ICRA 2023 (London), then ICRA 2024 (Yokohama), IROS 2024 (Abu Dhabi), ICRA 2025 (Atlanta), IROS 2025 (Hangzhou), and ICRA 2026 (Vienna) as "Legged Robot Challenges", extended to humanoids.
  - The ICRA 2024 course was about 30 m and had five modules: crossing ramps, soft foam, pallet steps with rotating pipes, K-rail diagonals, and a crate stepfield. Inspection meant reading letters inside pipes. Each section was worth 2 points, multiplied by 4 if autonomous. The separate teleop and autonomous categories were merged that year.
- **Winners:**
  - ICRA 2023: KAIST DreamSTEP (DreamWaQ blind RL), 246 points vs MIT's 60.
  - ICRA 2024: fuRo on a Go2 EDU, 336 points (264 mobility, all autonomous).
  - ICRA 2025: ETH Zurich PBL "QuadrupETH", the only team to complete all challenges.
  - ICRA 2026: reportedly FH Upper Austria with a Unitree robot, but this comes only from a vendor marketing blog and is unverified.
  - Go2 is clearly eligible in practice.
- **IROS 2027:** Florence, Italy, Fortezza da Basso. Dates are listed as 26 September to 1 October (IEEE RAS) or 27 September to 1 October (official site). Paper deadline: **1 March 2027**. The proposal's "early March 2027" deadline therefore belongs to **IROS 2027, not IROS 2028**. This review did not verify an IROS 2028 Sydney venue, so remove that reference unless the team confirms it. RSS 2027 (Athens, 6-11 July 2027; paper deadline reported as 16 April 2027 by a deadline aggregator) is a backup venue.
- **Alignment:** LRC scoring rewards autonomy and lane reliability, not Pareto coverage. MORL helps if (a) a terrain-aware selector raises the per-lane success rate or (b) efficiency preferences extend battery life over long trials. The team still needs a navigation and localisation stack (fuRo used FAST-LIO2 + GICP on a prior map, with waypoints). Budget this as a separate engineering track.

## 8. Ranked Refined Research Problems

### Problem 1 (Rank 1): Terrain-Adaptive Preference Selection under Safety Constraints (TAPS)

- **Research question:** Does the utility-optimal preference over {tracking, CoT, robustness} differ systematically across terrain classes? Can a selector that infers terrain from proprioceptive history choose w online so that one preference-conditioned policy outperforms every fixed-w policy and a terrain-oracle lookup?
- **Novelty versus prior art:**
  - PROMO: flat terrain, operator-chosen w.
  - AMOR: humanoid motion tracking, not terrain or constraints.
  - Walk These Ways: hand-specified gait parameters, not objectives.
- **Hypotheses:**
  - H1: the argmax-utility w differs significantly between at least three terrain classes (flat, slopes, stairs/steps, rough/stepfield, low friction).
  - H2: the selector achieves higher mission utility (for example success-weighted energy per metre) than the best single fixed w.
  - H3: CaT constraints keep falls and torque violations flat across w, unlike priors-only.
- **Method:**
  - Train a preference-conditioned PPO with a 3-head critic, fixed priors and CaT constraints, using Isaac Lab rough-terrain curricula for Go2.
  - Stage 2: freeze the policy and train a selector, either (a) supervised on the per-terrain argmax-utility w computed in simulation, or (b) with RL over w at about 1-2 Hz, using proprioceptive history or the policy's latent as input.
- **Baselines:** fixed weighted-sum PPO (5-10 weight sweep); PROMO-style policy with fixed balanced w; MOPPO; CaT single-objective; Walk These Ways-style behaviour conditioning with tuned gait parameters per terrain; terrain-oracle w (upper bound).
- **Metrics:** HV, EU, controllability; per-terrain success, falls, CoT, tracking RMSE; mission utility; hardware CoT from battery power.
- **Ablations:** selector input (proprioception vs privileged terrain label); constraints on/off; 2 vs 3 objectives; advantage normalisation scheme; preference-sampling range.
- **Feasibility:** High. It reuses existing code paths and needs only a few full training runs on the RTX 5090. Hardware needs 3-4 terrain mock-ups (ramp, foam, steps, low-friction sheet).
- **Main risk:** H1 might fail, meaning terrain barely moves the optimum. That would still be a publishable negative or diagnostic result if it is framed as a Pareto analysis.

### Problem 2 (Rank 2): Rough-Terrain MO Benchmark and the Amortisation Gap

- **Question:** On rough terrain, how much Pareto quality (HV, EU, falls) does one preference-conditioned policy lose compared with a set of specialists (PGMORL / C-MORL style) and a hypernetwork policy? Do discrete gait families appear along the energy-speed front?
- **Contribution:** An open-source vector-reward Isaac Lab Go2 benchmark with MORL baselines and metrics (a resource paper).
- **Feasibility:** Very high. **Novelty:** medium. **Risk:** "benchmark only" reviews. Mitigate with the gait-family analysis, linking PGMORL's policy families to Fu et al.'s gait emergence.

### Problem 3 (Rank 3): Objectives vs Constraints vs Priors for Locomotion MORL

- **Question:** Which locomotion reward terms should be preference axes, which hard constraints (CaT), and which fixed priors? What is the effect on Pareto quality and hardware safety?
- **Builds on:** PROMO's 6% vs 21.8% fall-rate ablation and CaT.
- **Feasibility:** High. **Novelty:** medium. Good fallback paper that can be combined with Problem 1.

### Problem 4 (Rank 4): Energy-Robustness Trade-off and Battery-Aware Preference Scheduling on Real Go2

- **Question:** Can preference scheduling based on state of charge extend mission range without lowering lane success rates?
- **Strong for the competition, moderate novelty.** Needs long hardware trials.

### Problem 5 (Rank 5, defer): World-Model-Assisted Preference Screening

- **Question:** Can an RWM-style model trained on real Go2 logs predict per-objective returns for unseen w well enough to pick preferences without hardware trials?
- **High risk:** world-model exploitation and contact-rich prediction error. Post-IROS only.

### Comparison

| Problem | Novelty | Feasibility by 1 March 2027 | Publishability (IROS) | Competition value |
|---|---|---|---|---|
| 1 TAPS | High | Medium-High | High | Medium-High |
| 2 Benchmark + amortisation | Medium | Very High | Medium | Low |
| 3 Objectives/constraints/priors | Medium | High | Medium | Medium |
| 4 Battery-aware scheduling | Medium | Medium | Medium | High |
| 5 World-model screening | Medium-High | Low | Low (in time) | Low |

## 9. Critique of the Current Proposal and Revised Research Question

**Weaknesses:**

1. **"Optimal" and "any terrain" are undefined.** Replace them with Pareto optimality over named objectives, subject to constraints, on a stated terrain set.
2. **Gait optimisation versus terrain generalisation are conflated.** The motivation is getting immobilised on hard terrain, which is a robustness and traversability problem. The method is about trade-offs. Problem 1 connects the two explicitly.
3. **The objective set mixes objectives and shaping terms** (smoothness, symmetry). PROMO shows this hurts.
4. **Venue inconsistency:** the deadline is IROS 2027 (Florence, 1 March 2027).
5. **A withdrawn citation:** Ding et al. arXiv:2510.10455 was withdrawn. The arXiv comment says it reuses "the main novel concept from arXiv:2403.10723".
6. **The world-model step is overambitious** and LeWM does not fit it.
7. **The algorithm choice is open-ended.** SAC and off-policy MORL do not exploit Isaac Lab's parallelism.
8. **Baselines are missing:** PROMO, MOPPO, weight sweeps, CaT, Walk These Ways, RMA/TAR-style single-objective controllers.
9. **The timeline is out of date.** As of 22 October 2026, about 4 months remain before IROS. Real-world deployment (November to January) overlaps with writing, and the competition is unconfirmed.
10. **Related work is thin.** It needs PROMO, AMOR, GCR-PPO, PGMORL, CaT, Lee et al. constraints, and Fu et al.

**Revised research question:**

> *"For a Unitree Go2 traversing heterogeneous terrain, how does the Pareto-optimal trade-off among velocity tracking, cost of transport and traversal robustness change with terrain? Can a constraint-aware, preference-conditioned locomotion policy, combined with a proprioceptive terrain-aware preference selector, achieve higher mission-level utility than fixed-weight and behaviour-conditioned controllers in simulation and on hardware?"*

## 10. Realistic Timeline Revision (from 22 October 2026)

| Window | Work | Exit criterion |
|---|---|---|
| 22 Oct to 10 Nov 2026 | Reproduce PROMO / GCR-PPO on the RTX 5090. Lock Isaac Sim / Isaac Lab versions. Set up vector-reward RewardManager + K-head critic. Check the ICRA 2027 competition list (31 Oct) | Balanced-w policy walks on rough-terrain curriculum |
| 10 Nov to 5 Dec | Train preference-conditioned + CaT policy on 5 terrain classes. Run fixed-weight sweep baselines on the IIT cluster | HV/EU per terrain; H1 test |
| 5 Dec to 31 Dec | Selector (supervised then RL). Ablations. Sim2sim in MuJoCo | H2 in simulation |
| Jan 2027 | Hardware: 4 terrain mock-ups, battery-power logging, ≥10 trials per condition | Real CoT/success tables |
| 1 Feb to 1 Mar 2027 | Write the IROS 2027 paper. Freeze experiments by 10 February | Submission by 1 March |
| Mar to May 2027 | If LRC is confirmed: navigation stack, lane rehearsals, battery-aware scheduling (Problem 4) | Competition readiness for 25-27 May |
| Post-May 2027 | World-model screening (Problem 5), journal extension | |

## 11. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Reviewers: "same as PROMO / just weight conditioning" | High | Lead with the terrain-dependence finding and selector; cite PROMO prominently; include it as a baseline |
| Terrain does not shift the optimal w (H1 fails) | Medium | Report as a Pareto diagnostic; pivot to Problem 3 framing |
| RTX 5090 / Isaac Sim incompatibility | Medium | Verify in week 1; fall back to the cluster or Genesis |
| Preference ignored by policy (low controllability) | Medium | PROMO's action-diversity regulariser; truncated simplex sampling; check Spearman ρ |
| Sim-to-real gap in energy (motor model) | Medium-High | Actuator randomisation; report electrical and mechanical power; calibrate on flat ground |
| Hardware damage on steps / foam | Medium | CaT torque and collision constraints; harness; staged terrains |
| LRC not accepted at ICRA 2027 | Medium | Treat competition as optional; target RoboCup Rescue or IROS 2027 competitions |
| Time | High | Freeze scope to Problem 1 (+ Problem 3 ablations); world model out of scope |

## Caveats

- PROMO (October 2026) is a preprint submitted to IEEE and not yet peer-reviewed. Its numbers come from its own evaluation protocol: five hardware trials per condition and flat terrain.
- Some entries (marked †) come from established domain knowledge and were not re-verified in this review. Confirm venues and code links before citing.
- The ICRA 2026 LRC winner claim comes only from a vendor marketing blog. The IROS 2024 and IROS 2025 QRC winners were not found.
- Go2 specifications vary between resellers. Use Unitree's official datasheet.
- IROS 2027 dates differ by one day between sources (26 vs 27 September start). The 1 March 2027 deadline is consistent across the IEEE RAS listing and several trackers, but confirm it on the official site when the call for papers is published.

## Sources

- [IROS 2027 (BERI events)](https://www.beri.net/events/iros-2027)
- [PROMO, arXiv:2610.01260 (HTML)](https://arxiv.org/html/2610.01260)
- [PROMO, arXiv:2610.01260 (abstract)](https://arxiv.org/abs/2610.01260)
- [Adaptive energy regularisation, arXiv:2403.20001](https://arxiv.org/pdf/2403.20001)
- [Multi-critic loco-manipulation, arXiv:2608.28140](https://arxiv.org/pdf/2608.28140)
- [APEX, arXiv:2505.10022](https://arxiv.org/pdf/2505.10022)
- [Robotic World Model project page](https://sites.google.com/view/roboticworldmodel)
- [RWM-U, arXiv:2504.16680](https://arxiv.org/html/2504.16680v3)
- [fuRo QRC 2024 paper (Irie et al.)](https://www.furo.org/irie/papers/ar_qrc2024.pdf)
- [arXiv:2403.18765 (PDF)](https://arxiv.org/pdf/2403.18765)
- [arXiv:2403.18765 (abstract)](https://arxiv.org/abs/2403.18765)
- [CaT: Constraints as Terminations (GitHub)](https://github.com/Gepetto/constraints-as-terminations)
- [Ding et al., arXiv:2510.10455 (withdrawn)](https://arxiv.org/abs/2510.10455)
- [PGMORL, ICML 2020 (PMLR 119)](https://proceedings.mlr.press/v119/xu20h/xu20h.pdf)
- [Hyper-MORL, IJCAI 2024](https://www.ijcai.org/proceedings/2024/0544.pdf)
- [PSL-MORL, AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/34068/36223)
- [C-MORL (ResearchGate)](https://www.researchgate.net/publication/384630691_C-MORL_Multi-Objective_Reinforcement_Learning_through_Efficient_Discovery_of_Pareto_Front)
- [Ambadkar et al., arXiv:2602.07764](https://arxiv.org/pdf/2602.07764)
- [PCHC, arXiv:2603.24047](https://arxiv.org/html/2603.24047)
- [AMOR, arXiv:2505.23708](https://arxiv.org/html/2505.23708v1)
- [unitree_rl_lab notes (Robotics_Notebooks)](https://github.com/ImChong/Robotics_Notebooks/blob/main/wiki/entities/unitree-rl-lab.md)
- [go2_rl_lab (GitHub)](https://github.com/wty-yy/go2_rl_lab)
- [robot_lab (GitHub)](https://github.com/fan-ziqi/robot_lab)
- [go2_omniverse (GitHub)](https://github.com/abizovnuralem/go2_omniverse)
- [go2_sim2real (GitHub)](https://github.com/GaganBhusal/go2_sim2real)
- [A synergetic theory of quadrupedal gaits and gait transitions](https://www.researchgate.net/publication/20816916_A_synergetic_theory_of_quadrupedal_gaits_and_gait_transitions)
- [Unitree Go2 brochure (Generation Robots)](https://static.generation-robots.com/media/brochure-unitree-go2-de.pdf)
- [Go2 EDU (Synergy Tech)](https://synergytech.es/en/elements/ver/robot-go2-edu)
- [Go2 EDU (Robostore)](https://robostore.com/products/go2-edu-40-tops-computing-quadruped-robot-dog)
- [Unitree Go2 specs (aihumanlove)](https://aihumanlove.com/tools/robots/unitree-go2/specs.html)
- [LeWorldModel, arXiv:2603.19312](https://arxiv.org/html/2603.19312v1)
- [Call for ICRA 2027 Competition Proposals (PDF)](http://2027.ieee-icra.org/wp-content/uploads/sites/4/2026/07/Call-for-ICRA-2027-Competition-Proposals.pdf)
- [ICRA 2027 call for competitions](https://2027.ieee-icra.org/announcements/call-for-competitions/)
- [ICRA 2027 call for papers](https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/)
- [ICRA 2026 competitions](https://2026.ieee-icra.org/program/competitions/)
- [KED Global: KAIST DreamSTEP wins ICRA 2023 QRC](https://www.kedglobal.com/robotics/newsView/ked202306070009)
- [ETH Zurich: QuadrupETH wins ICRA 2025 QRC](https://ee.ethz.ch/news-and-events/d-itet-news-channel/2025/06/quadrupeth-secures-first-place-in-icra-quadruped-robot-challenges.html)
- [CaddxFPV blog: Team Upper Austria at ICRA 2026](https://www.caddxfpv.com/blogs/news/from-fpv-to-robotics-caddxfpv-powers-team-upper-austria-to-an-icra-2026-championship)
- [IEEE RAS: IROS 2027 event listing](https://www.ieee-ras.org/event/2027-ieee-rsj-international-conference-on-intelligent-robots-and-systems-iros-70525/)
- [IROS 2027 official site](https://2027.ieee-iros.org/)
- [IROS 2027 deadline (trybibby)](https://trybibby.com/conference-deadlines/iros-2027)
- [AI conference deadlines (mlciv)](https://mlciv.com/ai-deadlines/)
