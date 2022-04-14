import time

from app import wifi
from app.displayserial import set_component_txt, CONNECTION_PAGE_NAME, uart_write, BUTTON_MESSAGE, TEXT_MESSAGE, \
    receive_text_message_str
from app.pages import ssid

_SSID_FIELD_OBJNAME = 'tssidfield'
_PASSWORD_FIELD_OBJNAME = 'tpassfield'
_WIFI_STATUS_OBJNAME = 'pwifi'
_AMPLIPI_STATUS_OBJNAME = 'pnet'

# picture ids
_WIFI_CONNECTED_PIC_ID = 30
_WIFI_DISCONNECTED_PIC_ID = 32

# component ids
_CONNECT_BUTTON_ID = 7
_BACK_BUTTON_ID = 8
_SSID_FIELD_ID = 3
_PASSWORD_FIELD_ID = 4 # might not be needed

ssid_list = []
ssid_field_txt = ''
pass_field_txt = ''

def load_connection_page():
    """Loads connection page contents. Can be called whenever since all relevant components are global in the
    connection page. Although, it shouldn't be called when the user is entering new wifi info since it would override it."""
    # load wifi info
    wifi_info = wifi.load_wifi_info()
    wifi_ssid = wifi_info['ssid']
    wifi_password = wifi_info['password']

    # update page components
    print(f'updating ssid and password fields to {wifi_ssid} and {wifi_password}')
    time.sleep_ms(10)
    # TODO: investigate effectiveness of delaying on improving the chances of the message being
    #  successfully sent to the display. if it actually helps, might make more sense to put the delay in
    #  every display update function
    set_component_txt(CONNECTION_PAGE_NAME, _SSID_FIELD_OBJNAME, wifi_ssid)
    time.sleep_ms(10)
    set_component_txt(CONNECTION_PAGE_NAME, _PASSWORD_FIELD_OBJNAME, wifi_password)
    time.sleep_ms(10)
    update_connection_status()

def update_connection_status():
    """Updates the config page's WiFi and AmpliPi status symbols."""
    if wifi.is_connected():
        uart_write(f'{CONNECTION_PAGE_NAME}.{_WIFI_STATUS_OBJNAME}.pic={_WIFI_CONNECTED_PIC_ID}')
    else:
        uart_write(f'{CONNECTION_PAGE_NAME}.{_WIFI_STATUS_OBJNAME}.pic={_WIFI_DISCONNECTED_PIC_ID}')
    # TODO: update AmpliPi connectivity info

def handle_connection_page_msg(message):
    global ssid_field_txt
    global pass_field_txt
    print("handling connection page message")
    if message[0] == BUTTON_MESSAGE and message[3] == 0x01:
        id = message[2]

        if id == _CONNECT_BUTTON_ID:
            # TODO: indicate that device is trying to connect here somehow
            print("Connect button pressed")
            wifi.disconnect()
            wifi.save_wifi_info(ssid_field_txt, pass_field_txt)
            wifi.try_connect()
            update_connection_status()

        elif id == _BACK_BUTTON_ID:
            # back button should reset the fields to their saved state
            # nextion handles the page change on press already
            load_connection_page()
        elif id == _SSID_FIELD_ID:
            # nextion will switch to ssidpage, so we need to init that page
            ssid.load_ssid_page()
    elif message[0] == TEXT_MESSAGE:
        id = message[2]
        text = receive_text_message_str(message)
        if id == _SSID_FIELD_ID:
            ssid_field_txt = text
        elif id == _PASSWORD_FIELD_ID:
            pass_field_txt = text
        print(f'Received string: {text}')