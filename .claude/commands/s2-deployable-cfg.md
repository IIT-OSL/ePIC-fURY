---
description: Sprint 2: only if the audit flagged inputs; make a deployable task variant
---

Read CLAUDE.md and experiments/policy_inputs.md. Sprint 2: only run this if the audit flagged policy inputs the real robot cannot measure.
1. Create a new task (new config class and new task name, e.g. Go2-Velocity-Flat-Deploy) that subclasses the unitree_rl_lab Go2 velocity task, keeps everything identical, and moves only the flagged terms from the policy group to the critic group.
2. Show me the full diff before registering it.
3. After I approve: register it, run 10 training iterations to check it starts, and update experiments/policy_inputs.md with the new policy input list.
