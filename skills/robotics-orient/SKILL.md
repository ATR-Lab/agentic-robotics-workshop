---
name: robotics-orient
description: Scope a workshop robotics change by inspecting the ROS environment and writing a testable interface contract before implementation.
---

Use this for the workshop's orientation and task-scoping stage. Read the target workspace's instructions and the participant's requested outcome. Inspect existing code before proposing new architecture.

Establish the selected ROS distribution, language, build/test entry points, workspace revision, sensor or simulator, and available recorded data. On a running system, inspect topic types and endpoints with `ros2 topic list -t`, `ros2 topic info --verbose <topic>`, and `ros2 interface show <type>`. Those commands are examples to adapt to the installed CLI. Do not invent live output if ROS is unavailable.

Capture the contract using [the template](../../templates/interface-contract.md). Resolve units, frames/transforms, clock source, validity, QoS compatibility, and failure behavior before implementing consumers. Distinguish the cloud-processing exercise from the TurtleBot command path. Read [WORKSHOP.md](../../WORKSHOP.md) for their relationship.

Ask for a missing decision only when it blocks meaningful work; otherwise make an explicit bounded assumption and record it. Choose acceptance cases that would expose a plausible integration error. Prefer an existing fixture/replay path before creating a new test harness.

Deliver a short data-flow description, the smallest useful implementation task, acceptance checks, and remaining environment unknowns. Keep this stage read-only apart from requested notes. A workshop-planning request does not authorize connecting to or moving a robot.
