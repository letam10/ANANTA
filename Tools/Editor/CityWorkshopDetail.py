"""Replace workshop blockout pieces without moving routes or interactive objects."""


def apply_workshop_detail(items):
    result = []
    for original in items:
        label = original["label"]
        if label.startswith("Dressing_Workshop_ToolRail"):
            continue
        item = dict(original)
        if label == "Dressing_Workshop_ToolBoard":
            item.update(mesh="WorkshopToolBoard", location=(*item["location"][:2], 110),
                        scale=(1, 1, 1), yaw=180, collision=False)
            item.pop("material", None)
        elif label == "Dressing_Workshop_PartsCrate":
            item.update(mesh="WorkshopPartsCrate", location=(*item["location"][:2], 15),
                        scale=(1, 1, 1), yaw=180)
            item.pop("material", None)
        result.append(item)
    return result
