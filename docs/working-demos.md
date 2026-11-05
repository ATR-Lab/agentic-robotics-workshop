# ROS replay and TurtleBot3 demos

Implementation uses ROS 2 Jazzy on Ubuntu 24.04 and the ROBOTIS Jazzy Gazebo simulation. Run in a dedicated simulation environment, not on a physical robot. Sources live in [ros2/agentic_workshop](../ros2/agentic_workshop). Read [the verification report](verification.md) before claiming a scenario passed. In the hands-on lab, `bash lab/03-replay.sh` and `bash lab/04-simulate.sh` wrap the replay and capstone commands below, with a doctor check and fresh output folders ([lab/README.md](../lab/README.md)).

## Where to run

For the lab steps, the simplest route is Docker on any laptop: `bash lab/03-replay.sh` and `bash lab/04-simulate.sh` run these same commands in the station image ([lab/README.md](../lab/README.md#ros-2-through-docker)). For the talk's live demos, use one Ubuntu 24.04 machine with `scripts/boat-setup.sh` and `scripts/boat-build.sh`: a Boat VM as below, an OrbStack machine ([rehearsal](rehearsal.md)) or any fresh Ubuntu 24.04 VM with an account named `user`.

## Boat environment

Boat is the cloud VM tool used for the Nov. 3 and Nov. 4 runs. `boat new --no-env --type default --ttl 7200 --name agentic-robotics-workshop` creates a bounded VM without copying stored account secrets. Use the returned ID in place of `BOX` below. Do not provision a new machine if you can resume the prepared workshop snapshot.

```bash
boat push BOX . --to /home/user/workshop
boat exec BOX --detach -- bash /home/user/workshop/scripts/boat-setup.sh
```

Inspect the returned setup PID with `boat exec BOX --status PID`. Setup fetches ROBOTIS revision `45633014a14e8f438495b532a723e4ad45cbbd31` into `/home/user/sim_ws/src/turtlebot3_simulations`. Run `bash /home/user/workshop/scripts/boat-build.sh` on the VM afterward. Dependency installation and build output stay on the VM. The setup script installs system packages; it is intended only for a fresh Ubuntu 24.04 workshop VM.

## Replay lab

Source `/opt/ros/jazzy/setup.bash` and `/home/user/ros_ws/install/setup.bash` inside the VM, then choose a dedicated ROS domain, for example `export ROS_DOMAIN_ID=77`. Use the same domain in every shell belonging to that demo. Run replay and Gazebo sequentially on the default-size VM. Then:

```bash
ros2 run agentic_workshop replay_demo --output /home/user/runs/replay-01
```

Use a new output directory for each replay run. The program creates a real SQLite rosbag with **authored synthetic** PointCloud2 messages, runs the diagnostic node and plays the bag with `/clock`. Its nine checks cover clear/blocked/empty/missing-TF phases, padded big-endian organized clouds, stale/future stamps, the transform's numerical effect and post-playback reception timeout. The static transform translates the sensor by 0.10 m, so successful output also exercises the TF lookup path.

The cloud node reads XYZ field offsets, scalar float datatype, byte order, point stride and row stride. It transforms points into `base_link`, filters finite values by height and sector and reports JSON diagnostics on `/workshop/cloud_status`. A steady-clock timer detects reception loss even when the replay clock freezes. It never publishes motor commands.

For an actual UniLiDAR bag, first inspect the model/driver, topic, schema, QoS and TF/clock contract. Then run `cloud_diagnostic` with its `cloud_topic` and `target_frame` ROS parameters and use the corresponding bag playback command. A synthetic bag validates ROS transport/replay behavior; it is not a capture from Unitree hardware.

## TurtleBot3 capstone

In a prepared VM shell:

```bash
ros2 launch agentic_workshop capstone.launch.py
```

This starts a Gazebo server without the GUI, spawns the ROBOTIS Burger model, bridges scan/odometry/TF/clock, starts the explicit scan fault-injection relay, bounded controller and independent command watchdog. Software rendering is enabled for a VM without a GPU. Gazebo transport uses loopback and the explicit `agentic_workshop` partition, which fixed world discovery in Boat. To view the scene, open `boat desktop BOX` and run `GZ_IP=127.0.0.1 GZ_PARTITION=agentic_workshop gz sim -g` in a sourced VM terminal; the GUI route has not been visually verified here. A static obstacle sits ahead of the robot.

The default controller advances at 0.10 m/s, stops after 0.45 m or 10 seconds and stops when forward collision-envelope clearance reaches 0.30 m. Geometry assumptions are front extent 0.11 m and corridor half-width 0.15 m, including a teaching margin. These are simulator exercise settings, not a hardware stopping calibration. Velocity uses TwistStamped in the tested Jazzy bridge.

```bash
ros2 service call /workshop/start std_srvs/srv/Trigger '{}'
ros2 service call /workshop/stop std_srvs/srv/Trigger '{}'
ros2 service call /workshop/reset std_srvs/srv/Trigger '{}'
```

Stopped/faulted runs do not auto-resume; reset then issue a fresh start. Start requires fresh scan/odometry and clearance. The controller checks freshness on a periodic tick. `/workshop/controller_status` reports state, reason, command, gap and traveled distance. Observe `/odom` separately from commanded velocity.

The simulator fault relay has `mode` values `pass`, `drop`, `invalid` and `missing_tf`. It makes injected failures explicit. The command guard relays `/cmd_vel` to `/base_cmd_vel`; the Gazebo bridge consumes only the guarded output and sends zero after 0.30 seconds without controller updates. Do not bypass the guard or add another command publisher.

## Scenario checks

With the capstone running in one VM process, run in another sourced shell:

```bash
ros2 run agentic_workshop capstone_check --output /home/user/runs/capstone-01
```

The ten-check runner verifies rejected speed settings and reset-before-restart, observes displacement from odometry, distance-bound stop and obstacle stop, moves the Gazebo obstacle away, injects scan loss/invalidity/TF failure, exercises operator and time stops and suspends the controller process to verify the independent watchdog. It resumes the process afterward. This checker deliberately changes the isolated simulator scene; do not attach it to a shared or physical robot graph.

Reports and event logs are written even on an assertion failure. Only a successful process exit with the complete expected scenario list is a passed run. Preserve the simulator and controller logs when diagnosing a failure.

## Retain the environment

Copy verification artifacts to the chosen evidence location. Save a named Boat snapshot if the environment should be retained; snapshots may incur storage charges under the account's plan. Stop the VM when finished, retaining its resumable state. Do not delete a VM containing the only copy of evidence or workshop work.
