"""Approved civic dressing additions; existing bar fixtures retain their owners.

Call generate once after civic rooms, replacing the six procedural arcade
stand-ins in CityCivicDistrict.room_details. Existing living props remain in
CityLivingDetails; the bar specification approves no additional instances.
"""


def generate(layout):
    """Place six colliding cabinets in the layout's shared HISM mesh group."""
    from CityCivicDistrict import FLOOR_Z, SITES

    for name, x, y, _, _ in SITES:
        if name != "Arcade":
            continue
        for offset in (2550, 3300, 4050):
            for side in (-1, 1):
                # Hai hang quay vao phong, giu trong lan vao va loi den ban dich vu.
                layout.add("ArcadeCabinet", (x + offset, y + side * 1250, FLOOR_Z),
                           yaw=-90 * side, collision=True)


def furnish():
    """No extra visual actors are approved by the current placement budget.

    CityLivingDetails.furnish retains the bar's lamp and other authored props.
    Any future visual-only additions here must use the Living_CivicDressing_
    label prefix and CityScene helpers with collision disabled.
    """
    return []
