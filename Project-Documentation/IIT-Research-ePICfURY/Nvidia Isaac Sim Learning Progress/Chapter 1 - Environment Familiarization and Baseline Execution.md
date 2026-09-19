
Mental model for how Isaac Lab is structured,

Application - the whole studio, manages everything
Simulation - the director, controls gravity and time steps
World - the sound stage, the global coordinate system
Stage - the film set, where all the assets sit in a tree
Scene - the actors and props, one instance of the environment. for RL we clone this thousands of times in parallel

Install is the usual, driver, Omniverse Launcher, Isaac Sim, clone IsaacLab repo, run `./isaaclab.sh --install`

Train command they use as the baseline test

```
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-Unitree-Go2-v0 --headless
```


Then play it back

```
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Velocity-Flat-Unitree-Go2-Play-v0
```

green arrow = commanded velocity
blue arrow = actual velocity
closer they match = better policy

quick visual check without reading numbers