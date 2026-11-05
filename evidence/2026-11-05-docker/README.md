# Docker station tests — November 5, 2026

Lab steps 03 and 04 now run in a container built from `lab/docker/Dockerfile` when a computer has Docker and no native ROS 2. The image was built separately on each host from the same Dockerfile: arm64 on macOS, amd64 on Ubuntu. Hosts, image IDs and package versions: [environment](environment.txt). The input is the authored synthetic bag and a headless Gazebo simulation; no physical sensor or robot was used.

| Host | Route | Test | Result |
|---|---|---|---|
| macOS 27.2, Apple M3 Max, OrbStack Docker 29.4 | Docker | `00-check.sh`, including the doctor inside the container | No FAIL |
| macOS | Docker | `03-replay.sh`, `04-simulate.sh` in a fresh practice copy | 9/9 in 28 s; 10/10 in 42 s ([replay](replay-report-macos-arm64.json), [simulation](capstone-report-macos-arm64.json)) |
| macOS | Docker | Ctrl-C through a terminal at 6, 10 and 20 s; SIGINT without a terminal at 3, 4, 5, 6, 8 and 20 s | Exit 130, no container left in any case |
| Ubuntu 26.04 x86-64, Docker Engine 29.9 | Docker | Steps 00–05 in a fresh copy (02 with the reference solution) | 10/12 then 12/12; 9/9 in 26 s; 10/10 in 34 s ([replay](replay-report-ubuntu-amd64.json), [simulation](capstone-report-ubuntu-amd64.json)); handoff listed all four |
| Ubuntu | Docker | Ctrl-C through a terminal at 8, 10 and 20 s; SIGINT at 15 s | Clean stop, no container left |
| Ubuntu | Docker | A container named `atr-lab-04` left running, then `doctor`, `clean`, `doctor` | FAIL naming the container; removed; PASS |
| Ubuntu | Docker | Results written through the bind mount | Owned by the host user (uid 1000) |
| OrbStack Ubuntu 24.04 arm64 machine | Native | `03-replay.sh`, `04-simulate.sh` with the final `lab.py` | 9/9; 10/10 |
| Windows 11 ARM64 (Parallels), Git Bash and `py -3` from Command Prompt | Laptop steps | 00, 01, 02, 05; 03 and 04 doctor without Docker | 10/12 then 12/12; report drafted; FAIL naming Docker as the fix |

## Bugs found and fixed

- **A non-ASCII character in an attendee's edit crashed step 02 on Windows.** `lab.py` read files and command output in the Windows code page; a `ρ` in a comment raised `UnicodeDecodeError`. It now reads and writes UTF-8 and replaces any character the terminal cannot show.
- **Container output appeared only at the end when not on a terminal**, and was lost on interrupt; the container's Python is now unbuffered and the host flushes its lines first.
- **Result folders were stamped in UTC** inside the container; the host's UTC offset is now passed in.
- **The OrbStack Ubuntu image has no Git**, so `scripts/boat-setup.sh` now installs it (found on November 4).

## Not tested

- Docker Desktop on Windows. Turning on nested virtualization for this Windows 11 ARM64 VM (Parallels Desktop 27.1, macOS 27.2) made it crash at boot (`PANIC ... UEFI-exception-bootmgfw`), so it was turned off again. The Docker route on Windows needs a Windows PC with hardware virtualization.
- Docker Desktop on macOS (the Mac used OrbStack's engine), rootless Docker, a Linux host user whose uid is not 1000, the permission-denied fix and SELinux hosts.
