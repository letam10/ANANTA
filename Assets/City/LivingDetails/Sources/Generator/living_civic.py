"""Original park sculpture, playground equipment, extinguisher and arcade machine."""
import math
import living_geometry as g


def extinguisher():
    g.lathe("Pressure cylinder", [(.012, 0), (.075, 0), (.095, .022), (.098, .37),
                                 (.080, .414), (.027, .44), (.012, .44)], color="red")
    g.cylinder("Valve collar", (0, 0, .45), .029, .035, mat="Living_Steel")
    g.box("Valve body", (0, 0, .48), (.075, .040, .045), mat="Living_Steel")
    for z, x in ((.51, -.01), (.545, -.006)):
        g.box("Squeeze handle", (x, 0, z), (.145, .025, .014), "black", .004)
    g.cylinder("Pressure gauge rim", (.048, 0, .487), .025, .015, axis="X", mat="Living_Steel")
    g.cylinder("Pressure gauge face", (.059, 0, .487), .021, .006, "cream", axis="X")
    g.beam("Gauge needle", (.064, 0, .487), (.064, -.011, .498), .0018, "Living_Enamel", "red")
    g.torus("Safety pin ring", (-.04, -.033, .493), .018, .003, rotation=(math.pi / 2, 0, 0))
    g.tube("Discharge hose", [(0, .025, .48), (0, .115, .48), (0, .14, .39),
                              (0, .14, .22), (.015, .115, .14)], .011, "Living_Dark")
    g.beam("Hose nozzle", (.015, .115, .14), (.035, .10, .09), .018, "Living_Dark")
    g.box("Instruction band", (.098, 0, .245), (.007, .092, .17), "cream", .002)
    for z in (.29, .275, .255, .20):
        g.box("Instruction rules", (.103, 0, z), (.004, .070, .004), "black", .0005)
    for y in (-.03, 0, .03):
        g.box("Operating pictogram", (.104, y, .232), (.004, .018, .022), "red", .001)
    return g.finish("FireExtinguisher")


def monument():
    for z, size in ((.11, (2.2, 2.2, .22)), (.32, (1.9, 1.9, .20)), (.65, (1.5, 1.5, .46))):
        g.box("Granite stepped plinth", (0, 0, z), size, mat="Living_Stone", bevel=.04)
    g.box("Bronze dedication tablet", (.757, 0, .66), (.024, .75, .26), "bronze", .01)
    for z in (.60, .65, .72):
        g.box("Dedication relief rule", (.774, 0, z), (.012, .54, .009), "cream", .001)
    # Hai nhanh xoan bat cheo tao bieu tuong cong dong, mat cat dac lien tuc.
    for phase in (0, math.pi):
        points = []
        rings = 30
        segments = 8
        for i in range(rings):
            t = i / (rings - 1)
            a = phase + t * math.pi * 1.5
            r = .25 + .22 * math.sin(t * math.pi)
            width = .12 * (1 - .45 * t)
            for j in range(segments):
                b = j * math.tau / segments
                points.append((r * math.cos(a) + width * math.cos(b),
                               r * math.sin(a) + width * math.sin(b), .88 + t * 2.8))
        faces = [tuple(reversed(range(segments)))]
        for i in range(rings - 1):
            for j in range(segments):
                faces.append((i * segments + j, i * segments + (j + 1) % segments,
                              (i + 1) * segments + (j + 1) % segments, (i + 1) * segments + j))
        faces.append(tuple((rings - 1) * segments + j for j in range(segments)))
        g.mesh("Rising civic ribbon", points, faces, mat="Living_Steel")
    g.torus("Unity ring", (0, 0, 3.72), .42, .055, rotation=(math.pi / 2, 0, 0))
    for x in (-.67, .67):
        for y in (-.67, .67):
            g.cylinder("Bronze mount stud", (x, y, .91), .038, .025, "bronze", vertices=12)
    return g.finish("CivicMonument")


def slide():
    for x in (-1.05, -.50):
        for y in (-.45, .45):
            g.beam("Platform post", (x, y, .025), (x, y, 2.17), .045, "Living_Enamel", "teal")
            g.cylinder("Anchoring foot", (x, y, .028), .105, .056, "gray")
            g.cylinder("Post cap", (x, y, 2.17), .053, .08, "yellow")
    g.box("Raised standing platform", (-.78, 0, 1.4), (.72, .93, .075), "teal", .02)
    for y in (-.45, .45):
        g.beam("Platform guard", (-1.05, y, 2.05), (-.50, y, 2.05), .026)
        for x in (-.91, -.74, -.58):
            g.beam("Guard spindle", (x, y, 1.46), (x, y, 2.04), .014)
        g.beam("Ladder rail", (-1.95, y, .09), (-1.05, y, 1.45), .028)
        g.beam("Climb handle", (-1.40, y, 1.27), (-1.04, y, 1.91), .025)
    for i in range(6):
        t = (i + .4) / 6
        g.box("Non slip ladder step", (-1.95 + .9 * t, 0, .09 + 1.36 * t),
              (.18, .90, .045), "yellow", .008)
    path = [(-.45, 1.44), (-.24, 1.4), (.05, 1.28), (.36, 1.04),
            (.71, .77), (1.08, .50), (1.38, .28), (1.65, .18), (1.92, .17)]
    points = [(x, y, z + dz) for dz in (0, -.025) for x, z in path for y in (-.34, .34)]
    n = len(path) * 2
    faces = []
    for i in range(len(path) - 1):
        a = i * 2
        faces.extend([(a, a + 1, a + 3, a + 2), (n + a + 2, n + a + 3, n + a + 1, n + a),
                      (a, a + 2, n + a + 2, n + a), (a + 3, a + 1, n + a + 1, n + a + 3)])
    faces.extend([(0, n, n + 1, 1), (n - 2, n - 1, 2 * n - 1, 2 * n - 2)])
    g.mesh("Curved stainless chute", points, faces, mat="Living_Steel")
    for y in (-.36, .36):
        for a, b in zip(path, path[1:]):
            points = [(x, y + dy, z + dz) for dy in (-.016, .016)
                      for x, z, dz in ((a[0], a[1], -.02), (b[0], b[1], -.02),
                                       (b[0], b[1], .14), (a[0], a[1], .14))]
            faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
                     (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
            g.mesh("Raised chute sidewall", points, faces, "orange")
            g.beam("Rounded chute lip", (a[0], y, a[1] + .14),
                   (b[0], y, b[1] + .14), .024, "Living_Enamel", "orange")
        g.beam("Chute support", (.9, y, .03), (.9, y, .56), .032)
    return g.finish("PlaygroundSlide")


def swing():
    for y in (-1.4, 1.4):
        for x in (-1.0, 1.0):
            g.beam("A frame leg", (x, y, .055), (0, y, 2.45), .060, "Living_Enamel", "teal")
            g.cylinder("Leg footing", (x, y, .04), .14, .08, "gray")
        g.beam("A frame brace", (-.70, y, .74), (.70, y, .74), .035)
        g.cylinder("Frame apex bolt", (0, y, 2.42), .09, .16, "yellow", axis="Y")
    g.beam("Top beam", (0, -1.52, 2.43), (0, 1.52, 2.43), .07, "Living_Enamel", "teal")
    for middle in (-.69, .69):
        g.box("Moulded seat", (0, middle, .51), (.37, .52, .055), "red", .025)
        for y in (middle - .23, middle + .23):
            g.torus("Top swivel eye", (0, y, 2.32), .038, .010, rotation=(math.pi / 2, 0, 0))
            # Ma xich that xen ke, du nhe cho static mesh game.
            for i in range(24):
                angle = (math.pi / 2, 0, 0 if i % 2 else math.pi / 2)
                obj = g.torus("Alternating chain link", (0, y, .56 + i * .072), .024, .005,
                              rotation=angle, segments=12, sides=6)
                obj.scale = (1, 1.65, 1)
    return g.finish("PlaygroundSwing")


def arcade():
    outline = [(-.36, 0), (.34, 0), (.39, .91), (.47, 1.06), (.43, 1.17),
               (.19, 1.20), (.05, 1.60), (.34, 1.71), (.31, 1.91), (-.36, 1.91)]
    for y in (-.38, .38):
        points = [(x, y + offset, z) for offset in (-.022, .022) for x, z in outline]
        n = len(outline)
        faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
        faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
        g.mesh("Shaped arcade side panel", points, faces, "blue", bevel=.01)
    g.box("Rear cabinet", (-.30, 0, .94), (.08, .72, 1.88), "black", .01)
    g.box("Front kick panel", (.29, 0, .48), (.09, .70, .93), "navy", .01)
    g.box("Coin door frame", (.345, 0, .64), (.035, .27, .31), mat="Living_Steel", bevel=.012)
    g.box("Coin door inset", (.367, 0, .64), (.02, .23, .27), "black", .009)
    g.box("Coin slot", (.381, -.047, .73), (.012, .075, .018), mat="Living_Steel", bevel=.003)
    g.box("Return flap", (.381, 0, .56), (.012, .085, .065), "gray", .003)
    g.box("Control deck", (.31, 0, 1.105), (.34, .72, .075), "black", .014)
    for y in (-.24, .07):
        g.cylinder("Joystick collar", (.30, y, 1.155), .044, .022, mat="Living_Steel")
        g.cylinder("Joystick shaft", (.30, y, 1.20), .011, .09, mat="Living_Steel")
        g.lathe("Joystick grip", [(.008, 1.225), (.027, 1.237), (.030, 1.259),
                                  (.014, 1.28), (.008, 1.28)], (.30, y, 0), "red", segments=16)
        for x, dy in ((.29, .11), (.37, .12), (.33, .17)):
            g.cylinder("Arcade pushbutton", (x, y + dy, 1.155), .021, .024, "yellow", vertices=16)
    g.box("Monitor bezel", (.095, 0, 1.43), (.045, .68, .40), "black", .015)
    g.box("Game display", (.122, 0, 1.44), (.012, .57, .31), "navy", .006)
    for row in range(4):
        for col in range(7):
            g.box("Game pixel target", (.131, -.22 + col * .073, 1.40 + row * .044),
                  (.007, .030, .020), "screen" if row % 2 else "pink", .001)
    g.box("Player paddle", (.132, .01, 1.317), (.008, .11, .012), "yellow", .001)
    g.box("Lightbox marquee", (.292, 0, 1.79), (.05, .70, .16), "teal", .008)
    for y in (-.23, 0, .23):
        g.cylinder("Marquee star disc", (.32, y, 1.79), .048, .012, "yellow", axis="X", vertices=5)
    g.box("Cabinet roof", (-.02, 0, 1.885), (.66, .73, .05), "blue", .009)
    for y in (-.31, .31):
        for x in (-.24, .24):
            g.cylinder("Levelling foot", (x, y, .023), .035, .046, mat="Living_Dark")
    return g.finish("ArcadeCabinet")
