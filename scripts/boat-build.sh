#!/usr/bin/env bash
set -euo pipefail
set +u
source /opt/ros/jazzy/setup.bash
set -u
mkdir -p /home/user/ros_ws/src
ln -sfn /home/user/workshop/ros2/agentic_workshop /home/user/ros_ws/src/agentic_workshop
ln -sfn /home/user/sim_ws/src/turtlebot3_simulations/turtlebot3_gazebo /home/user/ros_ws/src/turtlebot3_gazebo
cd /home/user/ros_ws
colcon build --symlink-install --packages-select turtlebot3_gazebo agentic_workshop --executor sequential
