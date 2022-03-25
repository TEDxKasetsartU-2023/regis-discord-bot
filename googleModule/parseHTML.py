# parse html (jinja like)
# | IMPORT
from typing import Dict

# | FUNCTIONS
def parseHTML(file: str, param: Dict[str, str]) -> str:
    lines = []
    _open = "{{"
    _close = "}}"
    with open(file, "rt", encoding="utf-8") as f:
        lines = f.readlines()

    for index in range(len(lines.copy())):
        line = lines[index]
        if _open in line and _close in line:
            cut_open = [c for c in line.split(_open) if c != ""][1]
            cut_close = [c for c in cut_open.split(_close) if c != ""][0]
            lines[index] = line.replace(f"{_open}{cut_close}{_close}", param[cut_close])

    return "\n".join([l.strip("\n") for l in lines])


# | MAIN
if __name__ == "__main__":
    print(
        parseHTML(
            r"D:\TEDxKasetsartU\Discord\regis-discord-bot\googleModule\content.html",
            {"OTP": "987654", "REF": "123"},
        )
    )
