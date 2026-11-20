# Literature Review Summary

Condensed from the Week 1–4 research-methodology documents and `start10papers.md`. This file is the
single reference point for "what does the literature already say" — the original weekly docs go into
more process detail (how the search was run, how papers were critically read) and are worth keeping
alongside this file, not replacing it.

## Research question funnel

| Level | Keywords / Scope | Paper count (est.) |
|---|---|---|
| Broad | Multi-objective reinforcement learning | >800 papers |
| Mid | MORL + robot control / locomotion | ~120 papers |
| Focused | MORL + quadruped + real-hardware evaluation | ~25 papers |
| **Target** | **MORL + Unitree Go2 + Pareto-front evaluation** | **<5 papers** |

Fewer than 5 papers directly on-point at the target level = genuine novelty potential: sparse enough
to be noticed, dense enough in the surrounding literature (levels 2–3) to have baselines to compare
against.

## Seed paper library (15 papers, clustered)

| # | Paper | Cluster | Gap it exposes |
|---|---|---|---|
| P01 | Hayes et al. (2022) — A Practical Guide to MORL and Planning | MORL Foundations | No locomotion/hardware treatment; canonical vocabulary source |
| P02 | Xu et al. (2020) — PGMORL | MORL Foundations | Sim-only (MuJoCo); smooth-landscape assumption may not hold on real actuators |
| P03 | Anon. (2024) — C-MORL | MORL Foundations | Sim-only; no hardware step-count cost modeled |
| P04 | Janwani et al. (2026) — MO-Playground / MORLAX | MORL Foundations | No hardware validation; no Go2 wrappers yet |
| P05 | Anon. (2024) — Preference-Conditioned MORL (humanoid) | MORL Foundations | Humanoid, not quadruped; runtime adaptation untested on hardware |
| P06 | Margolis & Agrawal (2023) — **Walk These Ways** | Quadruped RL | Gait descriptor hand-designed, not learned from a Pareto front; no energy/safety objectives |
| P07 | Anon. (2024) — Stage-Wise Reward Shaping (acrobatics) | Quadruped RL | Unclear if it generalizes to steady-state locomotion objectives |
| P08 | Anon. (2025) — **Kine2Go** dataset | Quadruped RL | Dataset only; no Pareto-front annotation of its 40 policies |
| P09 | Anon. (2024) — MetaLoco | Quadruped RL | Single-objective; multi-objective meta-policy adaptation unexplored |
| P10 | Miki et al. (2022) — Perceptive Locomotion (ANYmal) | Sim-to-Real/HW | Energy/safety folded into one scalar reward, not separate objectives |
| P11 | Anon. (2022) — Terrain Transformer sim-to-real | Sim-to-Real/HW | No multi-objective treatment; power/stability trade-offs implicit |
| P12 | Agrawal et al. (2022) — Rapid Locomotion | Sim-to-Real/HW | Speed is the sole objective |
| P13 | Anon. (2024) — CaT (Constraints as Terminations) | Constrained/Safe RL | Hard constraints only, not a Pareto front — constrained RL, not MORL |
| P14 | Anon. (2024) — Constrained Skill Discovery | Constrained/Safe RL | Skills not evaluated on a multi-objective Pareto front |
| P15 | Shu et al. (2024) — Learning Pareto Set for Continuous Robot Control | Constrained/Safe RL | Sim-only; Pareto-set network untested with real actuation noise |

Plus 10 broader locomotion/RL/controlled-environment seed papers in `start10papers.md` (Tan et al.
2018 sim-to-real; Rudin et al. 2022 legged_gym; Margolis et al. 2022 Rapid Locomotion; Lee et al. 2020
and Miki et al. 2022 terrain generalization; Walk These Ways again; Vollenweider et al. 2023 AMP;
a 2025 MPC-vs-RL MuJoCo benchmark; LocoMuJoCo; and a 2024 field survey) — these anchor the
"locomotion" and "controlled environment" axes independent of the MORL-specific search.

## Cross-cluster gaps (the actual opening)

Three gaps show up repeatedly across independent cuts of the literature — first from the citation
network (Week 2 doc §3.3), then again from the critical-reading literature matrix (Week 4 doc §3):

- **G1 — No real-hardware MORL evaluation.** P02/P03/P04/P15 all evaluate MORL in simulation only.
  P10/P12 provide sim-to-real pipelines, but for single objectives.
- **G2 — No Pareto-front analysis of existing Go2/quadruped policies.** P08 (Kine2Go) has 40 Go2
  policies with no Pareto annotation; P06 (Walk These Ways) conditions on gait parameters but never
  measures hypervolume/dominance.
- **G3 — Runtime preference adaptation not validated on hardware.** P05/P09 show inference-time
  adaptation in simulation only; whether a real quadruped can switch Pareto-optimal modes without
  falling is completely open.

The literature matrix (Week 4 doc) makes this concrete: of 5 closely-read papers, rows 3/4/5 (Legged
Gym, Walk These Ways, the fuRo QRC-winning Go2 policy) all have real-hardware evidence but no
multi-objective reward; rows 1/2 (the MORL survey, PGMORL) have multi-objective structure but no
real-hardware evidence. **No paper has both.** That empty cell is this project's opening.

## Subtopic map (from Week 2 doc §4)

| ID | Question | Effort/output | Chosen? |
|---|---|---|---|
| ST-A | What does the real Pareto front (speed/energy/safety) look like on the Go2? | Low algorithm risk, high hardware effort — benchmark/dataset paper | Folds into Milestone 5 |
| **ST-C** | Can MORL discover energy-optimal gaits the single-objective baseline misses? | Clear baseline (P06) exists; hardware validation feasible | **Primary track — see ROADMAP.md** |
| ST-E | Do Kine2Go's 40 policies already span a meaningful Pareto front? | Lowest effort, zero new hardware | Milestone 2, runs in parallel |
| ST-B | Can one preference-conditioned policy switch modes safely at runtime? | High novelty, high sim-to-real engineering risk | Stretch goal, after ST-C |
| ST-D | Safe exploration of the Pareto front without falls/over-torquing | Hardest subproblem, highest risk | Deferred |

**Decision criterion actually used (Week 2 doc §5):** pick the subtopic with the largest gap and the
strongest existing codebase/hardware support. That's ST-C → ST-B, because the Walk These Ways
pipeline already runs on Unitree hardware and the Isaac Lab + rsl_rl stack is already verified working
on this project's own workstation.

## Search methodology (Week 3 doc)

8 Boolean queries logged across arXiv (2026-07-17 to 2026-07-21), 59 results screened by
title/abstract, 16 papers kept. Full query strings and per-query hit/kept counts are in the Week 3
document — reproduce or extend using the same Boolean-query template (concept → synonyms →
AND across concepts) rather than ad hoc searching, so future search sessions stay auditable.

**Reference management:** Zotero library `MORL - Unitree Go2 Edu`, 6 collections (00 Inbox through
05 Controlled Environments) mirroring the clusters above, 4 tag families (subtopic / status / role /
hardware). Confirm this is actually populated and synced — it was set up as a Week 3 action item but
population status wasn't independently verified when this summary was written.

## Critical-reading notes (Week 4 doc)

Two worked examples of asking an AI tool a question about a paper and verifying against source text —
**both AI answers were wrong or partially wrong** (claimed Walk These Ways uses onboard vision when
it doesn't; claimed the fuRo Go2 policy scored "middle of the pack" when it actually had the highest
autonomy score of only two teams that scored autonomously at all). Standing rule for this project:
never cite a fact pulled from an AI summary — including from an assistant helping with this
project — without locating the matching sentence, table, or figure in the source PDF first.
