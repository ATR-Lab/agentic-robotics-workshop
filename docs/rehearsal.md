# Rehearsal

Practice the talk, its live demos and the lab on your own machines before the event. Everything here runs on a laptop and a simulated ROS 2 station; no physical sensor or robot is involved.

## Set up once

**Laptop copy.** Never practice in the master copy; step 01 refuses to run there. Make a fresh copy instead:

```bash
bash scripts/practice-copy.sh
```

It copies the folder without Git history, deliverables or old results to `$TMPDIR/agentic-workshop-practice` (or to a folder you name) and prints the next commands. Running it again renames the previous copy with a timestamp and makes a new one, so earlier practice work is kept.

**Docker station (lab steps 03–04).** OrbStack's Docker engine already runs here. Pull the image once; the lab scripts use it automatically:

```bash
docker pull ghcr.io/atr-lab/agentic-workshop-station:2026.11
```

**ROS 2 station (the talk's live demos).** The demos use four terminals on one machine, so they need a full station. Any fresh Ubuntu 24.04 machine works. On a Mac with OrbStack, run these from the workshop folder:

```bash
orb create -a arm64 -u user --isolated --mount "$PWD:/mnt/workshop-src" ubuntu:noble atr-ros-station
```

```bash
orb -m atr-ros-station -u user bash -c 'mkdir -p ~/workshop && tar -C /mnt/workshop-src --exclude=./.git --exclude=./deliverables --exclude=./runs -cf - . | tar -C ~/workshop -xf -'
```

```bash
orb -m atr-ros-station -u user bash ~/workshop/scripts/boat-setup.sh
```

```bash
orb -m atr-ros-station -u user bash ~/workshop/scripts/boat-build.sh
```

The user name `user` makes the `/home/user/...` paths in the presenter notes work unchanged. `--isolated` keeps the station from seeing anything on the Mac except the workshop folder. Setup takes about 10 minutes and about 4 GB. To use a Boat VM instead, follow [working demos](working-demos.md). After editing the workshop folder on the Mac, repeat the copy command so the station has the change.

**Station shell.** Open a terminal on the station, already sourced, on one ROS domain:

```bash
orb -m atr-ros-station -u user bash -c 'source /opt/ros/jazzy/setup.bash && source ~/ros_ws/install/setup.bash && export ROS_DOMAIN_ID=77 && cd ~/workshop && exec bash -i'
```

Change `77` to `78` for the simulator terminals.

## Talk run-through (1–2 p.m.)

Open the deck in presenter view: in Keynote, Play › Rehearse Slideshow shows the notes and a timer; in PowerPoint, use Rehearse Timings and answer **No** when it offers to keep the timings, or the slides will advance on their own. Each slide's notes start with its minute range and the line to say.

Be on these slides by these times:

| Clock | Slide | Topic |
|---|---|---|
| 1:03 | 3 | ROS 2 in three minutes |
| 1:14 | 8 | Reproduce before editing (laptop demo starts) |
| 1:20 | 10 | Explain the result back (replay has finished) |
| 1:22 | 12 | Parallel work needs an interface |
| 1:30 | 16 | Make the simulated path observable (capstone check starts) |
| 1:38 | 19 | Leave an understood, repeatable change |
| 1:40 | 20 | Choose your next bounded task |
| 1:45 | 21 | Questions; leave it up until the lab starts at 2:00 |

Open four terminals before slide 1 and pre-type each command:

| Terminal | Opened with | Slide | Command |
|---|---|---|---|
| A, laptop | `bash scripts/practice-copy.sh`, then in the copy `git init -q && git add -A && git commit -qm baseline` | 8–10 | `python3 -I exercises/check.py`, then your agent |
| B, station, domain 77 | Station shell | 3 | `ros2 interface show sensor_msgs/msg/PointCloud2` |
| B | | end of 9 | `ros2 run agentic_workshop replay_demo --output /home/user/runs/replay-$(date +%H%M%S)` |
| C, station, domain 78 | Station shell with `78` | 11, after replay exits | `ros2 launch agentic_workshop capstone.launch.py` |
| D, station, domain 78 | Station shell with `78` | start of 16 | `ros2 run agentic_workshop capstone_check --output /home/user/runs/capstone-$(date +%H%M%S)` |

The `$(date +%H%M%S)` suffix gives every run the fresh output folder it needs. Don't call `/workshop/start` by hand: the checker needs the first start. After the talk, press Ctrl-C in terminal C; if anything is still running, `bash lab/04-simulate.sh clean` in any station terminal stops it.

Practice each fallback once so you know where it is: a slow agent on slide 9 (`diff exercises/clearance.py solutions/clearance.py` is the prepared diff), a failed replay (`evidence/2026-11-03/replay-report.json`) and a failed simulation (`evidence/2026-11-03/capstone-report.json`, then slide 18).

## Lab dry run (2–3 p.m.)

Do the lab as an attendee, with a timer started at 2:00, then compare with the clock in the [facilitator guide](facilitator-guide.md):

1. In a fresh laptop copy: `bash lab/00-check.sh`, then `bash lab/01-reproduce.sh` (10/12 expected).
2. Fix `exercises/clearance.py` with your agent, as an attendee would; don't copy the solution. Rerun `bash lab/02-repair.sh` after each edit until 12/12, then answer its three explain-back prompts.
3. In the same laptop copy, `bash lab/03-replay.sh` and `bash lab/04-simulate.sh`: with Docker running and the station image loaded, they run in a container, as on an attendee's laptop. To practise the station route instead, run them in a station shell after `cd ~/workshop`.
4. Back on the laptop: `bash lab/05-handoff.sh`, and fill in the bracketed lines.

## Failure drills

Each one takes a minute or two and shows what an attendee sees and how you fix it:

| Drill | Do | Expect |
|---|---|---|
| Edited checker | In a laptop copy after step 01, add a line to `exercises/check.py`, then `bash lab/02-repair.sh` | FAIL `check.py differs from the baseline`; restore with `git checkout lab-baseline -- exercises/check.py` |
| Master copy | `bash lab/01-reproduce.sh doctor` in the master folder | FAIL `Git repository with no commits`, with the copy instructions |
| Stuck simulator | In a domain-78 station shell, start `ros2 launch agentic_workshop capstone.launch.py &`, wait 10 s, then `bash lab/04-simulate.sh doctor` | FAIL `earlier replay or simulator processes are still running`; `bash lab/04-simulate.sh clean` clears it and the doctor passes |
| Ctrl-C mid-run | Press Ctrl-C while `bash lab/04-simulate.sh` is starting or running | It stops the world itself; the doctor then reports no leftovers |

## Measured on this setup

Nov. 4, 2026: OrbStack 2.1.3, Ubuntu 24.04 arm64 machine on an Apple Silicon Mac. The lab scripts gave replay 9/9 in 25 s and simulation 10/10 in 38 s, with nothing left running. The talk's demo commands gave `replay_demo` 9/9 in 20 s, the world ready 6 s after launch and `capstone_check` 10/10 in 27 s. All four failure drills behaved as described; Ctrl-C at 3, 5, 8 and 15 s left nothing running. The deck opened in Keynote 15.4 with all 25 slides, the notes and the background videos, and its PDF export matched the reference PDF; the videos weren't watched in Keynote's playback. Not tested: PowerPoint, Windows, and the interactive station shell command (its non-interactive form was).
