"""Deliberately buggy starter for authored, already-transformed XYZ fixtures; no ROS or actuation."""
import math


def clearance(points, *, now=1.0, stamp=1.0, transform_ok=True):
    """Return (state, planar_distance_or_None, accepted_count).

    Workbook constants: meters, x forward; +/-30 degrees; z 0.05..0.50 m;
    at least one point; <=.50 blocked; same-clock age 0..0.25 seconds.
    All bounds are inclusive. This is a diagnostic, not a collision monitor.
    """
    if not transform_ok:
        return 'unknown', None, 0
    if not all(math.isfinite(t) for t in (now, stamp)):
        return 'unknown', None, 0
    if not 0 <= now - stamp <= 0.25:
        return 'unknown', None, 0
    distances = []
    for point in points:
        try:
            x, y, z = map(float, point)
        except (TypeError, ValueError):
            return 'unknown', None, 0
        if not all(math.isfinite(v) for v in (x, y, z)):
            continue
        if not 0.05 <= z <= 0.50:
            continue
        # Exercise: this reducer currently considers every horizontal direction.
        distances.append(math.hypot(x, y))
    if not distances:
        return 'unknown', None, 0
    distance = min(distances)
    return ('blocked' if distance <= 0.50 else 'clear'), distance, len(distances)
