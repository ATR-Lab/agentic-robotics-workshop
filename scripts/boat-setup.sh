#!/usr/bin/env bash
set -euo pipefail
# Fresh Ubuntu 24.04 station only (a Boat VM or an OrbStack machine with user "user"). Run explicitly; installs ROS and simulator packages.
source /etc/os-release
test "$VERSION_CODENAME" = noble
sudo apt-get update -qq
sudo apt-get install -y curl git gnupg lsb-release software-properties-common
sudo add-apt-repository -y universe
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor --yes -o /etc/apt/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ros-jazzy-ros-base ros-jazzy-sensor-msgs-py ros-jazzy-tf2-ros ros-jazzy-rosbag2 python3-colcon-common-extensions ros-jazzy-ros-gz ros-jazzy-turtlebot3-description ros-jazzy-robot-state-publisher xvfb libgl1-mesa-dri
apt-cache search ros-jazzy-turtlebot3

mkdir -p /home/user/sim_ws/src
if [ ! -d /home/user/sim_ws/src/turtlebot3_simulations/.git ]; then
  git init /home/user/sim_ws/src/turtlebot3_simulations
  git -C /home/user/sim_ws/src/turtlebot3_simulations remote add origin https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
  git -C /home/user/sim_ws/src/turtlebot3_simulations fetch --depth 1 origin 45633014a14e8f438495b532a723e4ad45cbbd31
  git -C /home/user/sim_ws/src/turtlebot3_simulations checkout --detach FETCH_HEAD
fi
