import api
from displayserial import ZONE_PAGE_NAME
from dropdown import DropDown

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_ID = 9

_NUM_ITEM_FIELDS = 4

dropdown = DropDown(ZONE_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID,
                    _DOWN_BUTTON_ID, _LOADING_TEXT_ID, _NUM_ITEM_FIELDS)

_zones = {}
_audioconf = None


# only call this when display is on this page
def load_zone_page(audioconf):
    global _zones
    global _audioconf
    _audioconf = audioconf
    dropdown.set_loading_state()
    # get list of zones
    print("Loading zone list")
    _zones = api.get_zones_dict()
    zone_names = []
    for zone in _zones['zones']:
        zone_names.append(zone['name'])

    print(f'{len(zone_names)} zones: ')
    print(zone_names)
    print(_zones)

    dropdown.populate(zone_names)


def handle_zone_page_msg(message):
    dropdown.handle_message(message)

def _change_zone_callback(index):
    new_zone = _zones[index]
    if _audioconf is not None:
        _audioconf.change_zone(int(new_zone['id']))