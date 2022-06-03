from app import polling
from app.audioconfig import AudioConfig
from app.displayserial import SOURCE_PAGE_NAME, message_is_button_event, button_is_pressed, message_id
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

dropdown = DropDown(SOURCE_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                    _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS)

_sources = ['Source 1', 'Source 2', 'Source 3', 'Source 4']


def _change_source_callback(index):
    audioconf = AudioConfig()
    new_source = _sources[index]
    print(f'changing source to {new_source}')
    audioconf.change_source(index)
    polling.invalid_group_handled()


dropdown.add_item_index_callback(_change_source_callback)


# only call this when on this page
# TODO: rename to load_page and change importing
def load_source_page():
    dropdown.set_loading_state()
    dropdown.populate(_sources)

def handle_msg(message):
    if message_is_button_event(message) and button_is_pressed(message) and message_id(message) == _BACK_BUTTON_ID:
        polling.invalid_group_handled()
    dropdown.handle_message(message)