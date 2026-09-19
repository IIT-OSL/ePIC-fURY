
Starting an own project!

New project template generator command

```
./isaaclab.sh --new
```

prompts to answer:

**Task type**: External (keeps it as its own repo, separate from IsaacLab source, this is the recommended way)
**Project path**: wherever I want to keep my stuff
**Project name**: they used manager_based_go2 as the example name
**Workflow**: Manager-based | single-agent (this is the important choice, more below)
**RL library**: rsl_rl

Installs

```
cd <project path>
python -m pip install -e source/<project name>/
```

Install check

```
python scripts/list_envs.py
```


run the default cartpole example that comes bundled to confirm the scaffold actually works 

```
python scripts/rsl_rl/train.py --task Template-Test-v0
```

### The big architectural thing to remember: config vs implementation

`_env_cfg.py` is the blueprint, defines what the environment is made of (robot, observations, rewards, actions). this is the file I'll be editing 90% of the time

`_env.py` is the engine, the actual code that reads the blueprint and runs it. for manager based workflow you basically never touch this, IsaacLab's own ManagerBasedRLEnv class handles it

### Manager-Based vs Direct workflow

**Manager-based**: LEGO blocks, drop reward term into config, RewardManager wires it up, modular

**Direct**: clay sculpting, subclass DirectRLEnv, write `_compute_rewards`/`_get_observations` by hand, more freedom more boilerplate

NOTE: basic-locomotion-isaaclab's locomotion_env.py is Direct workflow, that's why it had all that manual code instead of a plain config