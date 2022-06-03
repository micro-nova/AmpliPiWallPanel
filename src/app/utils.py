import os

def rmdir_all(dir):
    for item in os.listdir(dir):
        if '.' in item:
            os.remove(f'{dir}/{item}')
        else:
            rmdir_all(f'{dir}/{item}')
    os.rmdir(dir)


def compare_versions(v1: str, v2: str) -> int:
    """-1 is v1 < v2. 0 is v1 == v2, 1 is v1 > v2"""
    v1_ints = [int(s) for s in v1.split('.')]
    v2_ints = [int(s) for s in v2.split('.')]
