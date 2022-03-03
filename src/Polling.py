# note: track and song are the same thing
from API import get_source_json, get_zone_json
from DisplaySerial import send_title, send_artist, update_play_pause_button

track_name = ""
artist_name = ""
is_playing = False


def poll(zid):
    zone = get_zone_json(zid)
    # print(f'zone: {zone}')
    source = get_source_json(zone["source_id"])
    poll_track(source)
    poll_artist(source)
    poll_playing(source)


def poll_track(source):
    global track_name
    new_track_name = source["info"]["track"]
    if new_track_name != track_name:
        track_name = new_track_name
        send_title(track_name)


def poll_artist(source):
    global artist_name
    new_artist_name = source["info"]["artist"]
    if new_artist_name != artist_name:
        artist_name = new_artist_name
        send_artist(artist_name)


def poll_playing(source):
    global is_playing
    new_is_playing = source["info"]["state"] == "playing"
    if new_is_playing != is_playing:
        is_playing = new_is_playing
        update_play_pause_button(is_playing)


def get_is_playing():
    return is_playing


def get_source(zid):
    zone = get_zone_json(zid)
    return get_source_json(zone["source_id"])

