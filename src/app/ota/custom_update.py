import json
import machine
import os

from app.ota.ota_updater import OTAUpdater

_TAG_FILE = 'version_queue.txt'

def queue_update(tag):
    if _TAG_FILE in os.listdir():
        os.remove(_TAG_FILE)
    with open(_TAG_FILE, 'w') as file:
        file.write(tag)
    print(f'wrote "{tag}" to {_TAG_FILE}')


def handle_update():
    _update_if_queued()

def _update_if_queued():
    if _TAG_FILE in os.listdir():
        with open(_TAG_FILE) as file:
            version = file.read()
        os.remove(_TAG_FILE)
        with open('temp-token.txt') as file:
            token = json.loads(file.read())

        if token is None:
            ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src', module='')
            print('OTAUpdater loaded without token.')
        else:
            ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src', module='',
                              headers={'Authorization': 'token {}'.format(token['token'])})
            print('OTAUpdater loaded with token.')

        ota.install_tagged_release(version)
        print('resetting machine...')
        machine.reset()