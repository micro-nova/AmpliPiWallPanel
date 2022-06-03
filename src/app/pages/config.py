import machine

from app import displayserial
from app.displayserial import message_id, message_is_button_event, button_is_pressed
from app.pages import connection, zone, version

# component ids
ZONE_BUTTON_ID = 3
CONNECTION_BUTTON_ID = 5
UPDATE_BUTTON_ID = 6
REBOOT_BUTTON_ID = 7


def _on_zone_():
    zone.load_zone_page()

def _on_connection():
    connection.load_connection_page()

def _on_update():
    version.disable_prereleases()
    version.load_version_page()

def _on_reboot():
    displayserial.change_page(displayserial.BOOT_PAGE_NAME)
    machine.reset()

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
        elif id == REBOOT_BUTTON_ID:
            _on_reboot()