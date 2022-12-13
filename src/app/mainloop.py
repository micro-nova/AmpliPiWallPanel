

MAIN_PAGE_ID = 0
CONFIG_PAGE_ID = 2
SSID_PAGE_ID = 3
STREAM_PAGE_ID = 5
ZONE_PAGE_ID = 6
VERSION_PAGE_ID = 7
CONNECTION_PAGE_ID = 8
VERSIONINFO_PAGE_ID = 9
UPDATE_PAGE_ID = 10
SOURCE_PAGE_ID = 11
DEBUG_PAGE_ID = 12
GINVALID_PAGE_ID = 13
ADVANCED_CONFIG_PAGE_ID = 15
MQTT_PAGE_ID = 16
BRIGHTNESS_PAGE_ID = 17
PRESETS_PAGE_ID = 19

REBOOT_BUTTON_ID = 3

def run():
    # putting imports here to curb memory usage
    import machine

    from app import displayserial
    from app.displayserial import BUTTON_MESSAGE, PRESSED_EVENT

    try:
        run_h()
    except Exception as e:
        displayserial.change_page('debugpage')
        displayserial.set_component_txt('debugpage', 'tmessage', str(e))
        print(e)
        message = b''
        # raise e # temp
        while True:
            if displayserial.uart_any():
                message_part = displayserial.uart_read()
                byte_list = [message_part[i:i + 1] for i in range(len(message_part))]
                for i in byte_list:
                    message += i
                    if message[-3:] == bytes([0xff, 0xff, 0xff]):
                        message = message[0:-3]
                        if len(message) > 1:
                            if message[1] == DEBUG_PAGE_ID:
                                if message[0] == BUTTON_MESSAGE and message[3] == PRESSED_EVENT:
                                    if message[2] == REBOOT_BUTTON_ID:
                                        displayserial.change_page(displayserial.BOOT_PAGE_NAME)
                                        machine.reset()

def run_h():
    # putting imports here to curb memory usage
    import gc

    from machine import Pin

    from app import api, wifi, displayserial, dt, relay
    from app.audioconfig import AudioConfig
    from app.ota.check_for_updates import check_for_updates
    from app.pages import config, connection, home, ssid, stream, version, versioninfo, zone, source, ginvalid, advanced
    from app.polling import poll
    # pages
    from app import mqttconfig
    from app.pages import mqtt
    from app.pages import brightness
    from app.displayserial import message_is_sleep, message_is_wake
    from app.pages import presets
    tft_reset = Pin(4, Pin.OUT)
    print('enabling screen...')
    tft_reset.value(0)

    # polling constants
    POLLING_INTERVAL_SECONDS = 1
    CHECK_UPDATE_INTERVAL_SECONDS = 60 * 60 * 24  # checks every 24 hours
    RELAY_FILE_UPDATE_SECONDS = 30

    # initial startup stuff
    print('loading relay state...')
    relay.setup()

    connection.load_connection_page()
    audioconf = AudioConfig()
    wifi.try_connect()
    connection.update_connection_status()

    initialized = False

    # make sure display is on the home page
    displayserial.change_page(displayserial.HOME_PAGE_NAME)

    # initialize timeout, brightness
    brightness.init()

    curr_t = dt.time_sec()
    last_poll_time = curr_t - POLLING_INTERVAL_SECONDS
    last_check_update_time = curr_t - CHECK_UPDATE_INTERVAL_SECONDS
    last_relay_file_update_time = curr_t - RELAY_FILE_UPDATE_SECONDS
    message = b''
    while True:
        # handle api call queue
        api.update()

        # update brightness
        brightness.update()

        # poll info from amplipi api
        curr_time = dt.time_sec()

        if curr_time - last_relay_file_update_time > RELAY_FILE_UPDATE_SECONDS:
            last_relay_file_update_time = curr_time
            # handle relay file saving
            relay.update()

        if curr_time - last_check_update_time > CHECK_UPDATE_INTERVAL_SECONDS:
            last_check_update_time = curr_time
            check_for_updates()

        if curr_time - last_poll_time > POLLING_INTERVAL_SECONDS:
            last_poll_time = curr_time
            mqttconfig.update()
            gc.collect()
            try:
                if wifi.is_connected():
                    if not initialized:
                        # init audioconf
                        if audioconf.load_settings():
                            initialized = True
                            mqttconfig.start()
                    if audioconf.zone_id >= 0:
                        api.queue_call(poll)
                    else:
                        print("didn't poll because zone is not configured")
            except OSError as e:
                if not wifi.is_connected():
                    print("wifi disconnected.")
                print(f"polling failed with error: {e}.")

        # poll serial messages from display
        if displayserial.uart_any():
            # read stuff in
            message_part = displayserial.uart_read()
            byte_list = [message_part[i:i + 1] for i in range(len(message_part))]
            for i in byte_list:
                message += i

                # if message is terminated (valid message)
                if message[-3:] == bytes([0xff, 0xff, 0xff]):
                    # remove termination
                    message = message[0:-3]
                    brightness.reset_touch_timer()
                    if len(message) > 1:
                        if message_is_sleep(message):
                            print('screen is sleeping')
                        elif message_is_wake(message):
                            print('screen is awake')
                        elif message[1] == MAIN_PAGE_ID:
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
                        elif message[1] == SOURCE_PAGE_ID:
                            source.handle_msg(message)
                        elif message[1] == GINVALID_PAGE_ID:
                            ginvalid.handle_msg(message)
                        elif message[1] == ADVANCED_CONFIG_PAGE_ID:
                            advanced.handle_msg(message)
                        elif message[1] == MQTT_PAGE_ID:
                            mqtt.handle_msg(message)
                        elif message[1] == BRIGHTNESS_PAGE_ID:
                            brightness.handle_msg(message)
                        elif message[1] == PRESETS_PAGE_ID:
                            presets.handle_msg(message)

                    #  clear message
                    message = b''
