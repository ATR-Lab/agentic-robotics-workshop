"""Contract checks. Run from any directory; no external packages required."""
import argparse
import importlib.util
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solution', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    folder = 'solutions' if args.solution else 'exercises'
    path = root / folder / 'clearance.py'
    spec = importlib.util.spec_from_file_location('workshop_clearance', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Independently specified expectations from the workbook's teaching contract.
    cases = [
        ('side wall', [(0, .20, .20), (1, 0, .20)], {}, ('clear', 1.0, 1)),
        ('front obstacle', [(.25, 0, .20)], {}, ('blocked', .25, 1)),
        ('behind sensor', [(-.10, 0, .20), (1, 0, .20)], {}, ('clear', 1.0, 1)),
        ('threshold equality', [(.50, 0, .20)], {}, ('blocked', .50, 1)),
        ('ground only', [(.10, 0, 0)], {}, ('unknown', None, 0)),
        ('empty', [], {}, ('unknown', None, 0)),
        ('stale', [(.25, 0, .20)], {'now': 1.3}, ('unknown', None, 0)),
        ('future stamp', [(1, 0, .20)], {'stamp': 1.1}, ('unknown', None, 0)),
        ('missing transform', [(1, 0, .20)], {'transform_ok': False}, ('unknown', None, 0)),
        ('invalid point', [(float('nan'), 0, .20)], {}, ('unknown', None, 0)),
        ('age equality', [(1, 0, .20)], {'now': 1.25}, ('clear', 1.0, 1)),
        ('height equality', [(1, 0, .05), (2, 0, .50)], {}, ('clear', 1.0, 2)),
    ]
    failed = 0
    for name, points, kwargs, expected in cases:
        actual = module.clearance(points, **kwargs)
        distance_ok = (actual[1] is None if expected[1] is None else
                       actual[1] is not None and math.isclose(actual[1], expected[1]))
        ok = actual[0] == expected[0] and distance_ok and actual[2] == expected[2]
        failed += not ok
        print(f'{"PASS" if ok else "FAIL"} {name}: expected={expected}; observed={actual}')
    print(f'{len(cases)-failed}/{len(cases)} passed ({folder})')
    return int(failed > 0)


if __name__ == '__main__':
    raise SystemExit(main())
