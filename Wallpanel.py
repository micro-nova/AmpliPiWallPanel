from curses import baudrate
import urequests
import json
from machine import Pin, UART

# debugUart = UART(0, baudrate=115200, tx=1, rx=3)
tftUart = UART(2, baudrate=115200, tx=17, rx=16)
tftReset = Pin(4, Pin.OUT)

#constants for temporarily hardcoded stuff
IP = "192.168.0.195"
ZONE_ID = 1

#constants for ui
PLAY_BUTTON_ID = 1
NEXT_BUTTON_ID = 2
PREV_BUTTON_ID = 3
SONG_NAME_VAR = "gname"
ARTIST_NAME_VAR = "gartist"

stream_id = None

is_playing = False

def get_zone(zid):
    response = json.loads(urequests.get(f'{IP}/api/zones/{zid}'))
    return response


def get_stream(sid):
    response = json.loads(urequests.get(f'{IP}/api/streams/{sid}'))
    return response


def command_stream(sid, cmd):
    urequests.get(f'{IP}/api/{sid}/{cmd}')


def send_title(title):
    # check if string is too long and trim if it is
    if len(title) > 60:
        title = title[0:59]
    tftUart.write(f'{SONG_NAME_VAR}.txt="{title}"')


def send_artist(artist):
    # check if string is too long and trim if it is
    if len(artist) > 60:
        artist = artist[0:59]
    tftUart.write(f'{ARTIST_NAME_VAR}.txt="{artist}"')


def on_play():
    command_stream(stream_id, "play")


def on_pause():
    command_stream(stream_id, "pause")
    

def on_next():
    command_stream(stream_id, "next")


def on_prev():
    command_stream(stream_id, "prev")

def 

message = ''
while True:
    if tftUart.any():
        message += tftUart.read()

        if message[-3:] == chr(0xff)*3:
            print("message recieved!")

            if message[0] == chr(0x65):


            message == ''