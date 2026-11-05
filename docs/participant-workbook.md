# Participant workbook

The hands-on lab runs 2–3 p.m. in six short steps. Each step is one script in [lab/](../lab/README.md); run it from the workshop folder. If a step fails, run the same script with `doctor` and follow its `Fix:` line. Use [prompt cards](prompt-cards.md) when helpful, and the [command sheet](lab-commands.md) for Windows commands and common fixes. Results are saved in `runs/`.

## Step 00 — Check your machine (2:00)

```bash
bash lab/00-check.sh
```

Fix any `FAIL` line before 2:05. If you cannot, show the saved `runs/doctor-<time>.txt` to a facilitator. On Windows without Bash, run `py -3 lab\lab.py 00` instead (any step number works the same way).

## Step 01 — Reproduce the failure (2:05)

```bash
bash lab/01-reproduce.sh
```

It makes a baseline commit tagged `lab-baseline`, so `git diff lab-baseline` will show exactly what you changed, then runs the checker on the starter. A result of 10/12 is expected: the starter has a deliberate reducer bug.

Answer before editing: Why can the side-wall case fail when the point coordinates are valid? Which state should stale data produce? What would changing a threshold hide?

Our offline contract: already-transformed XYZ in meters, x forward, y left, z up; planar range from the working-frame origin; forward angles within ±30 degrees inclusive; heights 0.05–0.50 m inclusive; blocked at distance ≤0.50 m; at least one accepted point; age 0–0.25 s inclusive on the same clock. Empty, invalid, stale, future-stamped or untransformable data produces unknown. These values are authored teaching parameters, not a physical-robot calibration.

## Step 02 — Make and understand a bounded change (2:10–2:30)

Ask your agent to inspect `exercises/clearance.py` and the failure. First request an explanation without edits. Then authorize the smallest reducer fix. After each edit, run:

```bash
bash lab/02-repair.sh
```

It reruns the 12 checks, shows your diff against the baseline and fails if `exercises/check.py` changed: keep the checker unchanged and add extra cases in a separate file. When it reports 12/12, trace the side point and front point through the new code. Ask a follow-up whenever the explanation skips an assumption. Predict these inputs before running your own additional check:

- A valid point exactly at the blocked threshold.
- A cloud containing only ground points outside the height band.
- A transform failure with otherwise valid close points.

Have a partner or a separate review conversation review against the contract. Record one finding or explain why no consequential finding was reproduced. Do not treat agreement as executed evidence.

### Step 02 with Claude Code

You decide; Claude Code does the work. It asks before it edits a file or runs a command: read each request before you approve it. Open two terminals in the workshop folder: run `claude` in the first (the driver types there) and `bash lab/02-repair.sh` in the second (the navigator runs the checks there, so the evidence comes from your terminal, not from the agent's summary). The prompts are the [prompt cards](prompt-cards.md); in Codex, use the same prompts and say "read-only" for passes 1, 4 and 5.

| Clock | Part | In Claude Code | Done when |
|---|---|---|---|
| 2:10 | 1 Explain first | Press Shift+Tab until plan mode is on, so nothing can be edited. Paste: "Read exercises/clearance.py and run python3 -I exercises/check.py. Explain the failing behavior against the workbook contract first. Do not open the solution until I request it." | The explanation matches your step 01 prediction, or you know why it differs |
| 2:14 | 2 Smallest fix | Shift+Tab out of plan mode. "Make the smallest fix in clearance.py that satisfies the contract. Preserve exercises/check.py; add any new cases in a separate file." Read the diff before you accept it; reject changes to `check.py` or to any constant and say why. Esc stops a reply that goes the wrong way. | You can say what each changed line does |
| 2:17 | 3 Check it yourself | In the second terminal: `bash lab/02-repair.sh`. Repeat parts 2 and 3 until it passes. To start over: `git checkout lab-baseline -- exercises/clearance.py` | `All 12 checks pass`, a diff only in `clearance.py`, checker unchanged |
| 2:18 | 4 Understand | Plan mode again. Paste the "Understand the PR" card, which names `skills/explain-robotics-pr/SKILL.md`. Write your answers to the three inputs above first, then: "Add these three as cases in exercises/my_cases.py and run it." | Your predictions are checked; any wrong one has a named missing assumption |
| 2:24 | 5 Review fresh | `/clear` (or a new `claude` session), then paste the "Review" card | One finding written down, and whether it was run or only read |
| 2:28 | 6 Swap and explain | Driver and navigator swap; the new navigator explains, without the agent, why the side wall now reads clear | The explanation holds without the agent |

Short on time: parts 1–3 are required, and part 6 matters more than part 5. A passing run you cannot explain is not the end of step 02.

The skills can also be started as `/explain-robotics-pr` and so on. Naming the file path, as the prompt cards do, works on every computer: Git for Windows usually checks out the `.claude/skills` links as plain files, so the slash commands may not appear there.

## Step 03 — Replay a real ROS topic (2:30, Docker or a ROS 2 station)

```bash
bash lab/03-replay.sh
```

On a laptop with Docker it runs in the station container; on a ROS 2 station it runs directly. It builds a rosbag of **authored synthetic** PointCloud2 messages, replays it through the packaged reference diagnostic node on ROS domain 77 and prints the nine checks: clear, blocked and unknown phases, a padded big-endian cloud, stale and future stamps, the transform's effect and the reception timeout. It runs the reference node, not your edited file. A synthetic bag exercises ROS transport, QoS, TF and clock handling; it is not a capture from Unitree hardware.

Read one check aloud with your partner: which field of the message decided it? The offline checker did not test PointCloud2 decoding, QoS or TF; this step does.

## Step 04 — Observe a bounded robot application (2:38, Docker or a ROS 2 station)

```bash
bash lab/04-simulate.sh
```

It starts a fresh headless Gazebo world with a TurtleBot3 Burger on domain 78, waits for the controller, runs ten scenarios and shuts the world down: rejected speed, clear-path distance bound, obstacle stop, latched stop, dropped, invalid and untransformable scans, operator stop, time bound and a suspended controller caught by the independent watchdog. For each scenario, find the stop reason in the printed list. Which ones stop the robot even when no new sensor message arrives?

## Step 05 — Hand off (2:48)

```bash
bash lab/05-handoff.sh
```

It drafts a run report from the results saved on this machine. Fill in every `[bracketed]` line: one check you did not run, your next bounded task and one sentence on whether spending more tokens helped your understanding. If steps 03–04 ran on a station, paste their summaries in. Q&A starts at 2:50.

## If you finish early: metadata inspection card

A hypothetical cloud has frame `unilidar_lidar`, x/y/z FLOAT32 offsets 0/4/8, intensity FLOAT32 offset 16, point_step 32, width 2, height 1, row_step 64, little-endian. Acquisition stamp 12.5 s; current replay time 13.0 s. The two decoded points are `(0.4, 0, 0.1)` and `(NaN, 0, 0)`.

Identify what can be inferred and what is still unknown: buffer length/field counts, frame transform, clock comparability, freshness, valid count and coverage. Does a frame name prove forward direction? Complete the [contract template](../templates/interface-contract.md) for this exercise or your actual ROS station.

With an actual UniLiDAR recording, inspect before replaying:

```bash
ros2 topic list -t
ros2 topic info --verbose <resolved-cloud-topic>
ros2 interface show sensor_msgs/msg/PointCloud2
ros2 bag info <recording-path>
```

Replace angle-bracket placeholders with actual inspected values. Capture QoS and clock/TF requirements before replay, and follow the station's rehearsed replay command; do not guess transport parameters or bag storage format.

## Take-home extension: build the TurtleBot3 application

Step 04 observes a prepared application. To build one yourself, use `skills/turtlebot-capstone/SKILL.md` and [WORKSHOP](../WORKSHOP.md). The implementation target is a prepared simulator, with the native scan as the first adapter.

Build a ROS package with a sensor adapter, clearance estimate, deterministic controller, launch/configuration and logs. Record the actual velocity type and odometry source. Specify footprint/front extent, corridor half-width, margins, stop distance, speed, run duration and traveled-distance bounds before implementing motion.

A fresh start request arms a run. Idle and stopped states output zero; faults stop and require explicit reset/new start. An obstacle latches stopped rather than immediately restarting when it disappears. Invalid/stale sensing faults. Bounds, operator stop and shutdown stop the run. Check freshness on a periodic tick, including when callbacks cease. Verify the base command timeout for process loss. A final zero command alone is insufficient.

Show: clear corridor advance; obstacle stop; empty/invalid scan; sensing loss; unavailable transform; operator stop; distance/time limit; process loss; a second explicitly started run. Log sensing age, clearance metric, state, command and observed odometry. The diagnostic planar range is not the motion controller's collision-envelope clearance.
