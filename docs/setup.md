# Setup and presenter readiness

## Before participants arrive

Distribute this repository as a folder or Git checkout. Participants need Python 3.9 or newer, a terminal, a text editor and a working Codex or Claude Code login. Provide the prompt cards as a plain-file alternative to automatic skill discovery. Pair people without agent access with a participant or use a prepared transcript.

Ask participants to run `bash lab/00-check.sh` before the lab; it checks Python, Git, the folder, agent access and Docker, and saves a report a facilitator can read. Run the solution command in [Start here](start-here.md). The offline exercise uses only the standard library. It does not need ROS, a Python environment, network access or a sensor. Run commands from the repository root. `-I` isolates Python from user import configuration; the checker loads the chosen module explicitly.

For Codex, open this repo and invoke `$robotics-orient` or select the relevant skill. For Claude Code use `/robotics-orient` when that project skill is discovered. In either client, ask which file it loaded. Explicitly reading `skills/robotics-orient/SKILL.md` is a fallback. See [official Codex skills](https://learn.chatgpt.com/docs/build-skills) and [Claude Code skills](https://code.claude.com/docs/en/skills). Product guidance checked November 3, 2026; verify the installed client rather than relying on an old screenshot.

## ROS 2 on participant laptops (Docker)

Steps 03 and 04 run on any laptop with Docker: Docker Desktop on Windows or macOS (OrbStack also works on a Mac), Docker Engine on Linux, with at least 4 GB of memory for Docker and about 6 GB of free disk. Ask participants to install it and pull the station image before the event, not over the room's network. `scripts/install.sh` (macOS, Linux) and `scripts/install-windows.ps1` (Windows) do both, and install Python and Git; on Windows and macOS they run Docker Engine in a Linux VM (WSL 2, Colima) unless asked for Docker Desktop ([command sheet](lab-commands.md#before-the-workshop-15-minutes-needs-internet)). By hand:

```bash
docker pull ghcr.io/atr-lab/agentic-workshop-station:2026.11
```

The image is public on the GitHub Container Registry and holds both `amd64` and `arm64` builds; Docker fetches the one for the laptop, about 1.2 GB. `bash lab/00-check.sh` then confirms Docker, the image and the station inside it. The image holds the same ROS 2 Jazzy packages and ROBOTIS revision as the Boat setup scripts.

For a room without internet, save the image to a file on a machine of each architecture and hand it out on a drive; participants load it with `docker load -i <file>`:

```bash
docker save ghcr.io/atr-lab/agentic-workshop-station:2026.11 | gzip > agentic-workshop-station-2026.11-$(docker version -f '{{.Server.Arch}}').tar.gz
```

When `ros2/agentic_workshop` changes, publish a new tag and update `IMAGE` in `lab/lab.py`. From the workshop folder, with a Buildx builder that has an arm64 and an amd64 node (each building natively) and a GitHub login with `write:packages`:

```bash
docker buildx build --builder <builder> --platform linux/arm64,linux/amd64 -t ghcr.io/atr-lab/agentic-workshop-station:<new tag> -f lab/docker/Dockerfile \
  --annotation 'index:org.opencontainers.image.source=https://github.com/ATR-Lab/agentic-robotics-workshop' --push .
```

The `index:` annotation links the package to this repository on GitHub; the Dockerfile's matching label covers single-architecture builds.

Windows laptops need hardware virtualization for Docker Desktop's WSL 2 backend. A Windows virtual machine without nested virtualization cannot run it; pair that participant with a neighbour or an assigned station.

## Prepare the ROS station separately

Use a prepared Linux ROS 2 environment, with a pinned distribution, driver revision and TurtleBot model. Jazzy is a candidate teaching baseline, not a compatibility claim for every Unitree SDK. Record the combination that actually builds. Follow the selected sensor's official [SDK1](https://github.com/unitreerobotics/unilidar_sdk) or [SDK2](https://github.com/unitreerobotics/unilidar_sdk2) instructions; L1/L2 transport configuration is not interchangeable.

Fill the [interface contract](../templates/interface-contract.md). Supply a small actual bag with acquisition provenance, resolved topics, schema, QoS, frame transforms and clock notes. Store recordings outside tracked source. Confirm replay with the motor interface disconnected. Prepare broken/fixed diagnostic revisions, terminal output and an RViz recording. Do not label the offline tuples a PointCloud2 recording.

Prepare the matching [TurtleBot3 simulator](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/). Record the actual scan topic, odometry topic and velocity message type. The [bringup guide](https://emanual.robotis.com/docs/en/platform/turtlebot3/bringup/) documents version-dependent Twist/TwistStamped behavior. Use a separate ROS domain per station and one velocity-command owner per robot.

## Readiness decision

| Gate | Required evidence | Fallback if unavailable |
|---|---|---|
| Station doctor | `bash lab/00-check.sh` on each station or Docker laptop shows no FAIL, then one run each of `lab/03-replay.sh` and `lab/04-simulate.sh` | Saved reports in `evidence/2026-11-03/`; mark the live step unexecuted |
| Offline exercise | Solution passes and starter fails as documented | Prepared output plus code walkthrough |
| Sensor replay | The authored synthetic bag (or a real recording, if supplied) reproduces the agreed cases with TF/clock/QoS recorded | Saved replay report from Nov. 3; mark the live replay unexecuted |
| Simulated robot | Clear-path, obstacle and sensing-loss scenarios logged | Architecture exercise and supplied recording labeled prerecorded |
| Physical robot | Rehearsed bounded trial, stop control and observed response | Simulator; no hardware-success claim |

The hardware trial is optional and is not authorized by preparation of teaching materials. Scope any later operation to the chosen robot and prepared area. Keep the coding agent outside the control loop.

Keep participant work in a designated working copy. Never remove a participant's edits to reset an exercise; use a fresh copy.
