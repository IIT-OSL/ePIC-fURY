
using cartpole example, top level `TestEnvCfg` bundles:

**SceneCfg** - ground, robot asset, lighting, num parallel envs + spacing

**ActionsCfg** - what agent can do (cartpole: effort on one joint, scaled)

**ObservationsCfg** - what agent sees (cartpole: joint pos + vel, under PolicyCfg group)

**EventsCfg** - reset randomization so policy doesn't just memorize one start state

**RewardsCfg** - list of weighted terms summed each step (cartpole: alive bonus, terminate penalty, pole_pos main task reward, cart_vel + pole_vel small shaping penalties)

**TerminationsCfg** - time_out, cart_out_of_bounds

`__post_init__` - episode length, sim timestep, global stuff

reward weight experiment to remember: cart_vel weight -0.01 → balances fine. same weight -2.0 (200x) → agent just freezes, moving costs more than failing. same setup, one number changed, completely broken policy. reward weights are not safe to nudge casually, keep this in mind before touching go2_env_cfg.py reward scales.
