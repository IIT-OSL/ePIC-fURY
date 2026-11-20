---
description: Sprint 3/4: analyse robot logs copied back from WSO2
---

Read CLAUDE.md. Analyse the robot logs Daham copied into robot_logs/<session>/. Session: $ARGUMENTS
1. Joint check: from the hand-moved joint segment (passive state), confirm for each of the 12 joints which index changed and its sign. Table: joint, expected index, observed index, sign OK.
2. For each policy trial: commanded vs estimated velocity over time, joint torque peaks, loop period stats.
3. Compare with sim eval for the same commands: tracking error real vs sim.
4. Save figures and a summary to results/robot_<session>/. Flag anything that looks unsafe (torque near limits, loop overruns).
