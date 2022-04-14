import json

from app.displayserial import VERSION_PAGE_NAME
from app.dropdown import DropDown
from app.ota.ota_updater import OTAUpdater
from app.pages import versioninfo

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

_releases = [] # list of tag jsons (not just tag names)

_ota = None

def _select_version_callback(index):
    # load version info page since nextion display should be there already
    versioninfo.load_versioninfo_page(_ota, _releases[index])

dropdown.add_item_index_callback(_select_version_callback)

def load_version_page():
    """Loads version page contents. Should only be called when the display is on the version page."""
    global _releases
    global _ota
    dropdown.set_loading_state()
    if _ota is None:
        token = None
        with open('temp-token.txt') as file:
            token = json.loads(file.read())

        if token is None:
            # _ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src/app',
            #                   secrets_files=['wifi.txt', 'zone.txt', 'temp-token.txt'])
            _ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src', module='')
            print('OTAUpdater loaded without token.')
        else:
            _ota = OTAUpdater('micro-nova/WallPanel', main_dir='app', github_src_dir='src', module='',
                              headers={'Authorization': 'token {}'.format(token['token'])})
            print('OTAUpdater loaded with token.')

    _releases = _ota.get_all_releases()
    reload_version_page_ui()

def reload_version_page_ui():
    # take raw _releases data and extract just the names
    release_names = [release['name'] for release in _releases]

    dropdown.populate(release_names)

def handle_version_page_msg(message):
    """Handles messages from the display that are relevant to the version page."""
    dropdown.handle_message(message)
