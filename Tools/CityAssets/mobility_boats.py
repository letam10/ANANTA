"""Vessels with lofted multi-chine hulls, deck fittings and waterline origins."""
import math
from mobility_geometry import box, mesh, cylinder, beam, panel, text_label, seat, finish


def hull(length, width, depth, freeboard, color):
    rings = []
    for x, factor in ((-.5, .64), (-.43, .92), (-.22, 1), (.12, .94), (.34, .64), (.5, .055)):
        half = width * factor / 2
        rings += [(x * length, -half, freeboard), (x * length, -half * .79, -.15 * depth),
                  (x * length, -half * .32, -.82 * depth), (x * length, 0, -depth),
                  (x * length, half * .32, -.82 * depth), (x * length, half * .79, -.15 * depth),
                  (x * length, half, freeboard)]
    faces = [tuple(reversed(range(7)))]
    for i in range(5):
        for j in range(7):
            faces.append((i * 7 + j, i * 7 + (j + 1) % 7,
                          (i + 1) * 7 + (j + 1) % 7, (i + 1) * 7 + j))
    faces.append(tuple(range(35, 42)))
    mesh("Multi chine closed hull", rings, faces, color, bevel=.035)
    outline = [(x, y, z + .055) for x, y, z in rings[::7]]
    outline += [(rings[i][0], rings[i][1], rings[i][2] + .055) for i in range(41, 5, -7)]
    for i, a in enumerate(outline):
        beam("Gunwale rub rail", a, outline[(i + 1) % len(outline)], .035, "Mobility_Rubber")
    return outline


def guardrails(outline, height, interval=1):
    for i, point in enumerate(outline):
        end = outline[(i + 1) % len(outline)]
        a = (point[0], point[1], point[2] + height)
        b = (end[0], end[1], end[2] + height)
        beam("Safety rail", a, b, .024)
        distance = math.dist(point, end)
        count = max(1, int(distance / interval))
        for j in range(count):
            p = tuple(point[k] + (end[k] - point[k]) * j / count for k in range(3))
            beam("Rail stanchion", p, (p[0], p[1], p[2] + height), .021)


def cargo_ship():
    outline = hull(26, 6.1, 1.8, 1.5, "navy")
    box("Working deck", (-1.2, 0, 1.56), (20.7, 4.85, .18), "green")
    guardrails(outline, .90, 1.35)
    for x in (-3.8, .7, 5.2):
        for y in (-1.25, 1.25):
            color = "orange" if x < 0 else "teal" if y < 0 else "cream"
            box("Freight container", (x, y, 2.9), (4.24, 2.20, 2.48), color, .025)
            for side in (-1, 1):
                for i in range(15):
                    box("Container corrugation", (x - 1.98 + i * .282, y + side * 1.114, 2.9),
                        (.047, .035, 2.3), color, .004)
            for dy in (-.52, .52):
                beam("Container lock", (x + 2.14, y + dy, 1.82), (x + 2.14, y + dy, 4.0), .022)
    box("Aft accommodation", (-9.0, 0, 3.3), (4.0, 4.6, 3.3), "cream", .065)
    box("Wheelhouse", (-8.6, 0, 5.52), (3.45, 4.9, 1.30), "white", .06)
    for side in (-1, 1):
        for x in (-9.6, -8.6, -7.6):
            box("Bridge side window", (x, side * 2.461, 5.64), (.75, .02, .65), mat="Mobility_Glass")
        box("Accommodation door", (-8.8, side * 2.32, 2.8), (.73, .035, 1.85), "white")
        for x in (-10, -8.2):
            cylinder("Cabin porthole", (x, side * 2.335, 4.10), .24, .025,
                     axis="Y", mat="Mobility_Glass")
        for x in (-11, 9.2):
            cylinder("Deck bollard", (x, side * 1.6, 1.81), .16, .45, mat="Mobility_Steel")
    for y in (-1.7, -.85, 0, .85, 1.7):
        box("Bridge forward window", (-6.855, y, 5.64), (.023, .65, .65), mat="Mobility_Glass")
    cylinder("Funnel", (-10, 0, 6.33), .59, 1.30, "orange")
    cylinder("Funnel soot cap", (-10, 0, 7.01), .61, .12, mat="Mobility_Rubber")
    beam("Radar mast", (-7.5, 0, 6.2), (-7.5, 0, 8.4), .055)
    box("Radar scanner", (-7.5, 0, 8.4), (.20, 1.80, .14), "white")
    beam("Fore cargo boom", (8.9, 0, 1.8), (8.9, 0, 6.0), .14, "Mobility_Enamel", "yellow")
    beam("Cargo crane arm", (8.9, 0, 5.8), (4.6, 0, 6.9), .095, "Mobility_Enamel", "yellow")
    beam("Lifting wire", (4.6, 0, 6.9), (4.6, 0, 4.9), .017, "Mobility_Rubber")
    return finish("CargoShip")


def motorboat():
    outline = hull(6.4, 2.35, .64, .57, "white")
    box("Cockpit sole", (-.65, 0, .66), (3.5, 1.72, .13), "wood")
    for side in (-1, 1):
        box("Cushioned aft bench", (-2.0, side * .61, .92), (.57, .48, .30), mat="Mobility_Upholstery")
        seat(-.30, side * .48, .85, .9)
        beam("Bow rail", (.3, side * 1.04, .72), (2.5, side * .37, .98), .025)
        for x in (.5, 1.5):
            beam("Bow rail support", (x, side * (.99 - x * .2), .60),
                 (x, side * (.99 - x * .2), .85), .021)
    box("Helm console", (.45, 0, 1.02), (.54, 1.67, .40), "cream")
    panel("Angled windscreen", [(.64, -.90, 1.16), (.64, .90, 1.16),
                                (.38, .76, 1.65), (.38, -.76, 1.65)], mat="Mobility_Glass")
    for side in (-1, 1):
        beam("Windscreen frame", (.64, side * .9, 1.16), (.38, side * .76, 1.65), .027)
    cylinder("Helm wheel", (.09, -.45, 1.20), .16, .035, axis="X", mat="Mobility_Rubber")
    box("Outboard engine cowling", (-3.34, 0, .75), (.48, .65, .83), "navy", .13)
    box("Outboard shaft", (-3.37, 0, -.04), (.20, .24, .89), mat="Mobility_Steel")
    cylinder("Propeller boss", (-3.54, 0, -.38), .13, .32, axis="X", mat="Mobility_Steel")
    for angle in (0, math.tau / 3, 2 * math.tau / 3):
        blade = box("Propeller blade", (-3.66, .22 * math.sin(angle), -.38 + .22 * math.cos(angle)),
                    (.035, .13, .35), mat="Mobility_Steel")
        blade.rotation_euler.x = -angle
    text_label("NOVA 06", (-1.0, -1.035, .35), .16, color="navy")
    return finish("Motorboat")


def sailboat():
    outline = hull(8.6, 2.7, 1.12, .70, "cream")
    box("Deckhouse", (-.6, 0, 1.0), (2.85, 1.80, .58), "white", .18)
    for side in (-1, 1):
        for x in (-1.45, -.7, .05):
            box("Cabin portlight", (x, side * .91, 1.10), (.51, .022, .21), mat="Mobility_Glass")
        box("Cockpit bench", (-2.8, side * .64, .86), (1.45, .42, .30), "wood")
    guardrails(outline, .62, 1.5)
    beam("Aluminium mast", (.45, 0, .75), (.45, 0, 10.3), .075)
    beam("Boom", (.45, 0, 2.02), (-3.5, 0, 2.02), .048)
    beam("Mast spreader", (.45, -.85, 5.7), (.45, .85, 5.7), .029)
    panel("Battened mainsail", [(.35, .03, 2.13), (-3.35, .16, 2.13),
                                (-1.60, .24, 6.0), (.35, .03, 9.90)], "white", thickness=.012)
    panel("Foresail", [(.61, -.02, 2.20), (3.82, -.01, 1.13),
                        (1.12, -.04, 8.18), (.61, -.03, 9.35)], "cream", thickness=.012)
    for end in ((3.98, 0, .85), (-3.6, 0, .80), (.4, -1.22, .8), (.4, 1.22, .8)):
        beam("Standing rigging", (.45, 0, 10.1), end, .012, "Mobility_Rubber")
    for z, end in ((3.6, -2.83), (5.4, -1.98), (7.2, -.89)):
        beam("Sail batten", (.30, -.025, z), (end, .09, z), .012)
    cylinder("Helm pedestal", (-2.75, 0, 1.00), .10, .57, mat="Mobility_Steel")
    cylinder("Helm wheel", (-2.58, 0, 1.37), .29, .028, axis="X", mat="Mobility_Steel")
    box("Fin keel", (.1, 0, -1.24), (1.55, .15, 1.35), "navy", .07)
    return finish("Sailboat")
