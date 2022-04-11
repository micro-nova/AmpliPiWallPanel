from machine import Pin

import api
import displayserial
import wifi
import dt
from audioconfig import AudioConfig
from pages.config import handle_config_page_msg
from pages.connection import update_connection_status, load_connection_page, handle_connection_page_msg
from pages.home import handle_main_page_msg
from pages.ssid import handle_ssid_page_msg
from pages.stream import handle_stream_page_msg
from pages.zone import handle_zone_page_msg
from polling import poll

# TODO: replace from x import y with just import x for pages. do this everywhere, not just main

tft_reset = Pin(4, Pin.OUT)


# pages
MAIN_PAGE_ID = 0
CONFIG_PAGE_ID = 2
SSID_PAGE_ID = 3
STREAM_PAGE_ID = 5
ZONE_PAGE_ID = 6
CONNECTION_PAGE_ID = 8

# polling constants
POLLING_INTERVAL_SECONDS = 1


# initial startup stuff
print('resetting screen...')
tft_reset.value(0)

load_connection_page()
audioconf = AudioConfig()
wifi.try_connect()
update_connection_status()

initialized = False

last_poll_time = dt.time_sec() - POLLING_INTERVAL_SECONDS


message = b''
while True:
    # handle api call queue
    api.update()
    # poll info from amplipi api
    curr_time = dt.time_sec()
    if curr_time - last_poll_time > POLLING_INTERVAL_SECONDS:
        last_poll_time = dt.time_sec()
        try:
            if wifi.is_connected():
                if not initialized:
                    initialized = True
                    # init audioconf
                    audioconf.load_settings()
                if audioconf.zone_id >= 0:
                    api.queue_call(poll)
                    # poll()
                    print("queued poll from amplipi")
                else:
                    print("didn't poll because zone is not configured")
        except OSError as e:
            if not wifi.is_connected():
                print("wifi disconnected.")
            print("polling failed somehow.")
            print(e)

    # poll serial messages from display
    if displayserial.uart_any():
        # read stuff in
        message_part = displayserial.uart_read()
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
                    # TODO: adopt input multiplexer idea for pages. put these into a list and use oop in python somehow
                    #  to call handle_ methods.
                    if message[1] == MAIN_PAGE_ID:
                        handle_main_page_msg(message)
                    elif message[1] == CONFIG_PAGE_ID:
                        handle_config_page_msg(message)
                    elif message[1] == SSID_PAGE_ID:
                        handle_ssid_page_msg(message)
                    elif message[1] == STREAM_PAGE_ID:
                        handle_stream_page_msg(message)
                    elif message[1] == ZONE_PAGE_ID:
                        handle_zone_page_msg(message)
                    elif message[1] == CONNECTION_PAGE_ID:
                        handle_connection_page_msg(message)

                # clear message only if it was properly terminated
                message = b''
