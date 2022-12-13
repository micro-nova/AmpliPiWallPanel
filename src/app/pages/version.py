import gc

from app import wifi, sysconsts, displayserial
from app.displayserial import VERSION_PAGE_NAME, message_is_button_event, button_is_pressed, message_id
from app.dropdown import DropDown
from app.ota import ota_updater
from app.pages import versioninfo

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_BACK_BUTTON_ID = 7
_LOADING_TEXT_OBJNAME = 'tloading'
_UP_BUTTON_OBJNAME = 'bup'
_DOWN_BUTTON_OBJNAME = 'bdown'
VERSION_OBJNAME = 'tversion'

_NUM_ITEM_FIELDS = 4

dropdown = DropDown()
_releases = []  # list of tag jsons (not just tag names)


_show_prereleases = False
def disable_prereleases():
    global _show_prereleases
    _show_prereleases = False

def enable_prerelease():
    global _show_prereleases
    _show_prereleases = True

def _select_version_callback(index):
    # load version info page since nextion display should be there already
    versioninfo.load_versioninfo_page(_releases[index])


def load_version_page():
    """Loads version page contents. Should only be called when the display is on the version page."""
    global _releases
    dropdown.init(VERSION_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                    _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS)
    dropdown.add_item_index_callback(_select_version_callback)
    # write current version to field
    displayserial.set_component_txt(displayserial.VERSION_PAGE_NAME, VERSION_OBJNAME, sysconsts.VERSION)

    if wifi.is_connected():
        _ota = ota_updater.make_ota_updater()

        _releases = _ota.get_all_releases()
        if not _show_prereleases:
            _releases = [release for release in _releases if not release['prerelease']]
        reload_version_page_ui()

        print(f'mem free before del: {gc.mem_free()}')
        del _ota
        _ota = None
        gc.collect()
        print(f'mem free after del: {gc.mem_free()}')

def reload_version_page_ui():
    # take raw _releases data and extract just the names
    release_names = [f"  {release['tag_name']} {release['name']}" for release in _releases]
    dropdown.populate(release_names)

def handle_msg(message):
    """Handles messages from the display that are relevant to the version page."""
    global _releases
    if message_is_button_event(message) and button_is_pressed(message) and message_id(message) == _BACK_BUTTON_ID:
        del _releases
        _releases = None
        gc.collect()
    dropdown.handle_message(message)
