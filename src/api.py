import time

import urequests
import json

import wifi
import dt

IP = "192.168.0.195"

_NET_SLEEP_TIME_MS = 5
_QUEUE_DELAY_SECONDS = 0.1

# TODO: add helper method for handling urequests.get and returning None if its not okay
# TODO: add something similar for patch, post probably
# TODO: add doc strings
# TODO: add state machine for handling stuff. need it to handle error states. maybe keep track of screen states

_QUEUE_MAX_SIZE = 4

_queue = []
_droppable_queue = None
_last_call_time = dt.time_sec()


def queue_call(call, droppable=False):
    """Add a call to the queue. Returns true if adding succeeded. False if adding failed (queue full)."""
    global _droppable_queue
    if droppable:
        _droppable_queue = call
    else:
        if len(_queue) < _QUEUE_MAX_SIZE:
            _queue.append(call)
            print(f'queue length: {len(_queue)}')
        else:
            # can't add to queue; it's full
            print('queue full!')
            return False
    return True

def update():
    global _droppable_queue
    global _last_call_time
    curr_time = dt.time_sec()
    if curr_time - _last_call_time >= _QUEUE_DELAY_SECONDS:
        if len(_queue) > 0:
            _queue.pop()()  # pop call from queue and call it
            _last_call_time = curr_time
        elif _droppable_queue is not None:
            _droppable_queue()
            _droppable_queue = None
            _last_call_time = curr_time

def _get_safe(request):
    try:
        response = urequests.get(request)
        if response.status_code in [200, 201]:
            return json.loads(response.text)
        print(response.text)
    except OSError as e:
        print(e)
    return None

def _patch_safe(request, content):
    if wifi.is_connected():
        try:
            urequests.patch(request, json=content)
            time.sleep_ms(_NET_SLEEP_TIME_MS)
        except OSError as e:
            print(e)

def _post_safe(request):
    if wifi.is_connected():
        try:
            urequests.post(request)
            time.sleep_ms(_NET_SLEEP_TIME_MS)
        except OSError as e:
            print(e)

def get_source_dict(source_id):
    response = _get_safe(f'http://{IP}/api/sources/{source_id}')
    return response

def get_sources_dict():
    return _get_safe(f'http://{IP}/api/sources')

def get_streams_list():
    response = _get_safe(f'http://{IP}/api/streams')
    if response is not None:
        return response['streams']
    return None

def get_stream_dict(stream_id):
    return _get_safe(f'http://{IP}/api/streams/{stream_id}')

def set_stream(source_id, stream_id):
    _patch_safe(f'http://{IP}/api/sources/{source_id}', {"input": f'stream={stream_id}'})

def move_zone_to_source(zone_id, source_id):
    _patch_safe(f'http://{IP}/api/zones/{zone_id}', {"source-id": source_id})

def get_zones_dict():
    return _get_safe(f'http://{IP}/api/zones')

def get_zones_list():
    response = _get_safe(f'http://{IP}/api/zones')
    if response is not None:
        return response['zones']
    return None

def get_zone_dict(zone_id):
    return _get_safe(f'http://{IP}/api/zones/{zone_id}')

def command_stream(stream_id, cmd):
    _post_safe(f'http://{IP}/api/streams/{stream_id}/{cmd}')

def set_vol_f(zone_id, vol_f):
    _patch_safe(f'http://{IP}/api/zones/{zone_id}', {"vol_f": vol_f})

def set_mute(zone_id, muted):
    _patch_safe(f'http://{IP}/api/zones/{zone_id}', {"mute": muted})

def set_vol_f_mute(zone_id, vol_f, muted):
    _patch_safe(f'http://{IP}/api/zones/{zone_id}', {"vol_f": vol_f, "mute": muted})

def get_vol_f(zone_id):
    zone_response = get_zone_dict(zone_id)
    if zone_response is None:
        return None
    return zone_response["vol_f"]

def get_stream_id_from_source_dict(source):
    source_input = source['input']
    if source_input.startswith('local'):
        return None
    return int(source_input.split("=")[1])

def get_stream_id_from_zone_id(zone_id):
    zone = get_zone_dict(zone_id)
    if zone is None:
        return None
    source = get_source_dict(zone["source_id"])
    if source is None:
        return None
    return get_stream_id_from_source_dict(source)
