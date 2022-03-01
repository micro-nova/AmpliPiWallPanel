import urequests
import json
from Wallpanel import send_title, send_artist

# note: track and song are the same thing
trackName = ""
artistName = ""
isPlaying = False


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
    new_is_playing = source["state"] == "playing"
    if new_is_playing != isPlaying:
        isPlaying = new_is_playing



def poll_playing_state():
    pass
