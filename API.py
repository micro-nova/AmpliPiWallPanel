import urequests
import json

IP = "192.168.0.195"


def get_source_json(sid):
    response = json.loads(urequests.get(f'http://{IP}/api/sources/{sid}').text)
    return response


def get_zone_json(zid):
    response = json.loads(urequests.get(f'http://{IP}/api/zones/{zid}').text)
    return response


def command_stream(sid, cmd):
    urequests.post(f'http://{IP}/api/streams/{sid}/{cmd}')


def get_stream_id_from_zone(zid):
    zone = get_zone_json(zid)
    source = get_source_json(zone["source_id"])
    source_input = source["input"]

    if source_input.startswith("local"):
        return None

    return int(source["input"].split("=")[1])