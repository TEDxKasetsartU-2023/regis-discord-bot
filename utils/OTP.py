# OTP Generator
# | IMPORT
import base64
import os
import pickle
import shortuuid

from datetime import datetime
from random import randint, seed
from typing import Any, Dict, Union

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
CHAR_SET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# | FUNCTIONS
def gen_seed() -> int:
    global CHAR_SET

    DEFAULT_SEED = "TEDxKasetsartU" + shortuuid.uuid()
    seed(DEFAULT_SEED)

    res = ""

    for _ in range(4):
        res += CHAR_SET[randint(0, len(CHAR_SET) - 1)]

    return res


def gen_otp(otp_file: str, name: str, server_name: str, length: int = 6):
    global CHAR_SET
    global INIT_DUMP

    ref = gen_seed()
    seed(ref)

    while True:
        otp = ""

        for _ in range(length):
            otp += CHAR_SET[randint(0, len(CHAR_SET) - 1)]

        if write_otp_file(otp_file, otp, ref, name, server_name) == 0:
            return otp, ref



def write_otp_file(file: str, otp: str, ref: str, name: str, server_name: str, mode: str = "add") -> Union[None, int]:
    empty_structure = {}
    if not os.path.exists(file):
        with open(file, "wb") as f:
            data = base64.b85encode(pickle.dumps(empty_structure))
            f.write(data)

    data = read_otp_file(file)
    if mode == "add":
        for k in data.keys():
            if k == otp:
                return None
        data[otp] = {"ref": ref, "create_at": datetime.now(), "for": name, "server": server_name}
    elif mode == "remove":
        try:
            data.pop(otp)
        except KeyError:
            return None
    else:
        return None

    with open(file, "wb") as f:
        data = base64.b85encode(pickle.dumps(data))
        f.write(data)
    return 0

def read_otp_file(file: str) -> Dict[str, Dict[str, Union[str, Any]]]:
    if not os.path.exists(file):
        return None
    else:
        with open(file, "rt") as f:
            data = pickle.loads(base64.b85decode(f.read()))
        return data

def test(otp_file: str, no_first_print=False):
    s = set()
    first = not no_first_print
    for _ in range(2000):
        s.add(gen_otp(otp_file))
        if first:
            print(s)
            first = False
    return len(s)


# | MAIN
if __name__ == "__main__":
    file = "test.tmp"
    count = 0
    for _ in range(2):
        res = test(file, no_first_print=False)
        if res < 2000:
            print(res)
            count += 1
    print(count)
    print(read_otp_file(file))