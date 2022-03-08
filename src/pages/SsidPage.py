# component names
import Wifi
from DisplaySerial import BUTTON_MESSAGE, set_visible

_SSID_OBJNAME = "tssid"  # num

# component ids
_SSID_ID_START = 1  # + index

_NUM_SSID_FIELDS = 4

ssids = []
start_index = 0


# only call this when on this page
def load_ssid_page():
    global ssids
    # get list of ssid
    ssids = Wifi.get_ssid_list()
    _update_ssid_fields(ssids)


def handle_ssid_page_msg(message):
    # compute
    if message[0] == BUTTON_MESSAGE and message[3] == 0x00:
        id = message[2]
        if id in range(_SSID_ID_START, _SSID_ID_START + _NUM_SSID_FIELDS):
            screen_index = id - _SSID_ID_START
            ssid_index = screen_index + start_index
            ssid = ssids[ssid_index]
            # if ssid_index < len(ssids):
            #     ssid = ssids[ssid_index]
            # else:


# decrement list start index, keep within range
def _on_up():
    global start_index
    start_index -= 1
    if start_index < 0:
        start_index = 0
    _update_ssid_fields(ssids)


# increment list start index, keep within range
def _on_down():
    global start_index
    start_index += 1
    if start_index > len(ssids) - _NUM_SSID_FIELDS:
        start_index = len(ssids) - _NUM_SSID_FIELDS
    _update_ssid_fields(ssids)


def _ssid_name(index):
    return f'{_SSID_OBJNAME}{index}'


def _ssid_id(index):
    return _SSID_ID_START + index


def _update_ssid_fields(ssids):
    # populate ssid fields based on start_index
    # if there is less than _NUM_SSID, disable unnecessary fields
    # also make sure the necessary ones are enabled

    # make sure all fields are visible
    # TODO: make sure this is only called when on this page since set_visible only works locally
    for i in range(_NUM_SSID_FIELDS):
        set_visible(i + _SSID_ID_START, True)
