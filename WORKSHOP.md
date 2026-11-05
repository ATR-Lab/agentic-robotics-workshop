# Workshop plan and implementation contract

Drafted October 28, 2026; executable integrations added November 3, 2026. The ROS build, synthetic replay and Gazebo checks ran in Boat; see [verification](docs/verification.md). Actual UniLiDAR capture and hardware behavior remain unverified.

Expanded November 3, 2026: [the material pack](docs/start-here.md) now provides the slide manuscript, facilitator guide, workbook and executable offline exercise. The offline solution is checked separately from the ROS replay and simulator runs.

## Learning sequence

The lab runs 2–3 p.m. after the talk. Each step is a script in [lab/](lab/README.md) with `run`, `doctor` and `help`.

| One-hour lab | Activity | Participant artifact |
|---|---|---|
| 0–5 | Check the machine (`lab/00-check.sh`) | Doctor report with no FAIL |
| 5–10 | Reproduce the starter failure (`lab/01-reproduce.sh`) | Baseline commit and failing output |
| 10–30 | Implement the sector filter with an agent, then explain and review it (`lab/02-repair.sh`) | Small diff, 12/12 with the checker unchanged, explain-back |
| 30–38 | Replay the synthetic bag through ROS 2, in Docker or on a station (`lab/03-replay.sh`) | Replay report |
| 38–48 | Observe the bounded TurtleBot3 application in simulation (`lab/04-simulate.sh`) | Scenario report and stop reasons |
| 48–50 | Draft the handoff (`lab/05-handoff.sh`) | Run report |
| 50–60 | Questions | Next bounded task |

Building the TurtleBot3 application is a take-home extension; the hour observes the prepared one.

## UniLiDAR input and diagnostic exercise

Select the SDK matching the actual sensor model. Unitree maintains [SDK1](https://github.com/unitreerobotics/unilidar_sdk) and [SDK2](https://github.com/unitreerobotics/unilidar_sdk2); do not assume an L1 and an L2 share transport/setup instructions. The inspected SDK2 node publishes a configurable `unilidar/cloud` PointCloud2 stream and a separate IMU stream. Its [node source](https://github.com/unitreerobotics/unilidar_sdk2/blob/main/unitree_lidar_ros2/src/unitree_lidar_ros2/include/unitree_lidar_ros2.h) and [launch configuration](https://github.com/unitreerobotics/unilidar_sdk2/blob/main/unitree_lidar_ros2/src/unitree_lidar_ros2/launch/launch.py) are the source for defaults. Namespaces/remaps can change resolved topic names. Record the installed commit and actual parameters.

The node under exercise transforms points to an agreed working frame and reports minimum valid distance within a defined forward sector and height band. For this diagnostic exercise, use planar distance `sqrt(x*x + y*y)` from that frame's origin after filtering; record the frame and origin explicitly. It publishes diagnostic state and has no motor output. Choose the sector, height band, minimum valid point count, age limit, and threshold before implementation. If a different distance metric is desired, specify it before selecting the threshold. Empty, stale, malformed, or untransformable data yields `unknown`, not `clear`.

Use the message's metadata and a suitable ROS point-cloud reader rather than assuming XYZ floats are tightly packed. [PointCloud2](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/PointCloud2.msg) describes fields, byte order, dimensions, point/row strides, frame, and acquisition stamp. Verify coordinate units and point-field meaning against the selected driver. [REP 103](https://www.ros.org/reps/rep-0103.html) documents the ROS SI/frame conventions.

For the seeded demonstration, compare an incorrect all-around nearest-point reducer with a specified forward-sector reducer. A side wall closer than a front obstacle should not decide the forward-sector result. The acceptance fixture must also cover a true frontal obstacle; filtering is not permission to ignore hazards in a robot's swept volume.

## TurtleBot3 capstone: a complete robot application

**Task:** Starting from a commanded start, move a short bounded distance in a prepared clear corridor and stop before an introduced obstacle; missing/stale sensing or loss of run permission also stops motion. No navigation stack, mapping, or autonomous obstacle detour is required for this lesson.

**Architecture:** Sensor adapter → clearance estimate → deterministic state machine (`idle`, `advance`, `stopped`, `fault`) → bounded command publisher → TurtleBot3 base. Log inputs, estimates, transitions, commands, and odometry so observed behavior can be compared with intent. The agent writes and reviews code; it does not generate live motor decisions.

The capstone's stopping clearance is measured from the robot's collision envelope, not from the sensor origin. For this straight-ahead task, an explicit simple contract is longitudinal gap `obstacle_x - front_extent_x` in the robot base frame for obstacles inside the forward swept corridor, with corridor width expanded by the chosen margin. Record the footprint, sensor-to-base transform, margin, and braking/latency allowance before setting the stop threshold. A different geometry/metric is valid if specified and checked; the diagnostic planar norm is not a direct drop-in motion threshold.

For the baseline, use TurtleBot3's installed scan source and a LaserScan adapter after inspecting its contract. Reuse the clearance/state interface learned in the cloud exercise. Unitree PointCloud2 is a separate adapter: mounting, transform calibration, timing, support/power, and physical integration must be established before claiming a Unitree-equipped TurtleBot demo. A tabletop UniLiDAR session and a TurtleBot native-sensor capstone are valid, clearly labeled workshop stages.

Inspect `/cmd_vel` and its subscribers in the actual environment. ROBOTIS documents [TwistStamped from Jazzy](https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/), with a compatibility parameter; choose the installed interface rather than guessing from the topic name. Use the matching official [simulation setup](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/) for the selected ROS distribution.

Acceptance scenarios: clear corridor advances within configured speed/time/distance bounds; frontal obstacle stops; stale/missing/invalid sensing stops; unavailable transform stops; operator stop and process shutdown stop; repeated runs produce inspectable logs. Verify command arbitration and the base's command timeout. Simulator results establish that simulated configuration only. A physical trial requires a prepared area, an available stop control, and separately recorded results.

## Presenter readiness

Pin OS/ROS distribution, simulator, TurtleBot model/packages, driver commit, and transport; record them in the interface contract. Rehearse with recordings and simulation before scheduling live hardware. Prepare the broken/fixed perception revisions and a capstone recording. Store data and run output outside Git; do not present these draft instructions as a completed deployment.
