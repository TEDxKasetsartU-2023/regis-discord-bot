# parse sheet data
# | IMPORT
from typing import Dict, List

# | FUNCTIONS
def parseSheet(data: List[List[str]]) -> List[Dict[str, str]]:
    header = data[0]
    content = data[1:]
    res = []
    for c in content:
        dct = {}
        for h in range(len(header)):
            dct[header[h]] = c[h]
        res.append(dct)
    
    return res

# | MAIN
if __name__ == "__main__":
    print(parseSheet([['ชื่อ', 'อีเมล', 'ฝ่าย', 'สถานะ'], ['รัชพล จันทรโชติ', 'r.chantarachote@gmail.com', 'media', 'รอ']]))