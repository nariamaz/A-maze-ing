from app import config, visualizer
from typing import Any
from contextlib import redirect_stdout
import mazegen
import sys


if __name__ == "__main__":
    argc, argv = len(sys.argv), sys.argv
    config_file = "config.txt"
    if argc > 1:
        config_file = argv[1]
    conf = config.get_config(config_file=config_file)
    mandatory = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
    missing = [key for key in mandatory if key not in conf]
    if missing:
        print(f"Error: config file does not contain {", ".join(missing)}.")
        exit(1)
    in_seed = conf["SEED"] if "SEED" in conf else None
    in_entry = conf["ENTRY"] if "ENTRY" in conf else None
    in_exit = conf["EXIT"] if "EXIT" in conf else None
    in_perfect = conf["PERFECT"] if "PERFECT" in conf else True
    # TODO: Out of bounds is raised.
    gen = mazegen.MazeGenerator(width=conf["WIDTH"], height=conf["HEIGHT"], seed=in_seed, perfect=in_perfect, entry=in_entry, exit=in_exit)
    gen.generate(gen.grid, conf)    
    walls = gen.grid
    solution = gen.solution
    with open(conf["OUTPUT_FILE"], "w") as f:
        with redirect_stdout(f):
            print("--- MAZE HEX ---")
            visualizer.print_grid(walls, conf)
            print("\n--- ENTRY AND EXIT ---")
            print(f"{solution[0][0]}, {solution[0][1]}\n{solution[1][0]}, {solution[1][1]}\n")
            print("--- SOLUTION ---")
            print(solution[2])
    #visualizer.print_maze(walls, conf)