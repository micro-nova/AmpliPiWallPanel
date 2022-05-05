from app.displayserial import SOURCE_PAGE_NAME
from app.dropdown import DropDown

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_ID = 9

_NUM_ITEM_FIELDS = 4

dropdown = DropDown(SOURCE_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID,
                    _DOWN_BUTTON_ID, _LOADING_TEXT_ID, _NUM_ITEM_FIELDS)

_sources = []


def _change_source_callback(index):
    # TODO:
    # from stream.py:
    # audioconf = AudioConfig()
    # new_stream = _streams[index]
    # audioconf.change_stream(int(new_stream['id']))
    pass

dropdown.add_item_index_callback(_change_source_callback)


# only call this when on this page
# TODO: rename to load_page and change importing
def load_source_page():
    global _sources
    dropdown.set_loading_state()
    # get list of sources (???)
    print('Loading source list')
    _sources = api.get_sources() # TODO:
    names = ...