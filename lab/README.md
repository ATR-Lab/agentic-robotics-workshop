# Lab step scripts

The one-hour hands-on lab (2–3 p.m.) runs as six short steps. Each step is one script. Run it from the workshop folder:

```bash
bash lab/01-reproduce.sh            # run the step (the default)
bash lab/01-reproduce.sh doctor     # check only: what is wrong and how to fix it
bash lab/01-reproduce.sh help       # what the step does
```

Commands for Windows without Bash, and the common fixes on each operating system: [docs/lab-commands.md](../docs/lab-commands.md).

Each `run` first runs that step's doctor and stops on a `FAIL` line, so a problem is reported before anything changes. Every command the script executes is printed with a `$` in front, so you can see and repeat it. Results go to `runs/` (ignored by Git).

| Clock | Step | Script | Where | What it does |
|---|---|---|---|---|
| 2:00 | 00 Check | `bash lab/00-check.sh` | Laptop and station | Checks the machine for every step and saves `runs/doctor-<time>.txt` |
| 2:05 | 01 Reproduce | `bash lab/01-reproduce.sh` | Laptop | Makes the baseline commit and `lab-baseline` tag, then runs the starter: 10/12 is expected |
| 2:10 | 02 Repair | `bash lab/02-repair.sh` | Laptop | After each agent edit: reruns the 12 checks and shows your diff; checks that `check.py` is unchanged |
| 2:30 | 03 Replay | `bash lab/03-replay.sh` | Laptop with Docker, or a ROS 2 station | Replays the synthetic point-cloud bag through the reference node on domain 77 |
| 2:38 | 04 Simulate | `bash lab/04-simulate.sh` | Laptop with Docker, or a ROS 2 station | Starts a fresh headless Gazebo world on domain 78, runs the ten scenarios, shuts it down |
| 2:48 | 05 Hand off | `bash lab/05-handoff.sh` | Laptop | Drafts your run report from the saved results |
| 2:50 | Q&A | | | |

Steps 03 and 04 replay and simulate the packaged reference code, not your edited `clearance.py`. They show the same contract running through ROS 2 topics and a simulated robot.

## ROS 2 through Docker

Steps 03 and 04 need ROS 2 Jazzy and Gazebo. On a computer with Docker (macOS, Windows or Linux, x86-64 or arm64) the scripts run those two steps in the station container, on your own copy of the folder; results still land in your `runs/`. On a Linux machine with ROS 2 Jazzy installed in `/opt/ros/jazzy`, they run directly instead.

Before the lab, on each laptop, either run the install script (`bash scripts/install.sh` on macOS or Linux, `scripts\install-windows.ps1` on Windows; see the [command sheet](../docs/lab-commands.md)) or:

1. Install and start [Docker Desktop](https://docs.docker.com/desktop/) (Windows and macOS; OrbStack also works on a Mac) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux). Give Docker at least 4 GB of memory and keep about 6 GB of disk free.
2. Pull the station image (about 1.2 GB; Docker picks the version for your processor):

```bash
docker pull ghcr.io/atr-lab/agentic-workshop-station:2026.11
```

   Without internet, load the file a facilitator gives you with `docker load -i <file>`.

3. Run `bash lab/00-check.sh`. It checks Docker and the image, then runs the station's own doctor inside the container.

Each run starts a fresh container named `atr-lab-03` or `atr-lab-04` and removes it afterwards, so a crashed run cannot leave the simulator running on your laptop. Inside the container the ROS domain is private, so laptops on the same network do not need different domain numbers.

## When something goes wrong

1. Run the step again with `doctor`. Every `FAIL` and `WARN` line comes with a `Fix:` line.
2. Still stuck: run `bash lab/00-check.sh` and show the saved `runs/doctor-<time>.txt` to a facilitator. It records the OS, Python, Git, folder, ROS installation and every check result.
3. A ROS step left processes behind (after Ctrl-C or a crash): `bash lab/04-simulate.sh clean` (or `03-replay.sh clean`) stops them for your user only, or removes a leftover lab container.

| Symptom | Usual cause | Fix |
|---|---|---|
| `No Python 3.9 or newer found` | Python missing, or the Windows Store placeholder | Install Python 3.9+ and open a new terminal |
| `.sh` will not run on Windows | No Bash | Use Git Bash or WSL, or run `py -3 lab\lab.py 01 run` (any step number) |
| `docker command was not found` | Docker not installed | Install Docker Desktop or Docker Engine (see above) |
| `Docker is installed but its engine is not running` | Docker Desktop or the service is stopped | Start Docker Desktop (or OrbStack); on Linux `sudo systemctl start docker` |
| `permission denied` from Docker on Linux | User not in the `docker` group | `sudo usermod -aG docker $USER`, then log out and back in |
| `the station image ... is not on this computer` | Image not pulled | `docker pull ghcr.io/atr-lab/agentic-workshop-station:2026.11`, or `docker load -i <file>` offline |
| `image is built for ... but Docker runs ...` | Image copied from a different kind of computer | Pull the image again, or load the file for your architecture |
| `an earlier lab container is still running` | A run was killed from outside | `bash lab/04-simulate.sh clean` |
| Docker Desktop on Windows says WSL 2 or virtualization is unavailable | Virtualization off in the BIOS, or a virtual machine without nested virtualization | Turn on virtualization, or use another laptop or an assigned station |
| `Git is not installed` on macOS | Command line tools missing | `xcode-select --install` |
| `Git repository with no commits` | You are in the organizer's master copy, or ran `git init` yourself | Copy the folder, or commit once and rerun step 01 |
| `check.py differs from the baseline` | The agent edited the checker | `git checkout lab-baseline -- exercises/check.py`; put new cases in a separate file |
| `synced folder` warning | Folder inside OneDrive, iCloud or Dropbox | Copy it somewhere local |
| `ROS domain N already has nodes` | Another station or run shares the domain | `LAB_DOMAIN_ID=<unused number 0–101> bash lab/03-replay.sh` |
| `earlier ... processes are still running` | A previous run did not exit | `bash lab/04-simulate.sh clean` |
| `simulator did not start` | Leftover processes, shared domain, slow machine | Read the printed log tail; `clean`; set `LAB_LAUNCH_TIMEOUT=240` |
| `CONDA_PREFIX is set` | Conda Python shadows the ROS Python | `conda deactivate` and open a fresh terminal |

## Settings

| Variable | Default | Use |
|---|---|---|
| `LAB_DOMAIN_ID` | 77 for step 03, 78 for step 04 | ROS domain; give each station its own when they share a network |
| `LAB_ROS_DISTRO` | `jazzy` | ROS 2 distribution under `/opt/ros` |
| `LAB_ROS_WS` | `~/ros_ws` | Built workspace containing `agentic_workshop` (see `scripts/boat-build.sh`) |
| `LAB_LAUNCH_TIMEOUT` | 120 | Seconds to wait for the simulator to come up |
| `LAB_GPU` | unset | `1` lends step 04 `watch` the Linux graphics device (`/dev/dri`) instead of software rendering; needs OpenGL 3.3, so not on a Raspberry Pi |
| `LAB_VIEW_WAIT` | 30 | Step 04 `watch` without a terminal: seconds to let the windows open before the scenarios start (with a terminal it waits for Enter) |
| `LAB_STATION` | automatic | `docker` or `native` to choose how steps 03 and 04 run; automatic uses native ROS 2 when installed, otherwise Docker |
| `LAB_IMAGE` | `ghcr.io/atr-lab/agentic-workshop-station:2026.11` | Station image for the Docker route |
| `NO_COLOR` | unset | Set to turn off coloured output |

The scripts need only Bash and Python 3.9+ (standard library), plus Docker or a ROS 2 station for steps 03 and 04. `lab/lab.py` holds all the logic; the `.sh` files only find Python and call it. `bash lab/04-simulate.sh watch` adds the Gazebo client (`lab/gazebo/gui.config`) and RViz (`lab/rviz/capstone.rviz`) on your screen through X11; see the [command sheet](../docs/lab-commands.md#watching-the-simulation-step-04-watch). `lab/docker/Dockerfile` builds the station image with the same packages and ROBOTIS revision as `scripts/boat-setup.sh`.
