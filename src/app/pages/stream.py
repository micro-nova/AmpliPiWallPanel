from app import api, displayserial, polling
from app.audioconfig import AudioConfig
from app.displayserial import STREAM_PAGE_NAME, BUTTON_MESSAGE
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

dropdown = DropDown(STREAM_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                    _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS,
                    first_image_id=_IMAGE_FIRST_ID, image_objname_prefix=_IMAGE_OBJNAME)

_streams = []


def _change_stream_callback(index):
    audioconf = AudioConfig()
    new_stream = _streams[index]
    audioconf.change_stream(int(new_stream['id']))
    polling.invalid_group_handled()


dropdown.add_item_index_callback(_change_stream_callback)


# only call this when on this page
def load_stream_page():
    """Loads stream page contents. Should only be called when the display is on the stream page."""
    global _streams
    dropdown.set_loading_state()
    # get list of streams
    print("Loading stream list")
    _streams = api.get_streams()
    if _streams is None:
        _streams = []
    names = [stream['name'] for stream in _streams]  # if 'name' in stream
    types = [displayserial.stream_type_to_pic_id(stream['type']) for stream in _streams]

    print(f'{len(names)} streams: ')
    print(names)

    dropdown.populate(names, types)


def handle_msg(message):
    """Handles messages from the display that are relevant to the stream page."""
    if message[0] == BUTTON_MESSAGE and message[3] == 0x01 and message[2] == _BACK_BUTTON_ID:
        polling.invalid_group_handled()
    dropdown.handle_message(message)
