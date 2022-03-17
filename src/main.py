import time

from machine import Pin

import DisplaySerial
import Wifi
from API import get_stream_id_from_zone, get_vol_f
from Polling import poll
from pages.ConfigPage import handle_config_page_msg, load_config_page, update_config_status
from pages.MainPage import handle_main_page_msg
from pages.SsidPage import handle_ssid_page_msg

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


# initial startup stuff
print('resetting screen...')
tft_reset.value(0)

load_config_page()
Wifi.try_connect()
update_config_status()

initialized = False
stream_id = -1

last_poll_time = time.time() - POLLING_INTERVAL_SECONDS


message = b''
while True:
    # poll info from amplipi api
    curr_time = time.time()
    if curr_time - last_poll_time > POLLING_INTERVAL_SECONDS:
        last_poll_time = time.time()
        try:
            if Wifi.is_connected():
                if not initialized:
                    initialized = True
                    # get stream id from the current zone
                    stream_id = get_stream_id_from_zone(ZONE_ID)
                    # init gui volume slider
                    # DisplaySerial.set_vol_slider_vol_f(get_vol_f(ZONE_ID))
                    print(f"stream id is: {stream_id}")
                poll(ZONE_ID)
                print("polled from amplipi")
        except OSError:
            if not Wifi.is_connected():
                print("Wifi disconnected.")
            print("polling failed somehow.")

    # poll serial messages from display
    if DisplaySerial.uart_any():
        # read stuff in
        message_part = DisplaySerial.uart_read()
        byte_list = [message_part[i:i+1] for i in range(len(message_part))]
        for i in byte_list:
            message += i

            # if message is terminated (valid message)
            if message[-3:] == bytes([0xff, 0xff, 0xff]):
                # remove termination
                message = message[0:-3]
                if len(message) > 1:
                    # if message is a relay event,
                    print(f'Received message: {message}')
                    # if message[0] == b'#':
                    #
                    #     pass
                    # if message is for the main page
                    if message[1] == MAIN_PAGE_ID:
                        handle_main_page_msg(stream_id, ZONE_ID, message)
                    elif message[1] == CONFIG_PAGE_ID:
                        handle_config_page_msg(message)
                    elif message[1] == SSID_PAGE_ID:
                        handle_ssid_page_msg(message)

                # clear message only if it was properly terminated
                message = b''
