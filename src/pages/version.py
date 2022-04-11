import wifi
from displayserial import VERSION_PAGE_NAME
from dropdown import DropDown
from ota.ota_updater import OTAUpdater

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_ID = 9

_NUM_ITEM_FIELDS = 4

dropdown = DropDown(VERSION_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID,
                    _DOWN_BUTTON_ID, _LOADING_TEXT_ID, _NUM_ITEM_FIELDS)

_versions = []

def _select_version_callback(index):
    # TODO: move to version page
    #  grab version info from _versions[index]
    pass

dropdown.add_item_index_callback(_select_version_callback)

def load_version_page():
    """Loads version page contents. Should only be called when the display is on the version page."""
    global _versions
    dropdown.set_loading_state()
    # TODO: get list of versions from github api
    #  store in _versions

    # temporary test to get a list of tags
    ota = OTAUpdater('micro-nova/AmpliPi')

    _versions = ota.get_all_tags()

    # take raw _versions data and extract just the tag names
    tag_names = [tag['name'] for tag in _versions]

    dropdown.populate(tag_names)

def handle_version_page_msg(message):
    """Handles messages from the display that are relevant to the version page."""
    dropdown.handle_message(message)
