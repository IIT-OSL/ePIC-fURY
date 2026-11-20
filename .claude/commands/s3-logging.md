---
description: Sprint 3: add per-step CSV logging to the deploy controller (diff first)
---

Read CLAUDE.md. Sprint 3: add logging to the deploy controller.
Add CSV logging to the Go2 controller that writes, every policy step: timestamp, controller state, command, full policy input vector, raw action, joint targets, measured joint positions, velocities and torques, loop period. One file per session in a logs/ folder, named with date and time.
Keep the change small. Show me the full diff before building. After I approve, build and test it in MuJoCo and show me the first 5 lines of a log.
