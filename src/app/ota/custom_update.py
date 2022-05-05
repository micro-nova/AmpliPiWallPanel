import json
import time

import machine
import os

from machine import Pin
from app import wifi
from app.ota.ota_updater import OTAUpdater
from app.ota.upload import NexUpload
from app.utils import rmdir_all

_TAG_FILE = 'version_queue.txt'
_DISPLAY_FIRMWARE_DIR = 'app'
_DISPLAY_FIRMWARE_FILE = 'amplipi_v2.tft'
_MAX_RETRIES = 6

def queue_update(tag):
    if _TAG_FILE in os.listdir():
        with open(_TAG_FILE, 'w') as file:
            version = json.loads(file.read())
            if version['tag'] == tag:
                version['tries'] += 1
            else:
                version['tag'] = tag
                version['tries'] = 0
            print(f'Writing dict to json: {version}')
            json_str = json.dumps(version)
            print(f'String to write: {json_str}')
            file.write(json_str)

    else:
        with open(_TAG_FILE, 'w') as file:
            version = {'tag': tag, 'tries': 0}
            print(f'Writing dict to json: {version}')
            json_str = json.dumps(version)
            print(f'String to write: {json_str}')
            file.write(json_str)

# def requeue_update():
#     if _TAG_FILE in os.listdir():
#         with open(_TAG_FILE, 'w') as file:
#             version = json.load(file)
#             if version['tries'] < _MAX_RETRIES:
#                 version['tries'] += 1
#             else:
#                 file.close()
#                 os.remove(_TAG_FILE)


def handle_update():
    _update_app_if_queued()
    _update_display_if_queued()

def _update_app_if_queued():
    if _TAG_FILE in os.listdir():
        # connect to wifi
        wifi.try_connect()
        if wifi.is_connected():
            with open(_TAG_FILE) as file:
                file_str = file.read()
                print(f'version_queue.txt: {file_str}')

                version = json.loads(file_str)
                version['tries'] += 1
            with open(_TAG_FILE, 'w') as file:
                file.write(json.dumps(version))

            if version['tries'] <= _MAX_RETRIES:
                with open('temp-token.txt') as file:
                    token = json.loads(file.read())

                if token is None:
                    ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src', module='')
                    print('OTAUpdater loaded without token.')
                else:
                    ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src', module='',
                                      headers={'Authorization': 'token {}'.format(token['token'])})
                    print('OTAUpdater loaded with token.')

                print(f'Updating to version {version["tag"]}, try #{version["tries"]}')
                ota.install_tagged_release(version['tag'])
                print('removing version_queue.txt and resetting machine...')
                os.remove(_TAG_FILE)
                machine.reset()
            else:
                os.remove(_TAG_FILE)
                # update failed so remove the update folder
                rmdir_all('next')

def _update_display_if_queued():
    if _DISPLAY_FIRMWARE_FILE in os.listdir(_DISPLAY_FIRMWARE_DIR):
        tft_reset = Pin(4, Pin.OUT)
        tft_reset.value(1)
        time.sleep_ms(10)
        tft_reset.value(0)
        time.sleep_ms(1000)
        print("Starting display firmware update")
        updater = NexUpload(f'{_DISPLAY_FIRMWARE_DIR}/{_DISPLAY_FIRMWARE_FILE}')
        updater.upload()
