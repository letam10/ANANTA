"""Street furniture and an original compact electric sedan, metres and X forward."""
import math
from geometry import box, cylinder, beam, profile, combine, leaf, wheel_arches


def lamp():
    cylinder("Anchor base", (0, 0, 0.09), 0.25, 0.18, "Dark")
    cylinder("Pole collar", (0, 0, 0.45), 0.13, 0.72, "Dark")
    cylinder("Lamp pole", (0, 0, 2.5), 0.067, 4.3, "Dark")
    beam("Lamp arm", (0, 0, 4.60), (0, -1.0, 4.82), 0.058, "Dark")
    box("Lamp head", (0, -1.0, 4.78), (0.36, 0.75, 0.12), "Dark", 0.045)
    box("LED lens", (0, -1.02, 4.706), (0.28, 0.58, 0.024), "Light")
    for x in [-0.13, 0.13]:
        for y in [-0.13, 0.13]:
            cylinder("Anchor bolt", (x, y, 0.194), 0.024, 0.027, "Aluminium", vertices=6)
    return combine("StreetLamp")


def bench():
    for x in [-0.70, 0.70]:
        for y in [-0.21, 0.23]:
            box("Bench leg", (x, y, 0.23), (0.08, 0.08, 0.46), "Dark")
        beam("Back leg", (x, 0.20, 0.32), (x, 0.35, 0.90), 0.034, "Dark")
        box("Seat bearer", (x, 0, 0.42), (0.065, 0.60, 0.06), "Dark")
        beam("Armrest", (x, -0.23, 0.69), (x, 0.28, 0.73), 0.032, "Dark")
        beam("Armrest post", (x, -0.23, 0.44), (x, -0.23, 0.69), 0.026, "Dark")
    for y in [-0.23, -0.115, 0, 0.115, 0.23]:
        box("Timber seat slat", (0, y, 0.47), (1.8, 0.10, 0.045), "Wood")
    for z in [0.63, 0.75, 0.87]:
        box("Timber back slat", (0, 0.31, z), (1.80, 0.05, 0.10), "Wood")
    return combine("Bench")


def bollard():
    cylinder("Bollard base", (0, 0, 0.04), 0.16, 0.08, "Dark")
    cylinder("Bollard", (0, 0, 0.44), 0.085, 0.88, "Dark")
    cylinder("Reflective collar", (0, 0, 0.74), 0.087, 0.07, "Light")
    cylinder("Bollard cap", (0, 0, 0.90), 0.10, 0.05, "Aluminium")
    return combine("Bollard")


def planter():
    box("Planter base", (0, 0, 0.10), (1.40, 0.70, 0.20), "Stone", 0.04)
    for y in [-0.33, 0.33]:
        box("Planter wall", (0, y, 0.40), (1.4, 0.12, 0.60), "Stone", 0.02)
    for x in [-0.64, 0.64]:
        box("Planter return", (x, 0, 0.40), (0.12, 0.58, 0.60), "Stone", 0.02)
    box("Soil", (0, 0, 0.61), (1.18, 0.45, 0.08), "Soil")
    for i in range(9):
        x = -0.53 + i * 0.13
        for j in range(3):
            y = -0.17 + j * 0.17
            top = 0.91 + 0.13 * math.sin(i * 5 + j)
            beam("Stem", (x, y, 0.65), (x + 0.04, y, top), 0.012, "Foliage")
            for side in [-1, 1]:
                leaf((x + side * 0.08, y, top - 0.06), (0.115, 0.05, 0.012), side * 0.30)
                leaf((x + side * 0.06, y + 0.015, top - 0.19), (0.09, 0.042, 0.01), side * 0.50)
    return combine("Planter")


def car():
    body = profile("Lower body", [(-2.20, 0.72, 0.36, 0.66), (-1.86, 0.89, 0.30, 0.83),
                            (-0.8, 0.93, 0.30, 0.87), (0.75, 0.91, 0.30, 0.88),
                            (1.83, 0.83, 0.34, 0.74), (2.22, 0.69, 0.41, 0.64)], "CarPaint", 0.07)
    wheel_arches(body)
    profile("Cabin glass", [(-1.24, 0.79, 0.81, 0.90), (-0.66, 0.69, 0.86, 1.41),
                             (0.45, 0.67, 0.87, 1.42), (1.18, 0.78, 0.84, 0.89)], "Glass", 0.035)
    profile("Roof", [(-0.72, 0.68, 1.37, 1.43), (-0.55, 0.70, 1.42, 1.47),
                      (0.36, 0.67, 1.43, 1.48), (0.53, 0.64, 1.38, 1.44)], "CarPaint", 0.03)
    for side in [-1, 1]:
        for bottom, top in [((-1.20, side * 0.78, 0.86), (-0.65, side * 0.69, 1.40)),
                            ((1.15, side * 0.78, 0.87), (0.46, side * 0.67, 1.41)),
                            ((-0.14, side * 0.89, 0.86), (-0.14, side * 0.69, 1.43))]:
            beam("Cabin pillar", bottom, top, 0.037, "CarPaint")
        box("Sill trim", (0, side * 0.926, 0.40), (2.8, 0.035, 0.10), "Dark", 0.01)
        box("Waist trim", (0, side * 0.918, 0.88), (2.65, 0.025, 0.025), "Aluminium", 0.005)
        for x in [-0.58, 0.63]:
            box("Door handle", (x, side * 0.92, 0.78), (0.17, 0.035, 0.034), "Aluminium")
        beam("Door seam", (-0.13, side * 0.935, 0.43), (-0.13, side * 0.935, 0.86), 0.005, "Dark")
        beam("Mirror stalk", (0.71, side * 0.84, 0.96), (0.68, side * 1.03, 1.02), 0.027, "Dark")
        box("Mirror housing", (0.69, side * 1.04, 1.04), (0.24, 0.15, 0.11), "CarPaint", 0.038)
        for x in [-1.40, 1.38]:
            cylinder("Rubber tyre", (x, side * 0.87, 0.34), 0.34, 0.24, "Rubber", "Y", 40)
            cylinder("Wheel rim", (x, side * 1.001, 0.34), 0.235, 0.028, "Aluminium", "Y", 32)
            cylinder("Brake disc", (x, side * 1.020, 0.34), 0.175, 0.012, "Dark", "Y", 32)
            cylinder("Hub", (x, side * 1.037, 0.34), 0.066, 0.035, "Aluminium", "Y", 20)
            for spoke in range(8):
                angle = spoke * math.pi / 4
                beam("Alloy spoke", (x, side * 1.037, 0.34),
                     (x + 0.21 * math.cos(angle), side * 1.038, 0.34 + 0.21 * math.sin(angle)),
                     0.019, "Aluminium")
    box("Front lower grille", (2.195, 0, 0.47), (0.055, 1.08, 0.12), "Dark")
    for side in [-1, 1]:
        box("Headlight", (2.185, side * 0.49, 0.65), (0.07, 0.34, 0.072), "Light", 0.025)
        box("Tail light", (-2.182, side * 0.47, 0.67), (0.055, 0.39, 0.074), "Red", 0.025)
    for x in [-2.225, 2.235]:
        box("Registration plate", (x, 0, 0.53), (0.018, 0.38, 0.09), "Light", 0.005)
    return combine("CarBody")
