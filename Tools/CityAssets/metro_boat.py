"""Open clinker-style rowboat with seats, ribs and stowed oars."""
import math
from metro_geometry import g, panel, slender_beam, finish


def rowboat():
    stations = [(-2.05, .43, .45), (-1.55, .70, .15), (-.8, .84, .02),
                (0, .86, 0), (.8, .72, .05), (1.5, .44, .23), (2.08, .025, .56)]
    # Than ho rong co day va thanh day 45mm; khong dung mot khoi kin che khoang cheo.
    for side in [-1, 1]:
        for level in range(4):
            t0 = level / 4
            t1 = (level + 1) / 4
            for index in range(len(stations) - 1):
                a, b = stations[index:index + 2]
                outline = []
                for (x, width, bottom), t in [(a, t0), (b, t0), (b, t1), (a, t1)]:
                    outline.append((x, side * width * (.32 + .68 * t), bottom + (.72 - bottom) * t))
                panel("Overlapping hull plank", outline, side * .045, axis=1, color="wood", bevel=0)
        rim = [(x, side * w, .75) for x, w, z in stations]
        for start, end in zip(rim, rim[1:]):
            slender_beam("Gunwale", start, end, .036, "wood")
    panel("Keel floor", [(x, -w * .34, z) for x, w, z in stations]
          + [(x, w * .34, z) for x, w, z in reversed(stations)], .055, color="wood")
    panel("Stern transom", [(-2.055, -.44, .73), (-2.055, .44, .73),
                            (-2.055, .16, .43), (-2.055, -.16, .43)], .045, axis=0, color="wood")
    for x, width in [(-1.3, 1.37), (0, 1.63), (1.13, 1.0)]:
        g.box("Bench seat", (x, 0, .56), (.34, width, .065), color="wood", bevel=.018)
        a, b = next((a, b) for a, b in zip(stations, stations[1:]) if a[0] <= x <= b[0])
        floor = a[2] + (b[2] - a[2]) * (x - a[0]) / (b[0] - a[0]) + .05
        for y in [-width * .15, width * .15]:
            g.box("Seat support", (x, y, (floor + .535) / 2),
                  (.08, .075, .535 - floor), color="wood")
    for x, width, z in stations[1:-1]:
        for side in [-1, 1]:
            slender_beam("Inner rib", (x, side * width * .32, z + .07),
                         (x, side * (width - .02), .69), .024, "cream")
    for side in [-1, 1]:
        g.torus("Oarlock", (.25, side * .85, .82), .055, .012,
                rotation=(math.pi / 2, 0, 0), segments=16, sides=6)
        slender_beam("Stowed oar shaft", (-1.58, side * .32, .84),
                     (1.07, side * .50, .84), .026, "wood")
        panel("Oar blade", [(1.04, side * .50 - .08, .84), (1.75, side * .54 - .12, .84),
                            (1.82, side * .54 + .12, .84), (1.04, side * .50 + .08, .84)],
              .035, color="wood")
    g.torus("Bow painter ring", (2.10, 0, .63), .05, .012,
            rotation=(0, math.pi / 2, 0), segments=16, sides=6)
    return finish("Rowboat")
