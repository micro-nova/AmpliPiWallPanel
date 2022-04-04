import time

import urequests
import json

import wifi

IP = "192.168.0.195"

_NET_SLEEP_TIME_MS = 10

# TODO: add helper method for handling urequests.get and returning None if its not okay
# TODO: add something similar for patch, post probably
# TODO: remove type naming and add type hinting
# TODO: add doc strings
# TODO: add state machine for handling stuff. need it to handle error states. maybe keep track of screen states

def _get_safe(request):
    try:
        response = urequests.get(request)
        if response.status_code in [200, 201]:
            return json.loads(response.text)
        print(response.text)
    except Exception as e:
        print(e)
    return None


def get_source_dict(source_id):
    response = _get_safe(f'http://{IP}/api/sources/{source_id}')
    return response


def get_sources_dict():
    response = _get_safe(f'http://{IP}/api/sources')
    return response


def get_streams_list():
    response = _get_safe(f'http://{IP}/api/streams')
    return response['streams']


# returns dict
def get_stream_dict(stream_id):
    response = _get_safe(f'http://{IP}/api/streams/{stream_id}')
    return response


def set_stream(source_id, stream_id):
    if wifi.is_connected():
        urequests.patch(f'http://{IP}/api/sources/{source_id}', json={"input": f'stream={stream_id}'})
        time.sleep_ms(_NET_SLEEP_TIME_MS)


def move_zone_to_source(zone_id, source_id):
    if wifi.is_connected():
        urequests.patch(f'http://{IP}/api/zones/{zone_id}', json={"source-id": source_id})
        time.sleep_ms(_NET_SLEEP_TIME_MS)


def get_zones_dict():
    response = _get_safe(f'http://{IP}/api/zones')
    return response


def get_zones_list():
    response = _get_safe(f'http://{IP}/api/zones')
    return response['zones']


def get_zone_dict(zone_id):
    response = _get_safe(f'http://{IP}/api/zones/{zone_id}')
    return response


def command_stream(stream_id, cmd):
    if wifi.is_connected():
        urequests.post(f'http://{IP}/api/streams/{stream_id}/{cmd}')
        time.sleep_ms(_NET_SLEEP_TIME_MS)

# TODO: make queue system for this
def set_vol_f(zone_id, vol_f):
    if wifi.is_connected():
        urequests.patch(f'http://{IP}/api/zones/{zone_id}', json={"vol_f": vol_f})
        time.sleep_ms(_NET_SLEEP_TIME_MS)

# TODO: special handling for response error
def set_mute(zone_id, muted):
    if wifi.is_connected():
        response = urequests.patch(f'http://{IP}/api/zones/{zone_id}', json={"mute": muted})
        time.sleep_ms(_NET_SLEEP_TIME_MS)


def get_vol_f(zone_id):
    zone_response = get_zone_dict(zone_id)
    if zone_response is None:
        return None
    return zone_response["vol_f"]


# TODO: are there errors to handle?
def get_stream_id_from_source_dict(source):
    source_input = source['input']
    if source_input.startswith('local'):
        return None
    else:
        return int(source_input.split("=")[1])

# TODO: are there errors to handle?
def get_stream_id_from_zone_id(zone_id):
    zone = get_zone_dict(zone_id)
    if zone is None:
        return None
    source = get_source_dict(zone["source_id"])
    if source is None:
        return None
    return get_stream_id_from_source_dict(source)
