import time

import network
from machine import Pin
import DisplaySerial
from API import command_stream, get_stream_id_from_zone, set_vol_f, get_vol_f
from Polling import poll, get_is_playing, poll_playing, get_source

tft_reset = Pin(4, Pin.OUT)

# constants for temporarily hardcoded stuff
ZONE_ID = 4
WIFI_SSID = "home_2G"
WIFI_PASSWD = "***REMOVED***"

# constants for ui
PLAY_BUTTON_ID = 1
NEXT_BUTTON_ID = 2
PREV_BUTTON_ID = 3
VOL_SLIDER_ID = 6

# pages
MAIN_PAGE_ID = 0
CONFIG_PAGE_ID = 2
SSID_PAGE_ID = 3

# message types
BUTTON_MESSAGE = 0x65
SLIDER_MESSAGE = 0x64

# polling constants
POLLING_INTERVAL_SECONDS = 1


def on_play():
    command_stream(stream_id, "play")
    print("playing")


def on_pause():
    command_stream(stream_id, "pause")


def on_next():
    command_stream(stream_id, "next")


def on_prev():
    command_stream(stream_id, "prev")


def handle_main_page_msg(message):
    print("handling main page message")
    if message[0] == SLIDER_MESSAGE:
        # valid slider update
        id = message[2]
        if id == VOL_SLIDER_ID:
            vol_f = DisplaySerial.get_vol_slider_vol_f(message)
            set_vol_f(ZONE_ID, vol_f)
            print(f'new volume: {vol_f}')
    # if message is button and button is pressed
    elif message[0] == BUTTON_MESSAGE and message[3] == 0x00:
        # valid press/release event
        id = message[2]

        if id == PLAY_BUTTON_ID:
            if get_is_playing():
                on_pause()
            else:
                on_play()
            poll_playing(get_source(ZONE_ID))

        if id == NEXT_BUTTON_ID:
            on_next()

        if id == PREV_BUTTON_ID:
            on_prev()


def handle_config_page_msg(message):
    pass


def handle_ssid_page_msg(message):
    pass


# initial startup stuff
print('resetting screen...')
tft_reset.value(0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(WIFI_SSID, WIFI_PASSWD)
    while not wlan.isconnected():
        pass

    print('connected!')

stream_id = get_stream_id_from_zone(ZONE_ID)

print(f"stream id is: {stream_id}")

last_poll_time = time.time() - POLLING_INTERVAL_SECONDS

# init gui volume slider
DisplaySerial.set_vol_slider_vol_f(get_vol_f(ZONE_ID))

message = b''
while True:
    # poll info from amplipi api
    curr_time = time.time()
    if curr_time - last_poll_time > POLLING_INTERVAL_SECONDS:
        last_poll_time = time.time()
        poll(ZONE_ID)
        print("polled from amplipi")

    # poll serial messages from display
    if DisplaySerial.uart_any():
        # read stuff in
        message += DisplaySerial.uart_read()

        # if message is terminated (valid message)
        if message[-3:] == bytes([0xff, 0xff, 0xff]):
            # if message is for the main page
            if message[1] == MAIN_PAGE_ID:
                handle_main_page_msg(message)
            elif message[1] == CONFIG_PAGE_ID:
                handle_config_page_msg(message)
            elif message[1] == SSID_PAGE_ID:
                handle_ssid_page_msg(message)

            # clear message only if it was properly terminated
            message = b''
