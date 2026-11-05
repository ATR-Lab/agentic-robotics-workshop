# Hands-on lab: commands for each operating system

The lab runs 2–3 p.m. in six steps, one script each. This sheet gives the exact command for macOS, Linux and Windows, what you should see, and the fixes for the problems people hit most. The [workbook](participant-workbook.md) has the exercise itself; [lab/README.md](../lab/README.md) has every setting.

## Before the workshop (15 minutes, needs internet)

| | macOS | Linux | Windows |
|---|---|---|---|
| Python 3.9+ and Git | `xcode-select --install` (gives `python3` and `git`) | `sudo apt install python3 git` (or your distribution's packages) | `winget install -e --id Python.Python.3.13` and `winget install -e --id Git.Git`, then open a new terminal |
| Docker, for steps 03–04 | [Docker Desktop](https://docs.docker.com/desktop/) or [OrbStack](https://orbstack.dev) | [Docker Engine](https://docs.docker.com/engine/install/), then `sudo usermod -aG docker $USER` and log out and back in | [Docker Desktop](https://docs.docker.com/desktop/) with the WSL 2 backend; needs virtualization turned on |
| Coding agent | Codex or Claude Code, signed in | same | same |

Start Docker, give it at least 4 GB of memory (Docker Desktop: Settings › Resources) and keep about 6 GB of disk free. Then pull the station image, about 1.2 GB:

```bash
docker pull ghcr.io/atr-lab/agentic-workshop-station:2026.11
```

If the pull says `denied` or `unauthorized`, build the image from the workshop folder instead (about 10 minutes):

```bash
docker build -t ghcr.io/atr-lab/agentic-workshop-station:2026.11 -f lab/docker/Dockerfile .
```

**Put the workshop folder somewhere local**, such as your home folder: not OneDrive, iCloud Drive, Dropbox or Google Drive. Open a terminal in it:

- **macOS:** Terminal, then `cd ~/agentic-robotics-workshop` (or wherever you put it).
- **Linux:** any terminal, then `cd` into the folder.
- **Windows:** right-click the folder › **Open Git Bash here** (recommended). PowerShell or Command Prompt also work with the `py -3` commands below.

Then run step 00. If it shows no `FAIL` line, you are ready.

## The six steps

| Clock | Step | macOS, Linux, Windows Git Bash | Windows PowerShell or Command Prompt | You should see |
|---|---|---|---|---|
| 2:00 | 00 Check | `bash lab/00-check.sh` | `py -3 lab\lab.py 00` | No `FAIL` lines; a saved `runs/doctor-<time>.txt` |
| 2:05 | 01 Reproduce | `bash lab/01-reproduce.sh` | `py -3 lab\lab.py 01` | `10/12 passed`: the starter fails on purpose |
| 2:10 | 02 Repair (after each agent edit) | `bash lab/02-repair.sh` | `py -3 lab\lab.py 02` | Your diff, then `All 12 checks pass` when the fix is right |
| 2:30 | 03 Replay | `bash lab/03-replay.sh` | `py -3 lab\lab.py 03` | `replay: 9/9 checks pass` (about 30 s) |
| 2:38 | 04 Simulate | `bash lab/04-simulate.sh` | `py -3 lab\lab.py 04` | `simulation: 10/10 scenarios pass` (about 40 s) |
| 2:48 | 05 Hand off | `bash lab/05-handoff.sh` | `py -3 lab\lab.py 05` | A drafted `runs/05-handoff/run-report-<time>.md` |

Every step takes the same extra words, in both columns:

- `doctor`: check only and print what is wrong and how to fix it, for example `bash lab/03-replay.sh doctor` or `py -3 lab\lab.py 03 doctor`.
- `help`: what the step does.
- `clean` (steps 03 and 04): stop a leftover simulator or lab container.

Steps 03 and 04 start a fresh ROS 2 container on your laptop and remove it when they finish; Ctrl-C stops them cleanly. On a prepared Linux station with ROS 2 Jazzy installed they run directly instead, with no Docker.

**Changing a setting** for one run (here, a longer simulator start-up on a slow laptop):

| Shell | Command |
|---|---|
| macOS, Linux, Git Bash | `LAB_LAUNCH_TIMEOUT=240 bash lab/04-simulate.sh` |
| PowerShell | `$env:LAB_LAUNCH_TIMEOUT=240; py -3 lab\lab.py 04` |
| Command Prompt | `set LAB_LAUNCH_TIMEOUT=240 && py -3 lab\lab.py 04` |

## When something goes wrong

First, run the same step with `doctor` and follow its `Fix:` line. If that doesn't help, run step 00 and show its saved report to a facilitator.

| What you see | Usual cause | Fix |
|---|---|---|
| `No Python 3.9 or newer found`, or `python3` opens the Microsoft Store | Python missing; Windows' Store placeholder | Install Python (table above), open a new terminal; on Windows use `py -3` |
| `bash: lab/00-check.sh: No such file or directory` | Terminal is not in the workshop folder | `cd` into the folder that contains `lab/` |
| `.sh` will not run on Windows | No Bash | Use Git Bash, or the `py -3 lab\lab.py` column |
| `Git is not installed` on macOS | Command line tools missing | `xcode-select --install` |
| `Git has no user.email` (WARN) | Git identity not set | Optional: the lab commits as "Workshop participant" |
| `Git repository with no commits` | You are in the organizer's master copy | Copy the folder and work in the copy |
| `check.py differs from the baseline` | The agent edited the checker | `git checkout lab-baseline -- exercises/check.py`; put new cases in another file |
| `synced folder` warning | Folder inside OneDrive, iCloud, Dropbox or Google Drive | Move it to a local folder |
| `the docker command was not found` | Docker not installed | Install it (table above); or pair with a neighbour for steps 03–04 |
| `Docker is installed but its engine is not running` | Docker Desktop or OrbStack closed; Linux service stopped | Start it and wait until it says running; Linux: `sudo systemctl start docker` |
| `permission denied` from Docker (Linux) | Not in the `docker` group | `sudo usermod -aG docker $USER`, then log out and back in |
| `the station image ... is not on this computer` | Image not pulled | `docker pull ghcr.io/atr-lab/agentic-workshop-station:2026.11`, or the build command above |
| `Docker may use only N GB of memory` | Docker's memory limit is low | Raise it to 4 GB or more in Docker Desktop's Settings › Resources |
| `an earlier lab container is still running` | A run was killed from outside | `bash lab/04-simulate.sh clean` (or `py -3 lab\lab.py 04 clean`) |
| Docker Desktop on Windows: WSL 2 or virtualization unavailable | Virtualization off in the BIOS, or a virtual machine | Turn virtualization on; otherwise pair with a neighbour |
| `simulator did not start` | Slow laptop, too little memory | Read the printed log lines; `clean`; rerun with `LAB_LAUNCH_TIMEOUT=240` |
| Agent cannot sign in | No access or no network | Pair with a neighbour; steps 00–02 still work offline |

No physical sensor or robot is used in any step. Steps 03 and 04 run the packaged reference code on an authored synthetic bag and a simulated TurtleBot3, not your edited file.

## Tested so far

November 4–5, 2026: all six steps on macOS (Apple Silicon, Docker through OrbStack) and Ubuntu 26.04 (x86-64, Docker Engine); steps 00, 01, 02 and 05 on Windows 11 ARM64 with Git Bash and with `py -3`. Not yet tested: Docker Desktop on Windows and on macOS. Details: [verification](verification.md).
