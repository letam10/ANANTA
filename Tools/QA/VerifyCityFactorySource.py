"""Measure the real factory source; no Unreal, actor, collision or visual acceptance."""

import hashlib
import inspect
import itertools
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
import CityMetroDistrict as metro
from CityAssetOrientation import imported_yaw

POST_HEIGHT_CM = (80, 140)
EPSILON = 0.001


class RecordingLayout:
    def __init__(self):
        self.items = []
        self.meshes = {}
        for path in sorted((ROOT / "Assets/City").glob("*manifest.json")):
            for mesh in json.loads(path.read_text(encoding="utf-8")).get("meshes", []):
                self.meshes[mesh["id"]] = (mesh["boundsCm"], str(path.relative_to(ROOT)))

    def box(self, material, location, size, collision=True):
        self.add("Cube", location, tuple(value / 100 for value in size), material=material,
                 collision=collision)

    def add(self, mesh, location, scale=(1, 1, 1), yaw=0, material=None, collision=True, hidden=False):
        caller = inspect.currentframe().f_back
        if caller.f_code.co_name == "box":
            caller = caller.f_back
        origin = dict(function=caller.f_code.co_name, line=caller.f_lineno)
        del caller
        if mesh == "Cube":
            bounds = dict(min=(-50, -50, -50), max=(50, 50, 50))
            manifest = "Unreal Engine BasicShapes/Cube: centred 100 cm cube"
        else:
            bounds, manifest = self.meshes[mesh]
        angle = math.radians(imported_yaw(mesh, yaw))
        corners = []
        # FBX doi dau Y; giu dung quy uoc cua bo kiem tra district hien co.
        for corner in itertools.product(*zip(bounds["min"], bounds["max"])):
            x, y, z = (corner[i] * scale[i] for i in range(3))
            if mesh != "Cube":
                y = -y
            corners.append((location[0] + x * math.cos(angle) - y * math.sin(angle),
                            location[1] + x * math.sin(angle) + y * math.cos(angle), location[2] + z))
        minimum = [round(min(c[i] for c in corners), 6) for i in range(3)]
        maximum = [round(max(c[i] for c in corners), 6) for i in range(3)]
        self.items.append(dict(index=len(self.items), mesh=mesh, material=material, locationCm=list(location),
                               sizeCm=[round(maximum[i] - minimum[i], 6) for i in range(3)],
                               min=minimum, max=maximum, collision=collision, hidden=hidden,
                               source=origin, boundsSource=manifest))


def overlaps(a, b):
    return all(a["min"][i] < b["max"][i] - EPSILON and b["min"][i] < a["max"][i] - EPSILON
               for i in range(3))


def within_x(item, shell):
    return item["min"][0] >= shell["min"][0] - EPSILON and item["max"][0] <= shell["max"][0] + EPSILON


def within_reserve(item, reserve):
    return all(item["min"][i] >= reserve[i] - EPSILON
               and item["max"][i] <= reserve[i + 2] + EPSILON for i in range(2))


def shutter_clearances(shutter, shell, apron):
    return dict(mountingGapCm=round(shell["min"][1] - shutter["max"][1], 6),
                apronGapCm=round(shutter["min"][2] - apron["max"][2], 6))


def shutter_mounted(shutter, shell):
    return abs(shell["min"][1] - shutter["max"][1]) <= EPSILON


def shutter_meets_apron(shutter, apron):
    return abs(shutter["min"][2] - apron["max"][2]) <= EPSILON


def post_height_accepted(post):
    return POST_HEIGHT_CM[0] <= post["max"][2] - post["min"][2] <= POST_HEIGHT_CM[1]


def audit_factory():
    name, x, y, height, material = next(site for site in metro.SITES if site[0] == "Factory")
    layout = RecordingLayout()
    metro.factory(layout, x, y, height, material)
    items = layout.items
    shell = next(item for item in items if item["source"]["function"] == "shell"
                 and item["material"] == material and item["locationCm"][:2] == [x, y])
    loading = [item for item in items if item["source"]["function"] == "factory"
               and item["max"][1] < y and item["min"][1] < shell["min"][1]]
    apron = next(item for item in loading if item["material"] == "DistrictPaving")
    steel = [item for item in loading if item["material"] == "DistrictSteel"]
    posts = [item for item in steel if item["max"][1] < apron["min"][1]
             and abs(item["sizeCm"][0] - item["sizeCm"][1]) <= EPSILON]
    shutters = [item for item in steel if item["sizeCm"][2] > item["sizeCm"][0]
                and item["sizeCm"][0] > 4 * item["sizeCm"][1]]
    planters = [item for item in items if item["mesh"] == "DetailedPlanter"]
    reserve = next(facility["bounds"] for facility in metro.FACILITIES if facility["id"] == name)
    lane = next(entry for entry in metro.access_lanes() if entry["id"] == name)
    issues = []
    checks = {}

    def record(key, passed, **evidence):
        checks[key] = dict(passed=passed, **evidence)
        if not passed:
            issues.append(dict(kind=key, **evidence))

    record("feature-inventory", len(posts) == 4 and len(shutters) == 2,
           bollardCount=len(posts), shutterCount=len(shutters))
    outside = [item for item in items if not within_reserve(item, reserve)]
    record("reserve-containment", not outside, outside=outside)
    collisions = [item for item in items if item["collision"] and overlaps(item, lane)]
    visible = [item for item in items if not item["hidden"] and overlaps(item, lane)]
    record("public-access-lane", not collisions and not visible,
           collisionCandidates=collisions, visibleCandidates=visible)
    overhangs = [dict(instance=item, leftOverhangCm=max(0, shell["min"][0] - item["min"][0]),
                     rightOverhangCm=max(0, item["max"][0] - shell["max"][0]))
                for item in loading if not within_x(item, shell)]
    record("loading-outside-shell-width", not overhangs, shell=shell, overhangs=overhangs)
    gaps = [dict(instance=item, **shutter_clearances(item, shell, apron)) for item in shutters]
    record("shutter-mounting-gap", all(shutter_mounted(item, shell) for item in shutters), shutters=gaps)
    record("shutter-apron-gap", all(shutter_meets_apron(item, apron) for item in shutters),
           apron=apron, shutters=gaps)
    record("bollard-human-scale", all(post_height_accepted(item) for item in posts),
           targetHeightCm=POST_HEIGHT_CM, bollards=posts)
    intersections = [dict(planter=planter, loading=item) for planter in planters for item in loading
                     if not item["hidden"] and overlaps(planter, item)]
    distances = [dict(planterIndex=planter["index"], bollardIndex=post["index"],
                      axisSeparationCm=[round(max(0, planter["min"][i] - post["max"][i],
                                                post["min"][i] - planter["max"][i]), 6) for i in range(3)])
                 for planter in planters for post in posts]
    record("planter-loading-aabb", not intersections, intersections=intersections,
           planterBounds=planters, bollardSeparations=distances)
    source = Path(metro.__file__)
    return dict(passed=not issues, issues=issues, instanceCount=len(items),
                sourceFile=str(source.relative_to(ROOT)), sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                reserveCm=reserve, accessLaneCm=lane, geometryChecks=checks, units="cm",
                scope="Source AABBs only; imported collision, rendering and player acceptance remain unverified",
                runtimeAccepted=False)


def main():
    result = audit_factory()
    path = ROOT / "Saved/QA/CityFactorySourceAudit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(passed=result["passed"], instanceCount=result["instanceCount"],
                          issues=[issue["kind"] for issue in result["issues"]])))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
