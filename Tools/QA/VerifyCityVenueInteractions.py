"""Source gate for authored venue service interactions; no Unreal runtime required."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
EDITOR = ROOT / "Tools" / "Editor"
sys.path.insert(0, str(EDITOR))
from CityExpansionData import VENUES
from CityCivicDistrict import SERVICES, SITES

ALLOWED_KINDS = {"Read", "Heal", "Supplies", "Rest"}
REQUIRED_KEYS = {
    "id", "centre", "size", "face", "title",
    "service", "serviceId", "description",
}


def main():
    errors = []
    venue_ids = [venue.get("id") for venue in VENUES]
    service_ids = [venue.get("serviceId") for venue in VENUES]
    if len(venue_ids) != len(set(venue_ids)):
        errors.append("Expansion venue ids are not unique")
    if len(service_ids) != len(set(service_ids)):
        errors.append("Expansion service ids are not unique")
    for venue in VENUES:
        missing = sorted(REQUIRED_KEYS - set(venue))
        if missing:
            errors.append(f"{venue.get('id', '<missing>')}: missing keys {missing}")
        if venue.get("service") not in ALLOWED_KINDS:
            errors.append(f"{venue.get('id')}: unsupported service kind {venue.get('service')}")
        if not venue.get("title") or not venue.get("description"):
            errors.append(f"{venue.get('id')}: service copy is incomplete")

    expansion_text = (EDITOR / "CityExpansionVenues.py").read_text(encoding="utf-8")
    civic_text = (EDITOR / "CityCivicDistrict.py").read_text(encoding="utf-8")
    apply_text = (EDITOR / "ApplyCityExpansion.py").read_text(encoding="utf-8")
    if "CityServiceInteractable" not in expansion_text:
        errors.append("Expansion venue service actor is missing")
    if 'service(item["serviceId"]' not in expansion_text:
        errors.append("Expansion venues do not dispatch their service ids")
    if "CityServiceInteractable" not in civic_text:
        errors.append("Civic service actor is missing")
    if "actor.set_editor_property(\"service_kind\"" not in civic_text:
        errors.append("Civic service kind is not assigned")
    for call in ("furnish()", "furnish_civic()", "furnish_transit()"):
        if call not in apply_text:
            errors.append(f"ApplyCityExpansion is missing {call}")
    civic_ids = [name for name, _, _, _, _ in SITES if name != "AmusementPark"]
    civic_service_ids = [name for name, _ in SERVICES]
    if set(civic_ids) != set(civic_service_ids):
        errors.append("Civic service list does not cover civic rooms")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "sourceOnly": True,
        "runtimeVerified": False,
        "expansionVenueCount": len(VENUES),
        "expansionServiceIds": service_ids,
        "civicVenueCount": len(civic_service_ids),
        "allowedServiceKinds": sorted(ALLOWED_KINDS),
        "errors": errors,
    }
    output = ROOT / "Saved" / "QA" / "CityVenueInteractionSourceAudit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
