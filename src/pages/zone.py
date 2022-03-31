import api
from audioconfig import AudioConfig
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

_zones = []


def _change_zone_callback(index):
    audioconf = AudioConfig()
    new_zone = _zones[index]
    audioconf.change_zone(int(new_zone['id']))


dropdown.add_item_index_callback(lambda index: _change_zone_callback(index))


# only call this when display is on this page
def load_zone_page():
    global _zones
    dropdown.set_loading_state()
    # get list of zones
    print("Loading zone list")
    _zones = api.get_zones_list()
    names = [zone['name'] for zone in _zones]

    print(f'{len(names)} zones: ')
    print(names)
    # print(_zones)

    dropdown.populate(names)


def handle_zone_page_msg(message):
    dropdown.handle_message(message)
