from typing import Any
import sys

from app import config, visualizer
from app.colours import THEME_NAMES, DEFAULT_THEME
from app.visualizer import SPEEDS, SPEED_NAMES, DEFAULT_SPEED
import mazegen


def build_maze(conf: dict[str, Any], seed: int | None):
    gen = mazegen.MazeGenerator(
        width=conf["WIDTH"],
        height=conf["HEIGHT"],
        seed=seed,
        perfect=conf["PERFECT"],
        entry=config.to_cell(conf["ENTRY"]),
        exit=config.to_cell(conf["EXIT"]),
    )
    visualizer.animate_generation(gen, conf)
    walls = gen.grid
    solution = gen.solution
    with open(conf["OUTPUT_FILE"], "w") as f:
        print("--- MAZE HEX ---", file=f)
        visualizer.print_grid(walls, conf, file=f)
        print("\n--- ENTRY AND EXIT ---", file=f)
        x, y = config.to_xy(solution[0])
        ex, ey = config.to_xy(solution[1])
        print(f"{x}, {y}", file=f)
        print(f"{ex}, {ey}\n", file=f)
        print("--- SOLUTION ---", file=f)
        print(solution[2], file=f)
    return walls, solution


def choose_theme(current: str) -> str:
    print("Available themes:")
    for i, name in enumerate(THEME_NAMES, start=1):
        mark = " (current)" if name == current else ""
        print(f"  {i}. {name}{mark}")
    choice = input("Theme number: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(THEME_NAMES):
        return THEME_NAMES[int(choice) - 1]
    print("Invalid option, keeping the current theme.")
    return current


def choose_speed(current: str) -> str:
    print("Available speeds:")
    for i, name in enumerate(SPEED_NAMES, start=1):
        mark = " (current)" if name == current else ""
        print(f"  {i}. {name}{mark}")
    choice = input("Speed number: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(SPEED_NAMES):
        return SPEED_NAMES[int(choice) - 1]
    print("Invalid option, keeping the current speed.")
    return current


def main() -> None:
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.txt"
    conf = config.get_config(config_file=config_file)
    config.validate_config(conf)

    walls, solution = build_maze(conf, conf.get("SEED"))
    theme = DEFAULT_THEME
    speed = DEFAULT_SPEED
    show_path = False

    while True:
        visualizer.clear_screen()
        cells = visualizer.path_to_cells(
            config.to_xy(solution[0]), solution[2]) if show_path else ()
        visualizer.print_maze(walls, conf, path=cells, theme=theme)
        print()
        visualizer.print_menu(theme, show_path)
        option = input(visualizer.style("Choice: ", 1)).strip()
        if option == "1":
            walls, solution = build_maze(conf, None)
            show_path = False
        elif option == "2":
            show_path = not show_path
            if show_path:
                cells = visualizer.path_to_cells(
                    config.to_xy(solution[0]), solution[2]
                )
                visualizer.animate_path(
                    walls, conf, cells, theme=theme, fps=visualizer.SPEEDS[speed]
                )
        elif option == "3":
            theme = choose_theme(theme)
        elif option == "4":
            speed = choose_speed(speed)
        elif option == "5":
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
