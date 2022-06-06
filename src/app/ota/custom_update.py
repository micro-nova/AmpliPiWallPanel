

_TAG_FILE = 'version_queue.txt'
_DISPLAY_FIRMWARE_DIR = 'app'
_DISPLAY_FIRMWARE_FILE = 'amplipi_v2.tft'
_MAX_RETRIES = 6

def queue_update(tag):
    import json

    import os

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


def handle_update():
    import gc
    import time

    import machine

    # this is here to temporarily halt the update process to keep the display firmware on the esp32
    try:
        with open('halt.txt'):
            while True:
                print('halting! remove halt.txt to stop halting.')
                time.sleep(1)
    except OSError:
        pass
    gc.collect()

    try:
        _update_app_if_queued()
    except Exception as e:
        print(e)
        print(gc.mem_free())
        machine.reset()
    try:
        _update_display_if_queued()
    except Exception as e:
        print(e)
        print(gc.mem_free())
        machine.reset()

def _update_app_if_queued():
    import json

    import machine
    import os

    from app import wifi, displayserial
    from app.ota import ota_updater
    from app.utils import rmdir_all
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
                ota = ota_updater.make_ota_updater()

                print(f'Updating to version {version["tag"]}, try #{version["tries"]}')
                ota.install_tagged_release(version['tag'])
                print('removing version_queue.txt and resetting machine...')
                os.remove(_TAG_FILE)
                displayserial.change_page(displayserial.BOOT_PAGE_NAME)
                machine.reset()
            else:
                os.remove(_TAG_FILE)
                # update failed so remove the update folder
                rmdir_all('next')

def _update_display_if_queued():
    import time

    import os

    from machine import Pin
    from app.ota.upload import NexUpload
    if _DISPLAY_FIRMWARE_FILE in os.listdir(_DISPLAY_FIRMWARE_DIR):
        tft_reset = Pin(4, Pin.OUT)
        tft_reset.value(1)
        time.sleep_ms(10)
        tft_reset.value(0)
        time.sleep_ms(1000)
        print("Starting display firmware update")
        updater = NexUpload(f'{_DISPLAY_FIRMWARE_DIR}/{_DISPLAY_FIRMWARE_FILE}')
        updater.upload()
