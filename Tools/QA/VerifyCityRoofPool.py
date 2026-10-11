"""Reject hidden tread height jumps and gaps using actual generated collision boxes."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
from CityRoofPool import generate
from VerifyCityDistricts import Layout, catalogues


def height(layout, x, y):
    surfaces = [item["max"][2] for item in layout.items if item["collision"] and item["mesh"] == "Cube"
                and item["min"][0] <= x <= item["max"][0] and item["min"][1] <= y <= item["max"][1]]
    assert surfaces, ("Unsupported floor", x, y)
    return max(surfaces)


def main():
    layout = Layout(*catalogues())
    generate(layout, 102000, 198000)
    failures = []
    treads = []
    for index in range(41):
        y = 195800 + index * 100
        actual = height(layout, 98350, y)
        expected = 40 + index * 20
        treads.append(dict(index=index, actualZ=actual, expectedZ=expected))
        if abs(actual - expected) > .01:
            failures.append(dict(index=index, actualZ=actual, expectedZ=expected))
    for y in (199800, 199900, 200000):
        for x in range(98350, 98851, 50):
            actual = height(layout, x, y)
            if abs(actual - 840) > .01:
                failures.append(dict(landing=[x, y], actualZ=actual, expectedZ=840))
    result = dict(passed=not failures, scope="Source collision tread and roof support, not player runtime",
                  treads=treads, failures=failures, runtimeAccepted=False)
    path = ROOT / "Saved/QA/CityRoofPoolSource.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(passed=result["passed"], treads=len(treads), failures=failures)))
    assert not failures, failures


if __name__ == "__main__":
    main()
