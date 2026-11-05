---
name: unilidar-replay
description: Implement and verify the Unitree UniLiDAR workshop's diagnostic point-cloud exercise using an inspected ROS 2 driver contract and recorded-data replay.
---

Read [WORKSHOP.md](../../WORKSHOP.md) for the exercise and [the contract template](../../templates/interface-contract.md). Preserve the chosen sensor and driver; SDK1 versus SDK2, transport, topic remaps, and time configuration are environment decisions to inspect.

First identify the actual cloud publisher and PointCloud2 schema. Capture the frame, acquisition clock, fields/datatypes, byte order, dimensions/strides, and validity behavior; inspect any required transform. Do not treat this as a scalar range or a 2-D LaserScan. The separate IMU topic is not a point-cloud field. Check publisher/subscriber QoS and bag metadata before declaring a missing stream.

Implement the smallest node that reports minimum valid clearance in a specified forward sector and height band, plus `blocked`, `clear`, or `unknown`. The diagnostic default is planar norm `sqrt(x*x + y*y)` from the agreed working-frame origin after filtering. Record the metric and origin explicitly before choosing a threshold; agree on any alternative metric rather than silently substituting 3-D norm or longitudinal distance. Use a supported point reader and finite-value filtering; empty or stale data and unavailable transforms yield unknown. Keep the first exercise diagnostic-only, with no motor publisher.

Use an existing small bag if supplied. Otherwise prepare a synthetic fixture for the reducer and separately arrange a real recording; label their provenance. Do not fabricate a captured bag or silently substitute synthetic input for hardware evidence. Record/replay only requested topics with clock/QoS settings compatible with the inspected setup.

Check frontal obstacles, a nearer side wall, invalid points, empty input, stale input, and transform failure. A seeded all-around reducer should fail the agreed sector case; the corrected implementation should preserve true frontal-obstacle detection. Run the affected checks, replay the same data, inspect the diff, and have the participant explain a point's path to the output.

Deliver source changes, launch/configuration appropriate to the actual workspace, and [a run report](../../templates/run-report.md) with exact commands and results. If ROS or the bag is unavailable, finish the specification/fixture work possible and identify the unexecuted replay stage plainly.
