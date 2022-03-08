import time

from machine import Pin

import DisplaySerial
import Wifi
from API import get_stream_id_from_zone, get_vol_f
from Polling import poll
from pages.ConfigPage import handle_config_page_msg, load_config_page, update_config_status
from pages.MainPage import handle_main_page_msg

tft_reset = Pin(4, Pin.OUT)

# constants for temporarily hardcoded stuff
ZONE_ID = 4
# WIFI_SSID = "home_2G"
# WIFI_PASSWD = "***REMOVED***"
# Wifi.save_wifi_info(WIFI_SSID, WIFI_PASSWD)


# pages
MAIN_PAGE_ID = 0
CONFIG_PAGE_ID = 2
SSID_PAGE_ID = 3

# polling constants
POLLING_INTERVAL_SECONDS = 1


def handle_ssid_page_msg(message):
    pass


# initial startup stuff
print('resetting screen...')
tft_reset.value(0)

load_config_page()
while not Wifi.try_connect():
    pass
update_config_status()

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
        try:
            poll(ZONE_ID)
            print("polled from amplipi")
        except OSError:
            if not Wifi.is_connected():
                print("Wifi disconnected.")
            print("polling failed.")

    # poll serial messages from display
    if DisplaySerial.uart_any():
        # read stuff in
        message += DisplaySerial.uart_read()

        # if message is terminated (valid message)
        if message[-3:] == bytes([0xff, 0xff, 0xff]):
            # if message is for the main page
            if message[1] == MAIN_PAGE_ID:
                handle_main_page_msg(stream_id, ZONE_ID, message)
            elif message[1] == CONFIG_PAGE_ID:
                handle_config_page_msg(message)
            elif message[1] == SSID_PAGE_ID:
                handle_ssid_page_msg(message)

            # clear message only if it was properly terminated
            message = b''
