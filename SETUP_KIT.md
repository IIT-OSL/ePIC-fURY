# Claude Code kit for ~/ePICfURY/work

## Install (once)

From Windows (PowerShell), in the folder holding the zip:

```powershell
scp epicfury-claude-kit.zip root-daham@<workstation>:/home/root-daham/ePICfURY/
```

On the workstation:

```bash
cd /home/root-daham/ePICfURY/ePIC-fURY
unzip -n ../epicfury-claude-kit.zip     # -n never overwrites files you already have
tmux new -s claude                       # so the session survives a dropped SSH
claude                                   # start Claude Code here, in work/
```

Then in Claude Code type `/s0-discover`. It fills the Environment section of CLAUDE.md for you.

## What is in here

- `CLAUDE.md`: project context and hard rules. Claude Code reads it every session.
- `.claude/settings.json`: asks before sudo, installs, git commit/push, rm, mv, docker; blocks ssh and pinging the robot subnet.
- `.claude/commands/`: one slash command per plan task. Type `/` in Claude Code to see them.
- `experiments/README.md`, `experiments/NOTES.md`: version table and error log templates.
- `papers/existing/`: the team's paper lists, for `/s1-paper-dupcheck`. Put your own titles in `papers/my_titles.txt`.

## Commands, in order

| Sprint | Command | Needs an argument? |
| --- | --- | --- |
| 0 | `/s0-discover` | no |
| 1 | `/s1-baseline-train` | no |
| 1 | `/s1-baseline-play` | no |
| 1 | `/s1-curves` | no |
| 1 | `/s1-paper-dupcheck` | no (fill papers/my_titles.txt first) |
| 1 | `/s1-log-summary` | no |
| 2 | `/s2-install-rl-lab` | no (stops to confirm versions) |
| 2 | `/s2-audit` | no (stops for your sign-off) |
| 2 | `/s2-deployable-cfg` | no (only if the audit flagged inputs) |
| 2 | `/s2-train` | optional: task name |
| 2 | `/s2-eval` | no |
| 2 | `/s2-video` | run folder of the chosen policy |
| 2 | `/s2-medium-material` | no |
| 3 | `/s3-build-deploy` | no |
| 3 | `/s3-check-cfg` | run folder |
| 3 | `/s3-golden` | run folder |
| 3 | `/s3-sim2sim` | no |
| 3 | `/s3-logging` | no (shows diff first) |
| 3 | `/s3-print-sheets` | no |
| 3/4 | `/s3-parse-robot-logs` | session folder name in robot_logs/ |
| 4 | `/s4-fix` | what you saw on the robot, in words |
| 4 | `/s4-results` | no |
| 4 | `/s4-appendix` | no |
| 4 | `/s4-numbercheck` | optional: draft path |
| 4 | `/s4-tutorial-test` | optional: tutorial path |
| 4 | `/s4-repo-release` | no (asks before commit/tag/push) |

Example with an argument: `/s3-golden experiments/own_flat_seed43_20261127-2210`
