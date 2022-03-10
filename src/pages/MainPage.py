# message types
# import DisplaySerial
from DisplaySerial import BUTTON_MESSAGE, SLIDER_MESSAGE, get_vol_slider_vol_f
from API import command_stream, set_vol_f
from Polling import get_is_playing, poll_playing, get_source, set_is_playing

# component ids
PLAY_BUTTON_ID = 1
NEXT_BUTTON_ID = 2
PREV_BUTTON_ID = 3
VOL_SLIDER_ID = 6


def _on_play(stream_id):
    command_stream(stream_id, "play")
    set_is_playing(True)
    print("playing")


def _on_pause(stream_id):
    command_stream(stream_id, "pause")
    set_is_playing(False)
    print("pausing")


def _on_next(stream_id):
    try:
        command_stream(stream_id, "next")
    except OSError:
        print("next button failed.")


def _on_prev(stream_id):
    try:
        command_stream(stream_id, "prev")
    except OSError:
        print("prev button failed.")


def handle_main_page_msg(stream_id, zone_id, message):
    print("handling main page message")
    if message[0] == SLIDER_MESSAGE:
        # valid slider update
        id = message[2]
        if id == VOL_SLIDER_ID:
            vol_f = get_vol_slider_vol_f(message)
            try:
                set_vol_f(zone_id, vol_f)
                print(f'new volume: {vol_f}')
            except OSError:
                print("set volume failed.")

    # if message is button and button is pressed
    elif message[0] == BUTTON_MESSAGE and message[3] == 0x01:
        # valid press/release event
        id = message[2]

        if id == PLAY_BUTTON_ID:
            try:
                if get_is_playing():
                    _on_pause(stream_id)
                else:
                    _on_play(stream_id)
                # poll_playing(get_source(zone_id))
            except OSError:
                print("play/pause button event failed.")

        if id == NEXT_BUTTON_ID:
            _on_next(stream_id)

        if id == PREV_BUTTON_ID:
            _on_prev(stream_id)
