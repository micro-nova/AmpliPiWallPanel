import os

import machine

from app import displayserial
from app.displayserial import message_is_button_event, button_is_pressed, message_id
from app.pages import version

_REBOOT_BUTTON_ID = 1
_PRE_RELEASES_BUTTON_ID = 2
_FACTORY_RESET_BUTTON_ID = 3

def handle_msg(message):
    if message_is_button_event(message) and button_is_pressed(message):
        id = message_id(message)
        if id == _REBOOT_BUTTON_ID:
            _on_reboot()
        elif id == _PRE_RELEASES_BUTTON_ID:
            version.enable_prerelease()
            version.load_version_page()
        elif id == _FACTORY_RESET_BUTTON_ID:
            _on_factory_reset()

def _on_reboot():
    displayserial.change_page(displayserial.BOOT_PAGE_NAME)
    machine.reset()

def _on_factory_reset():
    # remove all config files
    _try_remove('relay.txt')
    _try_remove('version_queue.txt')
    _try_remove('wifi.txt')
    _try_remove('zone.txt')
    _try_remove('halt.txt')

    # reboot
    _on_reboot()

def _try_remove(file):
    try:
        os.remove(file)
    except OSError:
        pass
