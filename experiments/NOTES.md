# Errors and fixes

One entry per problem. Newest at the bottom.

<!--
## YYYY-MM-DD: short title
- What I was doing:
- Error (exact line):
- Cause:
- Fix:
-->

## 2026-11-20: list_envs.py rejects --headless
- What I was doing: Sprint 0 smoke test, `./isaaclab.sh -p scripts/environments/list_envs.py --headless`
- Error (exact line): `list_envs.py: error: unrecognized arguments: --headless`
- Cause: in Isaac Lab 2.3.2 list_envs.py hard-codes `AppLauncher(headless=True)` and only accepts `--keyword`.
- Fix: run without the flag: `./isaaclab.sh -p scripts/environments/list_envs.py --keyword Go2`

## 2026-11-20: list_envs.py prints no table when output goes to a file
- What I was doing: same command, stdout redirected to a log file
- Error (exact line): none; exit code 0 but the environment table is missing from the log
- Cause: stdout is block-buffered when redirected, and `simulation_app.close()` exits the process before the buffer is flushed.
- Fix: set `PYTHONUNBUFFERED=1` (or pass `python -u`) whenever an Isaac Lab script's output is tee'd/redirected.
