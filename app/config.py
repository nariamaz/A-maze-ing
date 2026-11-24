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
                f"line {i}: variable names must contain only letters, '_', '.' or '-'"
            )
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