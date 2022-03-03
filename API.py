import urequests
import json

IP = "192.168.0.195"


def get_source_json(source_id):
    response = json.loads(urequests.get(f'http://{IP}/api/sources/{source_id}').text)
    return response


def get_zone_json(zone_id):
    response = json.loads(urequests.get(f'http://{IP}/api/zones/{zone_id}').text)
    return response


def command_stream(stream_id, cmd):
    urequests.post(f'http://{IP}/api/streams/{stream_id}/{cmd}')


def set_vol_f(zone_id, vol_f):
    print(urequests.patch(f'http://{IP}/api/zones/{zone_id}', json={"vol_f": vol_f}).text)


def get_image(zone_id, height):
    source_id = get_zone_json(zone_id)["source_id"]
    return urequests.get(f'http://{IP}/api/sources/{source_id}/image/{height}')


def get_stream_id_from_zone(zone_id):
    zone = get_zone_json(zone_id)
    source = get_source_json(zone["source_id"])
    source_input = source["input"]

    if source_input.startswith("local"):
        return None

    return int(source["input"].split("=")[1])
