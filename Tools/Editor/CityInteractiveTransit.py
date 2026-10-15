"""Persistent train shuttles and a player rowboat, instead of immobile display meshes."""

ROWBOAT = (129440, -137000, -120)


def rowboat_dock(layout):
    layout.box("DistrictTimber", (128620, -137000, -10), (1360, 600, 50))
    layout.box("DistrictSteel", (128620, -137000, -70), (1320, 560, 30))
    for x in (128150, 128900):
        for y in (-137250, -136750):
            layout.box("DistrictTimber", (x, y, -810), (25, 25, 1580))


def furnish():
    from CityScene import mesh_asset, spawn
    import unreal

    result = []
    boat = spawn(unreal.load_class(None, "/Script/ANANTA.CityRowboat"), "Living_PlayerRowboat", ROWBOAT, 90)
    boat.body_mesh.set_static_mesh(mesh_asset("Rowboat"))
    # Actor authored o ben cu phai con song khi nguoi choi cheo ra khoi cell do.
    boat.set_editor_property("is_spatially_loaded", False)
    boat.set_editor_property("enable_auto_lod_generation", False)
    result.append(boat)
    for sign, name in ((1, "East"), (-1, "West")):
        actor = spawn(unreal.load_class(None, "/Script/ANANTA.CityRailShuttle"), f"Living_Rail{name}",
                      (-66000 - sign * 2000, 198000 + sign * 500, 51), 0 if sign > 0 else 180)
        actor.set_editor_property("direction_sign", sign)
        actor.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh_asset("PassengerTrain"))
        actor.set_editor_property("is_spatially_loaded", True)
        actor.set_editor_property("enable_auto_lod_generation", False)
        result.append(actor)
    return result
