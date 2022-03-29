import api
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
    new_stream = _streams[index]

    pass


dropdown.add_item_index_callback(lambda index: _change_stream_callback(index))


# only call this when on this page
def load_stream_page():
    global _streams
    dropdown.set_loading_state()
    # get list of streams
    print("Loading stream list")
    _streams = api.get_streams_dict()
    print(_streams)
    names = [stream['name'] for stream in _streams]  # if 'name' in stream

    # stream_id_names = {stream.id: stream.name for stream in _streams}
    #
    # names = stream_id_names.values()
    # ids = stream_id_names.keys()
    # stream = stream_id_names[id]

    print(f'{len(names)} streams: ')
    print(names)
    print(_streams)

    dropdown.populate(names)


def handle_stream_page_msg(message):
    dropdown.handle_message(message)
