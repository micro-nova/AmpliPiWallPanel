import time

import urequests
import json
import gc

from app import wifi
from app import dt

_amplipi_ip = ''

_NET_SLEEP_TIME_MS = 5
_QUEUE_DELAY_SECONDS = 0.1

# TODO: add state machine for handling stuff. need it to handle error states. maybe keep track of screen states
# TODO: try replacing json library with urequests.json (where .text is normally)

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
            # print(f'queue length: {len(_queue)}')
        else:
            # can't add to queue; it's full
            print('queue full!')
            return False
    return True

def update():
    """Processes call queue."""
    global _droppable_queue
    global _last_call_time
    global _amplipi_ip
    curr_time = dt.time_sec()
    if curr_time - _last_call_time >= _QUEUE_DELAY_SECONDS:
        _amplipi_ip = wifi.get_amplipi_ip()
        if len(_queue) > 0:
            _queue.pop()()  # pop call from queue and call it
            _last_call_time = curr_time
        elif _droppable_queue is not None:
            _droppable_queue()
            _droppable_queue = None
            _last_call_time = curr_time

def _get_safe(request):
    """Wraps get with try-except, checks status_code, and checks if wifi is connected first.
    Returns dict if success, returns None if failed """
    if wifi.is_connected() and _amplipi_ip:
        try:
            response = urequests.get(request)
            if response.status_code in [200, 201]:
                return json.loads(response.text)
            print(response.text)
        except OSError as e:
            print(e)
    return None

def _patch_safe(request, content):
    """Wraps get with try-except, checks if wifi is connected"""
    if wifi.is_connected() and _amplipi_ip:
        try:
            urequests.patch(request, json=content)
            # TODO: get response and handle status_code similarly to _get_safe
            # maybe not because its too big
            time.sleep_ms(_NET_SLEEP_TIME_MS)
        except OSError as e:
            print(e)

def _post_safe(request):
    """Wraps post with try-except, checks if wifi is connected"""
    if wifi.is_connected() and _amplipi_ip:
        try:
            urequests.post(request)
            # TODO: get response and handle status_code similarly to _get_safe
            time.sleep_ms(_NET_SLEEP_TIME_MS)
        except OSError as e:
            print(e)

def get_source(source_id):
    """API call to get source from source_id. Returns it as a dict or None if failed."""
    response = _get_safe(f'http://{_amplipi_ip}/api/sources/{source_id}')
    return response

# def get_sources_dict():
#     """API call to get all sources. Returns it as a dict or None if failed."""
#     return _get_safe(f'http://{IP}/api/sources')

def get_streams():
    """API call to get all streams. Returns it as a list or None if failed."""
    response = _get_safe(f'http://{_amplipi_ip}/api/streams')
    if response is not None:
        return response['streams']
    return None

def get_stream(stream_id):
    """API call to get a stream. Returns it as a dict or None if failed."""
    return _get_safe(f'http://{_amplipi_ip}/api/streams/{stream_id}')

def set_stream(source_id, stream_id):
    """API call to change a source's input to a stream."""
    _patch_safe(f'http://{_amplipi_ip}/api/sources/{source_id}', {"input": f'stream={stream_id}'})

def move_zone_to_source(zone_id, source_id):
    """API call to move a zone to a source"""
    _patch_safe(f'http://{_amplipi_ip}/api/zones/{zone_id}', {"source_id": source_id})

def move_group_to_source(group_id, source_id):
    """API call to move a group to a source"""
    _patch_safe(f'http://{_amplipi_ip}/api/groups/{group_id}', {"source_id": source_id})

def get_zones():
    """API call to get all zones. Returns it as a list or None if failed."""
    response = _get_safe(f'http://{_amplipi_ip}/api/zones')
    if response is not None:
        return response['zones']
    return None

def get_groups():
    """API call to get all groups. Returns it as a list or None if failed."""
    response = _get_safe(f'http://{_amplipi_ip}/api/groups')
    if response is not None:
        return response['groups']
    return None

def get_zone(zone_id):
    """API call to get a zone. Returns it as a dict or None if failed."""
    return _get_safe(f'http://{_amplipi_ip}/api/zones/{zone_id}')

def get_group(group_id):
    """API call to get a group. Returns it as a dict or None if failed."""
    return _get_safe(f'http://{_amplipi_ip}/api/groups/{group_id}')

def send_stream_command(stream_id, cmd):
    """API call to post a command to a stream. Takes in the stream_id and command as cmd."""
    _post_safe(f'http://{_amplipi_ip}/api/streams/{stream_id}/{cmd}')

def set_vol_f(id, vol_f, using_group=False):
    """API call to set vol_f. Takes in zone_id and vol_f where vol_f is within the range [0, 1]"""
    if using_group:
        _patch_safe(f'http://{_amplipi_ip}/api/groups/{id}', {"vol_f": vol_f})
    else:
        _patch_safe(f'http://{_amplipi_ip}/api/zones/{id}', {"vol_f": vol_f})

def set_mute(id, muted, using_group=False):
    """API call to set muted state. Takes in zone_id and muted"""
    if using_group:
        _patch_safe(f'http://{_amplipi_ip}/api/groups/{id}', {"mute": muted})
    else:
        _patch_safe(f'http://{_amplipi_ip}/api/zones/{id}', {"mute": muted})

def set_vol_f_mute(id, vol_f, muted, using_group=False):
    """API call combining mute and vol_f assignment."""
    if using_group:
        _patch_safe(f'http://{_amplipi_ip}/api/groups/{id}', {"vol_f": vol_f, "mute": muted})
    else:
        _patch_safe(f'http://{_amplipi_ip}/api/zones/{id}', {"vol_f": vol_f, "mute": muted})

def get_vol_f(id, using_group=False):
    """API call to get vol_f from a zone_id"""
    if using_group:
        group_response = get_group(id)
        if group_response is None:
            return None
        return group_response["vol_f"]
    else:
        zone_response = get_zone(id)
        if zone_response is None:
            return None
        return zone_response["vol_f"]

def get_stream_id_from_source_dict(source):
    """Takes in a source dict and pulls out the stream id and returns it if it has one, or returns None if not"""
    if source is None:
        return None
    source_input = source['input']
    if source_input.startswith('local'):
        return None
    source_split = source_input.split("=")
    if len(source_split) == 2:
        return int(source_split[1])
    return None

# TODO: this should probably take in a dict instead of an id. I don't think these helper methods should be
#  making api calls
def get_stream_id_from_zone_id(zone_id):
    """Makes an API call to grab the stream id from zone_id. Returns the stream id from zone, or returns None if failed."""
    zone = get_zone(zone_id)
    if zone is None:
        return None
    source = get_source(zone["source_id"])
    if source is None:
        return None
    return get_stream_id_from_source_dict(source)

def get_stream_id_from_group_id(group_id):
    """Makes an API call to grab the stream_id from group_id. Returns the stream id from group, or returns None if failed."""
    group = get_group(group_id)
    if group is None:
        return None
    source = get_source(group['source_id'])
    if source is None:
        return None
    return get_stream_id_from_source_dict(source)
