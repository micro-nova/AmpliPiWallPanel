# component names
import Wifi
from DisplaySerial import BUTTON_MESSAGE, set_visible, SSID_PAGE_NAME, set_component_txt

_SSID_OBJNAME = "tssid"  # num

# component ids
_SSID_ID_START = 1  # + index
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6

_NUM_SSID_FIELDS = 4

ssids = []
start_index = 0


# only call this when on this page
def load_ssid_page():
    global ssids
    # get list of ssid
    print("Loading SSID list")
    ssids_with_hidden = Wifi.get_ssid_list()
    ssids.clear()
    for s in ssids_with_hidden:
        if len(s) > 0:
            ssids.append(s)
    print(f'{len(ssids_with_hidden)} networks are available')
    print(f'{len(ssids)} networks are visible (non-hidden)')
    _update_ssid_fields(ssids)


def handle_ssid_page_msg(message):
    # compute
    if message[0] == BUTTON_MESSAGE and message[3] == 0x01:
        id = message[2]
        if id in range(_SSID_ID_START, _SSID_ID_START + _NUM_SSID_FIELDS):
            screen_index = id - _SSID_ID_START
            ssid_index = screen_index + start_index
            ssid = ssids[ssid_index]
            # nextion already copies this over to the config screen ssid field
            # i don't think anything needs to be done here.

            # if ssid_index < len(ssids):
            #     ssid = ssids[ssid_index]
            # else:
        elif id == _UP_BUTTON_ID:
            _on_up()
        elif id == _DOWN_BUTTON_ID:
            _on_down()


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


def _update_nav_button_vis():
    if start_index == 0:
        # make up button invisible
        set_visible(_UP_BUTTON_ID, False)
    else:
        # make up button visible
        set_visible(_UP_BUTTON_ID, True)
    if start_index == len(ssids) - _NUM_SSID_FIELDS:
        # make down button invisible
        set_visible(_DOWN_BUTTON_ID, False)
    else:
        # make down button visible
        set_visible(_DOWN_BUTTON_ID, True)


def _ssid_name(index):
    return f'{_SSID_OBJNAME}{index}'


def _ssid_id(index):
    return _SSID_ID_START + index


def _update_ssid_fields(ssids):
    # print("Updating SSID fields")
    # print(f'There are {len(ssids)} ssids')
    # # for now, drop empty (hidden networks) ssids
    # ssids_non_null = []
    # for s in ssids:
    #     if len(s) > 0:
    #         ssids_non_null.append(s)
    # print(f'{num_ssids} networks are visible (non-hidden)')

    num_ssids = len(ssids)
    # make sure all fields are visible
    # TODO: make sure this is only called when on this page since set_visible only works locally
    for i in range(_NUM_SSID_FIELDS):
        set_visible(i + _SSID_ID_START, True)
        print(f'Making {i}th field visible')

    # if there is less than _NUM_SSID, disable unnecessary fields
    if num_ssids < _NUM_SSID_FIELDS:
        for i in range(num_ssids, _NUM_SSID_FIELDS):
            set_visible(i + _SSID_ID_START, False)
            print(f'Making {i}th field invisible')

    # populate fields
    for i in range(min(_NUM_SSID_FIELDS, num_ssids)):
        # ssid_string = str(ssids[i + start_index])
        ssid_string = ssids[i + start_index].decode("utf-8")
        _set_ssid_field_txt(i, ssid_string)
        print(f'Making {i}th field say {ssid_string}')

    # since we just changed the state of the displayed ssid list,
    # we need to update the up/down button visibilities
    _update_nav_button_vis()


def _set_ssid_field_txt(index, txt):
    set_component_txt(SSID_PAGE_NAME, _ssid_name(index), txt)
