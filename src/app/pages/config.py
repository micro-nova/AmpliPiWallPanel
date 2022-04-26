from app.displayserial import BUTTON_MESSAGE
from app.pages import connection, zone, version

# component ids
ZONE_BUTTON_ID = 3
CONNECTION_BUTTON_ID = 5
UPDATE_BUTTON_ID = 6



def _on_zone_():
    zone.load_zone_page()

def _on_connection():
    connection.load_connection_page()

def _on_update():
    version.load_version_page()

def handle_msg(message):
    print("handling config page message")
    if message[0] == BUTTON_MESSAGE and message[3] == 0x01:
        id = message[2]
        if id == ZONE_BUTTON_ID:
            _on_zone_()
        elif id == CONNECTION_BUTTON_ID:
            _on_connection()
        elif id == UPDATE_BUTTON_ID:
            _on_update()