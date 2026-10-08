"""Manufactured fixture geometry in metres, with four slots per model."""
import bpy
import geometry as g
from workshop_detail_geometry import box, cylinder

COAT = "VenueFixture_Enamel"
TEAL = "VenueFixture_Teal"
STEEL = "VenueFixture_Steel"
LABEL = "VenueFixture_SupplyLabels"
GUIDE = "VenueFixture_Guide"

def print_panel(name, x, y, z, width, height, material, row=None):
    vertices = [(x - width / 2, y, z - height / 2), (x + width / 2, y, z - height / 2),
                (x + width / 2, y, z + height / 2), (x - width / 2, y, z + height / 2)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.materials.append(g.MATERIALS[material])
    uv = mesh.uv_layers.new(name="UVMap")
    low, high = (0, 1) if row is None else (1 - (row + 1) / 4, 1 - row / 4)
    for loop, value in zip(uv.data, ((0, low), (1, low), (1, high), (0, high))):
        loop.uv = value
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["printed"] = True
    g.PARTS.append(obj)

def screw(x, y, z, radius=.006):
    cylinder("Recessed screw head", (x, y, z), radius, .003, STEEL, "Y", 8)
    box("Screw slot", (x, y - .0017, z), (radius * 1.3, .0006, .0012), TEAL, 0)

def combine(name):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in g.PARTS:
        if obj.get("printed"):
            continue
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
        for face in obj.data.polygons:
            axis = max(range(3), key=lambda i: abs(face.normal[i]))
            for index in face.loop_indices:
                co = obj.data.vertices[obj.data.loops[index].vertex_index].co
                pair = (co.y, co.z) if axis == 0 else (co.x, co.z) if axis == 1 else (co.x, co.y)
                uv.data[index].uv = pair
        obj.select_set(False)
    return g.combine(name, tile_uv=False)

def cabinet():
    for x in (-1.02, 1.02):
        for y in (-.24, .25):
            box("Adjustable cabinet foot", (x, y, .045), (.13, .15, .09), TEAL, .005)
    box("Recessed kick plate", (0, -.225, .12), (2.17, .045, .11), TEAL, .003)
    box("Cabinet folded rear", (0, .35, .98), (2.26, .04, 1.66), COAT, .003)
    for x in (-1.1275, 1.1275):
        box("Folded side casing", (x, .025, .9775), (.045, .65, 1.665), COAT, .005)
    box("Full width top", (0, .0275, 1.8175), (2.3, .685, .045), COAT, .006)
    box("Cabinet bottom", (0, .025, .17), (2.27, .65, .045), COAT, .004)
    box("Upper identity rail", (0, -.30, 1.755), (2.23, .034, .077), TEAL, .003)
    print_panel("Clinic identification", 0, -.318, 1.755, 1.12, .060, LABEL, 0)
    for i, x in enumerate((-.75, 0, .75)):
        box("Door shadow reveal", (x, -.293, .959), (.728, .02, 1.512), TEAL, .002)
        box("Upper folded door", (x, -.31, 1.145), (.70, .035, 1.11), COAT, .005)
        box("Recessed enamel insert", (x - .035, -.329, 1.155), (.54, .007, .946), TEAL, .003)
        box("Static lower drawer", (x, -.314, .391), (.70, .036, .342), COAT, .004)
        print_panel("Supply compartment label", x - .035, -.334, 1.43, .485, .12125, LABEL, i + 1)
        for z in (.70, 1.57):
            cylinder("Door hinge pin", (x - .324, -.332, z), .009, .075, STEEL, vertices=10)
            box("Hinge leaf", (x - .306, -.328, z), (.043, .008, .059), STEEL, .001)
        for z in (.96, 1.16):
            box("Handle mounting foot", (x + .23, -.344, z), (.025, .030, .026), STEEL, .003)
        box("Brushed vertical handle", (x + .23, -.359, 1.06), (.027, .022, .23), STEEL, .007)
        for z in (.955, 1.165):
            screw(x + .23, -.359, z)
        box("Drawer pull rail", (x, -.354, .45), (.24, .024, .026), STEEL, .004)
        for dx in (-.10, .10):
            box("Drawer pull bracket", (x + dx, -.338, .45), (.027, .024, .028), STEEL, .002)
        cylinder("Door lock escutcheon", (x + .23, -.333, 1.31), .012, .008, STEEL, "Y", 12)
        box("Key slot", (x + .23, -.338, 1.31), (.002, .002, .013), TEAL, 0)
        for dx in (-.13, -.065, 0, .065, .13):
            box("Drawer ventilation pressed recess", (x + dx, -.333, .293), (.034, .002, .004), TEAL, .001)
    return combine("ClinicSupplyCabinet")

def display():
    box("Closed display rear tray", (0, .045, .75), (3.64, .10, 1.44), TEAL, .006)
    for x in (-1.82, 1.82):
        box("Extruded aluminium side rail", (x, -.018, .75), (.06, .164, 1.50), STEEL, .005)
        box("Painted side insert", (x, -.103, .75), (.025, .014, 1.39), TEAL, .002)
    for z in (.03, 1.47):
        box("Extruded aluminium cross rail", (0, -.018, z), (3.58, .164, .06), STEEL, .005)
    box("Continuous protective gasket", (0, -.087, .75), (3.59, .022, 1.39), TEAL, .004)
    box("Matte print backing", (0, -.102, .75), (3.51, .012, 1.31625), COAT, .002)
    print_panel("Protected neighborhood guide", 0, -.109, .75, 3.48, 1.305, GUIDE)
    for x in (-1.42, 1.42):
        for z in (.27, 1.23):
            box("Wall mounting standoff", (x, .1075, z), (.15, .025, .14), STEEL, .004)
    for x in (-1.82, 1.82):
        for z in (.09, 1.41):
            cylinder("Flush captive screw", (x, -.117, z), .009, .006, STEEL, "Y", 10)
            box("Captive screw slot", (x, -.1199, z), (.010, .0002, .002), TEAL, 0)
    return combine("TransitRouteDisplay")
