"""Fire engine and self contained passenger train carriage static meshes."""
import math
from metro_geometry import g, wheel, panel, text, finish


def fire_engine():
    g.box("Chassis", (0, 0, .73), (7.65, 2.2, .27), mat="Living_Dark", bevel=.03)
    g.box("Equipment body", (-1.05, 0, 1.96), (5.6, 2.38, 2.05), color="red", bevel=.055)
    g.box("Crew cab", (2.70, 0, 2.08), (2.23, 2.40, 2.29), color="red", bevel=.14)
    g.box("Cab roof", (2.68, 0, 3.24), (2.34, 2.48, .12), bevel=.04)
    g.box("Front windscreen", (3.829, 0, 2.62), (.036, 2.07, .91), color="navy", bevel=.09)
    g.box("Glass divider", (3.86, 0, 2.62), (.04, .045, .88), color="black")
    g.box("Grille", (3.845, 0, 1.57), (.06, 1.20, .57), mat="Living_Dark", bevel=.025)
    for z in [1.35, 1.48, 1.61, 1.74]:
        g.box("Grille slat", (3.887, 0, z), (.025, 1.12, .027), mat="Living_Steel")
    g.box("Front bumper", (3.98, 0, 1.00), (.28, 2.51, .25), mat="Living_Steel", bevel=.035)
    g.box("Rear bumper", (-4.00, 0, .86), (.26, 2.51, .22), mat="Living_Steel")
    for side in [-1, 1]:
        y = side * 1.21
        g.box("Side window", (2.70, y, 2.60), (1.87, .032, .84), color="navy", bevel=.05)
        g.box("Door seam", (2.10, y + side * .018, 1.60), (.025, .015, 1.06), color="black")
        g.box("Door handle", (2.05, y + side * .037, 2.02), (.24, .04, .065), mat="Living_Steel")
        g.box("Reflective belt", (2.70, y + side * .012, 1.82), (2.12, .025, .17), color="yellow")
        g.box("Cab step", (2.64, side * 1.28, .96), (1.70, .28, .10), mat="Living_Steel")
        g.beam("Mirror stalk", (3.31, y, 2.83), (3.45, side * 1.52, 2.82), .025)
        g.box("Mirror", (3.45, side * 1.53, 2.64), (.14, .08, .39), mat="Living_Dark")
        for x in [-2.87, -1.24, .39]:
            g.box("Equipment roller shutter", (x, side * 1.206, 2.16), (1.47, .035, 1.46),
                  mat="Living_Steel", bevel=.02)
            for z in [1.53 + i * .14 for i in range(10)]:
                g.box("Shutter seam", (x, side * 1.231, z), (1.39, .01, .014), color="gray", bevel=0)
            g.box("Shutter handle", (x, side * 1.25, 1.58), (.36, .055, .045), color="black")
        g.box("Equipment yellow belt", (-1.04, side * 1.22, 1.29), (5.53, .035, .16), color="yellow")
        for x in [-2.70, 2.62]:
            wheel(x, side * 1.11, .57, .57, .36)
        for x in [-2.70, 2.62]:
            g.box("Mudguard top", (x, side * 1.20, 1.16), (1.38, .32, .11), color="red", bevel=.04)
        for z in [1.56, 1.83]:
            g.box("Headlamp", (3.895, side * .89, z), (.04, .40, .18), color="lamp", bevel=.035)
        g.box("Emergency beacon", (2.66, side * .82, 3.41), (.55, .34, .22), color="blue", bevel=.04)
        g.box("Tail lamp", (-3.888, side * .96, 1.45), (.035, .25, .34), color="orange")
    for y in [-.56, .56]:
        g.box("Roof ladder rail", (-.85, y, 3.20), (5.44, .065, .12), mat="Living_Steel")
    for i in range(18):
        g.box("Roof ladder rung", (-3.30 + i * .29, 0, 3.20), (.055, 1.11, .06), mat="Living_Steel")
    for z in [1.05, 1.44, 1.83, 2.22, 2.61, 3.0]:
        g.beam("Rear access rung", (-3.96, -.36, z), (-3.96, .36, z), .025)
    for y in [-.39, .39]:
        g.beam("Rear access rail", (-3.96, y, .92), (-3.96, y, 3.16), .028)
    text("FIRE  119", (3.897, 0, 2.04), .19, (math.pi / 2, 0, math.pi / 2))
    return finish("FireEngine")


def passenger_train():
    g.box("Carriage body", (0, 0, 2.30), (21.1, 2.95, 2.60), color="cream", bevel=.22)
    g.box("Rounded roof", (0, 0, 3.57), (20.84, 2.93, .34), color="gray", bevel=.15)
    g.box("Underframe", (0, 0, 1.0), (20.4, 2.55, .28), mat="Living_Dark")
    for side in [-1, 1]:
        y = side * 1.487
        g.box("Blue waist band", (0, y, 1.63), (20.60, .03, .45), color="blue", bevel=.015)
        g.box("Window belt", (0, y, 2.66), (20.24, .023, 1.05), color="navy", bevel=.07)
        for x in [-9.6, -8.05, -6.50, -4.95, -3.40, -1.85, -.30, 1.25, 2.80, 4.35, 5.9, 7.45, 9.0]:
            g.box("Window divider", (x, y + side * .018, 2.67), (.12, .03, 1.06), color="cream", bevel=0)
        for x in [-8.45, 8.45]:
            g.box("Door gasket", (x, y + side * .029, 2.08), (1.43, .04, 2.13), color="black", bevel=.06)
            g.box("Sliding doors", (x, y + side * .058, 2.08), (1.33, .03, 2.04), mat="Living_Steel")
            g.box("Door centre seam", (x, y + side * .079, 2.08), (.028, .012, 2.01), color="black")
            for dx in [-.33, .33]:
                g.box("Door glass", (x + dx, y + side * .08, 2.54), (.49, .018, .90), color="navy")
            g.box("Door step", (x, side * 1.54, 1.0), (1.58, .25, .10), mat="Living_Steel")
        for x in [-7.0, -5.25, 5.25, 7.0]:
            wheel(x, side * 1.05, .47, .47, .17)
        for x in [-6.12, 6.12]:
            g.box("Bogie frame", (x, side * 1.12, .66), (2.61, .17, .23), mat="Living_Dark")
            for dx in [-.87, .87]:
                g.cylinder("Axle bearing", (x + dx, side * 1.19, .47), .16, .14,
                           axis="Y", mat="Living_Steel", vertices=16)
        text("ANANTA   REGIONAL", (0, side * 1.522, 1.52), .22,
             (math.pi / 2, 0, 0 if side < 0 else math.pi), "white")
    for x in [-10.59, 10.59]:
        g.box("End gangway gasket", (x, 0, 2.24), (.10, 1.35, 2.17), mat="Living_Dark", bevel=.11)
        g.box("End vestibule door", (x * 1.006, 0, 2.19), (.08, 1.03, 1.94), mat="Living_Steel")
        g.box("Vestibule glass", (x * 1.011, 0, 2.59), (.045, .68, .66), color="navy")
        g.box("Coupler mounting bracket", (x * .968, 0, .82), (.80, .46, .38), mat="Living_Dark")
        g.box("Coupler", (x * 1.027, 0, .69), (.75, .35, .23), mat="Living_Dark")
    for x in [-4.4, 0, 4.4]:
        g.box("Roof HVAC", (x, 0, 3.91), (2.3, 1.40, .42), color="gray", bevel=.08)
        for y in [-.73, .73]:
            for i in range(8):
                g.box("HVAC grille", (x - .91 + i * .26, y, 3.91), (.08, .025, .22), color="black", bevel=0)
    for x in [-2.8, 2.8]:
        g.box("Underfloor service pack", (x, 0, .60), (2.8, 1.7, .53), mat="Living_Dark", bevel=.04)
    return finish("PassengerTrain")
