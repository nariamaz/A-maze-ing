"""
Configuration file parser and validator for the maze generator.

This module is responsible for reading the configuration file, converting
its string values into appropriate Python data types, and validating
the configuration before it is used by the maze engine.

The configuration file follows the KEY=VALUE format and supports
comments using ‘#’.

Constants:
    MANDATORY:
        Tuple containing the configuration keys that must be present:
        WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE and PERFECT.

Functions:
    read_config_file(config_file):
        Opens the configuration file and returns its contents as a
        list of lines.

    convert_to_value(value):
        Converts a configuration string into its corresponding Python
        data type:
            - Numeric strings become integers.
            - “True” and “False” become booleans.
            - Comma-separated numeric values become lists of integers.
            - Other values remain strings with surrounding quotes removed.

    to_cell(point):
        Converts coordinates from configuration format (x, y) into
        the maze engine format (row, column).

    to_xy(cell):
        Converts coordinates from maze engine format (row, column)
        back into configuration format (x, y).

    get_config(config_file):
        Reads and parses the configuration file into a dictionary.
        Removes comments, ignores empty lines, normalizes variable
        names to uppercase and converts values into Python types.
        Raises ValueError when a line does not follow the expected
        KEY=VALUE format or contains an invalid variable name.

    check_point(name, point, width, height):
        Validates a maze coordinate, ensuring it contains exactly
        two integers and that both coordinates are within the maze
        boundaries.

    validate_config(conf):
        Validates the complete configuration dictionary.
        Checks mandatory keys, positive maze dimensions, boolean
        PERFECT value, optional integer SEED, valid ENTRY and EXIT
        coordinates, and ensures the entry and exit are different.

Raises:
    ValueError:
        When configuration values are missing, incorrectly formatted,
        have invalid data types, or violate maze constraints.

Coordinate convention:
    Configuration files use Cartesian coordinates (x, y), where
    x represents the horizontal position and y the vertical position.

    The maze engine uses matrix coordinates (row, column), where
    row represents the vertical position and column the horizontal
    position.

    The to_cell() and to_xy() functions handle the conversion
    between these two coordinate systems.
"""
from typing import Any

MANDATORY = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


def read_config_file(config_file: str) -> list[str]:
    with open(config_file) as f:
        return f.read().splitlines()


def convert_to_value(value: str) -> Any:
    if value.isnumeric():
        return int(value)
    if value in ("True", "False"):
        return value == "True"
    if "," in value:
        parts = value.split(",")
        if not all(p.strip().isnumeric() for p in parts):
            raise ValueError(f"expecting only positive numbers, got: {value}")
        return [int(p) for p in parts]
    return value.strip("\"'")


def to_cell(point: list[int]) -> tuple[int, int]:
    """Config (x,y) -> engine (row,col)."""
    return point[1], point[0]


def to_xy(cell: tuple[int, int]) -> tuple[int, int]:
    """Engine (row,col) -> config (x,y)."""
    return cell[1], cell[0]


def get_config(config_file: str = "config.txt") -> dict[str, Any]:
    lines = read_config_file(config_file)
    conf: dict[str, Any] = {}
    for i, line in enumerate(lines, start=1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"line {i}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip().upper()
        if not key or not all(c.isalpha() or c in "_.-" for c in key):
            raise ValueError(
                f"line {i}: variable names must contain only letters,"
                f"'_', '.' or '-'")
        conf[key] = convert_to_value(value.strip())
    return conf


def check_point(name: str, point: Any, width: int, height: int) -> None:
    if (not isinstance(point, list) or len(point) != 2
            or not all(type(v) is int for v in point)):
        raise ValueError(f"{name} must be two integers: x,y")
    x, y = point
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"{name} outside the bounds: {point}")


def validate_config(conf: dict[str, Any]) -> None:
    missing = [k for k in MANDATORY if k not in conf]
    if missing:
        raise ValueError(f"missing keys: {', '.join(missing)}")
    for key in ("WIDTH", "HEIGHT"):
        if type(conf[key]) is not int or conf[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    if type(conf["PERFECT"]) is not bool:
        raise ValueError("PERFECT must be True or False")
    if "SEED" in conf and type(conf["SEED"]) is not int:
        raise ValueError("SEED must be an integer")
    check_point("ENTRY", conf["ENTRY"], conf["WIDTH"], conf["HEIGHT"])
    check_point("EXIT", conf["EXIT"], conf["WIDTH"], conf["HEIGHT"])
    if conf["ENTRY"] == conf["EXIT"]:
        raise ValueError("ENTRY and EXIT must be different")
