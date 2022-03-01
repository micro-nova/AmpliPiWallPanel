# note: track and song are the same thing
from API import get_source, get_zone
from DisplaySerial import send_title, send_artist

trackName = ""
artistName = ""
isPlaying = False


def poll(zid):
    zone = get_zone(zid)
    # print(f'zone: {zone}')
    source = get_source(zone["source_id"])
    poll_track(source)
    poll_artist(source)
    poll_playing(source)


def poll_track(source):
    global trackName
    new_track_name = source["info"]["track"]
    if new_track_name != trackName:
        trackName = new_track_name
        send_title(trackName)


def poll_artist(source):
    global artistName
    new_artist_name = source["info"]["artist"]
    if new_artist_name != artistName:
        artistName = new_artist_name
        send_artist(artistName)


def poll_playing(source):
    global isPlaying
    new_is_playing = source["info"]["state"] == "playing"
    if new_is_playing != isPlaying:
        isPlaying = new_is_playing
