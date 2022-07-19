import gc

from app import api
from app.displayserial import PRESET_PAGE_NAME, message_is_button_event, button_is_pressed, message_id, set_visible
from app.dropdown import DropDown

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_UP_BUTTON_OBJNAME = 'bup'
_DOWN_BUTTON_ID = 6
_DOWN_BUTTON_OBJNAME = 'bdown'
_LOADING_TEXT_OBJNAME = 'tloading'

_NUM_ITEM_FIELDS = 4
_BACK_BUTTON_ID = 7

_dropdown = DropDown()
_preset_ids = []
_preset_names = []

def _apply_preset_callback(index):
    set_visible('zspinner', True)
    api.load_preset(_preset_ids[index])
    set_visible('zspinner', False)
    _preset_ids.clear()
    _preset_names.clear()
    gc.collect()

def load_preset_page():
    global _preset_ids
    global _preset_names
    _dropdown.init(PRESET_PAGE_NAME, _ITEM_FIRST_ID,
                     _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                     _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS)

    _dropdown.set_loading_state()
    _dropdown.clear_item_index_callbacks()
    _dropdown.add_item_index_callback(_apply_preset_callback)

    presets = api.get_presets()
    if presets is None:
        presets = []
    _preset_ids = [p['id'] for p in presets]
    _preset_names = [p['name'] for p in presets]
    gc.collect()

    _dropdown.populate(_preset_names)

def handle_msg(message):
    if message_is_button_event(message) and button_is_pressed(message):
        id = message_id(message)
        if id == _BACK_BUTTON_ID:
            _preset_ids.clear()
            _preset_names.clear()
            gc.collect()
    _dropdown.handle_message(message)
