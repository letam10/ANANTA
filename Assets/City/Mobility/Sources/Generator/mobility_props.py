"""Human scale street and harbour dressing with manufactured edges."""
import math
import bpy
from mobility_geometry import box, cylinder, beam, mesh, text_label, finish, uv
import geometry as g


def planter():
    box("Concrete plinth", (0, 0, .10), (1.24, 1.24, .20), "cream", .055)
    for side in (-1, 1):
        box("Planter wall X", (side * .57, 0, .49), (.14, 1.20, .68), "cream", .024)
        box("Planter wall Y", (0, side * .57, .49), (1.02, .14, .68), "cream", .024)
        for i in range(9):
            box("Vertical timber slat", (side * .657, -.50 + i * .125, .48), (.055, .074, .52), "wood")
    box("Soil bed", (0, 0, .75), (1.03, 1.03, .08), "soil")
    for i in range(15):
        angle = i * 2.399
        distance = .40 * math.sqrt(i / 15)
        x, y = math.cos(angle) * distance, math.sin(angle) * distance
        height = .40 + (i % 4) * .075
        beam("Plant stem", (x, y, .76), (x, y, .76 + height), .009, "Mobility_Enamel", "leaf")
        for j in range(3):
            a = angle + j * 2.1
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4,
                                                location=(x + .13 * math.cos(a), y + .13 * math.sin(a),
                                                          .88 + height * j / 4))
            obj = bpy.context.object
            obj.scale = (.23, .067, .024)
            obj.rotation_euler = (0, -.35, a)
            g.finish(obj, "Mobility_Enamel")
            for face in obj.data.polygons:
                face.use_smooth = True
            uv(obj, "leaf")
    return finish("DetailedPlanter")


def lamp():
    cylinder("Anchor base", (0, 0, .09), .23, .18, mat="Mobility_Steel")
    cylinder("Pole socket", (0, 0, .38), .14, .65, "navy")
    cylinder("Tapered mast", (0, 0, 3.65), .068, 6.4, "navy")
    for x in (-.13, .13):
        for y in (-.13, .13):
            cylinder("Anchor bolt", (x, y, .20), .026, .065, mat="Mobility_Steel", vertices=8)
    beam("Curved arm rise", (0, 0, 6.4), (.40, 0, 6.82), .060)
    beam("Luminaire arm", (.40, 0, 6.82), (1.40, 0, 6.82), .052)
    box("LED fixture shell", (1.52, 0, 6.78), (.81, .36, .14), "navy", .045)
    box("Diffuser lens", (1.52, 0, 6.701), (.69, .29, .025), "lamp")
    for x in (1.26, 1.4, 1.54, 1.68, 1.82):
        box("Heatsink fin", (x, 0, 6.88), (.035, .28, .06), mat="Mobility_Steel")
    box("Pole service hatch", (.071, 0, .83), (.024, .095, .29), mat="Mobility_Steel")
    return finish("DetailedStreetLamp")


def signal():
    box("Signal plinth", (0, 0, .12), (.46, .46, .24), "cream")
    cylinder("Traffic pole", (0, 0, 2.0), .077, 3.8, mat="Mobility_Steel")
    box("Signal backplate", (0, -.11, 3.36), (.56, .11, 1.49), "yellow", .06)
    box("Signal housing", (0, -.21, 3.36), (.41, .28, 1.34), mat="Mobility_Rubber")
    for z, color in ((3.78, "brake"), (3.36, "amber"), (2.94, "green")):
        cylinder("Lamp bezel", (0, -.377, z), .164, .045, axis="Y", mat="Mobility_Rubber")
        cylinder("Signal lens", (0, -.405, z), .132, .021, color, axis="Y")
        box("Rain hood", (0, -.46, z + .16), (.31, .26, .031), mat="Mobility_Rubber")
    box("Crossing request box", (0, -.13, 1.15), (.16, .14, .29), "yellow")
    cylinder("Crossing button", (0, -.211, 1.16), .043, .022, axis="Y", mat="Mobility_Steel")
    return finish("TrafficSignal")


def barrier():
    sections = [(-1.20, .29, .04, .82), (1.20, .29, .04, .82)]
    for x in (-1.02, 1.02):
        box("Barrier foot", (x, 0, .10), (.44, .73, .20), mat="Mobility_Rubber")
    box("Barrier body", (0, 0, .52), (2.48, .39, .73), "orange", .07)
    for side in (-1, 1):
        for x in (-.98, -.49, 0, .49, .98):
            box("Reflector patch", (x, side * .201, .66), (.24, .015, .21), "white")
        beam("Moulded stiffener", (-1.13, side * .207, .33), (1.13, side * .207, .33),
             .027, "Mobility_Enamel", "orange")
    for x in (-.81, .81):
        box("Grab handle recess", (x, 0, .88), (.35, .15, .08), mat="Mobility_Rubber")
    return finish("RoadBarrier")


def bollard():
    cylinder("Cast base", (0, 0, .06), .35, .12, mat="Mobility_Steel")
    cylinder("Mooring post", (0, 0, .39), .17, .65, "navy")
    cylinder("Flared cap", (0, 0, .75), .23, .13, "yellow")
    cylinder("Mooring crossbar", (0, 0, .59), .083, .74, "navy", axis="Y")
    for i in range(6):
        angle = i * math.tau / 6
        cylinder("Foundation bolt", (.26 * math.cos(angle), .26 * math.sin(angle), .14),
                 .028, .06, mat="Mobility_Steel", vertices=8)
    return finish("HarborBollard")


def bus_stop():
    box("Stop footing", (0, 0, .09), (.46, .46, .18), "cream")
    cylinder("Stop post", (0, 0, 1.65), .048, 3.22, mat="Mobility_Steel")
    box("Stop marker frame", (0, 0, 2.96), (.75, .13, .78), "teal", .045)
    box("Stop marker face", (0, -.074, 2.96), (.66, .023, .68), "cream")
    text_label("BUS", (0, -.09, 3.05), .21, color="teal")
    text_label("01 / 08", (0, -.09, 2.83), .12, color="navy")
    box("Timetable case", (0, -.035, 1.83), (.54, .11, .83), "teal")
    box("Timetable print", (0, -.099, 1.83), (.47, .016, .73), "cream")
    for i in range(6):
        box("Schedule row", (0, -.111, 2.09 - i * .103), (.37, .008, .016), "navy", .002)
    return finish("BusStopSign")
