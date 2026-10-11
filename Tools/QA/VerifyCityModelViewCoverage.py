"""Source-only model, dressing, and eight-view/five-angle quality gate."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = ROOT / "Assets" / "City"
EDITOR_ROOT = ROOT / "Tools" / "Editor"

MODEL_VIEWS = (
    "front", "rear", "left", "right",
    "front_left", "front_right", "rear_left", "rear_right",
)
PLACEMENT_VIEWS = (
    "road_approach", "side_approach", "rear_approach",
    "elevated_view", "interior_close",
)
MANIFEST_FAMILIES = {
    "manifest.json": "architecture_shells",
    "expansion_manifest.json": "public_dressing",
    "ferris_manifest.json": "landmarks",
    "finishing_manifest.json": "interior_furniture",
    "interior_architecture_manifest.json": "interior_architecture",
    "living_manifest.json": "interior_equipment",
    "metro_manifest.json": "transport_vehicles",
    "mobility_manifest.json": "transport_vehicles",
    "small_manifest.json": "small_props",
    "venue_fixture_manifest.json": "venue_fixtures",
    "workshop_detail_manifest.json": "venue_fixtures",
}
FAMILY_DESCRIPTIONS = {
    "architecture_shells": "facades, entries, cornices, balconies, roof details",
    "public_dressing": "trees, shelters, stalls, signs, bins, racks",
    "landmarks": "Ferris wheel, civic monument, playground structures",
    "transport_vehicles": "road, rail, air, and water vehicles",
    "interior_furniture": "house furniture, tables, seating, rugs, curtains",
    "interior_architecture": "service desks, slat panels, art and botanical frames",
    "interior_equipment": "living equipment and room details",
    "small_props": "small kitchen, room, bathroom, and play props",
    "venue_fixtures": "clinic, transit, and workshop fixture meshes",
}
REQUIRED_FAMILIES = tuple(FAMILY_DESCRIPTIONS)
PUBLIC_PROP_IDS = {
    "StreetLamp", "Bench", "Bollard", "Planter", "BusShelter", "MarketStall",
    "TrashBin", "BikeRack", "StreetSign", "DetailedPlanter", "DetailedStreetLamp",
    "TrafficSignal", "RoadBarrier", "HarborBollard", "BusStopSign",
}
VEHICLE_IDS = {
    "CarBody", "FireEngine", "PassengerTrain", "Helicopter", "CivilianPlane",
    "Rowboat", "Coach", "CityBus", "Taxi", "BoxTruck", "CargoTruck",
    "TankerTruck", "PoliceCar", "Ambulance", "CargoShip", "Motorboat",
    "Sailboat",
}
LANDMARK_IDS = {"FerrisWheel", "CivicMonument", "PlaygroundSlide", "PlaygroundSwing"}
VENUE_REQUIREMENTS = {
    "Cafe": {"seating": ("House_",), "surface": ("CafeTable", "House_modern_coffee_table_01")},
    "Apartment": {"dining": ("House_dining_chair_02", "CafeTable")},
    "Bookshop": {"books": ("House_book_encyclopedia_set_01",), "reading": ("House_",)},
    "Clinic": {"medical_storage": ("ClinicSupplyCabinet",)},
    "Market": {"stock": ("House_brass_pot_01",), "checkout": ("CafeCounter",)},
    "ToyShop": {"toys": ("ToyBlocks",), "checkout": ("CafeCounter",)},
    "Gallery": {"display": ("InteriorGalleryFrame",)},
    "Workshop": {"tools": ("WorkshopToolBoard",), "parts": ("WorkshopPartsCrate",)},
    "Transit": {"route": ("TransitRouteDisplay",)},
    "Library": {"books": ("House_book_encyclopedia_set_01",)},
    "Restaurant": {"menu_or_dining": ("House_", "InteriorWovenRug")},
    "Cinema": {"lobby_or_posters": ("Cube", "House_")},
    "Hotel": {"room_detail": ("House_", "Cube")},
}


def classify_mesh(mesh_id, manifest_name):
    if mesh_id in VEHICLE_IDS:
        return "transport_vehicles"
    if mesh_id in LANDMARK_IDS:
        return "landmarks"
    if mesh_id in PUBLIC_PROP_IDS:
        return "public_dressing"
    if mesh_id in {"ClinicSupplyCabinet", "TransitRouteDisplay",
                   "WorkshopToolBoard", "WorkshopPartsCrate"}:
        return "venue_fixtures"
    if mesh_id.startswith("Interior"):
        return "interior_architecture"
    if mesh_id.startswith("House_") or mesh_id in {
            "CafeCounter", "CafeTable", "ApartmentBed",
            "InteriorWovenRug", "InteriorLinenCurtain"}:
        return "interior_furniture"
    if manifest_name == "small_manifest.json":
        return "small_props"
    if manifest_name == "living_manifest.json":
        return "interior_equipment"
    if mesh_id.startswith("Facade") or mesh_id in {
            "Storefront", "CafeEntry", "ApartmentEntry", "Cornice",
            "Balcony", "RoofEquipment"}:
        return "architecture_shells"
    if manifest_name == "expansion_manifest.json":
        return "public_dressing"
    return None


def load_models(errors):
    records = []
    seen = set()
    manifest_names = set()
    for path in sorted(ASSET_ROOT.glob("*manifest.json")):
        name = path.name
        manifest_names.add(name)
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected = MANIFEST_FAMILIES.get(name)
        if expected is None:
            errors.append(f"Unlisted manifest {name}")
        for key, expected_value in (
                ("schemaVersion", 1), ("units", "cm"),
                ("forwardAxis", "X"), ("upAxis", "Z")):
            if payload.get(key) != expected_value:
                errors.append(f"{name}: {key} must be {expected_value!r}")
        for source in payload.get("sourceFiles", []):
            source_path = ASSET_ROOT / source["file"]
            if not source_path.is_file():
                errors.append(f"{name}: missing source file {source['file']}")
        for mesh in payload.get("meshes", []):
            mesh_id = mesh.get("id")
            if not mesh_id:
                errors.append(f"{name}: mesh without id")
                continue
            if mesh_id in seen:
                errors.append(f"Duplicate mesh id {mesh_id}")
                continue
            seen.add(mesh_id)
            mesh_path = ASSET_ROOT / mesh.get("file", "")
            if not mesh_path.is_file():
                errors.append(f"{mesh_id}: missing source mesh {mesh.get('file')}")
            if mesh.get("triangles", 0) <= 0:
                errors.append(f"{mesh_id}: triangles must be positive")
            if not mesh.get("materialSlots"):
                errors.append(f"{mesh_id}: materialSlots is empty")
            family = classify_mesh(mesh_id, name)
            if family is None:
                errors.append(f"{mesh_id}: no model family")
            records.append({
                "id": mesh_id,
                "manifest": name,
                "family": family,
                "file": mesh.get("file"),
            })
    expected_names = set(MANIFEST_FAMILIES)
    errors.extend(f"Missing manifest {name}"
                 for name in sorted(expected_names - manifest_names))
    return records


def import_dressing(errors):
    sys.path.insert(0, str(EDITOR_ROOT))
    try:
        from CityVenueDressing import ROOMS, describe
        items = describe()
        repeat = describe()
    except Exception as exc:
        errors.append(f"CityVenueDressing source import failed: {exc}")
        return (), ()
    if items != repeat:
        errors.append("CityVenueDressing.describe() is not deterministic")
    labels = [item.get("label") for item in items]
    if len(labels) != len(set(labels)):
        errors.append("Dressing labels are not unique")
    for item in items:
        if not str(item.get("label", "")).startswith("Dressing_"):
            errors.append(f"Invalid dressing label {item.get('label')}")
    return ROOMS, items


def has_mesh(meshes, prefixes):
    return any(any(mesh == token or mesh.startswith(token) for token in prefixes)
               for mesh in meshes)


def check_venues(rooms, items, errors):
    room_counts = Counter()
    room_meshes = {}
    for item in items:
        parts = str(item.get("label", "")).split("_", 2)
        if len(parts) < 2:
            continue
        room_counts[parts[1]] += 1
        room_meshes.setdefault(parts[1], []).append(item.get("mesh"))
    expected_rooms = [room["id"] for room in rooms]
    if set(room_counts) != set(expected_rooms):
        errors.append("Venue set differs from CityVenueDressing.ROOMS")
    # Gioi han theo so phong de giu noi that thua khi them venue moi.
    sparse_limit = max(250, len(expected_rooms) * 21)
    if len(items) > sparse_limit:
        errors.append(f"Interior additions exceed sparse limit {sparse_limit} ({len(items)})")
    non_collision = sum(not item.get("collision", True) for item in items)
    if items and non_collision / len(items) < 0.35:
        errors.append("Interior dressing is too collision-heavy for sparse rooms")
    for room in expected_rooms:
        count = room_counts[room]
        if count < 10 or count > 40:
            errors.append(f"{room}: dressing count {count} outside 10..40")
        meshes = room_meshes.get(room, [])
        if meshes.count("InteriorServiceDesk") != 1:
            errors.append(f"{room}: requires exactly one service desk")
        for category, prefixes in VENUE_REQUIREMENTS.get(room, {}).items():
            if not has_mesh(meshes, prefixes):
                errors.append(f"{room}: missing {category} review category")
    return room_counts, room_meshes, sparse_limit

def main():
    errors = []
    records = load_models(errors)
    rooms, items = import_dressing(errors)
    room_counts, room_meshes, sparse_limit = check_venues(rooms, items, errors)

    family_counts = Counter(record["family"] for record in records)
    for family in REQUIRED_FAMILIES:
        if family_counts[family] == 0:
            errors.append(f"Required model family is empty: {family}")

    reuse_counts = Counter(item.get("mesh") for item in items)
    reusable = {mesh: count for mesh, count in reuse_counts.items() if count > 1}
    scene_source = EDITOR_ROOT / "CityScene.py"
    scene_text = scene_source.read_text(encoding="utf-8")
    if "HierarchicalInstancedStaticMeshComponent" not in scene_text:
        errors.append("CityScene.py has no HISM instance path")
    if "add_instances" not in scene_text:
        errors.append("CityScene.py has no bulk instance insertion")
    if len(reusable) < 5:
        errors.append("Fewer than five repeated prop meshes are available for reuse")

    model_metadata = {
        "count_per_model": len(MODEL_VIEWS),
        "views": list(MODEL_VIEWS),
        "unique": len(set(MODEL_VIEWS)) == 8,
    }
    placement_metadata = {
        "count_per_model": len(PLACEMENT_VIEWS),
        "views": list(PLACEMENT_VIEWS),
        "unique": len(set(PLACEMENT_VIEWS)) == 5,
        "interior_close": "when relevant to the asset or venue",
    }
    if model_metadata["count_per_model"] != 8 or not model_metadata["unique"]:
        errors.append("Model review metadata must contain eight unique views")
    if placement_metadata["count_per_model"] != 5 or not placement_metadata["unique"]:
        errors.append("Placement review metadata must contain five unique angles")

    checks = {
        "source_manifests": not any("manifest" in error.lower() for error in errors),
        "model_families": all(family_counts[family] > 0 for family in REQUIRED_FAMILIES),
        "model_views": model_metadata["count_per_model"] == 8 and model_metadata["unique"],
        "placement_views": (
            placement_metadata["count_per_model"] == 5
            and placement_metadata["unique"]
        ),
        "venue_categories": bool(rooms) and set(room_counts) == {room["id"] for room in rooms},
        "sparse_interiors": len(items) <= sparse_limit and (
            not items or sum(not item.get("collision", True) for item in items) / len(items) >= 0.35
        ),
        "instance_reuse_source": len(reusable) >= 5 and "add_instances" in scene_text,
    }
    report = {
        "status": "PASS" if not errors else "FAIL",
        "sourceOnly": True,
        "visualAcceptance": "UNVERIFIED",
        "modelCount": len(records),
        "manifestCount": len({record["manifest"] for record in records}),
        "modelFamilies": {
            family: {
                "description": FAMILY_DESCRIPTIONS[family],
                "models": family_counts[family],
            }
            for family in REQUIRED_FAMILIES
        },
        "modelReview": model_metadata,
        "placementReview": placement_metadata,
        "venues": {
            "count": len(rooms),
            "sparseInteriorLimit": sparse_limit,
            "dressingItems": len(items),
            "itemsByRoom": dict(sorted(room_counts.items())),
            "categories": {
                room: sorted(set(meshes))
                for room, meshes in sorted(room_meshes.items())
            },
        },
        "instanceReuse": {
            "repeatedMeshTypes": len(reusable),
            "reusableReferences": sum(count - 1 for count in reusable.values()),
            "topRepeatedMeshes": dict(
                sorted(reusable.items(), key=lambda pair: (-pair[1], pair[0]))[:12]
            ),
            "evidence": "Source HISM/add_instances path plus repeated mesh references",
        },
        "checks": checks,
        "errors": errors,
        "limitations": [
            "No Unreal editor, game, native capture, port probe, benchmark, or soak test was run.",
            "Eight model and five placement entries prove review coverage metadata only.",
            "Materials, silhouettes, collision, lighting, HLOD, Nanite, and persistence remain unverified visually.",
            "Instance reuse is a source candidate audit, not a renderer or draw-call measurement.",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

