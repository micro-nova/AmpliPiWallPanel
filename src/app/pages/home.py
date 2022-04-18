from app import api, polling
from app.audioconfig import AudioConfig
from app.displayserial import BUTTON_MESSAGE, SLIDER_MESSAGE, get_vol_slider_vol_f
from app.pages import stream, zone
from app.polling import get_is_playing, set_is_playing, get_muted, set_muted

# component ids
PLAY_BUTTON_ID = 1
NEXT_BUTTON_ID = 2
PREV_BUTTON_ID = 3
MUTE_BUTTON_ID = 13
VOL_SLIDER_ID = 6
STREAM_BUTTON_ID = 11
ZONE_BUTTON_ID = 12

_audioconf = AudioConfig()

def _on_source():
    stream.load_stream_page()

def _on_zone():
    zone.load_zone_page()

def _on_play(stream_id):
    polling.skip_next_playing()

    def call():
        api.send_stream_command(stream_id, "play")
        polling.skip_next_playing()
        print("playing")

    # if successfully queued call, change display's playing state
    if api.queue_call(call):
        set_is_playing(True)

def _on_pause(stream_id):
    polling.skip_next_playing()

    def call():
        api.send_stream_command(stream_id, "pause")
        polling.skip_next_playing()
        print("pausing")

    # if successfully queued call, change display's playing state
    if api.queue_call(call):
        set_is_playing(False)

def _on_mute(zone_id):
    polling.skip_next_mute()

    def call():
        api.set_mute(zone_id, True)
        polling.skip_next_mute()
        print("muting...")

    # if successfully queued call, change display's mute state
    if api.queue_call(call):
        # update mute button graphic
        set_muted(True)

def _on_unmute(zone_id):
    polling.skip_next_mute()

    def call():
        # set muted state using amplipi API
        api.set_mute(zone_id, False)
        polling.skip_next_mute()
        print("unmuting...")

    # if successfully queued call, change display's mute state
    if api.queue_call(call):
        # update mute button graphic
        set_muted(False)

def _on_next(stream_id):
    try:
        api.send_stream_command(stream_id, "next")
    except OSError:
        print("next button failed.")

def _on_prev(stream_id):
    try:
        api.send_stream_command(stream_id, "prev")
    except OSError:
        print("prev button failed.")

def _on_vol(message):
    vol_f = get_vol_slider_vol_f(message)
    polling.skip_next_vol_f()
    polling.skip_next_mute()

    # define the call to be queued
    # using function def instead of lambda so that multiple statements can be used

    def unmute_call():
        polling.skip_next_vol_f()
        polling.skip_next_mute()
        api.set_vol_f_mute(_audioconf.zone_id, vol_f, False)

    def call():
        polling.skip_next_vol_f()
        polling.skip_next_mute()
        api.set_vol_f(_audioconf.zone_id, vol_f)

    if get_muted():
        if api.queue_call(unmute_call):
            set_muted(False)
    else:
        api.queue_call(call, droppable=True)

def handle_main_page_msg(message):
    """Receives a message from the main page (from the display) and processes it."""
    print("handling main page message")
    if message[0] == SLIDER_MESSAGE:
        # valid slider update
        id = message[2]
        if id == VOL_SLIDER_ID:
            # TODO: technically should check if the id is correct, but its not
            #  needed right now because there is only one slider on the home page
            _on_vol(message)

    # if message is button and button is pressed
    elif message[0] == BUTTON_MESSAGE and message[3] == 0x01:
        # valid press event
        id = message[2]

        if id == PLAY_BUTTON_ID:
            try:
                if get_is_playing():
                    _on_pause(_audioconf.stream_id)
                else:
                    _on_play(_audioconf.stream_id)
                # poll_playing(get_source(zone_id))
            except OSError as e:
                print("play/pause button event failed due to internet probably. error:")
                print(e)

        elif id == NEXT_BUTTON_ID:
            _on_next(_audioconf.stream_id)

        elif id == PREV_BUTTON_ID:
            _on_prev(_audioconf.stream_id)

        elif id == STREAM_BUTTON_ID:
            _on_source()

        elif id == ZONE_BUTTON_ID:
            _on_zone()

        elif id == MUTE_BUTTON_ID:
            try:
                if get_muted():
                    _on_unmute(_audioconf.zone_id)
                else:
                    _on_mute(_audioconf.zone_id)
            except OSError:
                print("mute/unmute button event failed due to internet probably")