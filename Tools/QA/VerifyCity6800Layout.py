"""Streaming source audit for the 6.8 km layout; no Unreal or visual acceptance."""

from collections import Counter
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Editor"))
import CityExpansionData as dimensions
import CityExpansionLayout as city
import CityCoastalDistrict as coast
import CityMetroDistrict as metro
from CityAssetOrientation import imported_yaw
from CityCivicDistrict import generate as civic
from CityExpansionLandscape import perimeter


def overlaps(a, b):
    return all(a[0][axis] < b[1][axis] - 0.001 and a[1][axis] > b[0][axis] + 0.001
               for axis in range(len(a[0])))


def catalogues():
    result = {"Cube": dict(min=[-50] * 3, max=[50] * 3)}
    for path in (ROOT / "Assets/City").glob("*manifest.json"):
        for mesh in json.loads(path.read_text(encoding="utf-8")).get("meshes", []):
            result[mesh["id"]] = mesh["boundsCm"]
    return result


class AuditLayout(city.Layout):
    def __init__(self):
        super().__init__()
        self.catalogue = catalogues()
        self.counts = Counter()
        self.errors = []
        self.lanes = metro.access_lanes()
        self.support = {lane["id"]: [] for lane in self.lanes}
        self.boundaries = []
        self.water = []
        self.rails = []
        self.platforms = []
        self.phase = ""

    def add(self, mesh, location, scale=(1, 1, 1), yaw=0, material=None, collision=True, hidden=False):
        self.counts[mesh] += 1
        # Nha nen chi can footprint; khong giu hang trieu instance trong RAM cua audit.
        if self.building_centre:
            return
        bounds = self.catalogue.get(mesh)
        if bounds is None:
            assert mesh in {"FireEngine", "PassengerTrain", "Helicopter", "CivilianPlane", "Rowboat"}, mesh
            return
        angle = math.radians(imported_yaw(mesh, yaw))
        corners = []
        for xx in (bounds["min"][0] * scale[0], bounds["max"][0] * scale[0]):
            for yy in (bounds["min"][1] * scale[1], bounds["max"][1] * scale[1]):
                yy *= -1 if mesh != "Cube" else 1
                corners.append((location[0] + xx * math.cos(angle) - yy * math.sin(angle),
                                location[1] + xx * math.sin(angle) + yy * math.cos(angle)))
        low = tuple(min(point[i] for point in corners) for i in range(2))
        high = tuple(max(point[i] for point in corners) for i in range(2))
        low += (location[2] + bounds["min"][2] * scale[2],)
        high += (location[2] + bounds["max"][2] * scale[2],)
        if material in ("Ground", "Asphalt"):
            for left, bottom, right, top in coast.ocean_rectangles():
                if overlaps((low[:2], high[:2]), ((left, bottom), (right, top))):
                    self.errors.append(f"{material} closes sea: {location}")
        if hidden and max(scale) * 100 > dimensions.WORLD_EXTENT * 1.9:
            self.boundaries.append((low, high))
        if material == "DistrictWater" and location[2] < 0:
            assert not collision and high[2] == coast.WATER_LEVEL
            self.water.append((low, high))
        if self.phase == "metro" and mesh == "Cube":
            if tuple(scale) == (81, 0.08, 0.14):
                self.rails.append((low, high))
            if tuple(scale) == (80, 9.4, 0.8):
                self.platforms.append((low, high))
            assert any(low[0] >= left - 0.01 and high[0] <= right + 0.01
                       and low[1] >= bottom - 0.01 and high[1] <= top + 0.01
                       for left, bottom, right, top in metro.RESERVES + coast.RESERVES), (material, low, high)
        if not collision:
            return
        for lane in self.lanes:
            if overlaps((low, high), (lane["min"], lane["max"])):
                self.errors.append(f"Blocked {lane['id']} entrance: {mesh} {material} {location}")
            if mesh == "Cube" and -0.1 <= high[2] <= 20.01:
                if overlaps((low[:2], high[:2]), (lane["min"][:2], lane["max"][:2])):
                    self.support[lane["id"]].append((low, high))


def check_access(layout):
    for lane in layout.lanes:
        assert lane["widthCm"] >= 220
        low, high = lane["min"], lane["max"]
        for x in (low[0] + 1, (low[0] + high[0]) / 2, high[0] - 1):
            for y in range(int(low[1]) + 1, int(high[1]), 50):
                assert any(a[0] <= x <= b[0] and a[1] <= y <= b[1]
                           for a, b in layout.support[lane["id"]]), (lane["id"], "floor gap", x, y)


def check_dimensions_and_ocean(layout):
    assert dimensions.GRID_EXTENT == 336000 and dimensions.BLOCK == 12000
    assert dimensions.GRID_BLOCKS == 56 and dimensions.SEED == 81026
    assert math.isclose(dimensions.WORLD_EXTENT, 240000 * math.sqrt(2))
    assert math.isclose(dimensions.WORLD_EXTENT / (120000 * math.sqrt(2)), 2)
    assert len(layout.boundaries) == 4
    edge = dimensions.WORLD_EXTENT
    for axis in (0, 1):
        assert any(math.isclose(low[axis], edge) for low, _ in layout.boundaries)
        assert any(math.isclose(high[axis], -edge) for _, high in layout.boundaries)
    assert len(layout.water) == 3
    # Truc dong va nam deu co nuoc qua bien choi; luong tau cu thong ra dai duong.
    for x, y in ((170000, -130000), (edge + 10000, -130000), (130000, -edge - 10000),
                 (131000, -134000), (167999, -130000), (168001, -130000)):
        assert any(low[0] <= x <= high[0] and low[1] <= y <= high[1] for low, high in layout.water)
    assert coast.DOCK_Y == -141000 and coast.QUAY_Y == -146000
    assert tuple(dock[1] for dock in coast.DOCKS) == (131000, 135200, 139400)
    assert tuple(venue["centre"] for venue in dimensions.VENUES) == (
        (-38150, 2700), (-9750, 2550), (-21750, -2800), (14200, 2550), (38200, 2500), (62200, 2500))
    for facility in metro.FACILITIES:
        left, bottom, right, top = facility["bounds"]
        assert -edge <= left < right <= edge and -edge <= bottom < top <= edge
        assert bottom > 170000 and facility["entryWidthCm"] >= 220
    assert len(layout.rails) == 4 and len(layout.platforms) == 2


def check_buildings(layout):
    for building in layout.buildings:
        x, y = building["centre"]
        width, depth = building["width"], building["depth"]
        assert not building["interior"]
        assert not dimensions.coastal_cutout(x, y)
        assert not dimensions.overlaps_reserved(x, y, width, depth)
        assert min(abs(x - road) for road in dimensions.ROAD_LINES) >= width / 2 + 1350
        assert min(abs(y - road) for road in dimensions.ROAD_LINES) >= depth / 2 + 1350
    assert len(layout.buildings) > 7000
    assert len({building["style"] for building in layout.buildings}) == 7
    schema = city.Layout()
    schema.collider((200000, 200000, 50), (100, 100, 100))
    data = schema.export()
    assert data["schemaVersion"] == 2 and data["units"] == "cm"
    assert data["groups"][0]["hidden"] and data["groups"][0]["collision"]


def main():
    layout = AuditLayout()
    for name, generate in (("streets", city.streets), ("buildings", city.city_blocks),
                           ("perimeter", perimeter), ("civic", civic), ("coast", coast.generate),
                           ("metro", metro.generate)):
        layout.phase = name
        generate(layout)
    check_access(layout)
    check_dimensions_and_ocean(layout)
    check_buildings(layout)
    report = dict(status="PASS" if not layout.errors else "FAIL", errors=layout.errors,
                  widthMetres=dimensions.WORLD_EXTENT * 2 / 100, previousWidthRatio=2, previousAreaRatio=4,
                  buildings=len(layout.buildings), instances=sum(layout.counts.values()),
                  facilityIds=[item["id"] for item in metro.FACILITIES], hiddenBoundaries=len(layout.boundaries),
                  oceanSurfaces=len(layout.water), accessLanes=len(layout.lanes),
                  pendingAssetMeshes=sorted(set(layout.counts) - set(layout.catalogue)),
                  inEngineVerified=False, visualAccepted=False, gameplayFacilities=False)
    output = ROOT / "Saved/QA/City6800SourceAudit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    assert not layout.errors, layout.errors[:10]


if __name__ == "__main__":
    main()
