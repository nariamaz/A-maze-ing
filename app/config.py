def read_config_file(config_file: str) -> list[str]:
    try:
        with open(config_file) as opened_file:
            lines = opened_file.read().split("\n")
    except Exception as error:
        print("Error:", error)
    return lines

def convert_to_value(value) -> any:
    if value.isnumeric():
        value = int(value)
    elif value == "True" or value == "False":
        value = value == "True"
    elif value.find(",") > 0:
        value = value.split(",")
        if not all(v.isnumeric() for v in value):
            print(f"ERROR: Syntax error on line:{i+1}: expecting only numbers")
            return None
        value = [int(v) for v in value]
    else:
        value = value.strip("\"'")
    return value
        
def get_config(config_file: str = "config.txt") -> dict[str, int|str|bool|list]:
    lines = read_config_file(config_file)
    config = {}
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split('#', 1)[0].strip()
        if "=" in line:
            key, value = line.split("=", 1)
        else:
            print(f"ERROR: Syntax error on line:{i+1}: expected A = B")
            continue
        key = values[0].upper().strip()
        if not key.isalpha():
            print(f"ERROR: Syntax error on line:{i+1}: variables should only contains alpha characters")
        value = convert_to_value(values[1].strip())
        if value is None:
            continue
        config[key] = value
    return config
