import json
import network
import time

from app.displayserial import change_page, CONFIG_PAGE_NAME, CONNECTION_PAGE_NAME
from app.pages.connection import load_connection_page

_WIFI_CONFIG_FILENAME = '../../wifi.txt'

# create wlan for connecting to router
_wlan = network.WLAN(network.STA_IF)
_wlan.active(True)
_set_page_config = False

_amplipi_ip = ''
def load_wifi_info():
    global _amplipi_ip
    """Loads wifi info from file (creates file if it doesn't exist). Returns wifi dict with ssid and password"""
    wifi_file_dict = {'ssid': '', 'password': '', 'ip': ''}
    try:
        with open(_WIFI_CONFIG_FILENAME) as wifi_file:
            wifi_file_str = wifi_file.read()
            wifi_file_dict = json.loads(wifi_file_str)
            if 'ip' in wifi_file_dict:
                _amplipi_ip = wifi_file_dict['ip']
    except OSError:
        # open failed, make file
        _save_wifi_info(wifi_file_dict)
    return wifi_file_dict


def save_wifi_info(ssid, password, ip):
    """Saves wifi info to file"""
    _save_wifi_info({'ssid': ssid, 'password': password, 'ip': ip})


def _save_wifi_info(wifi_file_dict):
    # TODO: specify encoding??? works fine without it
    with open(_WIFI_CONFIG_FILENAME, 'w') as wifi_file:
        wifi_file_str = json.dumps(wifi_file_dict)
        wifi_file.write(wifi_file_str)


# returns a list of tuples that look like
# (ssid, bssid, channel, RSSI, authmode, hidden)
def get_ssid_list():
    """Returns a list of SSIDs as tuples that look like (ssid, bssid, channel, RSSI, authmode, hidden)"""
    # TODO: investigate effectiveness of reactivating wifi
    _wlan.active(False)
    time.sleep_ms(100)
    _wlan.active(True)
    tuples = _wlan.scan()
    # what happens if there is a hidden network? would the ssid be an empty string?
    # TODO: handle hidden networks
    return [t[0] for t in tuples]

def try_connect():
    """Tries connecting to wifi. Should be called during initialization or after applying new wifi configuration."""
    global _set_page_config
    if not _wlan.active():
        _wlan.active(True)

    wifi_info_dict = load_wifi_info()
    if len(wifi_info_dict['ssid']) != 0:
        start_time = time.time()
        try:
            _wlan.connect(wifi_info_dict['ssid'], wifi_info_dict['password'])
        except OSError as e:
            print("uhh I don't think it should crash here")
            print(e)
        print(f"Connecting to ssid: {wifi_info_dict['ssid']} pass: {wifi_info_dict['password']}...")
        while time.time() - start_time <= 3 and not _wlan.isconnected():
            # TODO: try connecting more. it often fails to connect where it should be able to.
            pass

        if _wlan.isconnected():
            print(f"Connected to {wifi_info_dict['ssid']}")
            return True
        print(f"Failed to connect to {wifi_info_dict['ssid']}")
        needs_config = True
    else:
        needs_config = True

    if needs_config:
        if not _set_page_config:
            print("Please configure wifi settings.")
            change_page(CONNECTION_PAGE_NAME)
            load_connection_page()
            _set_page_config = True
        return False

# TODO: use this function. investigate micropython's wifi disconnect behavior
def keep_connected():
    """Can be called periodically to reconnect if needed."""
    if not _wlan.active():
        _wlan.active(True)
    wifi_info_dict = load_wifi_info()
    if not _wlan.isconnected():
        _wlan.connect(wifi_info_dict['ssid'], wifi_info_dict['password'])

def is_connected():
    """Returns true if connected to wifi. False if not."""
    return _wlan.isconnected()

def disconnect():
    """Disconnects from the currently connected wireless network."""
    _wlan.disconnect()

def get_amplipi_ip():
    return _amplipi_ip