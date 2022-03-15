# component names
import Wifi
from DisplaySerial import BUTTON_MESSAGE, set_visible, SSID_PAGE_NAME, set_component_txt
from DropDown import DropDown

_SSID_OBJNAME = "tssid"  # num

# component ids
_SSID_FIRST_ID = 1  # + index
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6

_NUM_SSID_FIELDS = 4

dropdown = DropDown(SSID_PAGE_NAME, _SSID_FIRST_ID,
                    _SSID_OBJNAME, _UP_BUTTON_ID,
                    _DOWN_BUTTON_ID, _NUM_SSID_FIELDS)


# only call this when on this page
def load_ssid_page():
    # get list of ssid
    print("Loading SSID list")
    ssids_with_hidden = Wifi.get_ssid_list()
    ssids = []
    for s in ssids_with_hidden:
        s_str = s.decode("utf-8")
        if len(s) > 0:
            if s_str not in ssids:
                ssids.append(s_str)
    print(f'{len(ssids_with_hidden)} networks are available')
    print(f'{len(ssids)} networks are visible (non-hidden)')

    dropdown.populate(ssids)


def handle_ssid_page_msg(message):
    dropdown.handle_message(message)
    # # compute
    # if message[0] == BUTTON_MESSAGE and message[3] == 0x01:
    #     id = message[2]
    #     if id in range(_SSID_FIRST_ID, _SSID_FIRST_ID + _NUM_SSID_FIELDS):
    #         screen_index = id - _SSID_FIRST_ID
    #         ssid_index = screen_index + start_index
    #         ssid = ssids[ssid_index]
    #         # nextion already copies this over to the config screen ssid field
    #         # i don't think anything needs to be done here.
    #
    #         # if ssid_index < len(ssids):
    #         #     ssid = ssids[ssid_index]
    #         # else:
    #     elif id == _UP_BUTTON_ID:
    #         _on_up()
    #     elif id == _DOWN_BUTTON_ID:
    #         _on_down()







