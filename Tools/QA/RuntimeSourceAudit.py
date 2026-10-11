"""Audit the native city contract and cooked asset references without opening UE."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "ANANTA"
errors = []
city_headers = list((SOURCE / "Public" / "City").glob("*.h"))
city_source = list((SOURCE / "Private" / "City").glob("*.cpp"))
test_source = list((SOURCE / "Private" / "Tests").glob("*.cpp"))
headers = "\n".join(path.read_text(encoding="utf-8-sig") for path in city_headers)
all_source = "\n".join(
    path.read_text(encoding="utf-8-sig")
    for path in SOURCE.rglob("*")
    if path.suffix in {".cpp", ".h"}
)

for name in (
    "AANANTACityGameMode",
    "AANANTACityVehicle",
    "AANANTACityInteractable",
    "AANANTACityEnemy",
    "AANANTACityCrowd",
    "UANANTACitySubsystem",
    "ECityMissionStage",
    "ECityInteractionKind",
):
    if name not in headers:
        errors.append(f"Missing runtime contract type: {name}")

for name in ("VehicleId", "BodyMesh", "InteractionId", "InteractionKind", "VisualMesh", "EnemyId"):
    pattern = rf"UPROPERTY\([^\n]*\)\s*[^;\n]*\b{re.escape(name)}\b"
    if not re.search(pattern, headers):
        errors.append(f"Missing reflected property: {name}")

for path in city_headers + city_source + test_source:
    if len(path.read_text(encoding="utf-8-sig").splitlines()) > 300:
        errors.append(f"File exceeds 300 lines: {path.relative_to(ROOT)}")

assets = sorted(set(re.findall(r'TEXT\("(/Game/[^"\s]+)"\)', all_source)))
for asset in assets:
    package = asset.split(".")[0]
    path = ROOT / "Content" / (package.removeprefix("/Game/") + ".uasset")
    if not path.is_file():
        errors.append(f"Missing hard referenced asset: {asset}")

controller = (SOURCE / "Private" / "City" / "ANANTACityController.cpp").read_text()
for key in ("W", "A", "S", "D", "E", "F", "F5", "SpaceBar", "LeftMouseButton", "Escape", "LeftShift"):
    if f"EKeys::{key}" not in controller:
        errors.append(f"Missing real input: {key}")

for name in (
    "ANANTA.City.Mission.InvalidOrderAndDuplicateIds",
    "ANANTA.City.Mission.RewardExactlyOnce",
    "ANANTA.City.Save.SerializationAndValidation",
):
    if name not in all_source:
        errors.append(f"Missing automation test registration: {name}")

print(json.dumps({
    "passed": not errors,
    "cityFiles": len(city_headers) + len(city_source),
    "automationFiles": len(test_source),
    "hardAssetReferences": assets,
    "errors": errors,
    "scope": "Static contract audit only. UE automation and real input acceptance are separate gates.",
}, indent=2))
raise SystemExit(1 if errors else 0)
