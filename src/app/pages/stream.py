import gc

from app import api, displayserial, polling
from app.audioconfig import AudioConfig
from app.displayserial import STREAM_PAGE_NAME, message_is_button_event, button_is_pressed, message_id
from app.dropdown import DropDown

_ITEM_OBJNAME = "titem"  # num
_IMAGE_OBJNAME = "picon"

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_OBJNAME = 'tloading'
_IMAGE_FIRST_ID = 10
_UP_BUTTON_OBJNAME = 'bup'
_DOWN_BUTTON_OBJNAME = 'bdown'
_BACK_BUTTON_ID = 7


_NUM_ITEM_FIELDS = 4

dropdown = DropDown()

_streams = []


def _change_stream_callback(index):
    audioconf = AudioConfig()
    if index == 0:
        audioconf.use_rca()
    else:
        new_stream = _streams[index]
        audioconf.change_stream(int(new_stream['id']))
    polling.invalid_group_handled()

# only call this when on this page
def load_stream_page():
    """Loads stream page contents. Should only be called when the display is on the stream page."""
    global _streams
    dropdown.init(STREAM_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                    _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS,
                    first_image_id=_IMAGE_FIRST_ID, image_objname_prefix=_IMAGE_OBJNAME)
    dropdown.add_item_index_callback(_change_stream_callback)
    # get list of streams
    print("Loading stream list")
    del _streams
    _streams = None
    gc.collect()
    _streams = api.get_streams()
    if _streams is None:
        _streams = []
        names = []
        types = []
    else:
        names = [stream['name'] for stream in _streams]  # if 'name' in stream
        types = [displayserial.stream_type_to_pic_id(stream['type']) for stream in _streams]
        _streams.insert(0, None) # RCA is handled differently in _change_stream_callback
        names.insert(0, polling.source_name)
        types.insert(0, displayserial.stream_type_to_pic_id('rca'))
    print(f'{len(names)} streams: ')
    print(names)

    dropdown.populate(names, types)


def handle_msg(message):
    """Handles messages from the display that are relevant to the stream page."""
    if message_is_button_event(message) and button_is_pressed(message) and message_id(message) == _BACK_BUTTON_ID:
        polling.invalid_group_handled()
        _streams.clear()
        gc.collect()
    dropdown.handle_message(message)