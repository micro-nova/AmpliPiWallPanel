from app import displayserial
from app.displayserial import message_id, message_is_button_event, button_is_pressed
from app.pages import connection, zone, version

# component ids
ZONE_BUTTON_ID = 3
CONNECTION_BUTTON_ID = 5
UPDATE_BUTTON_ID = 6

UPDATE_AVAILABLE_FIELD_OBJNAME = 'tuavailable'

_update_available = False
def set_update_available(available):
    global _update_available
    _update_available = available

def load_config_page():
    displayserial.set_visible(UPDATE_AVAILABLE_FIELD_OBJNAME, _update_available)

def _on_zone_():
    zone.load_zone_page()

def _on_connection():
    connection.load_connection_page()

def _on_update():
    version.disable_prereleases()
    version.load_version_page()

def handle_msg(message):
    print("handling config page message")
    if message_is_button_event(message) and button_is_pressed(message):
        id = message_id(message)
        if id == ZONE_BUTTON_ID:
            _on_zone_()
        elif id == CONNECTION_BUTTON_ID:
            _on_connection()
        elif id == UPDATE_BUTTON_ID:
            _on_update()