# Lab step scripts on a ROS 2 station: November 4, 2026

The `lab/` scripts were run in a fresh Boat default-size VM (Ubuntu 24.04, x86-64, 4 vCPU, 8 GB), set up with `scripts/boat-setup.sh` and `scripts/boat-build.sh`. ROS 2 Jazzy packages and the ROBOTIS revision match the Nov. 3 run ([environment](environment.txt)). The input is the authored synthetic bag and a headless Gazebo simulation; no physical sensor or robot was used.

| Check | Observed |
|---|---|
| `00-check.sh` before ROS was installed | Step 03 doctor: FAIL, ROS 2 jazzy not installed, with the fix |
| `04-simulate.sh doctor` before the workspace was built | FAIL, workspace not built, fix names `scripts/boat-build.sh` |
| `00-check.sh` on the built station | No FAIL; steps 01, 03 and 04 doctors pass ([report](station-doctor.txt)) |
| `03-replay.sh` | 9/9 checks pass in about 25 s ([report](replay-report.json)) |
| `04-simulate.sh` | 10/10 scenarios pass in about 32 s including start-up and shutdown; no processes left ([report](capstone-report.json)) |
| A capstone launch left running, then `04-simulate.sh doctor` | FAIL listing the leftover processes; `clean` stopped them and the doctor then passed |
| A node from "another station" on domain 77 | FAIL naming `/other_station`; `LAB_DOMAIN_ID=87` passed |
| `LAB_DOMAIN_ID=abc` | FAIL with the allowed range |
| Ctrl-C at 4, 5, 6, 7, 9 and 12 s into `04-simulate.sh` (doctor, start-up and checker phases) | No simulator processes left each time; a full run afterwards passed 10/10 |
| Ctrl-C at 8 and 14 s into `03-replay.sh` | No replay processes left; a full run afterwards passed 9/9 |
| Steps 01, 02 and 05 on the station | 10/12 before the fix, 12/12 after; the drafted run report listed all four steps |
| Bytecode in the source tree after lab runs | None |

Bugs found and fixed during this run: the leftover-process check matched the shell that started the script (it now skips its own parent processes, and `clean` signals only the listed processes); `robot_state_publisher` survived `clean`; and Ctrl-C during simulator start-up could orphan the Gazebo server (cleanup now waits for the whole process group, escalating to SIGKILL). All checks above were rerun after the fixes.
