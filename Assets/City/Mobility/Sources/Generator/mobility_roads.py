"""Original road fleet: shaped cabins, open glazing, seats and functional trim."""
import math
from mobility_geometry import box, profile, panel, tire, arch, seat, end_lights, mirrors
from mobility_geometry import cylinder, beam, text_label, finish, uv


def sedan(kind):
    color = "yellow" if kind == "Taxi" else "white"
    body = profile("Stamped body", [(-2.3, .76, .40, .94), (-1.9, .88, .33, 1.03),
                                    (1.35, .88, .33, 1.04), (2.3, .79, .48, .90)], color, .07)
    arch(body, (-1.45, 1.43), .35, 1.8)
    uv(body, color)
    box("Passenger floor", (-.2, 0, .59), (2.7, 1.55, .10), mat="Mobility_Rubber")
    profile("Roof", [(-1.20, .69, 1.60, 1.68), (-.92, .71, 1.66, 1.73),
                     (.60, .67, 1.65, 1.73), (.82, .63, 1.59, 1.68)], color)
    panel("Front windshield", [(1.26, -.79, 1.04), (1.26, .79, 1.04),
                                 (.78, .63, 1.61), (.78, -.63, 1.61)], mat="Mobility_Glass")
    panel("Rear windshield", [(-1.74, .79, 1.04), (-1.74, -.79, 1.04),
                                (-1.17, -.68, 1.60), (-1.17, .68, 1.60)], mat="Mobility_Glass")
    for side in (-1, 1):
        y = side * .815
        panel("Side glazing", [(-1.67, y, 1.06), (1.21, y, 1.06),
                                (.73, side * .65, 1.62), (-1.15, side * .70, 1.62)],
              mat="Mobility_Glass")
        for x, top in ((-1.67, -1.15), (-.34, -.34), (1.21, .73)):
            beam("Window pillar", (x, y, 1.02), (top, side * .67, 1.66), .042,
                 "Mobility_Enamel", color)
        box("Door belt", (-.20, side * .881, 1.055), (2.82, .045, .052), mat="Mobility_Rubber")
        box("Service livery stripe", (-.25, side * .889, .78), (2.80, .017, .20),
            "navy" if kind == "PoliceCar" else "black")
        for x in (-1.03, .35):
            box("Door release", (x, side * .911, .99), (.18, .025, .035), mat="Mobility_Steel")
        for x in (-.32, -1.66, 1.23):
            box("Door shutline", (x, side * .885, .75), (.012, .011, .41), mat="Mobility_Rubber")
        for x in (-1.45, 1.43):
            tire(x, side, .855, .35, .23)
        rotation = (math.pi / 2, 0, 0) if side == -1 else (math.pi / 2, 0, math.pi)
        text_label("POLICE" if kind == "PoliceCar" else "CITY TAXI", (-.2, side * .909, .72),
                   .15, rotation, "white" if kind == "PoliceCar" else "yellow")
        for x in (-.80, .50):
            seat(x, side * .43, .68, .85)
    end_lights(4.6, 1.8, .83)
    mirrors(.80, 1.8, 1.16)
    box("Dashboard", (.87, 0, 1.03), (.24, 1.46, .13), mat="Mobility_Rubber")
    cylinder("Steering wheel", (.71, -.43, 1.14), .15, .035, axis="X", mat="Mobility_Rubber")
    if kind == "Taxi":
        box("Taxi roof sign", (-.15, 0, 1.83), (.60, .20, .20), "lamp")
        text_label("TAXI", (-.15, -.108, 1.78), .13, color="black")
    else:
        box("Lightbar mount", (-.12, 0, 1.79), (.32, 1.08, .08), mat="Mobility_Rubber")
        for side, lamp in ((-1, "brake"), (1, "blue")):
            box("Emergency beacon", (-.12, side * .33, 1.88), (.27, .43, .12), lamp)
    return finish(kind)


def bus(kind):
    coach = kind == "Coach"
    length = 11.6 if coach else 10.4
    width = 2.48
    roof = 3.36 if coach else 3.08
    color = "navy" if coach else "teal"
    front = length / 2
    axles = (-front + 2.2, front - 2.05)
    body = profile("Lower monocoque", [(-front, 1.14, .58, 1.52), (-front + .20, 1.24, .40, 1.53),
                                       (front - .22, 1.24, .40, 1.53), (front, 1.14, .58, 1.52)], color)
    arch(body, axles, .49, width)
    uv(body, color)
    box("Floor", (0, 0, .99), (length - .22, 2.35, .12), mat="Mobility_Rubber")
    box("Roof cap", (0, 0, roof), (length - .14, 2.44, .18), "cream", .09)
    for end in (-1, 1):
        box("End cap belt", (end * (front - .04), 0, 1.57), (.12, 2.34, .16), color)
        box("Panoramic end window", (end * (front + .027), 0, 2.40),
            (.018, 2.02, 1.16), mat="Mobility_Glass")
        for side in (-1, 1):
            box("Corner pillar", (end * (front - .15), side * 1.19, 2.30), (.17, .12, 1.68), color)
    count = 9 if coach else 8
    pitch = (length - .60) / count
    for side in (-1, 1):
        for i in range(count):
            x = -front + .30 + pitch * (i + .5)
            box("Passenger glazing", (x, side * 1.222, 2.36),
                (pitch - .075, .025, roof - 1.70), mat="Mobility_Glass")
            box("Window mullion", (x - pitch / 2, side * 1.236, 2.38), (.055, .05, roof - 1.64), color)
            if i < count - 1:
                seat(x, side * .78, 1.53 if coach else 1.43, .92)
        box("Livery ribbon", (0, side * 1.249, 1.35), (length - .35, .016, .22),
            "orange" if coach else "yellow")
        for x in axles:
            tire(x, side, 1.16, .49, .31)
        for x in (-2.6, -.7, 1.2):
            box("Luggage hatch", (x, side * 1.249, .87), (1.75, .012, .63), color)
            box("Luggage lock", (x, side * 1.264, 1.05), (.15, .017, .027), mat="Mobility_Steel")
        rotation = (math.pi / 2, 0, 0) if side == -1 else (math.pi / 2, 0, math.pi)
        text_label("NOVA EXPRESS" if coach else "NOVA CITY TRANSIT", (0, side * 1.267, 1.10),
                   .19, rotation)
    for x in ((front - 1.05,) if coach else (front - 1.05, -1.4)):
        box("Door frame", (x, -1.265, 1.64), (.88, .035, 2.12), mat="Mobility_Rubber")
        for dx in (-.21, .21):
            box("Folding glazed door", (x + dx, -1.29, 1.83), (.38, .021, 1.67), mat="Mobility_Glass")
            box("Door lower panel", (x + dx, -1.30, .81), (.38, .027, .36), color)
        box("Boarding tread", (x, -1.34, .55), (.86, .34, .09), mat="Mobility_Steel")
    for x in (-2.7, .6):
        box("HVAC rooftop housing", (x, 0, roof + .19), (1.50, 1.45, .23), "cream", .07)
        for dx in range(9):
            box("HVAC vent", (x - .56 + dx * .14, 0, roof + .315), (.04, 1.05, .016),
                mat="Mobility_Rubber")
    end_lights(length, width, 1.0)
    mirrors(front - .25, width, 2.52)
    box("Destination display", (front + .075, 0, 2.94), (.04, 1.75, .27), mat="Mobility_Rubber")
    seat(front - .80, -.66, 1.43)
    return finish(kind)


def truck(kind):
    ambulance = kind == "Ambulance"
    length = 5.9 if ambulance else 8.4
    front = length / 2
    rear = -front
    cabrear = front - 2.1
    color = "white" if ambulance else "orange" if kind == "CargoTruck" else "blue"
    radius = .40 if ambulance else .48
    axles = (rear + 1.35, front - 1.1) if ambulance else (rear + 1.25, rear + 2.45, front - 1.05)
    body = profile("Cab lower shell", [(cabrear, 1.09, .49, 1.50), (front - .2, 1.09, .49, 1.50),
                                      (front, 1.0, .63, 1.40)], color)
    arch(body, (front - 1.05,), radius, 2.2)
    uv(body, color)
    box("Chassis rails", (-.2, 0, .63), (length - .25, 1.53, .22), mat="Mobility_Rubber")
    roof = 2.65 if ambulance else 2.94
    box("Cab roof", (front - 1.14, 0, roof), (1.96, 2.16, .16), color, .07)
    box("Cab back", (cabrear + .08, 0, 2.12), (.13, 2.14, 1.57), color)
    panel("Sloped windshield", [(front - .035, -1.0, 1.52), (front - .035, 1.0, 1.52),
                                 (front - .30, 1.0, roof - .10), (front - .30, -1.0, roof - .10)],
          mat="Mobility_Glass")
    for side in (-1, 1):
        box("Side glass", (front - 1.06, side * 1.075, (roof + 1.48) / 2),
            (1.55, .025, roof - 1.66), mat="Mobility_Glass")
        for x in (cabrear + .13, front - .28):
            beam("Cab pillar", (x, side * 1.055, 1.43), (x, side * 1.055, roof),
                 .05, "Mobility_Enamel", color)
        box("Door latch", (cabrear + .45, side * 1.10, 1.37), (.20, .03, .045), mat="Mobility_Steel")
        box("Cab access step", (front - 1.83, side * 1.12, .61), (.44, .34, .10), mat="Mobility_Steel")
        seat(front - 1.22, side * .58, 1.11)
        for x in axles:
            tire(x, side, 1.06, radius, .32)
    end_lights(length, 2.18, 1.13)
    mirrors(front - .38, 2.2, 2.09)
    cargo_length = cabrear - rear - .15
    cx = (rear + cabrear - .15) / 2
    if kind in ("BoxTruck", "Ambulance"):
        box("Cargo body", (cx, 0, 1.99), (cargo_length, 2.27, 2.14), "white", .05)
        for side in (-1, 1):
            box("Fleet band", (cx, side * 1.147, 1.81), (cargo_length - .12, .02, .33),
                "brake" if ambulance else "blue")
            rotation = (math.pi / 2, 0, 0) if side == -1 else (math.pi / 2, 0, math.pi)
            text_label("AMBULANCE" if ambulance else "NOVA LOGISTICS", (cx, side * 1.166, 2.33),
                       .20, rotation, "brake" if ambulance else "blue")
            if ambulance:
                box("Medical cross H", (cx, side * 1.165, 2.06), (.60, .02, .15), "brake")
                box("Medical cross V", (cx, side * 1.165, 2.06), (.15, .02, .57), "brake")
            else:
                for i in range(10):
                    box("Body seam rib", (rear + .3 + i * cargo_length / 10, side * 1.148, 2.05),
                        (.022, .019, 1.85), "cream", .002)
        for y in (-.55, .55):
            box("Rear door", (rear - .024, y, 2.0), (.025, 1.02, 1.90), "cream")
            beam("Rear locking bar", (rear - .056, y, 1.16), (rear - .056, y, 2.86), .018)
        if ambulance:
            for side in (-1, 1):
                box("Emergency roof LED", (front - .95, side * .58, roof + .16),
                    (.29, .48, .15), "blue")
    elif kind == "CargoTruck":
        box("Flatbed", (cx, 0, 1.05), (cargo_length, 2.35, .18), "wood")
        for side in (-1, 1):
            for z in (1.32, 1.63, 1.94):
                box("Dropside board", (cx, side * 1.18, z), (cargo_length, .075, .25), "green")
            for i in range(5):
                box("Stake", (rear + .13 + i * cargo_length / 4.3, side * 1.22, 1.57),
                    (.09, .055, 1.16), mat="Mobility_Steel")
        for x in (cx - 1.1, cx + .7):
            box("Secured freight crate", (x, 0, 1.66), (1.48, 1.62, 1.04), "wood")
            for y in (-.54, .54):
                box("Cargo strap", (x, y, 2.19), (1.50, .055, .02), mat="Mobility_Rubber")
    else:
        cylinder("Pressure tank", (cx, 0, 2.05), .97, cargo_length, axis="X", mat="Mobility_Steel", vertices=48)
        for x in (cx - cargo_length * .31, cx + cargo_length * .31):
            cylinder("Tank retaining band", (x, 0, 2.05), .995, .11, "blue", axis="X", vertices=48)
            cylinder("Filler manway", (x, 0, 3.08), .26, .15, mat="Mobility_Steel")
        for side in (-1, 1):
            beam("Tank top rail", (rear + .2, side * .47, 3.27), (cabrear - .30, side * .47, 3.27))
            box("Hazard placard", (cx, side * .979, 2.12), (.56, .025, .37), "orange")
        for z in (1.2, 1.55, 1.9, 2.25, 2.6, 2.95):
            beam("Access ladder rung", (rear - .08, -.35, z), (rear - .08, .35, z), .022)
    return finish(kind)
