# Facilitator guide

## Preparation

Use [setup](setup.md) and choose which stations have actually passed readiness. Read the [answer key](answer-key.md). Keep the solution folder available for recovery, but ask participants to attempt the task first. Split pairs into driver (operates the agent) and navigator (predicts and checks behavior); switch roles after the first fix.

Participants with Docker and the station image run steps 03–04 on their own laptops ([setup](setup.md#ros-2-on-participant-laptops-docker)); ask them to run `bash lab/00-check.sh` the day before. Before 2 p.m., run `bash lab/00-check.sh` on every ROS 2 station, then `bash lab/03-replay.sh` and `bash lab/04-simulate.sh` once each, so the first participant run is not the first run on that machine. Give each station its own `LAB_DOMAIN_ID` if the stations share a network; Docker runs need none. Pairs without Docker use a station in turns or watch a facilitator's run; the saved report is the evidence either way.

State the learning goal: participants own the contract and the judgment; agents assist implementation and explanation. No ranking of clients or measured speedup is assumed.

## One-hour run of show (2–3 p.m.)

Each step is a script in [lab/](../lab/README.md) with `run`, `doctor` and `help`.

| Clock | Step and script | Facilitation | Evidence to collect |
|---|---|---|---|
| 2:00–2:05 | 00 `bash lab/00-check.sh` | Everyone checks their laptop; triage any FAIL line | `runs/doctor-*.txt` with no FAIL |
| 2:05–2:10 | 01 `bash lab/01-reproduce.sh` | Baseline commit; the starter fails 10/12; written prediction | Saved failing output |
| 2:10–2:30 | 02 `bash lab/02-repair.sh` | Agent explains first, then the smallest fix; rerun after each edit; explain-back | 12/12, `check.py` unchanged, diff and a new predicted case |
| 2:30–2:38 | 03 `bash lab/03-replay.sh` (station) | Synthetic bag through the reference node; read the nine checks | `runs/03-replay/<time>/replay-report.json` |
| 2:38–2:48 | 04 `bash lab/04-simulate.sh` (station) | Fresh headless world; read each scenario's stop reason | `runs/04-simulate/<time>/capstone-report.json` |
| 2:48–2:50 | 05 `bash lab/05-handoff.sh` | Fill the bracketed lines of the drafted run report | `runs/05-handoff/run-report-*.md` |
| 2:50–3:00 | Q&A | One result, one limitation, next bounded task | |

The 45-minute talk follows [slides](slides.md). The lab assumes the station image is built and has passed its doctor. Participants observe the TurtleBot3 application rather than building it in this hour; building it is the take-home extension in the [workbook](participant-workbook.md#take-home-extension-build-the-turtlebot3-application).

## Diagnosing a participant's machine

Ask for the step's doctor before reading code: `bash lab/<step>.sh doctor`. Every FAIL and WARN line has a fix. For anything unclear, ask for `bash lab/00-check.sh`; its saved report lists the OS, Python, Git, folder, agent CLIs, ROS installation and each check. The [troubleshooting table](../lab/README.md#when-something-goes-wrong) covers Windows without Bash, missing Git on macOS, synced folders, the master-copy guard, an edited checker, busy ROS domains, leftover simulator processes and Conda.

## Hints, in order

1. Ask which question the current reducer answers. Do not give the corrected code immediately.
2. Ask participants to draw the forward wedge and height band.
3. Ask where the filter belongs relative to the minimum operation.
4. If still stuck, point to `atan2(y, x)` and ask what angle a side point has.
5. Let them inspect the answer key, then request an explanation and a new case rather than copying blindly.

## Checkpoints and recovery

- At 2:10, every pair should have a saved failing run. If step 01 fails, its doctor names the cause; pair the participant with a neighbour while it is fixed.
- At 2:25, require the frontal-obstacle and unknown cases to remain intact. If the agent rewrote the checker, step 02 says so; restore it with `git checkout lab-baseline -- exercises/check.py` and discuss why the evidence changed.
- At 2:30, ask each navigator to explain a new input. A green terminal without explain-back misses the PR-understanding objective.
- Replay failure: run `bash lab/03-replay.sh doctor`; inspect topic type, QoS, TF and clock before asking for code changes. Never silently substitute a synthetic result for captured data.
- Simulator failure: `bash lab/04-simulate.sh clean`, then rerun. Still failing: use `evidence/2026-11-03/capstone-report.json`, read the launch log tail the script printed, and mark the step unexecuted on that station.
- Agent access failure: use a prepared prompt/diff transcript and do the same predictions and review. Participants can still learn the workflow.

## Discussion questions

Which extra question was worth the tokens? Which instruction prevented a wrong assumption? What would the fixture miss? Which failure has to be checked even when no new sensor message arrives? How would the same approach apply to a web API or ETL pipeline?

## Completion standard

Use the [rubric](answer-key.md#assessment). Do not require a physical robot to earn completion. Require an honest handoff: observed fixture/replay/simulator result or a clear statement of which stage remains pending.
