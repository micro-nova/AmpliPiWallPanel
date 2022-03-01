import urequests
import json
from machine import Pin, UART
import network

# debugUart = UART(0, baudrate=115200, tx=1, rx=3)
tftUart = UART(2, baudrate=115200, tx=16, rx=17)
tftReset = Pin(4, Pin.OUT)

#constants for temporarily hardcoded stuff
IP = "192.168.0.195"
ZONE_ID = 4
WIFI_SSID = "home_2G"
WIFI_PASSWD = "***REMOVED***"

#constants for ui
PLAY_BUTTON_ID = 1
NEXT_BUTTON_ID = 2
PREV_BUTTON_ID = 3
SONG_NAME_VAR = "gname"
ARTIST_NAME_VAR = "gartist"

def get_zone(zid):
    response = json.loads(urequests.get(f'http://{IP}/api/zones/{zid}').text)
    print(response)
    return response


def get_source(sid):
    response = json.loads(urequests.get(f'http://{IP}/api/sources/{sid}').text)
    print(response)
    return response


def command_stream(sid, cmd):
    response = json.loads(urequests.post(f'http://{IP}/api/streams/{sid}/{cmd}').text)
    print(response)


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
    print("playing")


def on_pause():
    command_stream(stream_id, "pause")
    

def on_next():
    command_stream(stream_id, "next")


def on_prev():
    command_stream(stream_id, "prev")


def get_stream_id_from_zone(zid):
    zone = get_zone(zid)
    source = get_source(zone["source_id"])
    source_input = source["input"]
    
    if source_input.startswith("local"):
        return None
    
    return int(source["input"].split("=")[1])


# initial startup stuff
print('resetting screen...')
tftReset.value(0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(WIFI_SSID, WIFI_PASSWD)
    while not wlan.isconnected():
        pass
    
    print('connected!')

# currently not doing any polling from amplipi at all
stream_id = get_stream_id_from_zone(ZONE_ID)

print(f"stream id is: {stream_id}")

is_playing = True

send_artist("test artist")
send_title("test title")

message = b''
while True:
    if tftUart.any():
        message += tftUart.read()
        print("read stuff in!")

        if message[-3:] == bytes([0xff, 0xff, 0xff]):
            print(f"message recieved!\n{message}")

            if message[0] == 0x65 and message[3] == 0x00:
                id = message[2]

                print("valid message")

                if id == PLAY_BUTTON_ID:
                    if is_playing:
                        on_pause()
                    else:
                        on_play()

                    is_playing = not is_playing

                if id == NEXT_BUTTON_ID:
                    on_next()

                if id == PREV_BUTTON_ID:               
                    on_prev()

            message = b''