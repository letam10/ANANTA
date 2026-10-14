"""Ground-floor wall apertures, generated from widths rather than facade decals."""

import math


def ground_wall(scene, position, length, color, yaw=0, doorway=False):
    center_x, center_y, ground = position
    angle = math.radians(yaw)
    cosine, sine = math.cos(angle), math.sin(angle)

    def piece(horizontal, depth, height, width, thickness, tall, material, collision=True):
        scene.box((center_x + cosine * horizontal - sine * depth,
                   center_y + sine * horizontal + cosine * depth, ground + height),
                  (width, thickness, tall), material, yaw=yaw, collision=collision)

    window_width = min(3.6, length * 0.18)
    openings = [(side * length / 4 - window_width / 2, side * length / 4 + window_width / 2,
                 0.9, 2.4, True) for side in (-1, 1)]
    if doorway:
        openings.append((-0.49, 0.49, 0, 2.35, False))
    edge = -length / 2
    for lower, upper, sill, top, window in sorted(openings):
        piece((edge + lower) / 2, 0, 1.6, lower - edge, 0.22, 3.2, color)
        width = upper - lower
        if sill:
            piece((lower + upper) / 2, 0, sill / 2, width, 0.22, sill, color)
        piece((lower + upper) / 2, 0, (top + 3.2) / 2, width, 0.22, 3.2 - top, color)
        if window:
            midpoint = (lower + upper) / 2
            piece(midpoint, 0, (sill + top) / 2, width - 0.08, 0.008,
                  top - sill - 0.08, "WindowGlass", False)
            for horizontal in (lower + 0.025, midpoint, upper - 0.025):
                piece(horizontal, 0, (sill + top) / 2, 0.05, 0.23, top - sill, "White", False)
            for height in (sill, top):
                piece(midpoint, 0, height, width + 0.1, 0.3, 0.06, "White", False)
        edge = upper
    piece((edge + length / 2) / 2, 0, 1.6, length / 2 - edge, 0.22, 3.2, color)
