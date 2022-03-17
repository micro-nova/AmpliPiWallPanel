# note: track and song are the same thing
from API import get_source_json, get_zone_json
from DisplaySerial import send_title, send_artist, update_play_pause_button, send_album, update_mute_button

track_name = ""
album_name = ""
artist_name = ""
is_playing = False
is_muted = False


def poll(zid):
    zone = get_zone_json(zid)
    source = get_source_json(zone["source_id"])
    poll_muted(zone)
    poll_track(source)
    poll_album(source)
    poll_artist(source)
    poll_playing(source)


def poll_muted(zone):
    global is_muted
    new_is_muted = zone["mute"]
    if new_is_muted != is_muted:
        is_muted = new_is_muted
        update_mute_button(is_muted)


def poll_track(source):
    global track_name
    new_track_name = source["info"]["track"]
    if new_track_name != track_name:
        track_name = new_track_name
        send_title(track_name)


def poll_album(source):
    global album_name
    new_album_name = source["info"]["album"]
    if new_album_name != album_name:
        album_name = new_album_name
        send_album(album_name)


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


def set_is_playing(is_p):
    global is_playing
    is_playing = is_p
    update_play_pause_button(is_playing)


def get_muted():
    return is_muted


def set_muted(muted):
    global is_muted
    is_muted = muted
    update_mute_button(is_muted)


def get_source(zid):
    zone = get_zone_json(zid)
    return get_source_json(zone["source_id"])

