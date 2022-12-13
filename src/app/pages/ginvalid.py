from app.displayserial import message_is_button_event, button_is_pressed, message_id
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
    if message_is_button_event(message) and button_is_pressed(message):
        id = message_id(message)
        if id == _REGROUP_BUTTON_ID:
            _on_regroup()
        elif id == _CHANGE_ZONE_BUTTON_ID:
            _on_change_zone()
        elif id == _CHANGE_GROUP_BUTTON_ID:
            _on_change_group()