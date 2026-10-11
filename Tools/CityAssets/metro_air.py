"""Static light utility helicopter and twin engine civilian transport."""
import math
from metro_geometry import g, hull, panel, curved_glass, wheel, text, finish


def helicopter():
    cabin = [(-2.4, .28, .35, 1.65), (-1.8, .91, .88, 1.60),
             (-.4, 1.05, 1.05, 1.61), (1.15, .94, .91, 1.58),
             (2.0, .65, .62, 1.42), (2.55, .08, .13, 1.29)]
    hull("Cabin shell", cabin, color="red")
    hull("Tail boom", [(-7.1, .10, .14, 2.02), (-5.0, .22, .27, 1.9),
                       (-2.0, .52, .53, 1.74)], color="red", segments=20)
    for side in [-1, 1]:
        curved_glass("Windscreen", cabin, (1.55, 2.30), (.25, 1.45), side)
        curved_glass("Pilot side glass", cabin, (.12, 1.47), (.08, .88), side)
        curved_glass("Cabin side glass", cabin, (-1.55, -.13), (.08, .70), side)
        g.beam("Cabin door centre post", (-.05, side * 1.055, 1.31), (-.05, side * 1.04, 2.23),
               .03, mat="Living_Enamel", color="red")
        g.box("Cabin door handle", (-.45, side * 1.047, 1.43), (.23, .05, .035), mat="Living_Steel")
        g.tube("Landing skid", [(-2.20, side * 1.34, .23), (1.70, side * 1.34, .23),
                                (2.12, side * 1.34, .46)], .07)
        for x in [-1.35, .95]:
            g.beam("Skid strut", (x, side * .66, .96), (x, side * 1.34, .29), .065)
        panel("Tail stabilizer", [(-5.75, side * .12, 2.05), (-5.95, side * 1.55, 2.05),
                                   (-6.55, side * 1.55, 2.05), (-6.42, side * .12, 2.05)],
              .055, color="white")
        g.cylinder("Exhaust", (-1.32, side * .52, 2.68), .19, .65, axis="X", mat="Living_Steel")
    panel("Tail vertical fin", [(-7.16, -.05, 1.75), (-7.48, -.05, 3.6),
                                (-6.87, -.05, 3.5), (-6.15, -.05, 1.91)], .10, axis=1, color="white")
    g.box("Engine cowling", (-.79, 0, 2.69), (1.75, 1.08, .59), color="red", bevel=.20)
    for side in [-1, 1]:
        for x in [-1.4, -1.22, -1.04, -.86]:
            g.box("Intake louvers", (x, side * .546, 2.76), (.065, .015, .21), color="black")
    g.cylinder("Rotor mast", (-.4, 0, 3.19), .10, .76, mat="Living_Steel")
    g.cylinder("Rotor hub", (-.4, 0, 3.51), .30, .17, mat="Living_Steel")
    for yaw in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        coords = [(.35, -.12), (5.35, -.21), (5.48, .10), (.35, .15)]
        points = [(-.4 + x * math.cos(yaw) - y * math.sin(yaw),
                   x * math.sin(yaw) + y * math.cos(yaw), 3.54) for x, y in coords]
        panel("Main rotor blade", points, .035, color="black")
    g.cylinder("Tail rotor hub", (-6.94, -.22, 2.54), .12, .45, axis="Y", mat="Living_Steel")
    for angle in [math.pi / 4, 3 * math.pi / 4]:
        obj = g.box("Tail rotor blade", (-6.94, -.48, 2.54), (1.61, .045, .14), color="black")
        obj.rotation_euler.y = angle
    g.cylinder("Position beacon", (-.9, 0, 3.02), .07, .10, color="orange", vertices=12)
    return finish("Helicopter")


def civilian_plane():
    fuselage = [(-6.3, .04, .09, 2.21), (-5.2, .35, .40, 2.03),
                (-3.7, .68, .70, 1.95), (-2.3, .85, .92, 1.96),
                (2.0, .86, .95, 1.96), (3.3, .77, .78, 1.90),
                (4.20, .55, .52, 1.77), (4.91, .06, .12, 1.72)]
    hull("Pressurized fuselage", fuselage, segments=40)
    for side in [-1, 1]:
        # Canh loe goc va dau canh thu gon tao hinh twin turboprop dan dung.
        panel("Main tapered wing", [(1.52, side * .67, 1.35), (.22, side * 7.75, 1.55),
                                    (-1.05, side * 7.75, 1.55), (-1.62, side * .67, 1.35)],
              .14, color="white")
        panel("Flap hinge", [(-.90, side * 2.05, 1.508), (-.91, side * 7.2, 1.65),
                             (-.97, side * 7.2, 1.65), (-.96, side * 2.05, 1.508)],
              .004, color="gray", bevel=.0006)
        panel("Tailplane", [(-4.08, side * .22, 2.18), (-4.85, side * 2.97, 2.38),
                             (-5.87, side * 2.97, 2.38), (-5.75, side * .22, 2.18)], .095)
        hull("Turboprop nacelle", [(-1.48, .13, .20, 1.45), (-.6, .47, .48, 1.51),
                                   (1.64, .44, .45, 1.58), (2.02, .28, .30, 1.58)], segments=28)
        obj = g.g.PARTS[-1]
        obj.location.y = side * 2.55
        g.cylinder("Propeller spinner", (2.19, side * 2.55, 1.58), .27, .43, axis="X")
        for angle in [0, math.pi / 2, math.pi, math.pi * 1.5]:
            dy = math.cos(angle)
            dz = math.sin(angle)
            coords = [(2.23, side * 2.55 + dy * .18, 1.58 + dz * .18),
                      (2.23, side * 2.55 + dy * 1.22 - dz * .10, 1.58 + dz * 1.22 + dy * .10),
                      (2.23, side * 2.55 + dy * 1.27 + dz * .12, 1.58 + dz * 1.27 - dy * .12),
                      (2.23, side * 2.55 + dy * .18 + dz * .14, 1.58 + dz * .18 - dy * .14)]
            panel("Propeller blade", coords, .045, axis=0, color="black")
        for x in [-2.2, -1.40, -.60, .20, 1.0, 1.8]:
            g.box("Cabin porthole", (x, side * .853, 2.25), (.44, .032, .40), color="navy", bevel=.11)
        curved_glass("Cockpit side glass", fuselage, (2.45, 3.35), (.24, .97), side)
        curved_glass("Cockpit windshield", fuselage, (3.43, 4.22), (.45, 1.45), side)
        g.beam("Main landing oleo", (-.55, side * 2.55, 1.37), (-.55, side * 2.55, .40), .072)
        wheel(-.55, side * 2.55, .36, .36, .20)
        g.box("Navigation light", (-.17, side * 7.76, 1.64), (.17, .07, .065),
              color="red" if side < 0 else "green")
        text("ANANTA AIR", (-.2, side * .88, 1.80), .17,
             (math.pi / 2, 0, 0 if side < 0 else math.pi), "blue")
    panel("Vertical tail", [(-5.96, -.055, 2.17), (-5.55, -.055, 4.39),
                             (-4.78, -.055, 4.35), (-3.69, -.055, 2.20)], .11, color="blue", axis=1)
    g.beam("Nose gear", (3.35, 0, 1.31), (3.35, 0, .31), .065)
    wheel(3.35, 0, .28, .28, .16)
    return finish("CivilianPlane")
