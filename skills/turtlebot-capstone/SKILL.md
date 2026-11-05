---
name: turtlebot-capstone
description: Build the workshop's complete TurtleBot3 stop-before-obstacle application, starting in simulation and verifying the sensor-to-command path and failure behavior.
---

Read the capstone in [WORKSHOP.md](../../WORKSHOP.md), then inspect the participant's actual TurtleBot3/ROS workspace. The requested outcome is a complete small application, not just a perception node: sensing, clearance estimate, decision state, bounded velocity output, observed response, and evidence.

Start with the selected simulator. Use the installed TurtleBot scan source through a sensor adapter and preserve the clearance/state interface from the LiDAR exercise. A Unitree cloud adapter is an optional extension only after mounting/TF/timing and sensor integration are established. Do not claim the native TurtleBot LaserScan is the Unitree PointCloud2 stream.

Inspect the command topic type and subscribers. ROBOTIS's [bringup guide](https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/) documents the Jazzy transition to TwistStamped; topic name alone does not select the message. Confirm a single command owner or explicit arbitration and the base's command timeout.

Agree on speed, distance, run-duration, sensing-age, and stop-clearance bounds for the environment. Define the clearance metric against the robot's collision envelope, not the sensor origin. For the straight-ahead exercise, use obstacle longitudinal position minus the robot's front extent in base coordinates, considering obstacles inside the swept corridor expanded by the configured margin. Record footprint, sensor transform, margin, and braking/latency allowance. Accept a different metric only when explicitly specified and verified; do not reuse a diagnostic planar-range threshold without this geometry.

Implement deterministic states such as idle, advance, stopped, and fault. Missing/invalid/stale sensing, failed transforms, operator stop, exceeded bounds, and shutdown must reach the verified stop path. Keep the LLM outside the control loop.

Produce the ROS application/package, configuration and launch entry point in the requested workspace, using existing project conventions. Verify clear-path advance, obstacle stop, data-loss stop, timeout, stop control, and repeatability. Inspect odometry or another appropriate observation rather than equating published commands with robot motion.

Report exact simulated scenarios and limits with [the run-report template](../../templates/run-report.md). A physical trial requires the user's instruction to operate that robot, prepared stop control and area, and separately recorded observations. If hardware is unavailable, deliver the simulated result and a concrete physical-trial plan without claiming device validation.
