# Prompt cards

Use these after selecting the relevant repo skill. Substitute actual paths and commands. The same task content works in Codex or Claude Code; see [setup](setup.md) for invocation.

## Orient

> Read AGENTS.md and skills/robotics-orient/SKILL.md. Inspect this workspace without changing it. Identify the intended outcome, relevant files, environment and reproduction command. Separate observed settings from assumptions. Propose a small interface contract and acceptance checks for the workshop task.

## Reproduce and implement

> Read exercises/clearance.py and run python3 -I exercises/check.py. Explain the failing behavior against the workbook contract first. Then make the smallest useful fix in clearance.py. Preserve the supplied checker; add independent cases separately. Run the affected checks and report the diff, exact commands and remaining limits. Do not open the solution until I request it.

## Understand the PR

> Use skills/explain-robotics-pr/SKILL.md. Keep this pass read-only. I understand the inputs but not why the side wall affects the output. Trace that point and the front point through the old and new code with code references. Explain the units, frame, time and invalid-data assumptions. Give me a new input to predict, then check my reasoning against the code.

## Review

> Review the diff against the agreed contract and original checks. Look for reproducible failures at boundaries, stale/invalid data and frame assumptions. For each finding, provide an input, expected/observed behavior and code location. Distinguish checks you executed from conclusions inferred from reading.

## Integrate replay

> Use skills/unilidar-replay/SKILL.md with this supplied driver/workspace and bag. Inspect resolved topics, schema, QoS, TF and clock first. Implement a diagnostic adapter for the agreed reducer, with no motor publisher. Run the rehearsed replay and record provenance and outputs. If the runtime/data is missing, complete the adapter plan and state that replay was not executed.

## Implement the capstone

> Use skills/turtlebot-capstone/SKILL.md in the prepared simulation workspace. Follow the workbook's state and stopping contract. Inspect sensor, velocity and odometry interfaces; agree on numeric bounds before motion. Build the application, launch/configuration and scenario checks. Verify observed simulated response and report failures. This request covers simulation only.

## Hand off

> Write a run report with revision, environment, input provenance, exact reproduction commands, expected/observed results and failures. Separate fixtures, recorded replay, simulation and hardware evidence. State the next smallest useful task; do not describe planned checks as passed.
