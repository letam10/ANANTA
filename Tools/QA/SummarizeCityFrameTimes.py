"""Summarize every recorded gameplay frame, retaining streaming and slow frames."""

import argparse
import csv
import json
import math
from pathlib import Path
import statistics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    with (args.directory / "FrameTimes.csv").open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    assert rows, "No recorded frames"
    wall = [float(row["wall_ms"]) for row in rows]
    assert all(math.isfinite(value) and value > 0 for value in wall), "Invalid frame duration"
    ordered = sorted(wall)
    mean = statistics.mean(wall)
    result = dict(frames=len(rows), observedSeconds=sum(wall) / 1000,
                  averageFps=1000 / mean, meanWallMs=mean,
                  p95WallMs=ordered[math.ceil(len(ordered) * .95) - 1], maxWallMs=max(wall),
                  framesOver33Ms=sum(value > 33.3 for value in wall),
                  framesOver50Ms=sum(value > 50 for value in wall),
                  includesAllFrames=True, frameTargetMs=1000 / 90,
                  stable90Accepted=False)
    for name in ("game_ms", "render_ms", "rhi_ms", "gpu_ms"):
        result[name] = statistics.mean(float(row[name]) for row in rows)
    (args.directory / "Summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
