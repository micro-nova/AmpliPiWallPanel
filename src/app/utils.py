import os

def rmdir_all(dir):
    for item in os.listdir(dir):
        if '.' in item:
            os.remove(f'{dir}/{item}')
        else:
            rmdir_all(f'{dir}/{item}')
    os.rmdir(dir)


def compare_versions(v1: str, v2: str) -> int:
    """-1 is v1 < v2. 0 is v1 == v2, 1 is v1 > v2. The number of parts in v1 and v2 must be the same."""
    v1_ints = [int(s) for s in v1.split('.')]
    v2_ints = [int(s) for s in v2.split('.')]

    # does zip work on micropython? ill do this for now
    for i, v1_val in enumerate(v1_ints):
        v2_val = v2_ints[i]
        if v1_val < v2_val: return -1
        if v1_val > v2_val: return +1
    return 0



