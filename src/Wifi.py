# from os.path import exists
import os
import json
import network
import time

WIFI_CONFIG_FILENAME = 'wifi.txt'
RETRY_COUNT = 3
RETRY_TIME_MS = 500

# create wlan for connecting to router
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


# returns a dictionary containing keys ssid, password
def load_wifi_info():
    wifi_file_exists = os.path.exists(WIFI_CONFIG_FILENAME)
    wifi_file_dict = {'ssid': '', 'password': ''}

    # either create a new file with the empty dict or load the existing one
    if wifi_file_exists:
        with open(WIFI_CONFIG_FILENAME) as wifi_file:
            wifi_file_str = wifi_file.read()
            wifi_file_dict = json.loads(wifi_file_str)
    else:
        with open(WIFI_CONFIG_FILENAME, 'w') as wifi_file:
            wifi_file_str = json.dumps(wifi_file_dict)
            wifi_file.write(wifi_file_str)

    return wifi_file_dict


def save_wifi_info(wifi_file_dict):
    with open(WIFI_CONFIG_FILENAME, 'w') as wifi_file:
        wifi_file_str = json.dumps(wifi_file_dict)
        wifi_file.write(wifi_file_str)


# returns a list of tuples that look like
# (ssid, bssid, channel, RSSI, authmode, hidden)
def get_ssid_list():
    tuples = wlan.scan()
    ssids = []
    for t in tuples:
        # what happens if there is a hidden network? would the ssid be an empty string?
        # TODO: handle hidden networks
        ssids.append(t[0])
    return wlan.scan()


# called during initialization or after applying new wifi configuration
def try_connecting():
    wifi_info_dict = load_wifi_info()
    for i in range(RETRY_COUNT):
        if not wlan.isconnected():
            print(f"Connecting to {wifi_info_dict['ssid']}...{i + 1}")
            wlan.connect(wifi_info_dict['ssid'], wifi_info_dict['password'])
            time.sleep_ms(RETRY_TIME_MS)
        else:
            print(f"Connected to {wifi_info_dict['ssid']}")
            break

    if wlan.isconnected():
        return True
    else:
        print(f"Failed to connect to {wifi_info_dict['ssid']}")
        return False


# this can be called periodically to reconnect if needed
def keep_connected():
    wifi_info_dict = load_wifi_info()
    if not wlan.isconnected():
        wlan.connect(wifi_info_dict['ssid'], wifi_info_dict['password'])


def is_connected():
    return wlan.isconnected()
