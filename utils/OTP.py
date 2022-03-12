# OTP Generator
# | IMPORT
import shortuuid

from random import randint, seed

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
CHAR_SET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEFAULT_SEED = "TEDxKasetsartU" + shortuuid.uuid()
seed(DEFAULT_SEED)
INIT_DUMP = randint(0, 99)

# | FUNCTIONS
def gen_seed() -> int:
    global CHAR_SET

    res = ""

    for _ in range(4):
        res += CHAR_SET[randint(0, len(CHAR_SET) - 1)]

    return res


def gen_otp(length: int = 6):
    global CHAR_SET
    global INIT_DUMP

    for _ in range(INIT_DUMP):
        seed(shortuuid.uuid())
    INIT_DUMP = randint(0, 99)

    ref = gen_seed()
    seed(ref)

    otp = ""

    for _ in range(length):
        otp += CHAR_SET[randint(0, len(CHAR_SET) - 1)]

    return otp, ref


def test(no_first_print=False):
    s = set()
    first = not no_first_print
    for _ in range(2000):
        s.add(gen_otp())
        if first:
            print(s)
            first = False

    return len(s)


# | MAIN
if __name__ == "__main__":
    count = 0
    for _ in range(20):
        res = test(no_first_print=True)
        if res < 2000:
            print(res)
            count += 1
    print(count)
