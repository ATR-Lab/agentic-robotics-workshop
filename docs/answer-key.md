# Facilitator answer key

Open after attempting the exercise. `solutions/clearance.py` is a reference reducer, not a ROS driver or motion controller.

## Reducer diagnosis

The starter filters validity/height but reduces across all horizontal directions. The requested diagnostic needs a forward-angle filter before reduction. A side point can therefore dominate the current result even when the forward sector is clear. Changing the threshold would change the contract without fixing the angular selection.

The reference accepts finite XYZ points within the height band and ±30-degree sector, then takes planar `hypot(x,y)`. It requires a minimum accepted count, a valid transform and a same-clock age within bounds. Equality at 0.50 m is blocked. Missing usable points produces unknown, not clear.

The checker covers 12 cases: near side wall, true front obstacle, a behind-sensor point, threshold equality, ground rejection, empty input, stale input, future stamp, transform failure, NaN rejection, age equality and height equality. The starter should fail exactly the side-wall and behind-sensor cases. Both implementations retain conservative behavior for missing evidence. Add cases for angular boundaries and malformed coordinates when discussing further coverage.

## Metadata card

Width × point_step equals row_step for the given one-row cloud. That is internal consistency, not proof the bytes exist or decode correctly. The padding and intensity offset make an XYZ-only packed-array assumption unjustified. One point is finite and one is invalid. If stamps share a clock, age is 0.5 seconds, which exceeds the offline 0.25-second limit. With a different clock, subtraction is not meaningful until the clock contract is established.

The frame name does not prove mounting or robot-forward direction. Inspect the transform. The card has no real capture provenance and establishes no coverage of a physical corridor. Under the supplied age rule the output is unknown, even though one finite point is close.

## Capstone review guide

Require deterministic state transitions and explicit restart/reset semantics. Freshness must be evaluated on a periodic tick. Sensor-origin distance differs from collision-envelope clearance. Observe odometry/base response separately from commanded velocity. Test the base timeout independently, because a killed process may never execute shutdown logic. Unknown sensor state must not mean a clear corridor.

The reference integration is now implemented in ros2/agentic_workshop and exercised in Boat. Use [the demo guide](working-demos.md) and [verification report](verification.md). Participants can implement their own version against the same contract; simulator results do not establish physical-robot behavior.

## Assessment

Score each area 0 (absent), 1 (partial) or 2 (demonstrated):

| Area | Evidence for 2 points |
|---|---|
| Contract | Explicit metric/frame/time/invalid-data behavior |
| Reproduction | Original failing input and command recorded |
| Focused change | Fix addresses the contract without weakening the checker |
| Understanding | Participant traces a point and predicts an unseen case |
| Verification | Targeted results with provenance and honest limits |
| Handoff | Another person can reproduce the work and identify next task |

Use the score for feedback, not a claim of robotics certification. A participant can demonstrate the workflow offline; separately record whether replay or simulation was completed.
