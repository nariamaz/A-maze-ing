"""
Defines the color palettes used by the maze visualizer.

Each theme is represented by a dictionary containing RGB color values
for the different visual elements of the maze:

    - wall:    Color used to draw the maze walls.
    - floor:   Color used for the walkable cells.
    - entry:   Color used to highlight the maze entrance.
    - exit:    Color used to highlight the maze exit.
    - path:    Color used to display the solution path.
    - pattern: Color used for additional visual patterns or effects.

RGB values are represented as tuples of three integers ranging from
0 to 255, corresponding to red, green and blue channels.

Available themes:
    - classic:          Traditional high-contrast color palette.
    - EVA_01:           Purple and neon green palette.
    - late_capitalism:  Purple and neon green palette.
    - vaporwave:        Pink, purple and cyan palette.
    - blackhole:        Dark palette with red and black tones.

THEME_NAMES stores a list containing all available theme names.
DEFAULT_THEME selects the first registered theme as the default.
"""
THEMES = {
    "classic": {
        "wall":    (235, 235, 235),
        "floor":   (20, 20, 20),
        "entry":   (60, 200, 90),
        "exit":    (220, 60, 60),
        "path":    (240, 200, 60),
        "pattern": (80, 120, 230),
    },
    "EVA_01": {
        "wall":    (98, 55, 148),
        "floor":   (153, 234, 57),
        "entry":   (40, 180, 120),
        "exit":    (230, 90, 70),
        "path":    (232, 121, 12),
        "pattern": (11, 10, 13),
    },
    "late_capitalism": {
        "wall":    (188, 132, 219),
        "floor":   (98, 55, 148),
        "entry":   (172, 172, 172),
        "exit":    (172, 172, 172),
        "path":    (255, 255, 255),
        "pattern": (220, 220, 220),
    },
    "vaporwave": {
        "wall":    (255, 106, 213),
        "floor":   (188, 132, 219),
        "entry":   (173, 140, 255),
        "exit":    (135, 149, 232),
        "path":    (0, 220, 255),
        "pattern": (185, 236, 255),
    },
    "blackhole": {
        "wall":    (148, 37, 0),
        "floor":   (97, 17, 7),
        "entry":   (0, 0, 0),
        "exit":    (0, 0, 0),
        "path":    (10, 10, 10),
        "pattern": (180, 180, 180),
    },
}

THEME_NAMES = list(THEMES)
DEFAULT_THEME = THEME_NAMES[2]
