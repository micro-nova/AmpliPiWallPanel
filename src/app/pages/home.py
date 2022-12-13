from app import api, polling
from app.audioconfig import AudioConfig
from app.displayserial import get_vol_slider_vol_f, message_is_slider_event, message_id, \
    message_is_button_event, button_is_pressed
from app.pages import stream, source, config, presets
from app.polling import get_is_playing, set_is_playing, get_muted, set_muted

# component ids
PLAY_BUTTON_ID = 1
NEXT_BUTTON_ID = 2
PREV_BUTTON_ID = 3
MUTE_BUTTON_ID = 13
VOL_SLIDER_ID = 6
STREAM_BUTTON_ID = 11
SOURCE_BUTTON_ID = 12
PRESET_BUTTON_ID = 17

CONFIG_BUTTON_ID = 7
CONFIG_BUTTON_OBJNAME = 'bconfig'

_audioconf = AudioConfig()

def _on_stream():
    stream.load_stream_page()

def _on_source():
    source.load_source_page()

def _on_play(stream_id):
    polling.skip_next_playing()

    def play():
        api.send_stream_command(stream_id, "play")
        polling.skip_next_playing()
        print("playing")

    if 'play' in _audioconf.supported_cmds:
        # if successfully queued call, change display's playing state
        if api.queue_call(play):
            set_is_playing(True)

def _on_pause(stream_id):
    polling.skip_next_playing()

    def pause():
        api.send_stream_command(stream_id, "pause")
        polling.skip_next_playing()
        print("pausing")

    def stop():
        api.send_stream_command(stream_id, "stop")
        polling.skip_next_playing()
        print("stopping")

    if 'pause' in _audioconf.supported_cmds:
        # if successfully queued call, change display's playing state
        if api.queue_call(pause):
            set_is_playing(False)
    elif 'stop' in _audioconf.supported_cmds:
        # if successfully queued call, change display's playing state
        if api.queue_call(stop):
            set_is_playing(False)


def _on_mute():
    polling.skip_next_mute()

    def call():
        if _audioconf.using_group:
            api.set_mute(_audioconf.group_id, True, using_group=_audioconf.using_group)
        else:
            api.set_mute(_audioconf.zone_id, True, using_group=_audioconf.using_group)
        polling.skip_next_mute()
        print("muting...")

    # if successfully queued call, change display's mute state
    if api.queue_call(call):
        # update mute button graphic
        set_muted(True)

def _on_unmute():
    polling.skip_next_mute()

    def call():
        # set muted state using amplipi API
        if _audioconf.using_group:
            api.set_mute(_audioconf.group_id, False, using_group=_audioconf.using_group)
        else:
            api.set_mute(_audioconf.zone_id, False, using_group=_audioconf.using_group)
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
    id = _audioconf.group_id if _audioconf.using_group else _audioconf.zone_id

    # define the calls to be queued
    def unmute_call():
        polling.skip_next_vol_f()
        polling.skip_next_mute()
        api.set_vol_f_mute(id, vol_f, False, using_group=_audioconf.using_group)

    def call():
        polling.skip_next_vol_f()
        polling.skip_next_mute()
        api.set_vol_f(id, vol_f, using_group=_audioconf.using_group)

    if get_muted():
        if api.queue_call(unmute_call):
            set_muted(False)
    else:
        api.queue_call(call, droppable=True)

def handle_msg(message):
    """Receives a message from the main page (from the display) and processes it."""
    print("handling main page message")
    id = message_id(message)
    if message_is_slider_event(message):
        # valid slider update
        if id == VOL_SLIDER_ID:
            _on_vol(message)
    elif message_is_button_event(message) and button_is_pressed(message):
        # valid press event
        if id == PLAY_BUTTON_ID:
            if get_is_playing():
                _on_pause(_audioconf.stream_id)
            else:
                _on_play(_audioconf.stream_id)
        elif id == NEXT_BUTTON_ID:
            _on_next(_audioconf.stream_id)
        elif id == PREV_BUTTON_ID:
            _on_prev(_audioconf.stream_id)
        elif id == STREAM_BUTTON_ID:
            _on_stream()
        elif id == SOURCE_BUTTON_ID:
            _on_source()
        elif id == MUTE_BUTTON_ID:
            if get_muted():
                _on_unmute()
            else:
                _on_mute()
        elif id == CONFIG_BUTTON_ID:
            config.load_config_page()
        elif id == PRESET_BUTTON_ID:
            presets.load_preset_page()

