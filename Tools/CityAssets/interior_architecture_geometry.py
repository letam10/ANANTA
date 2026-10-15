"""Four original interior fixtures in metres; visible front is negative Y."""
from geometry import box, cylinder, combine


def service_desk():
    box("Recessed graphite carcass", (0, 0.008, 0.447), (1.02, 0.60, 0.686), "Arch_Graphite", 0.007)
    for x in (-0.47, 0.47):
        for y in (-0.265, 0.265):
            box("Metal foot", (x, y, 0.061), (0.04, 0.04, 0.122), "Arch_Graphite", 0.003)
    for x in (-0.511, 0.511):
        box("Veneered side", (x, 0, 0.45), (0.028, 0.64, 0.696), "Arch_Oak", 0.004)
    for x in (-0.247, 0.247):
        box("Inset cabinet door", (x, -0.315, 0.454), (0.481, 0.028, 0.65), "Arch_Oak", 0.004)
        handle_x = x - (0.17 if x > 0 else -0.17)
        for z in (0.60, 0.71):
            cylinder("Handle standoff", (handle_x, -0.335, z), 0.004, 0.022,
                     "Arch_Brass", "Y", 10)
        cylinder("Brushed brass handle", (handle_x, -0.345, 0.655), 0.0045, 0.119,
                 "Arch_Brass", "Z", 12)
    box("Stone top slab", (0, 0, 0.825), (1.1, 0.7, 0.05), "Arch_Stone", 0.006)
    box("Brass shadow reveal", (0, 0, 0.794), (1.065, 0.66, 0.008), "Arch_Brass", 0.001)
    box("Recessed toe plinth", (0, 0.015, 0.10), (0.93, 0.51, 0.05), "Arch_Graphite", 0.003)
    return combine("InteriorServiceDesk")


def slat_panel():
    box("Acoustic dark backing", (0, 0.027, 1.1), (2.40, 0.026, 2.2), "Arch_Graphite", 0.002)
    for index in range(30):
        x = -1.122 + index * 2.244 / 29
        box("Solid oak slat", (x, -0.009, 1.10), (0.042, 0.062, 2.14), "Arch_Oak", 0.003)
    for x in (-1.191, 1.191):
        box("Side frame", (x, 0, 1.1), (0.018, 0.079, 2.2), "Arch_Graphite", 0.002)
    for z in (0.009, 2.191):
        box("Thin frame rail", (0, 0, z), (2.36, 0.079, 0.018), "Arch_Graphite", 0.002)
    return combine("InteriorSlatPanel")


def art_frame(identifier, art_material):
    box("Frame rear board", (0, 0.019, 0.55), (1.4, 0.022, 1.10), "Arch_Graphite", 0.002)
    for x in (-0.684, 0.684):
        box("Brushed frame stile", (x, -0.008, 0.55), (0.032, 0.044, 1.10), "Arch_Brass", 0.002)
    for z in (0.016, 1.084):
        box("Brushed frame rail", (0, -0.008, z), (1.336, 0.044, 0.032), "Arch_Brass", 0.002)
    box("Passe partout", (0, -0.003, 0.55), (1.334, 0.014, 1.034), "Arch_Matboard", 0.001)
    box("Original archival print", (0, -0.012, 0.55), (1.17, 0.003, 0.804375), art_material, 0)
    obj = combine(identifier)
    uv = obj.data.uv_layers.active
    for face in obj.data.polygons:
        if obj.material_slots[face.material_index].material.name != art_material:
            continue
        if face.normal.y < -0.9:
            for index in face.loop_indices:
                co = obj.data.vertices[obj.data.loops[index].vertex_index].co
                uv.data[index].uv = ((co.x + 0.585) / 1.17, (co.z - 0.1478125) / 0.804375)
    return obj
