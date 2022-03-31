import time

from machine import Pin

import displayserial
import wifi
from audioconfig import AudioConfig
from pages.configpage import handle_config_page_msg, load_config_page, update_config_status
from pages.mainpage import handle_main_page_msg
from pages.ssidpage import handle_ssid_page_msg
from pages.streampage import handle_stream_page_msg
from pages.zonepage import handle_zone_page_msg
from polling import poll

tft_reset = Pin(4, Pin.OUT)


# pages
MAIN_PAGE_ID = 0
CONFIG_PAGE_ID = 2
SSID_PAGE_ID = 3
STREAM_PAGE_ID = 5
ZONE_PAGE_ID = 6

# polling constants
POLLING_INTERVAL_SECONDS = 1


# initial startup stuff
print('resetting screen...')
tft_reset.value(0)

load_config_page()
audioconf = AudioConfig()
wifi.try_connect()
update_config_status()

initialized = False

last_poll_time = time.time() - POLLING_INTERVAL_SECONDS


message = b''
while True:
    # poll info from amplipi api
    curr_time = time.time()
    if curr_time - last_poll_time > POLLING_INTERVAL_SECONDS:
        last_poll_time = time.time()
        try:
            if wifi.is_connected():
                if not initialized:
                    initialized = True
                    # init audioconf
                    audioconf.load_settings()
                if audioconf.zone_id >= 0:
                    poll()
                    print("polled from amplipi")
                else:
                    print("didn't poll because zone is not configured")
        except OSError:
            if not wifi.is_connected():
                print("wifi disconnected.")
            print("polling failed somehow.")

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

                # clear message only if it was properly terminated
                message = b''
