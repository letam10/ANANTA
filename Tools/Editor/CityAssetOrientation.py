"""Architectural kit facing after Blender FBX to Unreal handedness conversion."""


def imported_yaw(mesh, yaw):
    # FBX doi dau truc Y: mat truoc -Y cua nguon thanh +Y trong Unreal.
    if mesh.startswith("Facade") or mesh in ("Storefront", "Balcony", "Cornice", "CafeEntry", "ApartmentEntry"):
        return yaw + 180
    return yaw
