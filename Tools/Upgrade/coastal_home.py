"""Four furnished rooms with measurable clearances and five editor review views each."""

import math

import unreal


def transformed_bounds(item, position, yaw, scale):
    angle = math.radians(yaw)
    cosine, sine = math.cos(angle), math.sin(angle)
    corners = []
    for horizontal in (item["bounds_min_m"][0], item["bounds_max_m"][0]):
        for depth in (item["bounds_min_m"][1], item["bounds_max_m"][1]):
            corners.append((position[0] + cosine * horizontal * scale[0] - sine * depth * scale[1],
                            position[1] + sine * horizontal * scale[0] + cosine * depth * scale[1]))
    return [min(point[0] for point in corners), max(point[0] for point in corners),
            min(point[1] for point in corners), max(point[1] for point in corners)]


def room_light(scene, name, position, lumens=3200, radius=650):
    light = scene.spawn(unreal.PointLight, name, position)
    component = light.point_light_component
    component.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    component.set_intensity(lumens)
    component.set_editor_property("attenuation_radius", radius)
    component.set_editor_property("source_radius", 18)
    component.set_editor_property("cast_shadows", False)
    component.set_editor_property("max_draw_distance", 7000)
    component.set_editor_property("max_distance_fade_range", 1500)
    component.set_light_color(unreal.LinearColor(1, 0.89, 0.74, 1))
    scene.box((position[0], position[1], position[2] + 0.31), (0.7, 0.7, 0.06),
              "White", collision=False)


def furnish_home(scene, data):
    center_x, center_y = data["center_m"]
    ground = data["ground_m"]
    zones = {
        "living": (-9.88, -1.4, -10.88, 0.7),
        "bedroom": (-9.88, -1.4, 1.1, 10.88),
        "kitchen": (1.4, 9.88, -10.88, 2.7),
        "bathroom": (1.4, 9.88, 3.1, 10.88),
    }
    furnishings = []

    def prop(name, horizontal, depth, zone, elevation=0, yaw=0, scale=(1, 1, 1), wall_mount=False):
        limits = zones[zone]
        if wall_mount:
            # Mép trong tường 11 - 0.11 m; lưng khung chừa đúng 1 cm.
            back_limit = data["depth_m"] / 2 - 0.11 - 0.01
            depth = back_limit - scene.model_data[name]["bounds_max_m"][1]
            limits = (*limits[:3], back_limit + 0.00001)
        bounds = transformed_bounds(scene.model_data[name], (horizontal, depth), yaw, scale)
        assert bounds[0] >= limits[0] and bounds[1] <= limits[1], (name, bounds, limits)
        assert bounds[2] >= limits[2] and bounds[3] <= limits[3], (name, bounds, limits)
        scene.model(name, (center_x + horizontal, center_y + depth, ground + elevation), yaw, scale)
        furnishings.append({"model": name, "room": zone, "bounds_xy_m": bounds,
                            "elevation_m": elevation})

    # Hành lang 2.4 m; bốn cửa phòng 1.2 m, chừa đủ capsule người chơi 0.68 m.
    for wall_x, upper_door in ((-1.2, 6), (1.2, 6)):
        intervals = ((-10.89, -6.1), (-4.9, upper_door - 0.6), (upper_door + 0.6, 10.89))
        for lower, upper in intervals:
            scene.box((center_x + wall_x, center_y + (lower + upper) / 2, ground + 1.6),
                      (0.12, upper - lower, 3.2), "Plaster")
        for door_y in (-5.5, upper_door):
            scene.box((center_x + wall_x, center_y + door_y, ground + 2.8),
                      (0.12, 1.2, 0.8), "Plaster")
    scene.box((center_x - 5.55, center_y + 0.9, ground + 1.6), (8.58, 0.12, 3.2), "Plaster")
    scene.box((center_x + 5.55, center_y + 2.9, ground + 1.6), (8.58, 0.12, 3.2), "Plaster")

    for zone, limits in zones.items():
        midpoint = ((limits[0] + limits[1]) / 2, (limits[2] + limits[3]) / 2)
        floor_color = "Sidewalk" if zone == "bathroom" else "Wood"
        scene.box((center_x + midpoint[0], center_y + midpoint[1], ground + 0.006),
                  (limits[1] - limits[0] + 0.25, limits[3] - limits[2] + 0.25, 0.012),
                  floor_color, collision=False)
        room_light(scene, data["name"] + "_" + zone + "_Light",
                   (center_x + midpoint[0], center_y + midpoint[1], ground + 2.8))
        # Cả năm camera nằm trong phòng tương ứng, không nhìn xuyên vách để lấy bằng chứng.
        positions = ((limits[0] + 0.6, limits[2] + 0.6), (limits[1] - 0.6, limits[2] + 0.6),
                     (limits[1] - 0.6, limits[3] - 0.6), (limits[0] + 0.6, limits[3] - 0.6),
                     (midpoint[0], limits[2] + 0.7))
        for index, position in enumerate(positions):
            scene.review_views.append({
                "name": f"{data['name']}_{zone}_{index}",
                "position_m": [center_x + position[0], center_y + position[1], ground + 1.65],
                "target_m": [center_x + midpoint[0], center_y + midpoint[1], ground + 0.9],
            })

    prop("Sofa", -6.4, -7.2, "living", yaw=180)
    prop("Table", -6.4, -4.7, "living", scale=(1, 1, 0.65))
    prop("Book", -6.5, -4.7, "living", elevation=0.77 * 0.65)
    prop("Mug", -6, -4.7, "living", elevation=0.77 * 0.65)
    prop("TVConsole", -6.4, -2.4, "living")
    prop("FloorLamp", -8.8, -7.2, "living")
    prop("Bookshelf", -9.3, -2.8, "living", yaw=90)
    scene.box((center_x - 6.4, center_y - 5.2, ground + 0.02), (3.8, 3.4, 0.018),
              "Teal", collision=False)

    prop("Bed", -8.45, 6, "bedroom")
    prop("TeddyToy", -8.2, 6.15, "bedroom", elevation=0.75, scale=(0.5, 0.5, 0.5))
    prop("SideTable", -8.9, 7.5, "bedroom")
    prop("Book", -8.9, 7.5, "bedroom", elevation=0.5575)
    prop("Table", -5.2, 9.2, "bedroom")
    prop("Chair", -5.2, 8.2, "bedroom", yaw=180)
    prop("Perfume", -4.9, 9.2, "bedroom", elevation=0.77)
    prop("Lipstick", -5.3, 9.2, "bedroom", elevation=0.77)
    prop("CoastalPicture", -5.3, 0, "bedroom", elevation=1.2, wall_mount=True)

    east_limit = data["width_m"] / 2 - 0.11 - 0.01
    counter_x = east_limit - scene.model_data["KitchenCounter"]["bounds_max_m"][1]
    stove_x = east_limit - scene.model_data["Stove"]["bounds_max_m"][1]
    fridge_x = east_limit - scene.model_data["Fridge"]["bounds_max_m"][1]
    for depth in (-8.8, -7.2, -5.6):
        prop("KitchenCounter", counter_x, depth, "kitchen", yaw=-90)
    prop("Kettle", counter_x, -7.2, "kitchen", elevation=0.885, yaw=-90)
    prop("ChoppingBoard", counter_x, -5.6, "kitchen", elevation=0.885, yaw=-90)
    prop("BottleTray", counter_x, -8.8, "kitchen", elevation=0.885, yaw=-90)
    prop("Stove", stove_x, -4.3, "kitchen", yaw=-90)
    prop("CookingPot", stove_x, -4.3, "kitchen", elevation=0.89)
    prop("Fridge", fridge_x, -3.1, "kitchen", yaw=-90)
    prop("Table", 5.3, -4, "kitchen")
    for side in (-1, 1):
        prop("Chair", 5.3, -4 + side * 0.95, "kitchen", yaw=0 if side > 0 else 180)
        prop("DinnerPlate", 5.3 + side * 0.36, -4, "kitchen", elevation=0.77)
        prop("Cutlery", 5.3 + side * 0.36, -3.72, "kitchen", elevation=0.77, yaw=90)

    prop("ShowerTray", 3.8, 0, "bathroom", wall_mount=True)
    prop("Toilet", 8, 0, "bathroom", wall_mount=True)
    prop("Washbasin", 6, 0, "bathroom", wall_mount=True)
    prop("SideTable", 7.2, 8.2, "bathroom")
    prop("TowelStack", 7.2, 8.2, "bathroom", elevation=0.5575)
    basin_y = data["depth_m"] / 2 - 0.12 - scene.model_data["Washbasin"]["bounds_max_m"][1]
    prop("SoapDispenser", 6.27, basin_y, "bathroom", elevation=0.845)
    prop("WallMirror", 6, 0, "bathroom", elevation=1.15, wall_mount=True)
    data["rooms"] = zones
    data["furnishings"] = furnishings
