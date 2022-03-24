import time
import urequests
import json

import wifi

IP = "192.168.0.195"


def get_source_dict(source_id):
    response = json.loads(urequests.get(f'http://{IP}/api/sources/{source_id}').text)
    return response


def get_sources_dict():
    response = json.loads(urequests.get(f'http://{IP}/api/sources').text)
    return response


def get_zone_dict(zone_id):
    response = json.loads(urequests.get(f'http://{IP}/api/zones/{zone_id}').text)
    return response


def command_stream(stream_id, cmd):
    if wifi.is_connected():
        urequests.post(f'http://{IP}/api/streams/{stream_id}/{cmd}')
        time.sleep_ms(10)


def set_vol_f(zone_id, vol_f):
    if wifi.is_connected():
        urequests.patch(f'http://{IP}/api/zones/{zone_id}', json={"vol_f": vol_f})
        time.sleep_ms(10)


def set_mute(zone_id, muted):
    if wifi.is_connected():
        output_json = {"mute": muted}
        print(output_json)
        print(json.dumps(output_json))
        response = urequests.patch(f'http://{IP}/api/zones/{zone_id}', json=output_json)
        print(response.status_code)
        print(response.json())
        time.sleep_ms(10)


def get_vol_f(zone_id):
    zone_response = get_zone_dict(zone_id)
    return zone_response["vol_f"]


def get_image(zone_id, height):
    source_id = get_zone_dict(zone_id)["source_id"]
    return urequests.get(f'http://{IP}/api/sources/{source_id}/image/{height}')


def get_stream_id_from_zone(zone_id):
    zone = get_zone_dict(zone_id)
    source = get_source_dict(zone["source_id"])
    source_input = source["input"]

    if source_input.startswith("local"):
        return None

    return int(source["input"].split("=")[1])



