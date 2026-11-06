# Boat demo verification — November 3, 2026

Both demos were built and executed in a Boat default-size Ubuntu 24.04 x86-64 VM, using ROS 2 Jazzy and Python 3.12.3. TurtleBot3 Gazebo source was pinned to ROBOTIS revision `45633014a14e8f438495b532a723e4ad45cbbd31`. [Environment versions](../evidence/2026-11-03/environment.txt) and [node source hashes](../evidence/2026-11-03/source-sha256.txt) accompany the results.

## Results

| Surface | Observed result | Evidence |
|---|---|---|
| ROS package build | `agentic_workshop` and `turtlebot3_gazebo` built successfully | Reproduction instructions in the demo guide |
| Colcon/pytest | 6 tests collected, 6 passed, no failures or skipped tests | `contract-pytest.xml` in the evidence folder |
| ROS bag replay | 9/9 checks passed with strict phase-state checking | [Replay report](../evidence/2026-11-03/replay-report.json) and [events](../evidence/2026-11-03/replay-events.json) |
| Gazebo TurtleBot3 capstone | 10/10 scenario checks passed in a fresh world | [Capstone report](../evidence/2026-11-03/capstone-report.json) and [events](../evidence/2026-11-03/capstone-events.json) |
| Offline workshop reference | Original 12 contract checks passed | `python3 -I exercises/check.py --solution` |

The replay checks cover clear/blocked output, empty input, missing TF, organized big-endian row padding, stale and future acquisition times, the numerical effect of translation and post-replay reception timeout. The input is an authored synthetic ROS bag, not a physical UniLiDAR recording.

The capstone checks cover rejected speed settings, distance-bound advance, obstacle stop, latched stop requiring reset, dropped scans, invalid scans, unavailable scan transform, operator stop, time bound and controller-process suspension. The last scenario verifies that the separate command guard sends zero and observed odometry settles even while the suspended controller's last status still says advance.

On the final run the clear-path displacement was approximately 0.451 m for a 0.45 m command bound. The obstacle-stop position was approximately x=0.946 m against the obstacle's near face at x=1.35 m. These are simulator observations, not physical stopping specifications. An earlier fresh-world run also passed the initial eight scenarios: [first capstone report](../evidence/2026-11-03/capstone-first-report.json).

## Lab step scripts — November 4, 2026

The one-hour lab's scripts in `lab/` were run on a fresh station built the same way: the doctor caught a missing ROS install, an unbuilt workspace, leftover simulator processes, a domain used by another station and an invalid domain ID; `03-replay.sh` passed 9/9 and `04-simulate.sh` passed 10/10 with nothing left running, including after Ctrl-C at every phase. Details and reports: [evidence/2026-11-04-lab](../evidence/2026-11-04-lab/README.md). The laptop steps were also run on macOS with Python 3.9 and 3.14. Windows was not tested.

The same scripts and the talk's demo commands were then run on an Apple Silicon Mac, in an OrbStack Ubuntu 24.04 arm64 machine set up with the same two scripts (setup needed `git` added; the OrbStack image lacks it): replay 9/9, simulation 10/10, no leftovers after Ctrl-C at 3, 5, 8 and 15 s. Timings and the rehearsal setup: [rehearsal](rehearsal.md#measured-on-this-setup).

## Docker station — November 5, 2026

Steps 03 and 04 also run in a container built from `lab/docker/Dockerfile`, for laptops with Docker and no native ROS 2. Replay passed 9/9 and simulation 10/10 through Docker on macOS (arm64) and Ubuntu 26.04 (x86-64), with no container left after Ctrl-C. The laptop steps passed on Windows 11 ARM64. Docker Desktop on Windows was not tested: the Windows VM crashed at boot with nested virtualization on. After the package was made public, steps 00, 03 and 04 passed again from a fresh clone of the public repository on both hosts, with the image pulled without signing in. On November 6 the participant install script (`scripts/install.sh`) installed Docker Engine 29.9 with Buildx and Compose on fresh Ubuntu 24.04, Debian 13 and Fedora 43 machines, and steps 00 and 03 then passed on Ubuntu; its macOS Colima route and the Windows script's WSL part are untested. Step 04 `watch` (Gazebo client and RViz through X11) passed 10/10 through Docker on an Ubuntu 24.04 arm64 machine whose display was an Xvfb server with an access cookie; screenshots showed the robot moving in both windows at about 94% real time. On a slower arm64 Linux desktop, the first version's software-rendered windows slowed the simulator to about 45% of real time, and the controller correctly stopped with `sensing_or_tf` in the second scenario. Lending that machine's graphics chip (a Raspberry Pi's, OpenGL 3.1) left the Gazebo window black, so the graphics card is now opt-in (`LAB_GPU=1`). The windows render in software at low priority on one thread each, and the script measures the simulator's speed first; with the container pinned to two cores, `watch` then passed 10/10 at 98% of real time. It has not been tried on WSLg or XQuartz. Details: [evidence/2026-11-05-docker](../evidence/2026-11-05-docker/README.md).

## Findings incorporated into the implementation

- The verifier must subscribe to playback `/clock` with compatible best-effort QoS.
- Replay subprocesses need process-group cleanup; killing only a `ros2 run` wrapper can leave a child node publishing stale diagnostics.
- Boat Gazebo discovery required an explicit loopback `GZ_IP` and shared transport partition.
- Tests need pytest registration in `setup.py`; an initial colcon invocation collected no tests. The corrected run collected and passed all six.

## Operating limits

Run the two demos sequentially on a default-size VM. During a concurrent Gazebo startup/replay attempt, valid-data phases also produced unknown because reception/timing deadlines were missed. The strict verifier failed that run: [concurrent-load report](../evidence/2026-11-03/replay-concurrent-load-report.json). The freshness contract was preserved; the final isolated run passed. Do not loosen the contract or present that loaded run as a passing one.

The GUI has not been visually inspected; verification used a headless Gazebo server, ROS services/topics and odometry. No physical robot was operated and no actual UniLiDAR transport/capture was validated. A real sensor recording needs the selected driver's schema, frame, QoS and clock inspection before reuse.

## Reproduce

Follow [working demos](working-demos.md), using a fresh output directory for each replay and a fresh Gazebo world for the full capstone suite. Source both ROS and the built workspace in each VM shell. Use separate ROS domains for separate experiments, and keep all processes for one demo on the same domain. Keep setup/build logs and inspect process exit codes as well as report contents.
