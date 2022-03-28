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


streams_json = {}


# only call this when on this page
def load_stream_page():
    global streams_json
    dropdown.set_loading_state()
    # get list of sources
    print("Loading source list")
    streams_json = api.get_streams_dict()
    stream_names = []
    for stream in streams_json['streams']:
        stream_names.append(stream['name'])

    print(f'{len(stream_names)} sources: ')
    print(stream_names)
    print(streams_json)

    dropdown.populate(stream_names)


def handle_stream_page_msg(message):
    dropdown.handle_message(message)
