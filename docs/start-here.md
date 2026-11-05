# Agentic workflows: workshop material v0.2

Prepared November 3, 2026. For programmers; prior ROS experience is optional.

**Outcome:** Take an unfamiliar data contract, use an agent to fix a small reproducible bug, explain the change yourself and carry the contract into a bounded robot application.

## Choose your route

| Route | Needs | Result |
|---|---|---|
| Offline core | Python 3.9+, terminal, chosen coding agent | Working sector reducer, checks and explain-back |
| ROS replay lab | Docker with the station image on any laptop, or a prepared Linux/ROS station; the authored synthetic bag (a real recording and matching Unitree driver only if supplied) | Topic contract and repeatable diagnostic replay |
| TurtleBot3 capstone | The same station image, or a prepared simulator with matching TurtleBot packages | Integrated application and scenario evidence |

All three routes now have executable material. The [Boat demo guide](working-demos.md) covers the ROS package, synthetic rosbag playback and headless Gazebo capstone. Read [verification](verification.md) for the tested configuration. A physical UniLiDAR capture and physical robot trial remain separate from these synthetic/simulated checks.

## Materials

- [Slide deck (PDF)](../deliverables/atr-slides-agentic-robotics-2026-11-04-animated.pdf): all 25 slides, including the optional lab slides and sources. The [slide manuscript](slides.md) holds the narration and demo cues.
- [Setup and readiness](setup.md): participant requirements and presenter release gates.
- [Slide manuscript](slides.md): all 25 slides with on-screen text, narration and demonstration cues.
- [Lab commands for each operating system](lab-commands.md): macOS, Linux and Windows commands for every step, and the common fixes.
- [Lab step scripts](../lab/README.md): one script per step of the one-hour lab, each with a `doctor` check and a troubleshooting table.
- [Rehearsal](rehearsal.md): practice the talk, its live demos and the lab on your own machines, with a local ROS 2 station.
- [Facilitator guide](facilitator-guide.md): one-hour run of show (2–3 p.m.), hints and recovery paths.
- [Participant workbook](participant-workbook.md): tasks, commands and completion checks.
- [Prompt cards](prompt-cards.md): reusable prompts for either client.
- [Answer key](answer-key.md): expected results and assessment rubric; open after attempting the exercise.
- [Original talk outline](talk-outline.md) and [implementation contract](../WORKSHOP.md).

## Five-minute smoke check

From the repo root, `bash lab/00-check.sh` checks the machine for every lab step. Then:

```bash
python3 -I exercises/check.py --solution
python3 -I exercises/check.py
```

The solution should pass. The starter deliberately fails the side-wall and behind-sensor cases. Ask the agent to fix `exercises/clearance.py`, keeping the supplied checks unchanged. These are authored XYZ fixtures, not recorded UniLiDAR messages or simulator evidence.

Use the same task contract with Codex or Claude Code. Select the repo's relevant skill, or explicitly ask the client to read its `SKILL.md`. No API key or model-specific prompt is needed for the offline exercise beyond the participant's own agent access.
