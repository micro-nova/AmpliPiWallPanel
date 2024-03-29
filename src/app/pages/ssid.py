from app import wifi
from app.displayserial import SSID_PAGE_NAME
from app.dropdown import DropDown

_SSID_OBJNAME = "tssid"  # num

# component ids
_SSID_FIRST_ID = 1  # + index
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_OBJNAME = 'tloading'

_UP_BUTTON_OBJNAME = 'bup'
_DOWN_BUTTON_OBJNAME = 'bdown'

_NUM_SSID_FIELDS = 4

dropdown = DropDown()

def load_ssid_page():
    """Loads the contents of the SSID page. Should only be called when the display is on this page."""
    dropdown.init(SSID_PAGE_NAME, _SSID_FIRST_ID,
                    _SSID_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                    _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_SSID_FIELDS)
    # get list of ssid
    print("Loading SSID list")
    ssids_with_hidden = wifi.get_ssid_list()
    ssids = []
    for s in ssids_with_hidden:
        s_str = s.decode("utf-8")
        if len(s) > 0:
            if s_str not in ssids:
                ssids.append(s_str)
    print(f'{len(ssids_with_hidden)} networks are available')
    print(f'{len(ssids)} networks are visible (non-hidden)')

    dropdown.populate(ssids)


def handle_msg(message):
    """Receives a message from the ssid page (from the display) and processes it."""
    dropdown.handle_message(message)







