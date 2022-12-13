import gc

from app import api, displayserial, polling, mqttconfig
from app.audioconfig import AudioConfig
from app.displayserial import ZONE_PAGE_NAME, message_is_button_event, button_is_pressed, message_id
from app.dropdown import DropDown

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_OBJNAME = 'tloading'
_UP_BUTTON_OBJNAME = 'bup'
_DOWN_BUTTON_OBJNAME = 'bdown'
_GROUP_BUTTON_ID = 10
_GROUP_BUTTON_OBJNAME = 'bgroup'
_BACK_BUTTON_ID = 7

_NUM_ITEM_FIELDS = 4

_dropdown = DropDown()

_zones = []
_groups = []

_display_groups_last = False

def _on_group_zone_button():
    global _display_groups_last
    # temporarily just switch to group mode

    if _display_groups_last:
        load_zone_page(groups=False)
    else:
        load_zone_page(groups=True)

def _change_zone_callback(index):
    audioconf = AudioConfig()
    new_zone = _zones[index]
    audioconf.change_zone(int(new_zone['id']))
    polling.invalid_group_handled()

    # if mqtt's topic is empty, populate it with something reasonable
    topic = mqttconfig.get_topic()
    if topic is None or topic == '':
        mqttconfig.set_topic_base(new_zone['name'])

def _change_group_callback(index):
    audioconfig = AudioConfig()
    new_group = _groups[index]
    audioconfig.change_group(int(new_group['id']))
    polling.invalid_group_handled()

    # if mqtt's topic is empty, populate it with something reasonable
    topic = mqttconfig.get_topic()
    if topic is None or topic == '':
        mqttconfig.set_topic_base(new_group['name'])


# only call this when display is on this page
def load_zone_page(groups=False):
    global _display_groups_last
    global _zones
    global _groups
    _display_groups_last = groups
    _dropdown.init(ZONE_PAGE_NAME, _ITEM_FIRST_ID,
                     _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                     _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS)
    _dropdown.clear_item_index_callbacks()

    if groups:
        displayserial.set_component_txt(displayserial.ZONE_PAGE_NAME, 'tlabel', 'Groups')
        displayserial.set_component_txt(displayserial.ZONE_PAGE_NAME, 'bgroup', 'Zones')
        _dropdown.add_item_index_callback(_change_group_callback)
        # get list of groups
        print('Loading group list')
        _groups = api.get_groups()
        if _groups is None:
            _groups = []
        names = [group['name'] for group in _groups]
        _dropdown.populate(names)

    else:
        displayserial.set_component_txt(displayserial.ZONE_PAGE_NAME, 'tlabel', 'Zones')
        displayserial.set_component_txt(displayserial.ZONE_PAGE_NAME, 'bgroup', 'Groups')
        _dropdown.add_item_index_callback(_change_zone_callback)
        # get list of zones
        print("Loading zone list")
        _zones = api.get_zones()
        if _zones is None:
            _zones = []
        names = [zone['name'] for zone in _zones]
        _dropdown.populate(names)

def handle_msg(message):
    if message_is_button_event(message) and button_is_pressed(message):
        id = message_id(message)
        if id == _BACK_BUTTON_ID:
            _zones.clear()
            _groups.clear()
            gc.collect()
            polling.invalid_group_handled()
        if id == _GROUP_BUTTON_ID:
            _on_group_zone_button()
    _dropdown.handle_message(message)
