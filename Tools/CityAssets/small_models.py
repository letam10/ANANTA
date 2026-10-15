"""Original compact room props, dimensioned in metres; local front +X."""
import math
import living_geometry as g


def handle_arc(name, center, radius, thickness, axis="X", sign=1, color=None):
    # Tay cam chi uon nua vong phia ngoai, khong xuyen vao long coc/noi.
    points = []
    steps, sides = 16, 6
    for row in range(steps + 1):
        angle = math.radians(-100 + 200 * row / steps)
        for side in range(sides):
            phase = math.tau * side / sides
            radial = radius + thickness * math.cos(phase)
            outward = center[0] + radial * math.cos(angle)
            cross = thickness * math.sin(phase)
            height = center[1] + radial * math.sin(angle)
            points.append((outward, cross, height) if axis == "X" else (cross, sign * outward, height))
    faces = []
    for row in range(steps):
        for side in range(sides):
            following = (side + 1) % sides
            faces.append((row * sides + side, row * sides + following,
                          (row + 1) * sides + following, (row + 1) * sides + side))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple(steps * sides + side for side in range(sides)))
    obj = g.mesh(name, points, faces, color=color or "white", mat=None if color else "Living_Steel")
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def vessel(name, radius, height, color="white", metal=False):
    wall = .003
    profile = [(0, 0), (radius * .84, 0), (radius, height * .16),
               (radius, height - .002), (radius - .001, height),
               (radius - wall, height), (radius - wall, height * .18),
               (radius * .80, .006), (0, .006)]
    return g.lathe(name, profile, color=color, mat="Living_Steel" if metal else None, segments=32)


def cooking_pot():
    vessel("Hollow stainless pot", .11, .125, metal=True)
    for sign in (-1, 1):
        handle_arc("External pot handle", (.114, .084), .025, .006, axis="Y", sign=sign)
    return g.finish("CookingPot")


def saucepan():
    vessel("Open saucepan", .09, .075, metal=True)
    g.box("Riveted steel neck", (.108, 0, .057), (.045, .023, .012),
          mat="Living_Steel", bevel=.002)
    g.box("Long insulated handle", (.191, 0, .059), (.158, .03, .022),
          mat="Living_Dark", bevel=.007)
    return g.finish("Saucepan")


def kitchen_bowl():
    profile = [(0, 0), (.038, 0), (.051, .008), (.072, .034), (.085, .063),
               (.085, .067), (.081, .067), (.077, .049), (.063, .026),
               (.043, .009), (0, .009)]
    g.lathe("Glazed hollow bowl", profile, color="cream", segments=32)
    return g.finish("KitchenBowl")


def coffee_mug():
    vessel("Ceramic mug", .04, .10, color="teal")
    handle_arc("External ceramic handle", (.044, .054), .026, .006, color="teal")
    return g.finish("CoffeeMug")


def makeup_compact():
    g.cylinder("Compact base", (0, 0, .007), .035, .014, color="pink", vertices=32)
    g.cylinder("Pressed powder", (0, 0, .015), .029, .004, color="cream", vertices=32)
    lid = g.cylinder("Open compact lid", (-.027, 0, .042), .035, .007,
                     color="pink", axis="X", vertices=32)
    lid.rotation_euler.y = math.radians(70)
    mirror = g.cylinder("Inset metal mirror", (-.0215, 0, .042), .030, .0015,
                        mat="Living_Steel", axis="X", vertices=32)
    mirror.rotation_euler.y = math.radians(70)
    g.box("Hinge", (-.030, 0, .014), (.012, .025, .012), mat="Living_Dark", bevel=.002)
    return g.finish("MakeupCompact")


def toy_blocks():
    for x, y, z, color in [(-.075, -.027, .025, "red"), (-.021, -.027, .025, "blue"),
                           (.033, -.027, .025, "yellow"), (.075, .030, .025, "green"),
                           (-.048, -.027, .075, "orange"), (.010, .029, .025, "teal")]:
        g.box("Colored wooden block", (x, y, z), (.05, .05, .05), color=color, bevel=.003)
    return g.finish("ToyBlocks")


def room_vase():
    profile = [(0, 0), (.039, 0), (.047, .01), (.06, .06), (.055, .11),
               (.035, .16), (.026, .195), (.031, .216), (.031, .22),
               (.027, .22), (.022, .194), (.031, .16), (.050, .109),
               (.055, .06), (.039, .009), (0, .009)]
    g.lathe("Hollow glazed vase", profile, color="blue", segments=32)
    return g.finish("RoomVase")


def bathroom_soap():
    g.box("Soap dish base", (0, 0, .005), (.12, .082, .01), color="white", bevel=.004)
    for sign in (-1, 1):
        g.box("Raised dish side", (0, sign * .037, .013), (.112, .008, .015),
              color="white", bevel=.003)
        g.box("Raised dish end", (sign * .056, 0, .013), (.008, .072, .015),
              color="white", bevel=.003)
    g.box("Rounded soap bar", (0, 0, .027), (.086, .051, .026), color="cream", bevel=.011)
    return g.finish("BathroomSoap")


BUILDERS = [cooking_pot, saucepan, kitchen_bowl, coffee_mug,
            makeup_compact, toy_blocks, room_vase, bathroom_soap]
