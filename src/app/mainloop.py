from machine import Pin

from app import api, wifi, displayserial, dt
from app.audioconfig import AudioConfig
from app.pages import config, connection, home, ssid, stream, version, versioninfo, zone
from app.polling import poll

def run():
    tft_reset = Pin(4, Pin.OUT)

    # pages
    MAIN_PAGE_ID = 0
    CONFIG_PAGE_ID = 2
    SSID_PAGE_ID = 3
    STREAM_PAGE_ID = 5
    ZONE_PAGE_ID = 6
    VERSION_PAGE_ID = 7
    CONNECTION_PAGE_ID = 8
    VERSIONINFO_PAGE_ID = 9

    # polling constants
    POLLING_INTERVAL_SECONDS = 1


    # initial startup stuff
    print('resetting screen...')
    tft_reset.value(0)

    connection.load_connection_page()
    audioconf = AudioConfig()
    wifi.try_connect()
    connection.update_connection_status()

    initialized = False

    # make sure display is on the home page
    displayserial.change_page(displayserial.HOME_PAGE_NAME)

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
                        # print(f'Received message: {message}')
                        # if message is for the main page
                        # TODO: adopt input multiplexer idea for pages. put these into a list and use oop in python somehow
                        #  to call handle_ methods.
                        if message[1] == MAIN_PAGE_ID:
                            home.handle_msg(message)
                        elif message[1] == CONFIG_PAGE_ID:
                            config.handle_msg(message)
                        elif message[1] == SSID_PAGE_ID:
                            ssid.handle_msg(message)
                        elif message[1] == STREAM_PAGE_ID:
                            stream.handle_msg(message)
                        elif message[1] == ZONE_PAGE_ID:
                            zone.handle_msg(message)
                        elif message[1] == VERSION_PAGE_ID:
                            version.handle_msg(message)
                        elif message[1] == CONNECTION_PAGE_ID:
                            connection.handle_msg(message)
                        elif message[1] == VERSIONINFO_PAGE_ID:
                            versioninfo.handle_msg(message)

                    # clear message only if it was properly terminated
                    message = b''
