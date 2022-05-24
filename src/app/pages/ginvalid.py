from app import displayserial
from app.displayserial import BUTTON_MESSAGE
from app.pages import zone, source

_REGROUP_BUTTON_ID = 2
_CHANGE_ZONE_BUTTON_ID = 3
_CHANGE_GROUP_BUTTON_ID = 4

def _on_regroup():
    source.load_source_page()


def _on_change_zone():
    zone.load_zone_page()

def _on_change_group():
    zone.load_zone_page(groups=True)

def handle_msg(message):
    print('handling ginvalid page message')
    if message[0] == BUTTON_MESSAGE and message[3] == 0x01:
        id = message[2]
        if id == _REGROUP_BUTTON_ID:
            _on_regroup()
        elif id == _CHANGE_ZONE_BUTTON_ID:
            _on_change_zone()
        elif id == _CHANGE_GROUP_BUTTON_ID:
            _on_change_group()