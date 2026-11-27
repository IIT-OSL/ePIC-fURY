# Audit: unitree_rl_lab `Unitree-Go2-Velocity` (Sprint 2, read-only)

Date: 2026-11-27. Status: **signed off by Daham on 2026-11-27. Nothing has been changed.**

Sources (all read, nothing edited):
- Task config: `external/unitree_rl_lab/source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/robots/go2/velocity_env_cfg.py` (commit `4960b84`)
- Robot + actuator: `.../assets/robots/unitree.py` (`UNITREE_GO2_CFG`), `.../assets/robots/unitree_actuators.py` (`UnitreeActuatorCfg_Go2HV`)
- Resolved values as Isaac Lab actually built them: `experiments/_smoke_url_go2_20261127/env.yaml`, `agent.yaml`, `deploy.yaml`, `train.log`
- Joint names, default pose, Kp/Kd, joint limits and masses printed from the live env (1-env check, 2026-11-27)

Notes on the tables:
- "Noise" is uniform additive noise, applied only to the policy group (`enable_corruption: true`). The critic group gets no noise (`enable_corruption: false`).
- "Scale" multiplies the value **after** noise. A clip of (-100, 100) is effectively no clip.
- History length is 1 everywhere (no stacked past frames).

## 1. Policy (actor) observations: 45 inputs

| # | Term | Dim | Source on the real robot | Scale | Noise | Clip |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `base_ang_vel` (body angular velocity, base frame) | 3 | IMU gyroscope | **0.2** | ±0.2 rad/s | ±100 |
| 1 | `projected_gravity` (gravity direction in base frame) | 3 | IMU orientation (quaternion) | 1.0 | ±0.05 | ±100 |
| 2 | `velocity_commands` (vx, vy, yaw rate) | 3 | joystick / operator | 1.0 | none | ±100 |
| 3 | `joint_pos_rel` (joint angle − default pose) | 12 | joint encoders | 1.0 | ±0.01 rad | ±100 |
| 4 | `joint_vel_rel` (joint velocity) | 12 | joint encoders | **0.05** | ±1.5 rad/s | ±100 |
| 5 | `last_action` (previous policy output, before scaling) | 12 | controller memory | 1.0 | none | ±100 |
| | **Total** | **45** | | | | |

Joint terms (3, 4, 5) follow the policy joint order in section 3.
The deploy side must apply the same two scales: **0.2 on angular velocity, 0.05 on joint velocity**.
These are also in `deploy.yaml` under `observations`.

## 2. Critic observations: 60 inputs (training only, never deployed)

| # | Term | Dim | Scale | Noise | Clip |
| --- | --- | --- | --- | --- | --- |
| 0 | `base_lin_vel` (privileged: true body velocity) | 3 | 1.0 | none | ±100 |
| 1 | `base_ang_vel` | 3 | 0.2 | none | ±100 |
| 2 | `projected_gravity` | 3 | 1.0 | none | ±100 |
| 3 | `velocity_commands` | 3 | 1.0 | none | ±100 |
| 4 | `joint_pos_rel` | 12 | 1.0 | none | ±100 |
| 5 | `joint_vel_rel` | 12 | 0.05 | none | ±100 |
| 6 | `joint_effort` (privileged: applied joint torque) | 12 | 0.01 | none | ±100 |
| 7 | `last_action` | 12 | 1.0 | none | ±100 |
| | **Total** | **60** | | | |

A height scan exists in the scene (`height_scanner`, 1.6 × 1.0 m grid), but it is commented out of both groups, so neither network uses it.

## 3. Actions: 12 outputs

**Joint target = default pose + 0.25 × action**: `JointPositionAction`, `use_default_offset: true`, clip ±100 (effectively none).

| Policy index | Joint | Default pos (rad) | Action scale | SDK motor index (`joint_ids_map`) |
| --- | --- | --- | --- | --- |
| 0 | FL_hip_joint | 0.1 | 0.25 | 3 |
| 1 | FR_hip_joint | −0.1 | 0.25 | 0 |
| 2 | RL_hip_joint | 0.1 | 0.25 | 9 |
| 3 | RR_hip_joint | −0.1 | 0.25 | 6 |
| 4 | FL_thigh_joint | 0.8 | 0.25 | 4 |
| 5 | FR_thigh_joint | 0.8 | 0.25 | 1 |
| 6 | RL_thigh_joint | 1.0 | 0.25 | 10 |
| 7 | RR_thigh_joint | 1.0 | 0.25 | 7 |
| 8 | FL_calf_joint | −1.5 | 0.25 | 5 |
| 9 | FR_calf_joint | −1.5 | 0.25 | 2 |
| 10 | RL_calf_joint | −1.5 | 0.25 | 11 |
| 11 | RR_calf_joint | −1.5 | 0.25 | 8 |

How the two joint orders relate:
- **Policy order** (Isaac Lab): all hips, then all thighs, then all calves, each as FL, FR, RL, RR.
- **SDK order** (`joint_sdk_names`): grouped by leg, FR, FL, RR, RL, with hip, thigh, calf inside each leg.
- `deploy.yaml` maps policy index → SDK index: `joint_ids_map: [3, 0, 9, 6, 4, 1, 10, 7, 5, 2, 11, 8]`.

I checked this mapping against the joint names printed from the live env, and it is consistent. Checklist row 1 in Sprint 3 re-checks it on the deploy side.

**Soft joint limits** (90% of the USD limits, in rad):

| Joint | Limits |
| --- | --- |
| Hips | ±0.942 |
| Front thighs | −1.318 to 3.238 |
| Rear thighs | −0.271 to 4.285 |
| Calves | −2.628 to −0.932 |

## 4. Control timing

| Item | Value |
| --- | --- |
| Sim dt | 0.005 s (200 Hz physics) |
| Decimation | 4 |
| **Policy period / rate** | **0.02 s / 50 Hz** (`deploy.yaml: step_dt: 0.02`) |
| Render interval | 4 |
| Episode length | 20 s = 1000 policy steps |
| PPO rollout | 24 steps per env per iteration (0.48 s) |

## 5. Actuator model and PD gains

All 12 joints are one group, `GO2HV`, of class `UnitreeActuator`, a Unitree subclass of Isaac Lab's `DelayedPDActuator`. The torque is computed explicitly in Python, not by the PhysX implicit drive:

**torque = Kp·(q_target − q) − Kd·q̇**, then clipped by the torque-speed curve.

| Parameter | Value | Meaning |
| --- | --- | --- |
| Kp (stiffness) | **25.0** N·m/rad, all joints | |
| Kd (damping) | **0.5** N·m·s/rad, all joints | |
| Y1 | 20.2 N·m | peak torque when torque and speed point the same way |
| Y2 | 23.4 N·m | peak torque when they point opposite ways (braking) |
| X1 | 13.5 rad/s | full torque available up to this speed |
| X2 | 30 rad/s | no-load speed; available torque falls linearly to 0 between X1 and X2 |
| Joint friction (PhysX) | 0.01 | |
| Fs / Fd (actuator friction model) | 0 / 0 | off |
| Actuator delay | min 0, max 0 steps | **no delay** |
| Armature | not set | |

These Kp and Kd values match the built-in Isaac Lab task (25 / 0.5); the torque limit model is different.
`deploy.yaml` carries Kp and Kd in SDK order (all 25 / 0.5).

**Robot masses** from the USD: base 7.28 kg, each hip 0.77, thigh 1.24, calf 0.15, foot 0.04 kg. That is about 15.2 kg in total, before the random added mass in section 6.

## 6. Randomisation and other events

| Event | Range | When it fires |
| --- | --- | --- |
| `physics_material`: friction and restitution of every robot body | static friction 0.3 to 1.2, dynamic friction 0.3 to 1.2, restitution 0 to 0.15, 64 buckets | startup (once per env) |
| `add_base_mass`: extra mass on the base | −1.0 to +3.0 kg (added) | startup |
| `base_external_force_torque` | force 0, torque 0 (**effectively off**) | reset |
| `reset_base`: start position and heading | x, y ±0.5 m, yaw ±π; start velocity 0 | reset |
| `reset_robot_joints` | joint positions = default × 1.0 (no spread); joint velocities ±1.0 rad/s | reset |
| `push_robot`: sets the base velocity | vx, vy ±0.5 m/s | **every 5 to 10 s** (interval) |
| Observation noise | policy group only (see section 1) | every step |
| Ground friction (terrain material) | fixed 1.0 / 1.0, multiply combine mode (so the robot-side randomisation sets the effective friction) | fixed |

**Not present:**
- motor gain (Kp/Kd) randomisation
- actuator or action delay (the actuator supports it, but it is set to 0)
- observation latency
- centre-of-mass shift
- joint friction or armature randomisation
- gravity or IMU bias

**Other settings that shape training (not randomisation):**

- **Terrain.** `terrain_type: generator` with `COBBLESTONE_ROAD_CFG`. Only the `flat` (MeshPlane) sub-terrain is enabled; rough, slopes, boxes and stairs are commented out, so the ground is **flat**. The `terrain_levels` curriculum is active but has no effect on flat ground.
- **Commands.**
  - Resampled every 10 s. 10% of envs are commanded to stand still. Direct yaw-rate commands, no heading mode.
  - **Command curriculum (`lin_vel_cmd_levels`).** The ranges start at vx, vy ±0.1 m/s and yaw ±1.0 rad/s. When the mean linear tracking reward of an episode exceeds 80% of its maximum, vx and vy each widen by 0.1. This is checked once every 1000 env steps, about every 42 iterations.
  - Limits: **vx ±1.0, vy ±0.4, yaw ±1.0**, as exported to `deploy.yaml`.
  - So vx needs at least 9 widenings (≥ ~375 iterations) before 1.0 m/s is even being trained.
  - Play cfg (`RobotPlayEnvCfg`) uses the full limit ranges.
- **Terminations.**
  - `time_out` (20 s)
  - `base_contact` (base contact force > 1 N)
  - `bad_orientation` (tilt > 0.8 rad ≈ 46°)

## 7. Rewards (for the report, not to change)

17 terms are active.

| Term | Function | Weight | What it does |
| --- | --- | --- | --- |
| `track_lin_vel_xy` | `track_lin_vel_xy_exp`, std 0.5 | **+1.5** | follow the commanded vx, vy |
| `track_ang_vel_z` | `track_ang_vel_z_exp`, std 0.5 | **+0.75** | follow the commanded yaw rate |
| `base_linear_velocity` | `lin_vel_z_l2` | −2.0 | vertical bouncing |
| `base_angular_velocity` | `ang_vel_xy_l2` | −0.05 | roll and pitch rates |
| `joint_vel` | `joint_vel_l2` | −0.001 | joint speeds |
| `joint_acc` | `joint_acc_l2` | −2.5e-7 | joint accelerations |
| `joint_torques` | `joint_torques_l2` | −2e-4 | squared torques |
| `action_rate` | `action_rate_l2` | −0.1 | change of action between steps (smoothness) |
| `dof_pos_limits` | `joint_pos_limits` | −10.0 | joints beyond the soft limits |
| `energy` | Σ\|q̇\|·\|τ\| (unitree mdp) | −2e-5 | mechanical power; the same quantity as our eval power metric |
| `flat_orientation_l2` | `flat_orientation_l2` | −2.5 | body tilt |
| `joint_pos` | `joint_position_penalty`, stand_still_scale 5.0, velocity_threshold 0.3 | −0.7 | distance from the default pose; 5× stronger when the command is zero and the body is slower than 0.3 m/s |
| `feet_air_time` | `feet_air_time`, threshold 0.5 s | +0.1 | taking real steps |
| `air_time_variance` | `air_time_variance_penalty` | −1.0 | uneven air and contact times across the four feet (asymmetric gait) |
| `feet_slide` | `feet_slide` | −0.1 | feet sliding while in contact |
| `undesired_contacts` | `undesired_contacts` on Head, hip, thigh and calf, threshold 1 N | −1.0 | anything but the feet touching the ground |

## 8. Flagged: policy inputs the real robot cannot measure

**None.** All 45 policy inputs come from sensors the real Go2 has:
- IMU gyro and orientation
- joint encoders
- the joystick
- the controller's own last action

This matches the CLAUDE.md rule exactly.

- **Base linear velocity:** critic only (allowed).
- **Joint effort:** critic only (allowed).
- **Height scan:** not used at all.

So **`/s2-deployable-cfg` should not be needed.**

### Not input violations, but worth your eyes before sign-off (no change proposed)

1. **No actuator delay and no motor-gain randomisation.** The real robot has communication and actuation latency, and these are the usual sim-to-real gaps. If the robot jitters in MuJoCo or on the floor, adding them as a new config class is the first fallback (plan, Risks table). Keep the task as it is for now.
2. **Command curriculum.** 1.0 m/s is only trained once the curriculum has widened that far. A short run may never see 1.0 m/s, which matters for the eval's "walk fast" row. Check `Curriculum/lin_vel_cmd_levels` in TensorBoard before choosing the training length.
3. **Sidestep and yaw are inside the trained range** (eval sidestep 0.3 < 0.4; eval turn 0.8 < 1.0). On the real robot, joystick commands must be clipped to vx ±1.0, vy ±0.4, yaw ±1.0 (checklist row 5).
4. **Deploy-side scaling.** The deploy controller must apply 0.2 to angular velocity, 0.05 to joint velocity, 0.25 to actions, the default-pose offset, and the policy↔SDK joint map. All of these are in `deploy.yaml`; checklist rows 2, 3 and 5 verify them in Sprint 3.

## 9. PPO and training defaults (reference, for the training-length decision)

| Item | Value |
| --- | --- |
| Actor / critic | MLP 512-256-128, ELU, no obs normalisation, init action std 1.0 |
| PPO | clip 0.2, lr 1e-3 adaptive (KL 0.01), γ 0.99, λ 0.95, 5 epochs × 4 mini-batches, entropy 0.01, value loss 1.0 clipped, max grad norm 1.0 |
| Rollout | 4096 envs × 24 steps |
| `max_iterations` | **50,000** (unitree default) |
| `save_interval` | 100 |
| Measured speed | ≈ 2.05 s/iteration on the RTX 5090, so 50,000 iterations ≈ 28 h per run |

## Comparison with the Sprint 1 built-in task (`Isaac-Velocity-Flat-Unitree-Go2-v0`)

| | Built-in (Sprint 1) | unitree_rl_lab (this audit) |
| --- | --- | --- |
| `base_lin_vel` in policy | **yes (not deployable)** | no (critic only) |
| Policy inputs | 48 | 45 |
| Ang-vel / joint-vel scales | 1.0 / 1.0 | 0.2 / 0.05 |
| Actuator | DCMotor, 23.5 N·m | Unitree Go2HV torque-speed curve, 20.2 / 23.4 N·m |
| Kp / Kd | 25 / 0.5 | 25 / 0.5 |
| Friction randomisation | fixed 0.8 / 0.6 | 0.3 to 1.2 |
| Pushes | off | ±0.5 m/s every 5 to 10 s |
| Command ranges | ±1 / ±1 / ±1, no curriculum | ±1.0 / ±0.4 / ±1.0, with curriculum |
| Reward terms | 9 active | 17 active |
| Network | 128-128-128 | 512-256-128 |
| Default iterations | 300 | 50,000 |
| Exports `deploy.yaml` | no | yes |

---

**Sign-off**

- [x] Policy inputs (section 1) accepted as deployable
- [x] Randomisation (section 6) accepted as is
- [x] Rewards (section 7) recorded for the report, unchanged

Signed: Daham ("approved", in session) Date: 2026-11-27
