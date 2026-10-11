"""Compare all frames from isolated packaged graphics trials of the same artifact."""

import argparse
import json
from pathlib import Path

from CityGraphicsTrialData import TRIAL_CVARS, load_run, require


def compare_runs(baseline: Path, candidates: list[Path]) -> dict:
    base = load_run(baseline)
    require(base["qualityTrial"] == "Base", "Baseline must be Base")
    require(candidates, "At least one candidate is required")
    results = []
    seen = {"Base"}
    for path in candidates:
        run = load_run(path)
        name = run["qualityTrial"]
        require(name not in seen, "Candidates must be unique non-Base trials")
        seen.add(name)
        require(run["fingerprint"] == base["fingerprint"], "Packaged artifact mismatch")
        expected = dict(base["renderConfig"])
        changed = TRIAL_CVARS[("GI32", "Reflections4", "VsmBias0").index(name)]
        expected[changed] = run["renderConfig"][changed]
        require(run["renderConfig"] == expected, "Uncontrolled observed render state difference")
        delta = {key: run["statistics"][key] - base["statistics"][key]
                 for key in ("averageFps", "gpu_ms", "render_ms", "p95WallMs")}
        results.append(dict(qualityTrial=name, directory=run["directory"],
                            statistics=run["statistics"], deltaFromBase=delta))
    return dict(schemaVersion=1, baseline=base, candidates=results, includesAllFrames=True,
                visualAccepted=False, stable90Accepted=False,
                limitation="Requires matched visual review; these short gameplay runs do not prove stable 90 FPS.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidates", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare_runs(args.baseline, args.candidates)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
