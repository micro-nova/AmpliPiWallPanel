import json
import network
import time

from DisplaySerial import change_page, CONFIG_PAGE_NAME

_WIFI_CONFIG_FILENAME = '../wifi.txt'

# create wlan for connecting to router
_wlan = network.WLAN(network.STA_IF)
_wlan.active(True)
_set_page_config = False


# returns a dictionary containing keys ssid, password
def load_wifi_info():
    wifi_file_dict = {'ssid': '', 'password': ''}
    try:
        with open(_WIFI_CONFIG_FILENAME) as wifi_file:
            wifi_file_str = wifi_file.read()
            wifi_file_dict = json.loads(wifi_file_str)
    except OSError:
        # open failed, make file
        _save_wifi_info(wifi_file_dict)
    return wifi_file_dict


def save_wifi_info(ssid, password):
    _save_wifi_info({'ssid': ssid, 'password': password})


def _save_wifi_info(wifi_file_dict):
    with open(_WIFI_CONFIG_FILENAME, 'w') as wifi_file:
        wifi_file_str = json.dumps(wifi_file_dict)
        wifi_file.write(wifi_file_str)


# returns a list of tuples that look like
# (ssid, bssid, channel, RSSI, authmode, hidden)
def get_ssid_list():
    tuples = _wlan.scan()
    ssids = []
    for t in tuples:
        # what happens if there is a hidden network? would the ssid be an empty string?
        # TODO: handle hidden networks
        ssids.append(t[0])
    return ssids


# called during initialization or after applying new wifi configuration
def try_connect():
    global _set_page_config
    if not _wlan.active():
        _wlan.active(True)

    needs_config = False
    wifi_info_dict = load_wifi_info()
    if len(wifi_info_dict['ssid']) != 0:
        start_time = time.time()
        try:
            _wlan.connect(wifi_info_dict['ssid'], wifi_info_dict['password'])
        except OSError:
            print("uhh I don't think it should crash here")
        print(f"Connecting to ssid: {wifi_info_dict['ssid']} pass: {wifi_info_dict['password']}...")
        while time.time() - start_time <= 3 and not _wlan.isconnected():
            pass

        if _wlan.isconnected():
            print(f"Connected to {wifi_info_dict['ssid']}")
            return True
        else:
            print(f"Failed to connect to {wifi_info_dict['ssid']}")
            needs_config = True
    else:
        needs_config = True

    if needs_config:
        if not _set_page_config:
            print("Please configure wifi settings.")
            change_page(CONFIG_PAGE_NAME)
            _set_page_config = True
        return False


# this can be called periodically to reconnect if needed
def keep_connected():
    if not _wlan.active():
        _wlan.active(True)
    wifi_info_dict = load_wifi_info()
    if not _wlan.isconnected():
        _wlan.connect(wifi_info_dict['ssid'], wifi_info_dict['password'])


def is_connected():
    return _wlan.isconnected()


def disconnect():
    _wlan.disconnect()
