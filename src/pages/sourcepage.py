import api
from displayserial import SOURCE_PAGE_NAME
from dropdown import DropDown

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


sources_json = {}


# only call this when on this page
def load_source_page():
    global sources_json
    dropdown.set_loading_state()
    # get list of sources
    print("Loading source list")
    sources_json = api.get_sources_dict()
    source_names = []
    for source in sources_json['sources']:
        source_names.append(source['name'])

    dropdown.populate(source_names)


def handle_source_page_msg(message):
    dropdown.handle_message(message)