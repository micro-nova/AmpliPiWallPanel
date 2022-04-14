import os

def rmdir_all(dir):
    for item in os.listdir(dir):
        if '.' in item:
            os.remove(f'{dir}/{item}')
        else:
            rmdir_all(f'{dir}/{item}')
    os.rmdir(dir)