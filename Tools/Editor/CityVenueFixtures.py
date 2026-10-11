"""Detailed clinic and transit fixtures using the combined bounds of their blockouts."""


REMOVED_LABELS = {
    f"Dressing_Clinic_Storage{kind}{index}" for kind in ("Door", "Handle") for index in range(3)
} | {
    f"Dressing_Transit_Route{kind}{index}" for kind in ("Line", "Stop") for index in range(4)
} | {"Dressing_Transit_RouteBoard"}


def apply_venue_fixtures(items):
    result = []
    for original in items:
        if original["label"] in REMOVED_LABELS:
            continue
        item = dict(original)
        x, y, _ = item["location"]
        if item["label"] == "Dressing_Clinic_MedicalStorage":
            item.update(mesh="ClinicSupplyCabinet", location=(x, y - 4.5, 15),
                        scale=(1, 1, 1), yaw=180)
            item.pop("material", None)
        elif item["label"] == "Dressing_Transit_RouteFrame":
            item.update(mesh="TransitRouteDisplay", location=(x, y - 7, 115),
                        scale=(1, 1, 1), yaw=180, collision=False)
            item.pop("material", None)
        result.append(item)
    return result
