# Slide manuscript: an understood, verified change

45-minute presentation. Headings use the slide numbers of the 25-slide deck; slides 22–24 are optional lab aids and slide 25 lists sources. Speaker text is a suggested script, not a transcript of completed demonstrations; where wording differs, the PPTX speaker notes are canonical. Use [the facilitator guide](facilitator-guide.md) for the longer lab.

## Slides 1–2 — A cloud can be correct and the answer wrong (0–3 min)

**On screen:** A side wall at 0.20 m; an open forward sector; question: “Which distance answers the question?”

**Say:** Slide 1: “Welcome. Today we use Codex and Claude Code to turn a small robotics bug into an understood, verified change, using replay and simulation rather than a physical robot.” Then for slide 2: “A sensor can deliver valid data while our software answers the wrong question. Predict before I reveal it: is the forward sector clear?”

**Show:** The authored side-wall fixture: side `(0, .20, .20)` and front `(1, 0, .20)`, labeled as synthetic coordinates. Ask for a prediction before revealing output.

## Slide 3 — ROS 2 in three minutes (3–6 min)

**On screen:** Driver node → typed topic → your node, with “Inspect: frame · timestamp · fields · stride · QoS.”

**Say:** “A node runs one part of an application. A topic carries typed messages. A frame tells us what coordinates mean, a timestamp tells us when data was acquired and QoS affects delivery. RViz displays data; a bag lets us replay it.”

**Show:** `ros2 interface show sensor_msgs/msg/PointCloud2` (no running bag needed; no topic is live yet). PointCloud2 is a metadata-described binary buffer, not a single range value. Its [message definition](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/PointCloud2.msg) is the contract to inspect.

## Slide 4 — Give the agent an outcome (6–8 min)

**On screen:** “Write the acceptance contract”: frame, ±30° sector, 0.05–0.50 m height band, minimum hypot(x, y), blocked at ≤ 0.50 m, 0–0.25 s age, at least one point, and the callout “unknown is an explicit result. It must never silently mean ‘clear.’”

**Say:** “Specify the observable result before specifying classes and files. Our diagnostic needs a working frame, sector, height band, age bound, minimum point count and a distance definition.”

**Ask:** Which decisions would also matter in an API or data-processing task? Draw the connection to schemas, timeouts and invalid-input policy.

## Slide 5 — Context that earns its place (8–10 min)

**On screen:** Goal → Interface → Checks, with “Keep rules in AGENTS.md; load the relevant skill.”

**Say:** “Give the agent the relevant repository guidance, exact reproduction command and smallest useful input. Keep durable rules close to the code. Large unrelated logs cost attention without resolving the task.”

**Show:** `AGENTS.md`, the interface template and the selected skill. Ask the client to identify the files it actually read. Do not tour every configuration feature.

## Slide 6 — Implement and review deliberately (10–12 min)

**On screen:** Two columns, Implementer and Reviewer, four duties each (contract, bounded change or trace, diff and checks or reproducer, limits).

**Say:** “Either tool can implement or review. Give the reviewer the contract and code, not just the implementer's reassuring summary. Ask for a reproducer, expected result and code location.”

**Show:** The implementation and review cards. Separate agent review from a passing runtime check.

## Slide 7 — Spend tokens to understand the PR (12–14 min)

**On screen:** “Spend tokens until you can explain the change yourself.” Adapted from Theo Browne.

**Example question:** “I understand the subscriber. Why does the side wall decide the forward alert?”

**Say:** “Use more questions when they close a real understanding gap. Ask for a trace, simpler explanation or before/after example until you can explain the change yourself.”

**Attribution:** This lesson adapts [Theo Browne's explanation/refinement example around 20:34](https://www.youtube.com/watch?v=q1D90-uGvBg&t=1234). It is a paraphrase and a workshop application, not a verbatim quotation.

## Slide 8 — Reproduce before editing (14–16 min)

**On screen:** Starter output beside the side-wall contract.

**Say:** “Before we change anything, we reproduce. Input, expected result, observed result: that is a bug report.”

**Show:** Before this slide, `cp -R` the workshop folder to a scratch copy and run `git add -A && git commit -qm baseline` there so `git diff` shows the live edit. From the scratch copy, run `python3 -I exercises/check.py`. Ask the agent to explain one failure without editing. The checker's fixture labels make its scope visible. A good bug report includes input, expected result and observed result.

## Slide 9 — Make the smallest useful change (16–20 min)

**On screen:** Decode/transform → validity → height/sector → reduce → classify.

**Say:** “We are changing which points answer this diagnostic question. We are not solving whole-robot collision avoidance.”

**Show:** The narrow reducer fix and rerun. Preserve the true frontal-obstacle case and unknown-data behavior. If agent latency runs long, switch to a labeled prepared diff; let attendees still predict the result.

## Slides 10–11 — Explain back and replay (20–22 min)

**On screen:** Slide 10, questions to ask the agent beside independent checks; slide 11, the executed counts (12/12 fixtures, 9/9 synthetic replay, 6/6 package tests).

**Say:** “Trace a point through the new code and predict a boundary case before we run it. The ROS replay then runs our packaged reference node for the same contract, not the file we just edited, on an authored synthetic bag.” Then for slide 11: “Three checks, three different questions. None of them is a hardware result.”

**Do:** Trace a point and predict one boundary input (the 30° case), then name the topic and type `replay_demo` played (`/unilidar/cloud`, `sensor_msgs/msg/PointCloud2`, from `replay_demo.py`; started at the end of slide 9) and read its report. On slide 11, once `replay_demo` has exited, launch `capstone.launch.py` in a third sourced shell with `ROS_DOMAIN_ID=78`; do not call `/workshop/start`.

## Slide 12 — Parallel work starts with interfaces (22–24 min)

**On screen:** Decoder/reducer owner · replay owner · reviewer · integration owner.

**Say:** “Separate independent work only after agreeing on the contract. Worktrees isolate files. They do not isolate ROS domains, ports, sensors or velocity publishers.”

**Ask (rhetorical):** Who would own the decoder, the replay, the review and the integration of this change? Delegation is a technique participants may choose, not a requirement to launch more agents.

## Slide 13 — Match the claim to the evidence (24–26 min)

**On screen:** Fixture → replay → simulation → physical trial, with “This workshop: synthetic replay + headless simulation.”

**Say:** “Each surface answers a different question. Include commands, configuration, failures and unexecuted checks in the handoff. A published velocity message is not observed robot motion.”

## Slides 14–15 — Build the whole application (26–30 min)

**On screen:** Slide 14, LaserScan → clearance → state machine, then command guard → Gazebo base → odometry + log; slide 15, the diagnostic versus capstone geometry (front extent 0.11 m, half-width 0.15 m, stop gap 0.30 m).

**Say:** “The final application advances a short distance and stops before an obstacle. Runtime decisions belong to deterministic code. The LLM helps write and inspect that code.” Then for slide 15: “Geometry changes with the task. The diagnostic measured distance from the sensor origin; the controller needs the gap ahead of the robot's footprint.”

Use the native TurtleBot scan for the baseline. A separate Unitree adapter needs mounting/TF/timing integration. The motion threshold uses clearance from the robot envelope; the diagnostic distance from a frame origin cannot be copied directly.

## Slide 16 — Make the simulated path observable (30–34 min)

**Say:** “Commands alone prove nothing. We watch controller status and odometry to see that the simulated base moved and stopped at the bound.”

**Show:** With `capstone.launch.py` launched at slide 11 after `replay_demo` exited (`ROS_DOMAIN_ID=78`; replay used 77; do not call `/workshop/start` by hand), run `ros2 run agentic_workshop capstone_check --output /home/user/runs/capstone-NEW` at the start of this slide and narrate `clear_path_distance_bound`; slide 17 narrates the remaining scenarios from the same run, and slide 18 reviews the run record. Fallback: `evidence/2026-11-03/capstone-report.json` with this graph and slide 18.

**Ask:** What evidence establishes that the base responded rather than merely receiving a command?

## Slides 17–18 — Exercise the failure paths (34–38 min)

**On screen:** Slide 17, sensing lost → periodic check → zero command, with the independent guard timeout; slide 18, the run record (10/10 checks in one fresh world, 0.451 m observed for a 0.45 m bound, 0.30 s configured watchdog).

**Show:** Obstacle stop, sensing loss and operator stop. Inspect logs for the state transition and stopping response. Confirm the base command timeout independently of a process's final zero command.

**Say:** “A missing callback must not leave yesterday's forward command running. Check stale data on a periodic control tick.” Then for slide 18: “The simulation left a record: ten scenario checks passed in one fresh world, the run stopped at 0.451 m against a 0.45 m bound, and the guard zeroes commands after 0.30 s. All of it is simulation.”

## Slide 19 — Review and hand off (38–40 min)

**On screen:** Revision · reproduction command · scenario outcomes · limits · next task.

**Say:** “Leave a handoff someone else can repeat: revision, command, outcomes and limits. Then explain the change in your own words.”

**Show:** A completed run report. Compare the outcome with the original task. Discuss elapsed time to an understood, verified change and human correction effort, not tokens or lines of code alone.

## Slides 20–21 — Your next bounded task (40–45 min)

**On screen:** Read → specify → change → verify → explain (explain it, hand it off). Slide 21 keeps the same five words for questions.

**Ask:** “What is one small task in your own project with an input and an observable result?” Have everyone write one privately, map one volunteered example to the workflow, and share the workbook and skills. Protect at least three minutes for questions.

## Slides 22–24 — One-hour lab, 2–3 p.m. (facilitator aids)

**On screen:** Slide 22, the five lab steps (T+00 check and reproduce, T+10 repair and explain, T+30 replay through ROS 2, T+38 run the simulation, T+48 hand off, then Q&A) beside the prerequisites (Python 3.9+ and Docker); slide 23, Checkpoint 1 (steps 00–02 on the laptop); slide 24, Checkpoint 2 (steps 03–04 through ROS 2 in Docker on the laptop, or on a prepared station, then the handoff).

**Say:** Slide 22: “For the next hour you own the contract and the judgment; the agent helps you implement and explain. Each step is one script. If one fails, run it again with doctor and follow its fix line.” Slide 23: “Check your machine, then watch the starter fail before you touch it. Ask your agent to explain the failure first, then authorize the smallest fix, and rerun the repair script after every edit.” Slide 24: “Now the same contract runs through ROS 2: a replay, then a simulated robot. With Docker it runs in a fresh container on your own laptop. Read each stop reason, then draft your handoff.”

Follow the [facilitator guide](facilitator-guide.md) for the schedule and hints, [lab/README.md](../lab/README.md) for the scripts and the [command sheet](lab-commands.md) for each operating system's commands and common fixes. Windows without Bash runs `py -3 lab\lab.py 01` (any step number). No hardware is operated.

## Slide 25 — Sources and reproducible materials

Take questions on slide 21 and leave slide 21 up until the lab starts at 2 p.m. (it shows where the lab takes place); show slide 25 on request. Every source is for attribution and setup, not evidence of a physical trial; the executed evidence is in [verification](verification.md).
