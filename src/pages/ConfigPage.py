import Wifi
from DisplaySerial import set_component_txt, CONFIG_PAGE_NAME, BUTTON_MESSAGE

# component names
_SSID_FIELD_OBJNAME = 'tssidfield'
_PASSWORD_FIELD_OBJNAME = 'tpassfield'
_STATUS_LABEL_OBJNAME = 'tstatuslabel'

# component ids
_CONNECT_BUTTON_ID = 8
_BACK_BUTTON_ID = 9

ssid_list = []


# this can be called whenever since all relevant components are global in the config page.
# although, it shouldn't be called when the user is entering new wifi info since it would
# override it.
def load_config_page():
    # load wifi info
    wifi_info = Wifi.load_wifi_info()
    ssid = wifi_info['ssid']
    password = wifi_info['password']

    # update page components
    print(f'updating ssid and passworld fields to {ssid} and {password}')
    set_component_txt(CONFIG_PAGE_NAME, _SSID_FIELD_OBJNAME, ssid)
    set_component_txt(CONFIG_PAGE_NAME, _PASSWORD_FIELD_OBJNAME, password)
    update_config_status()


def update_config_status():
    status = "Status: "
    if Wifi.is_connected():
        status += "Connected"
    else:
        status += "Disconnected"
    set_component_txt(CONFIG_PAGE_NAME, _STATUS_LABEL_OBJNAME, status)


def handle_config_page_msg(message):
    print("handling config page message")
    if message[0] == BUTTON_MESSAGE and message[3] == 0x00:
        id = message[2]

        if id == _CONNECT_BUTTON_ID:

            # get wifi info from fields
            # update wifi config
            # disconnect()
            pass
        elif id == _BACK_BUTTON_ID:
            # back button should reset the fields to their saved state
            # nextion handles the page change on press already
            load_config_page()
    # when connect button is pressed, update wifi config
    # then call disconnect() and try_connect()
    # then
    pass
