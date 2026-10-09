"""Twin truss rims, cable spokes, bearings and eight enclosed hanging cabins."""
import math
from ferris_geometry import beam, box, cylinder, ring, slab, combine

HUB = 18.35
RADIUS = 15.35


def point(x, radius, angle):
    return (x, radius * math.cos(angle), HUB + radius * math.sin(angle))


def supports():
    for side in (-1, 1):
        x = side * 4.6
        for y in (-6.6, 6.6):
            box('Foundation plinth', (x, y, .25), (2.2, 2.4, .5), 'Ivory', .09)
            box('Bolted base plate', (x, y, .56), (1.45, 1.65, .12), 'Steel')
            beam('Tapered A frame leg', (x, y, .65), (side * 2.7, 0, HUB), .34, 'Teal', 24)
            for dx in (-.5, .5):
                for dy in (-.6, .6):
                    cylinder('Anchor hex bolt', (x + dx, y + dy, .68), .095, .12, vertices=6)
        beam('A frame cross brace', (side * 4.05, -4.45, 6.3),
             (side * 4.05, 4.45, 6.3), .16, 'Ivory')
        cylinder('Main bearing housing', (side * 2.65, 0, HUB), .91, .72, 'Teal', 'X', 48)
        cylinder('Bearing flange', (side * 3.04, 0, HUB), .77, .15, 'Steel', 'X', 48)
        for index in range(12):
            angle = index * math.tau / 12
            cylinder('Bearing flange bolt', (side * 3.14, .63 * math.cos(angle),
                                             HUB + .63 * math.sin(angle)), .065, .10,
                     'Steel', 'X', 6)
    cylinder('Main axle', (0, 0, HUB), .4, 6.5, 'Steel', 'X', 48)
    for y in (-6.6, 6.6):
        beam('Base transverse tie', (-4.6, y, .65), (4.6, y, .65), .20, 'Teal')


def wheel():
    for x in (-1.5, 1.5):
        ring('Outer continuous tubular rim', x, RADIUS, .15)
        ring('Inner continuous tubular rim', x, 14.70, .10, 'Teal')
        cylinder('Spoke hub drum', (x, 0, HUB), .66, .5, 'Coral', 'X', 48)
        for index in range(32):
            angle = index * math.tau / 32
            beam('Radial tension spoke', point(x, .65, angle), point(x, 14.70, angle), .055, 'Steel', 10)
            beam('Rim radial strut', point(x, 14.70, angle), point(x, RADIUS, angle), .065, 'Ivory', 10)
            if index % 4 == 0:
                cylinder('Cabin pivot flange', point(x, 15.10, angle), .28, .18, 'Coral', 'X', 24)
    for index in range(32):
        angle = index * math.tau / 32
        next_angle = (index + 1) * math.tau / 32
        beam('Rim cross member', point(-1.5, RADIUS, angle), point(1.5, RADIUS, angle), .065, 'Steel', 10)
        beam('Rim diagonal lattice', point(-1.5, 14.70, angle),
             point(1.5, 14.70, next_angle), .05, 'Ivory', 8)


def cabin(index):
    angle = index * math.tau / 8
    _, y, pivot = point(0, 15.10, angle)
    bottom = pivot - 2.60
    colour = 'Coral' if index % 2 else 'Teal'
    prefix = f'Cabin {index + 1:02d} '
    cylinder(prefix + 'suspension axle', (0, y, pivot), .105, 3.55, 'Steel', 'X', 24)
    for x in (-1.15, 1.15):
        beam(prefix + 'suspension hanger', (x, y, pivot), (x, y, pivot - .40), .10, 'Steel')
        cylinder(prefix + 'hanger bearing', (x, y, pivot), .19, .15, 'Steel', 'X', 20)
    # Cabin bat giac: kinh kin nam giua cot va thanh ngang, mai phu het cac goc.
    corners = [(-1.25, -.72), (-.86, -1.10), (.86, -1.10), (1.25, -.72),
               (1.25, .72), (.86, 1.10), (-.86, 1.10), (-1.25, .72)]
    for dx, dy in corners:
        beam(prefix + 'window mullion', (dx, y + dy, bottom + .66),
             (dx, y + dy, bottom + 2.08), .045, 'Ivory', 8)
    for j, start in enumerate(corners):
        end = corners[(j + 1) % 8]
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        centre = ((start[0] + end[0]) / 2, y + (start[1] + end[1]) / 2)
        for label, z, height, material, thick in (
                ('lower panel', .40, .56, colour, .08),
                ('sealed window', 1.35, 1.26, 'Glass', .025),
                ('waist rail', .69, .08, 'Ivory', .07),
                ('top rail', 2.03, .08, 'Ivory', .07)):
            panel = box(prefix + label, (*centre, bottom + z), (length, thick, height), material, .008)
            panel.rotation_euler.z = math.atan2(dy, dx)
    for z, depth, material in ((.07, .14, 'Steel'), (2.15, .18, colour), (2.28, .08, 'Ivory')):
        outline = [(x * 1.06, dy * 1.06) for x, dy in corners]
        slab(prefix + 'octagonal floor or roof', (0, y, bottom + z), outline, depth, material)
    for dx in (-.77, .77):
        box(prefix + 'bench cushion', (dx, y, bottom + .49), (.52, 1.35, .16), colour)
        box(prefix + 'bench back', (dx * 1.16, y, bottom + .81), (.13, 1.35, .52), colour)
    box(prefix + 'door centre stile', (1.27, y, bottom + 1.18), (.065, .045, 1.85), 'Ivory', .008)
    box(prefix + 'door handle', (1.32, y + .14, bottom + 1.05), (.065, .06, .27), 'Steel', .012)
    for z in (.36, 1.78):
        box(prefix + 'door hinge', (1.30, y - .66, bottom + z), (.08, .12, .15), 'Steel', .012)


def build():
    supports()
    wheel()
    for index in range(8):
        cabin(index)
    return combine()
