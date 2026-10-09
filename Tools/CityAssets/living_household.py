"""Recognizable appliances and light fittings with original manufactured components."""
import math
import living_geometry as g


def ceiling_fan():
    g.lathe("Ceiling canopy", [(.025, 0), (.11, 0), (.11, -.025), (.065, -.075), (.025, -.075)])
    g.cylinder("Down rod", (0, 0, -.20), .022, .29, mat="Living_Steel")
    g.lathe("Motor housing", [(.02, -.30), (.12, -.30), (.15, -.35), (.14, -.43), (.02, -.46)])
    for i in range(5):
        angle = i * math.tau / 5
        c, s = math.cos(angle), math.sin(angle)
        points = [(r * c - y * s, r * s + y * c, z)
                  for z in (-.384, -.396)
                  for r, y in ((.13, -.043), (.64, -.095), (.70, .065), (.28, .085))]
        faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        g.mesh("Swept timber blade", points, faces, "wood", bevel=.004)
        g.beam("Blade bracket", (.10 * c, .10 * s, -.39), (.26 * c, .26 * s, -.39), .013)
    for i in range(16):
        a = i * math.tau / 16
        g.box("Motor vent", (.137 * math.cos(a), .137 * math.sin(a), -.363),
              (.014, .014, .035), "black", bevel=.002)
    g.lathe("Light diffuser", [(.015, -.445), (.10, -.445), (.105, -.47), (.08, -.51), (.015, -.52)],
            color="lamp")
    g.beam("Pull chain", (.08, 0, -.44), (.08, 0, -.66), .0025)
    g.cylinder("Pull toggle", (.08, 0, -.68), .012, .035, "wood", vertices=12)
    return g.finish("CeilingFan")


def table_lamp():
    g.lathe("Weighted base", [(.015, 0), (.14, 0), (.16, .016), (.145, .038), (.025, .06)],
            color="teal")
    g.cylinder("Base trim", (0, 0, .015), .156, .012, mat="Living_Steel")
    g.cylinder("Lamp stem", (0, 0, .26), .018, .40, mat="Living_Steel")
    g.cylinder("Socket", (0, 0, .44), .035, .07, "cream")
    g.lathe("Bulb", [(.012, .455), (.042, .49), (.046, .53), (.025, .56), (.006, .563)], color="lamp")
    g.lathe("Hollow linen shade", [(.205, .34), (.12, .65), (.113, .65), (.198, .34)], mat="Living_Linen")
    for z, radius in ((.342, .202), (.648, .116)):
        g.torus("Shade rolled edge", (0, 0, z), radius, .004)
    for a in (0, math.tau / 3, math.tau * 2 / 3):
        g.beam("Shade spider", (0, 0, .59), (.12 * math.cos(a), .12 * math.sin(a), .64), .003)
    g.cylinder("Finial", (0, 0, .673), .014, .029, mat="Living_Steel")
    g.box("Switch", (.018, 0, .405), (.022, .02, .027), "black", .004)
    g.tube("Power cable", [(-.11, 0, .017), (-.22, .02, .008), (-.30, .08, .008)], .004, "Living_Dark")
    return g.finish("TableLamp")


def air_conditioner():
    g.box("Mount backplate", (-.105, 0, .16), (.03, .81, .25), "gray", .012)
    g.box("Rounded split unit", (0, 0, .17), (.24, .90, .32), "white", .045)
    g.box("Lower outlet cavity", (.119, 0, .072), (.017, .76, .075), "black", .010)
    for z in (.050, .077, .10):
        g.box("Angled outlet louver", (.134, 0, z), (.025, .72, .007), "cream", .002)
    for y in (-.28, -.14, 0, .14, .28):
        g.box("Outlet vane", (.134, y, .078), (.028, .004, .065), "gray", .001)
    g.box("Front face seam", (.122, 0, .25), (.004, .81, .004), "gray", .001)
    g.box("Status display", (.125, -.28, .16), (.006, .075, .029), "navy", .003)
    g.box("Power indicator", (.13, -.30, .16), (.005, .011, .004), "green", .001)
    for y in [i * .033 for i in range(-11, 12)]:
        g.box("Top air intake", (-.025, y, .327), (.10, .009, .006), "gray", .001)
    return g.finish("WallAirConditioner")


def refrigerator():
    g.box("Insulated cabinet", (-.018, 0, .90), (.66, .76, 1.72), "white", .033)
    g.box("Door seal reveal", (.316, 0, .90), (.02, .719, 1.64), "black", .018)
    for y in (-.18, .18):
        g.box("Upper french door", (.354, y, 1.22), (.08, .351, 1.02), "white", .014)
        g.beam("Handle upper", (.42, y * .29, .99), (.42, y * .29, 1.51), .018)
        for z in (.99, 1.51):
            g.beam("Handle standoff", (.39, y * .29, z), (.42, y * .29, z), .014)
    g.box("Freezer drawer", (.352, 0, .39), (.08, .71, .56), "white", .014)
    g.beam("Freezer handle", (.43, -.26, .57), (.43, .26, .57), .018)
    g.box("Ice dispenser recess", (.399, -.20, 1.20), (.012, .20, .29), "black", .016)
    g.box("Dispenser tray", (.435, -.20, 1.065), (.085, .20, .015), mat="Living_Steel")
    g.box("Dispenser control", (.408, -.20, 1.365), (.013, .16, .049), "navy", .004)
    for i in range(4):
        g.box("Temperature segment", (.417, -.24 + i * .025, 1.365), (.008, .008, .020), "screen", .001)
    for y in (-.26, .26):
        for x in (-.25, .25):
            g.cylinder("Adjustable foot", (x, y, .027), .035, .054, mat="Living_Dark")
    for y in [i * .045 for i in range(-7, 8)]:
        g.box("Kick grille", (.321, y, .08), (.012, .013, .040), "black", .002)
    return g.finish("Refrigerator")


def microwave():
    g.box("Enamel shell", (0, 0, .175), (.38, .55, .30), "cream", .013)
    g.box("Door reveal", (.193, -.046, .182), (.018, .418, .263), "black", .008)
    g.box("Metal door surround", (.207, -.048, .182), (.020, .391, .242), mat="Living_Steel")
    g.box("Screened glass window", (.220, -.066, .184), (.009, .284, .165), "navy", .005)
    for row in range(7):
        for col in range(12):
            g.box("Window shielding mesh", (.226, -.191 + col * .022, .12 + row * .021),
                  (.002, .012, .011), "black", .001)
    g.beam("Door pull", (.26, .12, .09), (.26, .12, .273), .013)
    g.box("Timer window", (.198, .224, .25), (.012, .063, .045), "navy", .003)
    for z in (.18, .14, .10):
        for y in (.204, .24):
            g.box("Keypad button", (.205, y, z), (.018, .026, .024), "gray", .003)
    g.cylinder("Control dial", (.209, .225, .065), .020, .015, axis="X", mat="Living_Steel")
    for i in range(9):
        g.box("Side vent slit", (-.06 + i * .022, -.278, .19), (.009, .005, .13), "black", .001)
    for y in (-.2, .2):
        for x in (-.12, .12):
            g.cylinder("Rubber foot", (x, y, .013), .021, .026, mat="Living_Dark")
    return g.finish("Microwave")


def kitchen_sink():
    # Bon rua co long rong, day va thanh rieng; khong lap mat kin tren mieng.
    points = []
    for z in (.2175, .2425):
        for x, y in ((-.30, -.355), (.30, -.355), (.30, .355), (-.30, .355),
                     (-.2325, -.3025), (.2325, -.3025), (.2325, .3025), (-.2325, .3025)):
            points.append((x, y, z))
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        faces.extend([(i, j, j + 4, i + 4), (i + 8, i + 12, j + 12, j + 8),
                      (i, i + 8, j + 8, j), (i + 4, j + 4, j + 12, i + 12)])
    g.mesh("Continuous sink rim", points, faces, mat="Living_Steel", bevel=.002)
    for y in (-.33, .33):
        g.box("Basin side wall", (0, y * .89, .12), (.51, .032, .20), mat="Living_Steel")
    for x in (-.27, .27):
        g.box("Basin end wall", (x * .88, 0, .12), (.035, .56, .20), mat="Living_Steel")
    g.box("Basin floor", (0, 0, .028), (.48, .56, .056), mat="Living_Steel", bevel=.023)
    g.cylinder("Drain black well", (0, 0, .060), .052, .008, "black")
    g.torus("Drain collar", (0, 0, .064), .049, .004)
    for y in (-.024, 0, .024):
        g.beam("Drain strainer", (-.03, y, .066), (.03, y, .066), .003)
    path = [(-.27, .13, .24), (-.27, .13, .46), (-.25, .13, .53),
            (-.19, .13, .56), (-.12, .13, .53), (-.10, .13, .47)]
    g.tube("Gooseneck mixer", path, .018)
    g.cylinder("Faucet base", (-.27, .13, .27), .028, .07, mat="Living_Steel")
    g.beam("Mixer lever", (-.27, .10, .30), (-.20, .06, .32), .010)
    g.cylinder("Aerator", (-.10, .13, .465), .023, .025, mat="Living_Steel")
    return g.finish("KitchenSink")
