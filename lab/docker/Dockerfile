# ROS 2 station for lab steps 03 and 04, for any computer with Docker (macOS, Windows or Linux; x86-64 or arm64).
# Published as ghcr.io/atr-lab/agentic-workshop-station:2026.11 (amd64 and arm64).
# Build from the workshop folder:  docker build -t ghcr.io/atr-lab/agentic-workshop-station:2026.11 -f lab/docker/Dockerfile .
# Same packages and ROBOTIS revision as scripts/boat-setup.sh and scripts/boat-build.sh.
FROM ros:jazzy-ros-base-noble@sha256:8eed0a4669bbf43ee331878a4c39bd8ebddea8e3312a58b4fae8edb14526b617

ARG TURTLEBOT3_SIMULATIONS_REVISION=45633014a14e8f438495b532a723e4ad45cbbd31
RUN apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git procps python3-colcon-common-extensions \
      ros-jazzy-sensor-msgs-py ros-jazzy-tf2-ros ros-jazzy-rosbag2 ros-jazzy-ros-gz \
      ros-jazzy-turtlebot3-description ros-jazzy-robot-state-publisher libgl1-mesa-dri \
 && rm -rf /var/lib/apt/lists/*

# The notes and scripts expect the account "user" with home /home/user; the base image's uid 1000 is "ubuntu".
RUN userdel -r ubuntu && useradd -m -u 1000 -s /bin/bash user
USER user
WORKDIR /home/user

RUN git init -q sim_ws/src/turtlebot3_simulations \
 && cd sim_ws/src/turtlebot3_simulations \
 && git remote add origin https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git \
 && git fetch -q --depth 1 origin "$TURTLEBOT3_SIMULATIONS_REVISION" \
 && git checkout -q --detach FETCH_HEAD

COPY --chown=user:user ros2/agentic_workshop ros_ws/src/agentic_workshop
RUN ln -s /home/user/sim_ws/src/turtlebot3_simulations/turtlebot3_gazebo ros_ws/src/turtlebot3_gazebo \
 && . /opt/ros/jazzy/setup.sh \
 && cd ros_ws \
 && colcon build --packages-select turtlebot3_gazebo agentic_workshop --executor sequential \
 && rm -rf build log \
 && chmod -R a+rX /home/user

# Inside the container the lab scripts run the ROS steps directly. HOME may be overridden when the
# container runs as the host user, so the workspace path is fixed here.
ENV LAB_STATION=native LAB_ROS_WS=/home/user/ros_ws PYTHONDONTWRITEBYTECODE=1
LABEL org.opencontainers.image.title="Agentic robotics workshop station" \
      org.opencontainers.image.description="ROS 2 Jazzy, Gazebo and the agentic_workshop package for lab steps 03 and 04" \
      org.opencontainers.image.source="https://github.com/ATR-Lab/agentic-robotics-workshop" \
      org.opencontainers.image.licenses="MIT"
WORKDIR /home/user/workshop
