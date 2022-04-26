import machine
import time

from app import displayserial

# objnames
from app.ota import custom_update
from app.pages import version

VERSION_INFO_OBJNAME = "tver"

# component IDs
BACK_BUTTON_ID = 2
APPLY_BUTTON_ID = 3

_tag_name = None
_ota = None

def handle_msg(message):
    print('handling versioninfo page message')
    if message[0] == displayserial.BUTTON_MESSAGE and message[3] == 0x01:
        # valid press event
        id = message[2]
        if id == BACK_BUTTON_ID:
            _on_back()
        elif id == APPLY_BUTTON_ID:
            _on_apply()

def load_versioninfo_page(ota, release):
    global _ota
    global _tag_name
    _ota = ota
    _tag_name = release['tag_name']
    # display version info
    release_body = release['body']
    if len(release_body) > 600:
        release_body = release_body[0:596] + '...'
    displayserial.set_component_txt(displayserial.VERSIONINFO_PAGE_NAME,
                                    VERSION_INFO_OBJNAME,
                                    release_body)


def _on_apply():
    if _tag_name is not None:
        custom_update.queue_update(_tag_name)
        # _ota.install_tagged_release(_tag_name)
        # # TODO: turn off display?
        # print('resetting machine...')
        # time.sleep_ms(100)
        machine.reset()


def _on_back():
    print('versioninfo back pressed')
    global _ota
    _ota = None # _ota should be deleted with del() elsewhere
    time.sleep_ms(50)
    version.reload_version_page_ui()

