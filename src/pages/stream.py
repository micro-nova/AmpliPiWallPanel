import api
from audioconfig import AudioConfig
from displayserial import STREAM_PAGE_NAME
from dropdown import DropDown

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_ID = 9

_NUM_ITEM_FIELDS = 4

dropdown = DropDown(STREAM_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID,
                    _DOWN_BUTTON_ID, _LOADING_TEXT_ID, _NUM_ITEM_FIELDS)

_streams = []


def _change_stream_callback(index):
    audioconf = AudioConfig()
    new_stream = _streams[index]
    audioconf.change_stream(int(new_stream['id']))


dropdown.add_item_index_callback(lambda index: _change_stream_callback(index))


# only call this when on this page
def load_stream_page():
    """Loads stream page contents. Should only be called when the display is on the stream page."""
    global _streams
    dropdown.set_loading_state()
    # get list of streams
    print("Loading stream list")
    _streams = api.get_streams()
    names = [stream['name'] for stream in _streams]  # if 'name' in stream

    print(f'{len(names)} streams: ')
    print(names)
    # print(_streams)

    dropdown.populate(names)


def handle_stream_page_msg(message):
    """Handles messages from the display that are relevant to the stream page."""
    dropdown.handle_message(message)
