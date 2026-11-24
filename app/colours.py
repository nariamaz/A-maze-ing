# ============================================================
#  CORES
#  Cada cor é uma tupla (R, G, B), com valores de 0 a 255.
#  (0, 0, 0) = preto | (255, 255, 255) = branco | (255, 0, 0) = vermelho
# ============================================================

THEMES = {
    "classic": {
        "wall":    (235, 235, 235),   # paredes
        "floor":   (20, 20, 20),      # corredores
        "entry":   (60, 200, 90),     # entrada
        "exit":    (220, 60, 60),     # saída
        "path":    (240, 200, 60),    # caminho da solução
        "pattern": (80, 120, 230),    # células do "42"
    },
    "EVA_01": {
        "wall":    (98, 55, 148),    # roxo
        "floor":   (153, 234, 57),    # verde
        "entry":   (40, 180, 120),
        "exit":    (230, 90, 70),
        "path":    (232, 121, 12),    # laranja
        "pattern": (11, 10, 13),      # dark
    },
    "florest": {
        "wall":    (40, 80, 40),
        "floor":   (230, 225, 200),
        "entry":   (60, 130, 220),
        "exit":    (200, 60, 60),
        "path":    (240, 170, 40),
        "pattern": (90, 55, 30),
    },
    "vaporwave": {
        "wall":    (255, 106, 213),
        "floor":   (152, 28, 201),
        "entry":   (173, 140, 255),
        "exit":    (135, 149, 232),
        "path":    (0, 220, 255),
        "pattern": (185, 236, 255),
    },
}

THEME_NAMES = list(THEMES)      # ["classic", "ocean", "florest", "vaporwave"]
DEFAULT_THEME = THEME_NAMES[1]

def choose_theme(current: str) -> str:
    print("Themes available:")
    for i, name in enumerate(THEME_NAMES, start=1):
        mark = " ←" if name == current else ""
        print(f"  {i}. {name}{mark}")
    choice = input("Theme number: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(THEME_NAMES):
        return THEME_NAMES[int(choice) - 1]
    print("Invalid option, keeping current theme.")
    return current