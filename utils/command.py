# command management
# | IMPORT
from typing import Dict, List, Union

# | GLOBAL VARIABLES
COMMAND_STRUCTURE = {
    "help": {"param": {}, "return": str},
    "regis": {"param": {"server_name": str, "name": str}, "return": str},
    "otp": {"param": {"otp": str}, "return": str}
}

# | FUNCTIONS
def custom_split(string: str, delimeter: str = " ", special: str = '"') -> List[str]:
    res = []
    word = ""
    skip_delim = False
    for c in string:
        if c == special:
            if not skip_delim:
                skip_delim = True
            else:
                skip_delim = False
            continue

        if c == delimeter and not skip_delim:
            res.append(word)
            word = ""
            continue
        else:
            word += c

    res.append(word)
    return [c for c in res if c != ""]


def command_parse(
    string: str, prefix: str
) -> Union[Dict[str, Union[str, Dict[str, str]]], None]:
    global COMMAND_STRUCTURE

    string_lst = custom_split(string)
    cmd = string_lst[0]
    param = string_lst[1:]

    if cmd[0] == prefix and cmd[1:] in COMMAND_STRUCTURE.keys():
        param_dct = {}
        param_lst = list(COMMAND_STRUCTURE[cmd[1:]]["param"].items())
        for index in range(len(param_lst)):
            try:
                param_dct[param_lst[index][0]] = param_lst[index][1](param[index])
            except IndexError:
                return None

        return {"command": cmd[1:], "param": param_dct}


# | MAIN
if __name__ == "__main__":
    while True:
        i = input(">>> ")
        if i == "":
            break
        print(command_parse(i, "$"))
