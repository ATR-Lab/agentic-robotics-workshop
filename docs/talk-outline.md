# Agentic workflows for robotics: build with Codex and Claude Code

**Format:** 45-minute talk: 22 minutes of explanation, 8-minute LiDAR debugging demo, 10-minute TurtleBot3 application demo, and a 5-minute close (2-minute next-task prompt, 3 minutes of Q&A).  
**Updated:** November 4, 2026. Slide numbers below match the 25-slide deck (`deliverables/atr-slides-agentic-robotics-2026-11-04-animated.pptx`); slides 22–24 are optional lab aids and slide 25 lists sources.  
**Event:** Saturday, Nov. 7, 2026, 1–3 p.m. EST, Mathematical Sciences Building room 228, Kent State University: the talk and demos from 1 to 2 p.m., then the hands-on lab and Q&A from 2 to 3 p.m.  
**Main examples:** an authored PointCloud2 replay on the driver's topic name and message type, followed by a TurtleBot3 application in headless Gazebo.

## Audience and prerequisites

This talk is for people who have programming experience and want to use agents to build and understand software. Attendees should be comfortable reading a small program, using a terminal, and reviewing a Git diff. Python familiarity helps; prior ROS experience is optional. Surface-level robotics knowledge is useful but not required.

A three-minute ROS 2 recap supplies the vocabulary needed for the examples. Most of the talk concerns task definition, project context, iterative implementation, PR understanding, parallel work, and verification. Those practices transfer to general software development.

For the optional hands-on workshop, participants need a laptop and an agent login. The core exercise needs only Python 3.9+; ROS 2 replay and simulation run in Docker on the laptop, or on prepared stations. A synthetic replay and simulation let them participate without a LiDAR or robot; no physical robot is used.

## Talk promise

Use an agent to turn a point-cloud stream into a small, understandable, verified software change. Then follow the same workflow through a complete TurtleBot3 application.

**Core message:** Use tokens to improve understanding and decisions. Measure efficiency by time to an understood, verified change, including the human review time.

## Timed outline

| Time | Slides | Topic | What to show |
|---|---:|---|---|
| 0:00–3:00 | 1–2 | Open with a reproducer | The side-wall fixture and a misleading all-around nearest-point alert |
| 3:00–6:00 | 3 | Just enough ROS 2 | Sensor driver → topic → typed message → processing node |
| 6:00–10:00 | 4–5 | Specify the task and prepare context | A small repository guide and a point-cloud processing contract |
| 10:00–14:00 | 6–7 | Implement, review, and understand | Codex/Claude roles plus the token-spending lesson (adapted from Theo Browne) |
| 14:00–22:00 | 8–11 | LiDAR debugging demonstration | Inspect → failing case → narrow fix → replay → explain-back |
| 22:00–26:00 | 12–13 | Parallel work and evidence | File ownership, shared interfaces, and levels of verification |
| 26:00–30:00 | 14–15 | Build the complete robot application | TurtleBot3 sensor → decision → command → observed response |
| 30:00–40:00 | 16–19 | TurtleBot3 capstone demonstration | Advance, obstacle stop, sensing failure, and inspectable run logs |
| 40:00–45:00 | 20–21 | Q&A and take-home skills | Companion repository and the audience's next bounded task |

## Slide-by-slide talking points

### Slides 1–2. Open with a reproducer

Open directly with the authored fixture. The question is “Is the specified forward sector clear?” A side wall is close, so a naive minimum over every point says blocked even when that sector is open.

Use two labeled synthetic situations to make the contract visible: a side point at (0, 0.20, 0.20) m with a front point at (1.0, 0, 0.20) m; then a front point at (0.25, 0, 0.20) m. These coordinates assume the agreed working frame has x forward. With a proposed 0.50 m diagnostic threshold, the first case should be clear and the second blocked.

This is a diagnostic sector exercise. A vehicle's safe swept volume needs additional treatment in the capstone.

### Slide 3. Give the three-minute ROS 2 recap

- A **node** runs a part of the application; the driver and our processor are separate nodes.
- A **topic** carries messages between nodes. A **message type** defines the data contract.
- A **frame** states what coordinates mean; a **timestamp** states when the measurement was acquired.
- **QoS** describes delivery expectations. A consumer must be compatible with its publisher.
- RViz visualizes messages; a bag records them so the same input can be replayed.

Show `ros2 interface show sensor_msgs/msg/PointCloud2`, which needs no running bag. No topic is live yet: `ros2 topic list -t` and `ros2 topic info --verbose` only work while the replay plays, so name the replay's topic and type (`/unilidar/cloud`, `sensor_msgs/msg/PointCloud2`, from `replay_demo.py`) at slide 10 instead. Explain the output rather than turning the talk into a CLI tutorial.

### Slides 4–5. Specify the task and establish context

Record the ROS distribution, workspace revision, sensor model, driver commit, transport, resolved topics, clock configuration, and available data. Unitree's inspected SDK2 driver uses a configurable `unilidar/cloud` PointCloud2 topic and a separate IMU topic. Namespaces/remaps may change the resolved names. Generic “UniLiDAR” does not establish whether the presenter has an L1 or L2; choose the corresponding official driver. [Unitree SDK1](https://github.com/unitreerobotics/unilidar_sdk), [SDK2 node](https://github.com/unitreerobotics/unilidar_sdk2/blob/main/unitree_lidar_ros2/src/unitree_lidar_ros2/include/unitree_lidar_ros2.h).

**Example contract:** Read the selected cloud topic, transform into the agreed working frame, select a configured forward sector and height band, and report minimum valid planar distance `sqrt(x*x + y*y)` from that frame's origin plus blocked/clear/unknown. Define the threshold, minimum valid point count, age limit, and unknown behavior. This stage has no motor output.

Show that PointCloud2 contains a binary point buffer described by field metadata, dimensions, byte order, point/row strides, and a stamped frame. Use a suitable point reader rather than assuming tightly packed XYZ floats. Check finite values and the selected driver's units. [PointCloud2 definition](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/PointCloud2.msg).

Keep durable context in the project's agent guide and link detailed designs/data. Show the actual instructions loaded by both clients. [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory).

### Slide 6. Give the tools clear roles

Have one agent implement a scoped change and the other review against the contract. Supply the reviewer with changed files and executed-check evidence. Ask for reproducible findings, not reassurance. Swapping the roles is valid; this is a workflow choice rather than a product ranking. [Claude Code best practices](https://code.claude.com/docs/en/best-practices).

### Slide 7. Spend tokens to understand the PR

In [Theo Browne's video around 20:34](https://www.youtube.com/watch?v=q1D90-uGvBg&t=1234), he asks for a simpler explanation when an agent's solution becomes difficult to follow. Use this as the starting point for a practical lesson: do not avoid spending tokens on the questions needed to understand a PR.

Trace a cloud point through decoding, frame transformation, sector filtering, clearance reduction, and diagnostic output. Ask for before/after behavior and a failure path. For example: “I understand the subscriber, but why does this side-wall point decide a forward alert? Walk it through the old and new code.”

Explain the change back in your own words and predict a new case. Token spending is useful when it closes a specific understanding gap; the prediction and executed check make that understanding inspectable.

### Slides 8–11. Eight-minute LiDAR debugging demonstration

1. **Minute 0–1:** Show the contract and run the unchanged starter (`python3 -I exercises/check.py`).
2. **Minute 1–2:** Reveal the seeded all-around minimum reducer.
3. **Minute 2–4:** Ask for a failing side-wall regression case and a true frontal-obstacle case.
4. **Minute 4–6:** Implement the smallest corrected sector reducer and run the affected checks.
5. **Minute 6–7:** `replay_demo`, launched at the end of slide 9, has finished (about 20 s; `/unilidar/cloud` publishes for about 14 s). Name the topic and PointCloud2 type it played and read its report. It runs the packaged reference node (same contract, not the edited exercise file) against the authored synthetic bag; compare its states with the fixture expectations, including invalid/stale-data behavior.
6. **Minute 7–8:** Read the three evidence counts (slide 11); review the diff if time remains. Once `replay_demo` has exited, launch `capstone.launch.py` on domain 78 for the capstone demo.

Make the live edit in a scratch copy of the workshop folder (`cp -R`; the checker resolves `clearance.py` relative to its own folder) with a baseline commit (`git add -A && git commit -qm baseline`) so `git diff` shows the edit, because the repository has no Git history to restore from; before the lab, confirm the distributed starter still shows 10/12. Prepare the synthetic bag, compatible QoS, required transforms, replay clock settings, and the offline starter/solution pair (the only broken/fixed revisions). A synthetic fixture tests selected logic; replay tests one bag. Label which is shown. Keep a terminal transcript and recording available if live generation runs long.

### Slides 12–13. Parallel work and honest evidence

Split independent tasks: point decoder/reducer, replay analysis, and read-only review. Agree on interfaces and file ownership first, with one integration owner. Separate Git worktrees isolate checkout changes; ROS domains, ports, devices, and datasets still need explicit ownership. [Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees).

| Evidence | What it establishes |
|---|---|
| Build/static checks | Selected compilation and rule checks |
| Synthetic fixtures | Expected behavior for specified inputs |
| Bag replay (here: authored synthetic bag) | Behavior on that recorded or authored dataset |
| Simulation | Behavior in that simulated setup |
| Physical trial | Behavior on that device and configuration |

Record failures, commands, configuration, and unexecuted checks. These habits apply equally to a web service or data pipeline.

### Slides 14–15. Introduce the complete TurtleBot3 application

**Task:** On a start command, advance a short bounded distance in a prepared corridor, stop before an obstacle, and stop on missing/stale input or loss of run permission.

Show the complete path: sensor adapter → clearance estimate → deterministic state machine → bounded velocity publisher → base motion → odometry/logs. Use idle, advance, stopped, and fault states. The agent helps build the application; deterministic code handles runtime control.

For motion, measure obstacle clearance against the robot's collision envelope. In the straight-ahead exercise, define longitudinal gap from the robot's front extent inside its swept corridor, including the chosen margin. Record footprint, transforms, and braking/latency allowance; the diagnostic sensor-origin planar range is a different metric.

Use TurtleBot3's installed sensor stream through a LaserScan adapter for the baseline. Reuse the clearance/state contract from the PointCloud2 exercise. Mounting a Unitree LiDAR is an optional extension requiring separate mechanical, power, frame, and timing integration.

Confirm the actual command type. ROBOTIS documents TwistStamped from Jazzy and a compatibility parameter; a `cmd_vel` name alone does not select the interface. [TurtleBot3 bringup](https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/).

### Slides 16–19. Ten-minute end-to-end capstone demonstration

- **Minutes 0–2:** In the world launched at slide 11, after `replay_demo` exited, on its own `ROS_DOMAIN_ID` (replay 77, capstone 78; the two demos run sequentially on the demo station), with no manual `/workshop/start` (start only succeeds from idle), start `ros2 run agentic_workshop capstone_check --output /home/user/runs/capstone-NEW` at minute 0. While it runs (about 30 s), show the application package, launch configuration, command ownership, bounds and stop path.
- **Minutes 2–4:** Narrate `clear_path_distance_bound` from that run (it reports at about 8 s): start, advance, observed odometry, stop at the bound.
- **Minutes 4–6:** From the same run, narrate `obstacle_stop` (the checker raises `max_distance` to 2.0 first) and compare clearance, state transition, velocity output and odometry.
- **Minutes 6–8:** Narrate `scan_drop`, `scan_invalid`, `scan_missing_tf`, `operator_stop` and `controller_process_loss_watchdog`: zero command and base-timeout behavior.
- **Minutes 8–10:** Review logs and the complete diff with the agent. State what ran in simulation and that no hardware was operated.

The demonstration uses headless Gazebo with the configured TurtleBot3 model; the fallback is the saved `evidence/2026-11-03/capstone-report.json` with slides 16 and 18. Configure the model and ROS distribution using the [official simulation guide](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/). A physical TurtleBot3 is not part of this event; any later physical trial needs a prepared area, a verified stop path and separate approval.

The simulated stack ran on Nov. 3, 2026 (10/10 capstone scenarios; see [verification](verification.md)). No physical robot or real UniLiDAR capture has been run.

### Slides 20–21. Close with the transferable workflow

Specify the outcome, inspect the environment, implement a bounded change, ask until you understand it, execute meaningful checks, and preserve the evidence. Measure time to an understood, verified result and the human correction effort.

### Slides 22–25. Optional lab aids and sources

Slides 22–24 frame the one-hour lab (2–3 p.m.): the five steps with their start times, then Checkpoint 1 (steps 00–02 on the laptop, T+00–T+30) and Checkpoint 2 (steps 03–04 through ROS 2 in Docker or on a station, then the handoff, T+30–T+50), with questions from T+50. Each step is a script in [lab/](../lab/README.md) with a `doctor` check. The [facilitator guide](facilitator-guide.md) holds the detailed schedule and hints. Slide 25 lists sources and the local take-home material; take questions on slide 21 and leave slide 21 up until the lab starts at 2 p.m. (it shows where the lab takes place); show slide 25 on request.

## Companion repository and prompts

The local companion is [agentic-robotics-workshop](../README.md). It contains four skills:

- `robotics-orient`: inventory the environment and write the contract.
- `explain-robotics-pr`: understand a change through code paths and evidence.
- `unilidar-replay`: implement and verify the diagnostic cloud exercise.
- `turtlebot-capstone`: build the complete robot application, starting in simulation.

**Orient:** “Use robotics-orient in this workspace. Explain the topic graph and propose the smallest change with acceptance cases.”

**Implement:** “Use unilidar-replay against this contract and recording. Implement the bounded diagnostic node, run the checks, and report exact results.”

**Understand:** “I understand [part] but not [gap]. Trace one normal point and one failure case through this PR, with code references.”

**Capstone:** “Use turtlebot-capstone to implement the complete application in the selected simulator. Verify start, obstacle stop, input loss, command timeout, and observed response.”

## Extended workshop and presenter preparation

A 45-minute slot demonstrates prepared implementations. The one-hour lab has participants fix and explain the diagnostic, then replay and simulate the prepared stages: check 5; reproduce 5; implement and explain 20; replay 8; simulation 10; handoff 2; Q&A 10. Building the TurtleBot application needs about two hours and is a take-home extension.

Before presenting, pin the software versions, prepare the ROS environment and data, rehearse both demonstrations, and record fallbacks. Recheck current client instructions and robot interfaces. The Theo passage is paraphrased from automatic English captions; the slide presents it as an adaptation, not a quotation. Confirm the UniLiDAR model and driver only if a hardware extension is added later.
