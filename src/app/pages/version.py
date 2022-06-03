import gc
import json

from app import wifi, sysconsts
from app.displayserial import VERSION_PAGE_NAME
from app.dropdown import DropDown
from app.ota.ota_updater import OTAUpdater
from app.pages import versioninfo

_ITEM_OBJNAME = "titem"  # num

# component ids
_ITEM_FIRST_ID = 1
_UP_BUTTON_ID = 5
_DOWN_BUTTON_ID = 6
_LOADING_TEXT_OBJNAME = 'tloading'
_UP_BUTTON_OBJNAME = 'bup'
_DOWN_BUTTON_OBJNAME = 'bdown'

_NUM_ITEM_FIELDS = 4

dropdown = DropDown(VERSION_PAGE_NAME, _ITEM_FIRST_ID,
                    _ITEM_OBJNAME, _UP_BUTTON_ID, _UP_BUTTON_OBJNAME,
                    _DOWN_BUTTON_ID, _DOWN_BUTTON_OBJNAME, _LOADING_TEXT_OBJNAME, _NUM_ITEM_FIELDS)

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


dropdown.add_item_index_callback(_select_version_callback)

def load_version_page():
    """Loads version page contents. Should only be called when the display is on the version page."""
    global _releases
    if wifi.is_connected():
        dropdown.set_loading_state()
        token = None
        try:
            with open('temp-token.txt') as file:
                token = json.loads(file.read())
        except Exception:
            pass

        if token is None:
            _ota = OTAUpdater(sysconsts.WALL_PANEL_REPO, main_dir='app', github_src_dir='src', module='')
            print('OTAUpdater loaded without token.')
        else:
            _ota = OTAUpdater(sysconsts.WALL_PANEL_REPO, main_dir='app', github_src_dir='src', module='',
                              headers={'Authorization': 'token {}'.format(token['token'])})
            print('OTAUpdater loaded with token.')

        _releases = _ota.get_all_releases()
        reload_version_page_ui()

        print(f'mem free before del: {gc.mem_free()}')
        del _ota
        _ota = None
        gc.collect()
        print(f'mem free after del: {gc.mem_free()}')

def reload_version_page_ui():
    # take raw _releases data and extract just the names
    if _show_prereleases:
        release_names = [release['name'] for release in _releases]
    else:
        release_names = [release['name'] for release in _releases if not release['prerelease']]


    dropdown.populate(release_names)

def handle_msg(message):
    """Handles messages from the display that are relevant to the version page."""
    dropdown.handle_message(message)
