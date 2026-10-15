"""Simple room props; silhouettes carry detail at third-person viewing distance."""

import math

from meshlib import box, cylinder, ellipsoid, finish, lathe, rod


def furniture():
    objects = []
    box((2.2, 0.95, 0.25), (0, 0, 0.35), "wood", 0.08)
    for x in (-0.72, 0, 0.72):
        box((0.68, 0.76, 0.23), (x, 0, 0.55), "fabric", 0.09)
    box((2.2, 0.22, 0.65), (0, 0.4, 0.68), "fabric", 0.08)
    for side in (-1, 1):
        box((0.22, 0.92, 0.4), (side * 1.04, 0, 0.58), "fabric", 0.08)
    objects.append(finish("Sofa"))
    box((1.5, 0.8, 0.08), (0, 0, 0.73), "wood")
    for x in (-0.6, 0.6):
        for y in (-0.3, 0.3):
            box((0.06, 0.06, 0.7), (x, y, 0.35), "metal")
    objects.append(finish("Table"))
    box((0.48, 0.48, 0.09), (0, 0, 0.48), "wood")
    box((0.48, 0.09, 0.48), (0, 0.22, 0.73), "wood")
    for x in (-0.18, 0.18):
        for y in (-0.18, 0.18):
            rod((x, y, 0), (x * 0.85, y * 0.85, 0.44), 0.025, "metal")
    objects.append(finish("Chair"))
    box((2.15, 1.6, 0.28), (0, 0, 0.3), "wood")
    box((2.05, 1.5, 0.26), (0, 0, 0.54), "white", 0.08)
    box((1.35, 1.52, 0.08), (0.29, 0, 0.71), "fabric")
    for side in (-1, 1):
        box((0.46, 0.6, 0.13), (-0.7, side * 0.38, 0.74), "white", 0.045)
    box((0.12, 1.65, 0.95), (-1.08, 0, 0.55), "wood")
    objects.append(finish("Bed"))
    box((1.5, 0.62, 0.84), (0, 0, 0.42), "white")
    box((1.55, 0.67, 0.05), (0, 0, 0.86), "stone")
    for x in (-0.5, 0, 0.5):
        box((0.43, 0.035, 0.73), (x, -0.33, 0.42), "wood")
        box((0.12, 0.04, 0.035), (x, -0.36, 0.7), "metal")
    objects.append(finish("KitchenCounter"))
    box((0.6, 0.62, 0.87), (0, 0, 0.435), "white")
    box((0.53, 0.02, 0.46), (0, -0.32, 0.4), "black")
    for x in (-0.15, 0.15):
        for y in (-0.15, 0.15):
            cylinder(0.1, 0.01, (x, y, 0.88), "black")
    objects.append(finish("Stove"))
    box((0.7, 0.65, 1.78), (0, 0, 0.89), "metal", 0.04)
    box((0.67, 0.02, 0.5), (0, -0.336, 1.49), "white")
    box((0.67, 0.02, 1.15), (0, -0.336, 0.65), "white")
    objects.append(finish("Fridge"))
    lathe([(0.001, 0), (0.18, 0), (0.23, 0.065), (0.218, 0.065), (0.175, 0.014),
           (0.001, 0.014)], "metal")
    rod((0.22, 0, 0.055), (0.66, 0, 0.055), 0.024, "black")
    objects.append(finish("CookingPan"))
    cylinder(0.16, 0.22, (0, 0, 0.11), "metal", vertices=24)
    cylinder(0.175, 0.035, (0, 0, 0.24), "metal", vertices=24)
    cylinder(0.035, 0.035, (0, 0, 0.27), "black")
    for side in (-1, 1):
        box((0.1, 0.06, 0.04), (side * 0.2, 0, 0.19), "black")
    objects.append(finish("CookingPot"))
    lathe([(0.001, 0), (0.047, 0), (0.05, 0.095), (0.044, 0.095),
           (0.041, 0.01), (0.001, 0.01)], "white")
    for start, end in (((0.047, 0, 0.02), (0.084, 0, 0.03)),
                       ((0.084, 0, 0.03), (0.084, 0, 0.068)),
                       ((0.084, 0, 0.068), (0.047, 0, 0.08))):
        rod(start, end, 0.008, "white")
    objects.append(finish("Mug"))
    cylinder(0.065, 0.12, (0, 0, 0.065), "pink")
    cylinder(0.045, 0.045, (0, 0, 0.15), "metal")
    box((0.04, 0.04, 0.05), (0, 0, 0.195), "black")
    objects.append(finish("Perfume"))
    cylinder(0.013, 0.07, (0, 0, 0.035), "black", vertices=12)
    cylinder(0.01, 0.035, (0, 0, 0.087), "red", vertices=12)
    objects.append(finish("Lipstick"))
    for position in ((0, 0, 0.2), (0, 0, 0.42), (-0.13, 0, 0.54), (0.13, 0, 0.54)):
        ellipsoid((0.13, 0.095, 0.12), position, "wood")
    for side in (-1, 1):
        ellipsoid((0.07, 0.08, 0.09), (side * 0.12, 0, 0.09), "wood")
        ellipsoid((0.08, 0.07, 0.13), (side * 0.16, 0, 0.27), "wood")
    ellipsoid((0.07, 0.03, 0.05), (0, -0.08, 0.41), "white")
    objects.append(finish("TeddyToy"))
    box((0.22, 0.3, 0.03), (0, 0, 0.018), "blue", 0.005)
    box((0.21, 0.28, 0.021), (0, 0, 0.019), "white", 0)
    objects.append(finish("Book"))
    bowl = lathe([(0.001, 0.28), (0.11, 0.28), (0.22, 0.47), (0.18, 0.48),
                  (0.12, 0.33), (0.001, 0.33)], "white")
    bowl.scale.y = 1.35
    bowl.location.y = -0.12
    box((0.43, 0.18, 0.42), (0, 0.24, 0.59), "white", 0.06)
    cylinder(0.14, 0.3, (0, 0, 0.18), "white")
    objects.append(finish("Toilet"))
    box((0.65, 0.47, 0.035), (0, 0, 0.7), "white")
    for side in (-1, 1):
        box((0.055, 0.47, 0.13), (side * 0.3, 0, 0.78), "white")
        box((0.59, 0.05, 0.13), (0, side * 0.21, 0.78), "white")
    cylinder(0.12, 0.66, (0, 0, 0.34), "white")
    rod((0, 0.17, 0.8), (0, 0.17, 1), 0.02, "metal")
    rod((0, 0.17, 1), (0, 0.02, 1), 0.02, "metal")
    objects.append(finish("Washbasin"))
    cylinder(0.18, 0.3, (0, 0, 0.15), "stone")
    rod((0, 0, 0.2), (0, 0, 0.9), 0.02, "wood")
    for side in (-1, 1):
        for height in (0.4, 0.65, 0.85):
            ellipsoid((0.23, 0.07, 0.06), (side * 0.13, 0, height), "green")
    objects.append(finish("PotPlant"))
    return objects
