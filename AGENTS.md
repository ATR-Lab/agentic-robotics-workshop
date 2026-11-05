# Agentic Robotics Workshop

This draft companion repository teaches an agent-assisted development workflow using Unitree UniLiDAR data and a TurtleBot3 capstone. Start with README.md and WORKSHOP.md; load only the skill relevant to the current request.

- `skills/` is the canonical skill source. `CLAUDE.md` imports this file.
- Preserve the user's chosen task, ROS distribution, driver version, and hardware. Inspect actual topics, message schemas, frames, clocks, and QoS before coding adapters.
- Draft specifications and proposed commands are not executed evidence. Record exactly what ran and what environment it covered.
- The starting mode is analysis/replay/simulation. A request to prepare workshop material does not authorize operating a physical robot.
- Keep the agent outside the real-time control loop. A robot application uses deterministic code with bounded commands, timeouts, and a verified stop path.
- Keep recordings, generated run output, virtual environments, ROS build/install/log directories, and credentials outside version control.
- Workshop material starts at docs/start-here.md. exercises/clearance.py is deliberately incorrect; do not repair it while maintaining the pack unless the user is taking the exercise. solutions/ contains the answer. Verify the solution passes and the starter fails the documented cases. Avoid importing modules in a way that leaves bytecode in source.
- lab/ holds the participant step scripts (run, doctor, help); keep lab/lab.py standard-library Python 3.9 and the .sh files as thin launchers.
- lab/docker/Dockerfile builds the station image that runs steps 03-04 on any OS with Docker. It is published as ghcr.io/atr-lab/agentic-workshop-station; when ros2/agentic_workshop changes, publish a new tag (see docs/setup.md) and bump IMAGE in lab/lab.py and the docs.
- Add only material needed by the requested exercise. Preserve existing participant work; do not install these skills globally or publish this repository unless requested.
