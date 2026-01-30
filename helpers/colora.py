# helpers/colora.py

from math import sqrt
from helpers.color_db import COLOR_DB

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def nearest_color(input_hex):
    input_rgb = hex_to_rgb(input_hex)

    min_dist = float('inf')
    closest_name = None
    closest_hex = None

    for name, hex_color in COLOR_DB.items():
        dist = color_distance(input_rgb, hex_to_rgb(hex_color))

        if dist < min_dist:
            min_dist = dist
            closest_name = name
            closest_hex = hex_color

    return {
        "input_hex": input_hex,
        "closest_name": closest_name,
        "closest_hex": closest_hex,
        "distance": round(min_dist, 4)
    }
