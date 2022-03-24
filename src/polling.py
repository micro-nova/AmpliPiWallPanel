# note: track and song are the same thing
from api import get_source_dict, get_zone_dict, get_vol_f
from displayserial import send_title, send_artist, update_play_pause_button, send_album, update_mute_button, \
    set_vol_slider_vol_f

track_name = ""
album_name = ""
artist_name = ""
is_playing = False
is_muted = False
vol_f = 0.0


def poll(zid):
    zone = get_zone_dict(zid)
    source = get_source_dict(zone["source_id"])
    poll_vol_f(zone)
    poll_muted(zone)
    poll_track(source)
    poll_album(source)
    poll_artist(source)
    poll_playing(source)


def poll_vol_f(zone):
    global vol_f
    new_vol_f = zone["vol_f"]
    if new_vol_f != vol_f:
        vol_f = new_vol_f
        set_vol_slider_vol_f(vol_f)


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
    zone = get_zone_dict(zid)
    return get_source_dict(zone["source_id"])

