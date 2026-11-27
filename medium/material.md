# Medium tutorial: raw material (Sprint 2)

Raw material only, not the article. Daham writes the article.
Everything here was run on the workstation between 2026-11-20 and 2026-11-27. Sources:
- each run's `cmd.txt`, `play_cmd.txt`, `eval_cmd.txt`, `record_cmd.txt`
- `experiments/NOTES.md` (errors), `experiments/policy_inputs.md` (audit), `experiments/DECISIONS.md`
- the unitree_rl_lab source at commit `4960b84`

Paths: the repo lives at `~/ePICfURY/ePIC-fURY` (called `$WORK` below). Commands are copied from the real runs, with the absolute
home path replaced by `$WORK`.

---

## 0. Versions (put these at the top of the tutorial)

| Item | Version |
| --- | --- |
| GPU | NVIDIA RTX 5090 32 GB, driver 580.173.02, CUDA 13.0 (PyTorch 2.7.0+cu128 inside the env) |
| OS | Ubuntu 26.04 |
| Isaac Sim | 5.1.0 (pip package `isaacsim` 5.1.0.0, conda env `env_isaaclab`) |
| Isaac Lab | 2.3.2 (`v2.3.2-32-g858234d06e`) |
| RSL-RL | rsl-rl-lib 5.0.1 |
| unitree_rl_lab | commit `4960b84` (package 0.2.1) |
| Python | 3.11.15 |

---

## 1. Commands that worked, in order (clean machine → recorded video)

### 1.1 Isaac Sim + Isaac Lab install

**Not captured in these sessions.** Isaac Sim 5.1.0 (pip) and Isaac Lab 2.3.2 were already installed in the conda env
`env_isaaclab` before Sprint 0, at `~/isaac-installations/IsaacLab`.
→ Daham: add the install commands you used (conda env create, `pip install isaacsim[...]`, `./isaaclab.sh --install`), or
point readers to the official Isaac Lab pip install guide for these exact versions.

Activate the env (needed before every command below):

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
```

### 1.2 Check the install: list the Go2 tasks (Sprint 0)

```bash
cd ~/isaac-installations/IsaacLab
PYTHONUNBUFFERED=1 ./isaaclab.sh -p scripts/environments/list_envs.py --keyword Go2
```

Notes: this script rejects `--headless` in Isaac Lab 2.3.2 (it is always headless). Without `PYTHONUNBUFFERED=1`, the table is
lost when output goes to a file. Both issues are in section 3.

### 1.3 Built-in Go2 baseline (Sprint 1), for comparison

Smoke test (20 iterations):

```bash
cd ~/isaac-installations/IsaacLab && ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Unitree-Go2-v0 --headless --seed 42 --max_iterations 20 --run_name smoke_seed42
```

Full run (300 iterations is the task default, about 2 min on the RTX 5090). Seeds 42, 43 and 44 used the same command:

```bash
cd ~/isaac-installations/IsaacLab && PYTHONUNBUFFERED=1 ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Unitree-Go2-v0 --headless --seed 42 --run_name baseline_seed42_20261120-0930
```

Playback video + policy export:

```bash
cd ~/isaac-installations/IsaacLab && PYTHONUNBUFFERED=1 ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Velocity-Flat-Unitree-Go2-Play-v0 --headless --video --video_length 500 --num_envs 16 \
    --checkpoint logs/rsl_rl/unitree_go2_flat/2026-11-20_09-30-45_baseline_seed42_20261120-0930/model_299.pt
```

All 3 seeds in a row: `$WORK/scripts/run_baseline.sh`. The script waits while another job is on the GPU.

### 1.4 Install unitree_rl_lab (same conda env as Isaac Lab)

```bash
cd $WORK/external && git clone https://github.com/unitreerobotics/unitree_rl_lab
# we used commit 4960b84
cd $WORK && pip install -e external/unitree_rl_lab/source/unitree_rl_lab   # pulls in argcomplete only
```

Download only the Go2 robot model from Hugging Face (19 MB, no git-lfs needed):

```bash
cd $WORK && python -c "
from huggingface_hub import snapshot_download
p=snapshot_download(repo_id='unitreerobotics/unitree_model',repo_type='dataset',allow_patterns=['Go2/*'],local_dir='external/unitree_model')
print(p)"
```

Point unitree_rl_lab at the model. This is the only edit to its files, in
`external/unitree_rl_lab/source/unitree_rl_lab/unitree_rl_lab/assets/robots/unitree.py`:

```python
UNITREE_MODEL_DIR = "/home/<user>/ePICfURY/ePIC-fURY/external/unitree_model"
# the Go2 config then loads f"{UNITREE_MODEL_DIR}/Go2/usd/go2.usd"
```

We did **not** use `./unitree_rl_lab.sh -i`: it needs git-lfs and changes the conda activate scripts and shell completion
(see section 3).

Check that the tasks are registered:

```bash
cd $WORK/external/unitree_rl_lab && PYTHONUNBUFFERED=1 python scripts/list_envs.py
```

### 1.5 Wrapper scripts for rsl-rl 5 (our repo: `scripts/unitree_rl_lab/`)

unitree_rl_lab's own `scripts/rsl_rl/train.py` and `play.py` were written for an older rsl-rl and do not work with rsl-rl-lib 5.0.1
(see section 3). We copied them to `url_train.py` and `url_play.py` and made small changes. All of them are marked `# ePIC fURY`:

```python
# url_train.py: convert unitree's legacy `policy=` config to the rsl-rl >= 4 actor/critic configs
from isaaclab_rl.rsl_rl import handle_deprecated_rsl_rl_cfg
agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_version)
```

```python
# url_play.py: rsl-rl >= 4 has no runner.alg.policy / actor_critic; use the runner's own exporters
if _vparse(version("rsl-rl-lib")) >= _vparse("4.0.0"):
    runner.export_policy_to_jit(path=export_model_dir, filename="policy.pt")
    runner.export_policy_to_onnx(path=export_model_dir, filename="policy.onnx")
```

```python
# url_play.py: module moved in Isaac Lab 2.3.2
from isaaclab_rl.utils.pretrained_checkpoint import ...   # was isaaclab.utils.pretrained_checkpoint
```

Smoke test (10 iterations):

```bash
cd $WORK/external/unitree_rl_lab && PYTHONUNBUFFERED=1 python $WORK/scripts/unitree_rl_lab/url_train.py \
    --headless --task Unitree-Go2-Velocity --max_iterations 10 --seed 42 --run_name smoke_url
```

### 1.6 Training task: full command range, no curriculum

The upstream command curriculum never widened past ±0.1 m/s in our 3,000-iteration budget (section 3). So we registered a
variant task in our own repo, `scripts/unitree_rl_lab/epic_tasks/`, and left upstream untouched:

```python
# epic_tasks/go2_fullcmd_cfg.py
def _full_command_range(cfg) -> None:
    cmd = cfg.commands.base_velocity
    lim = cmd.limit_ranges
    cmd.ranges.lin_vel_x = tuple(lim.lin_vel_x)  # (-1.0, 1.0)
    cmd.ranges.lin_vel_y = tuple(lim.lin_vel_y)  # (-0.4, 0.4)
    cmd.ranges.ang_vel_z = tuple(lim.ang_vel_z)  # (-1.0, 1.0)
    cfg.curriculum.lin_vel_cmd_levels = None

@configclass
class RobotEnvCfgFullCmd(RobotEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        _full_command_range(self)
```

```python
# epic_tasks/__init__.py
gym.register(
    id="Unitree-Go2-Velocity-FullCmd",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "epic_tasks.go2_fullcmd_cfg:RobotEnvCfgFullCmd",
        "play_env_cfg_entry_point": "epic_tasks.go2_fullcmd_cfg:RobotPlayEnvCfgFullCmd",
        "rsl_rl_cfg_entry_point": "unitree_rl_lab.tasks.locomotion.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",
    },
)
```

### 1.7 Train (3,000 iterations, 4,096 envs, headless; about 95–101 min per run)

The seed-44 run, which is the one chosen for deployment:

```bash
cd $WORK/external/unitree_rl_lab && PYTHONUNBUFFERED=1 python $WORK/scripts/unitree_rl_lab/url_train.py \
    --headless --task Unitree-Go2-Velocity-FullCmd --seed 44 --max_iterations 3000 --run_name own_seed44_20261127-1505
```

Seeds 42, 43, 44, then 42 again, in a row, in tmux:

```bash
tmux new-session -d -s epic -n own "cd $WORK && ITERS=3000 scripts/run_own.sh 2>&1 | tee experiments/run_own_<stamp>.log"
```

Logs and checkpoints go to `external/unitree_rl_lab/logs/rsl_rl/unitree_go2_velocity_fullcmd/<date>_<run_name>/`, along with
`params/deploy.yaml`.

Optional live viewer of the newest checkpoint while training runs headless (needs a display):

```bash
cd $WORK/external/unitree_rl_lab && DISPLAY=:2 PYTHONUNBUFFERED=1 python ../../tools/watch_ckpt.py --num_envs 16
```

### 1.8 Curves

```bash
cd $WORK
python tools/plot_curves.py experiments/own_flat_seed42_20261127-1142 experiments/own_flat_seed43_20261127-1324 \
    experiments/own_flat_seed44_20261127-1505 -o results/own_flat --preset url --label "Go2 own policy (FullCmd)"
python tools/plot_repro.py experiments/own_flat_seed42_20261127-1142 experiments/own_flat_seed42_repeat_20261127-1644 \
    -o results/own_flat/repro_seed42.png
```

### 1.9 Evaluate (fixed protocol: 7 conditions, 64 robots × 20 s)

```bash
cd $WORK/external/unitree_rl_lab && PYTHONUNBUFFERED=1 python $WORK/tools/eval.py --headless \
    --task Unitree-Go2-Velocity-FullCmd --run $WORK/experiments/own_flat_seed44_20261127-1505
# all own + baseline runs, then the summary table:
cd $WORK && scripts/run_eval.sh
python tools/eval_summary.py --own experiments/own_flat_seed4[234]_2026* --baseline experiments/baseline_flat_seed4[234]_2026* \
    --repeat experiments/own_flat_seed42_repeat_2026* -o results/eval_summary.md
```

### 1.10 Export the policy + playback video

```bash
cd $WORK/external/unitree_rl_lab && PYTHONUNBUFFERED=1 python ../../scripts/unitree_rl_lab/url_play.py --headless \
    --task Unitree-Go2-Velocity-FullCmd \
    --checkpoint ../../experiments/own_flat_seed44_20261127-1505/url_log/model_2999.pt --video --video_length 500
# → url_log/exported/policy.pt, policy.onnx and url_log/videos/play/rl-video-step-0.mp4
```

### 1.11 One clip per command + rough cut

```bash
cd $WORK/external/unitree_rl_lab && PYTHONUNBUFFERED=1 python ../../tools/record_clips.py --headless \
    --task Unitree-Go2-Velocity-FullCmd --run ../../experiments/own_flat_seed44_20261127-1505 --out ../../results/video
cd $WORK/results/video && ffmpeg -f concat -safe 0 -i clips.txt -c copy rough_cut.mp4
cd $WORK && python tools/plot_title_card.py results/own_flat/mean_reward.csv -o results/video/title_card_training_curve.png
```

---

## 2. Key config snippets (unitree_rl_lab `velocity_env_cfg.py` and `rsl_rl_ppo_cfg.py`, commit 4960b84, unchanged)

### 2.1 Policy inputs (45 values; everything the real Go2 can measure)

```python
@configclass
class PolicyCfg(ObsGroup):
    base_ang_vel = ObsTerm(func=mdp.base_ang_vel, scale=0.2, clip=(-100, 100), noise=Unoise(n_min=-0.2, n_max=0.2))
    projected_gravity = ObsTerm(func=mdp.projected_gravity, clip=(-100, 100), noise=Unoise(n_min=-0.05, n_max=0.05))
    velocity_commands = ObsTerm(func=mdp.generated_commands, clip=(-100, 100), params={"command_name": "base_velocity"})
    joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel, clip=(-100, 100), noise=Unoise(n_min=-0.01, n_max=0.01))
    joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel, scale=0.05, clip=(-100, 100), noise=Unoise(n_min=-1.5, n_max=1.5))
    last_action = ObsTerm(func=mdp.last_action, clip=(-100, 100))

    def __post_init__(self):
        self.enable_corruption = True
        self.concatenate_terms = True
```

3 + 3 + 3 + 12 + 12 + 12 = 45. The critic (training only) also gets `base_lin_vel` and `joint_effort` (×0.01), which makes 60.
That is the asymmetric actor-critic trick: privileged information is fine for the critic because only the actor is deployed.

### 2.2 Actions and timing

- Joint target = default pose + **0.25** × action (`JointPositionAction`, 12 joints)
- PD on the motors: **Kp 25, Kd 0.5**; Unitree torque–speed curve actuator (20.2 / 23.4 N·m)
- sim dt 0.005 s × decimation 4 = **50 Hz** policy
- `deploy.yaml`, written by training, carries all of these plus the policy→SDK joint map:

```yaml
joint_ids_map: [3, 0, 9, 6, 4, 1, 10, 7, 5, 2, 11, 8]
step_dt: 0.02
stiffness: [25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0]
damping: [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
default_joint_pos: [0.1, -0.1, 0.1, -0.1, 0.8, 0.8, 1.0, 1.0, -1.5, -1.5, -1.5, -1.5]
```

### 2.3 Rewards (16 active terms)

```python
@configclass
class RewardsCfg:
    # -- task
    track_lin_vel_xy = RewTerm(func=mdp.track_lin_vel_xy_exp, weight=1.5,
                               params={"command_name": "base_velocity", "std": math.sqrt(0.25)})
    track_ang_vel_z = RewTerm(func=mdp.track_ang_vel_z_exp, weight=0.75,
                              params={"command_name": "base_velocity", "std": math.sqrt(0.25)})
    # -- base
    base_linear_velocity = RewTerm(func=mdp.lin_vel_z_l2, weight=-2.0)
    base_angular_velocity = RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05)
    joint_vel = RewTerm(func=mdp.joint_vel_l2, weight=-0.001)
    joint_acc = RewTerm(func=mdp.joint_acc_l2, weight=-2.5e-7)
    joint_torques = RewTerm(func=mdp.joint_torques_l2, weight=-2e-4)
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.1)
    dof_pos_limits = RewTerm(func=mdp.joint_pos_limits, weight=-10.0)
    energy = RewTerm(func=mdp.energy, weight=-2e-5)
    # -- robot
    flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-2.5)
    joint_pos = RewTerm(func=mdp.joint_position_penalty, weight=-0.7,
                        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
                                "stand_still_scale": 5.0, "velocity_threshold": 0.3})
    # -- feet
    feet_air_time = RewTerm(func=mdp.feet_air_time, weight=0.1,
                            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"),
                                    "command_name": "base_velocity", "threshold": 0.5})
    air_time_variance = RewTerm(func=mdp.air_time_variance_penalty, weight=-1.0,
                                params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot")})
    feet_slide = RewTerm(func=mdp.feet_slide, weight=-0.1,
                         params={"asset_cfg": SceneEntityCfg("robot", body_names=".*_foot"),
                                 "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot")})
    # -- other
    undesired_contacts = RewTerm(func=mdp.undesired_contacts, weight=-1,
                                 params={"threshold": 1, "sensor_cfg": SceneEntityCfg(
                                     "contact_forces", body_names=["Head_.*", ".*_hip", ".*_thigh", ".*_calf"])})
```

16 terms, confirmed by `[INFO] Reward Manager: <RewardManager> contains 16 active terms.` in each run's `train.log`.

### 2.4 PPO settings

```python
@configclass
class BasePPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 50000          # we passed --max_iterations 3000
    save_interval = 100
    empirical_normalization = False
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2, entropy_coef=0.01,
        num_learning_epochs=5, num_mini_batches=4, learning_rate=1.0e-3, schedule="adaptive",
        gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0,
    )
```

4,096 envs × 24 steps = 98,304 transitions per iteration. 3,000 iterations ≈ 295 M env steps.

### 2.5 Domain randomisation (from the audit)

| Event | Range | When |
| --- | --- | --- |
| Friction (static and dynamic) | 0.3 to 1.2 | startup |
| Added base mass | −1 to +3 kg | startup |
| Push (set base velocity) | ±0.5 m/s in x and y | every 5–10 s |
| Start pose | x, y ±0.5 m, yaw ±π | reset |
| Observation noise | see 2.1 | every step |

Not randomised: motor gains, actuator delay (0), centre of mass, IMU bias.

---

## 3. Errors hit and how they were fixed

Full entries are in `experiments/NOTES.md`; the plain-words Sprint 1 version is in `experiments/sprint1_summary.md`.

| # | Problem (exact error where there was one) | Cause | Fix |
| --- | --- | --- | --- |
| 1 | `list_envs.py: error: unrecognized arguments: --headless` | Isaac Lab 2.3.2's list_envs.py is always headless and only accepts `--keyword` | Drop the flag |
| 2 | list_envs.py prints no table when output goes to a file | stdout is block-buffered and Kit exits hard before the flush | `PYTHONUNBUFFERED=1` on every Isaac Lab command whose output is saved |
| 3 | GPU busy (another user's job at 91%) | Shared workstation | Check `nvidia-smi` first; the launch scripts wait while another compute process is on the GPU |
| 4 | `ModuleNotFoundError: No module named 'pandas'` | Not in the Isaac Lab env | Tools use only csv + numpy + matplotlib + tensorboard |
| 5 | Playback silently loaded `model_50.pt` instead of `model_299.pt` | `sort -t_ -k2 -n` on full paths that contain underscores | `ls model_*.pt \| sort -V \| tail -n 1` in the log dir. Lesson: always print which checkpoint was loaded |
| 6 | git.txt shows `training-checkpoints-develop-17-g858234d06e` instead of `v2.3.2-...` | `git describe --tags` picks any tag | `git describe --tags --match "v*"` |
| 7 | unitree_rl_lab train/play scripts don't work with rsl-rl 5 (found by reading the code: rsl-rl 5 reads `cfg["actor"]`; play uses `runner.alg.policy`) | Repo targets Isaac Lab 2.3.0 / older rsl-rl | Wrapper copies with `handle_deprecated_rsl_rl_cfg` and `runner.export_policy_to_jit/onnx` (section 1.5) |
| 8 | `ModuleNotFoundError: No module named 'isaaclab.utils.pretrained_checkpoint'` | Moved to `isaaclab_rl.utils` in 2.3.2 | Fix the import in `url_play.py` |
| 9 | `unitree_rl_lab.sh -i` not used | Needs git-lfs, rewrites conda activate.d and shell completion | `pip install -e` + Hugging Face `snapshot_download(allow_patterns=["Go2/*"])` |
| 10 | No window for the Isaac Sim GUI (`DISPLAY` empty) | GNOME on Ubuntu 26.04 runs Wayland-only (`--no-x11`); Kit needs X11 | Rootful Xwayland: `Xwayland :2 -decorate -geometry 1900x1000 -noreset`, then `DISPLAY=:2` |
| 11 | Isaac Sim window doesn't resize inside that Xwayland window | No window manager inside a rootful Xwayland | `DISPLAY=:2 xfwm4 --compositor=off` |
| 12 | GUI training froze at iteration 178, then 184 (no error, GPU idle) | The sim timeline was paused (Space / pause button), and a paused sim stalls training | Train headless; watch with a separate checkpoint viewer (`tools/watch_ckpt.py`) |
| 13 | Training started by mistake | `source scripts/run_own.sh` executes the whole script | Killed and archived. Test functions by extracting them, not by sourcing the script |
| 14 | `xwininfo: error: unable to open display ":2"` | Closing the Xwayland window ends that X server | Restart Xwayland + xfwm4; headless training unaffected |
| 15 | Command curriculum stuck at ±0.1 m/s for 824 iterations (`Curriculum/lin_vel_cmd_levels: 0.1000`) while tracking reward was 1.45, above the 1.2 bar | `lin_vel_cmd_levels` only looks at the ~4 of 4,096 envs that reset exactly on every 1000th step | New task `Unitree-Go2-Velocity-FullCmd`: full range from the start, curriculum removed (section 1.6) |
| 16 | `RuntimeError: Inplace update to inference tensor outside InferenceMode is not allowed.` (eval) | `env.reset()` ran outside `torch.inference_mode()` after steps inside it | Do the reset inside `inference_mode` too |

Good "lessons" material for the article: #5 (always print the checkpoint), #12 (never train with the GUI), #15 (read your
curriculum curves). For #15 the evidence is kept in `experiments/_archive/own_flat_seed42_20261127-1108_curriculum_stuck`.

---

## 4. Results to quote

- Training (3 seeds): final reward **30.39 ± 0.16**, episode length 998.5 / 1000, velocity error 0.182 m/s (`results/own_flat/summary.md`)
- Reproducibility: the second seed-42 run is **bit-identical** to the first: every logged value and the final weights match
- Eval, seed 44 (`experiments/own_flat_seed44_20261127-1505/eval.csv`): 0 falls in all 7 conditions; velocity RMSE 0.021–0.071 m/s; about 24 W at 0.5 m/s
- Own vs built-in baseline: lower tracking error on every condition, about 3× less mechanical power (`results/eval_summary.md`)

---

## 5. Screenshots worth taking

Start TensorBoard once:

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
cd $WORK/external/unitree_rl_lab
tensorboard --logdir logs/rsl_rl --port 6006      # open http://localhost:6006
```

| # | Screenshot | How to get it |
| --- | --- | --- |
| 1 | **Train/mean_reward**, the 4 FullCmd runs overlaid (the curve rises then flattens around 30) | TensorBoard, filter runs with `fullcmd`, tag `Train/mean_reward`, smoothing ~0.9 |
| 2 | **Stuck curriculum**: `Curriculum/lin_vel_cmd_levels` flat at 0.1 in the archived upstream run | TensorBoard, run `unitree_go2_velocity/2026-11-27_11-09-03_own_seed42_20261127-1108`, tag `Curriculum/lin_vel_cmd_levels`; put it next to `Episode_Reward/track_lin_vel_xy` from the same run (already 1.45) |
| 3 | Tracking error falling: `Metrics/base_velocity/error_vel_xy` | TensorBoard, FullCmd runs |
| 4 | Falls disappearing: `Episode_Termination/bad_orientation` and `Train/mean_episode_length` reaching 1000 | TensorBoard, FullCmd runs |
| 5 | Exploration shrinking: `Policy/mean_std` | TensorBoard, FullCmd runs |
| 6 | Seeds 42 and 42-repeat lying exactly on top of each other | TensorBoard, select `own_seed42_20261127-1142` and `own_seed42_repeat_20261127-1644`; or use `results/own_flat/repro_seed42.png` |
| 7 | Report-style curves (grayscale, mean ± std) | `results/own_flat/*.png` (section 1.8 command) |
| 8 | Playback frame: 9 robots walking at 1.0 m/s | `ffmpeg -ss 6 -i results/video/03_walk_1.0.mp4 -frames:v 1 walk_1.0.png` |
| 9 | Playback frame: during a push | `ffmpeg -ss <t> -i results/video/07_walk_0.5_push.mp4 -frames:v 1 push.png` (step through the clip to find a push) |
| 10 | Playback frame: turning in place | `ffmpeg -ss 5 -i results/video/06_turn_0.8.mp4 -frames:v 1 turn.png` |
| 11 | Isaac Sim GUI with many robots training (only if you want a GUI shot: start the display as in CLAUDE.md, then run the viewer) | `cd $WORK/external/unitree_rl_lab && DISPLAY=:2 python ../../tools/watch_ckpt.py --num_envs 16`, then screenshot the window |
| 12 | Terminal: `url_train.py` iteration printout (reward terms, ETA) | Any training run's `train.log`, or run 1.5's smoke test and screenshot the terminal |
| 13 | `deploy.yaml` in an editor (the bridge to the real robot) | `experiments/own_flat_seed44_20261127-1505/deploy.yaml` |
| 14 | Eval table | `results/eval_summary.md` rendered on GitHub |
| 15 | Title card | `results/video/title_card_training_curve.png` |
