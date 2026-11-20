---
description: Sprint 3: checklist row 6, golden input/action test on the deploy-side policy
---

Read CLAUDE.md. Sprint 3: checklist row 6, golden test. Policy run: $ARGUMENTS
1. In Isaac Lab playback of that checkpoint (1 env, fixed command 0.5 m/s), record 200 consecutive steps of (policy input vector, policy output action) to experiments/golden/golden.npz.
2. Load the same exported policy file the deploy controller uses (ONNX or TorchScript) the same way the controller does, feed it the recorded inputs, compare actions.
3. Report max and mean absolute difference. Pass if max is around 1e-4 or less. If it fails, find out why (input order, scaling, normalisation, wrong file) before anything else.
