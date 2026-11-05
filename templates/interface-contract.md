# Interface contract

Fill this from the selected environment before implementation. Write `unknown` where inspection is pending.

- Outcome and observable success condition:
- Execution mode: replay / simulation / physical trial:
- OS, ROS distribution, language/runtime, workspace revision:
- Sensor model, driver source and pinned commit, transport:
- Resolved input topics, message types, publisher/subscriber QoS:
- Frame IDs, required transforms, units, timestamp source, replay clock:
- Relevant field schema, valid-data rules, missing/stale-data behavior:
- Sector/height limits, thresholds, minimum sample count, age bound:
- Clearance metric and reference origin/envelope (diagnostic default: planar norm in the agreed working frame):
- For motion: robot footprint/front extent, corridor width, geometry transform, and stopping margin:
- Output topics and semantics:
- Actuation interface and bounds, if included:
- Stop control, timeout, command ownership, shutdown behavior:
- Acceptance cases and expected outputs:
- Commands needed to reproduce:
