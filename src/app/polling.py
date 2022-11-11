# note: track and song are the same thing

from app import api, displayserial
from app import dt
from app.api import get_source, get_zone, get_group
from app.audioconfig import AudioConfig
from app.displayserial import send_title, send_artist, send_album, update_mute_button, \
    set_vol_slider_vol_f, send_stream_name, send_zone_or_group_name, send_source_name, HOME_PAGE_NAME, send_stream_type, \
    set_play_pause_button_state

track_name = " "
album_name = " "
artist_name = " "
stream_name = " "
stream_type = 'rca'
is_playing = None
is_muted = None
vol_f = 0.0


_skip_next_vol_f = False
_skip_next_playing = False
_skip_next_mute = False

_awaiting_user_input=False


_audioconf = AudioConfig()


def invalid_group_handled():
    global _awaiting_user_input
    _awaiting_user_input = False

def poll():
    global _skip_next_vol_f
    global _skip_next_playing
    global _skip_next_mute
    global _awaiting_user_input

    # poll_start_time = dt.time_sec()
    zone = None
    group = None
    if _audioconf.using_group:
        group = get_group(_audioconf.group_id)
    else:
        zone = get_zone(_audioconf.zone_id)
    source_id = None
    source = None
    stream = None
    if zone is not None:
        source_id = zone['source_id']
        source = get_source(source_id)
        _audioconf.stream_id = api.get_stream_id_from_source_dict(source)
        stream = api.get_stream(_audioconf.stream_id)
        if not _skip_next_vol_f:
            poll_vol_f(zone)
        else:
            _skip_next_vol_f = False
        if not _skip_next_mute:
            poll_muted(zone)
        else:
            _skip_next_mute = False
        if not _skip_next_playing:
            poll_playing(source)
        else:
            _skip_next_playing = False
        poll_zone_or_group_name(zone)
    elif group is not None:
        try:
            source_id = group['source_id']
            source = get_source(source_id)
            # if success, we are no longer waiting on the user to fix the invalid group
            _awaiting_user_input = False
            print('group valid')
            # print(source_id)
            # print(source)
        except Exception:
            # go to the ginvalid page once if the group is invalid
            print('group invalid')
            if not _awaiting_user_input:
                # the source_id isn't present, so the group is invalid
                displayserial.change_page(displayserial.GROUP_INVALID_PAGE_NAME)
                _awaiting_user_input = True

        if source is not None:
            new_stream_id = api.get_stream_id_from_source_dict(source)
            if new_stream_id is not None:
                _audioconf.stream_id = new_stream_id
                stream = api.get_stream(_audioconf.stream_id)
            else:
                _audioconf.stream_id = -1

        if not _skip_next_vol_f:
            poll_vol_f(group)
        else:
            _skip_next_vol_f = False
        if not _skip_next_mute:
            poll_muted(group)
        else:
            _skip_next_mute = False
        if not _skip_next_playing:
            poll_playing(source)
        else:
            _skip_next_playing = False
        poll_zone_or_group_name(group)
    poll_track(source)
    poll_album(source)
    poll_stream_name(stream)
    poll_source_name(source_id)
    poll_artist(source)

def poll_vol_f(zoneorgroup):
    global vol_f
    new_vol_f = zoneorgroup["vol_f"]
    if new_vol_f != vol_f:
        vol_f = new_vol_f
        set_vol_slider_vol_f(vol_f)


def poll_muted(zoneorgroup):
    global is_muted
    new_is_muted = zoneorgroup["mute"]
    if new_is_muted != is_muted:
        is_muted = new_is_muted
        update_mute_button(is_muted)


def poll_track(source):
    global track_name
    new_track_name = ''
    if source is not None:
        if 'track' in source['info']:
            new_track_name = source['info']['track']

    if new_track_name != track_name:
        track_name = new_track_name
        send_title(track_name)


def poll_album(source):
    global album_name
    # new_album_name = source["info"]["album"]
    new_album_name = ''
    if source is not None:
        if 'album' in source['info']:
            new_album_name = source['info']['album']

    if new_album_name != album_name:
        album_name = new_album_name
        send_album(album_name)


def poll_artist(source):
    global artist_name
    # new_artist_name = source["info"]["artist"]
    new_artist_name = ''
    if source is not None:
        if 'artist' in source['info']:
            new_artist_name = source['info']['artist']
    if new_artist_name != artist_name:
        artist_name = new_artist_name
        send_artist(artist_name)

def poll_playing(source):
    global is_playing
    if source is None:
        new_is_playing = False
    else:
        new_is_playing = source["info"]["state"] == "playing"
    if new_is_playing != is_playing:
        is_playing = new_is_playing
        set_play_pause_button_state(is_playing, _audioconf.supported_cmds)

def poll_stream_name(stream):
    global stream_name
    global stream_type
    new_stream_type = None
    new_stream_name = ''
    if stream is not None:
        new_stream_name = stream['name']
        new_stream_type = stream['type']
    if new_stream_name != stream_name:
        stream_name = new_stream_name
        send_stream_name(stream_name)
    if new_stream_type != stream_type:
        stream_type = new_stream_type
        send_stream_type(stream_type)

def poll_source_name(source_id):
    if source_id is not None:
        send_source_name(f'Source {source_id+1}')
    else:
        send_source_name('')

def poll_zone_or_group_name(zonegroup):
    if zonegroup is not None:
        send_zone_or_group_name(zonegroup['name'])
    else:
        send_zone_or_group_name('')

def get_is_playing():
    return is_playing

def set_is_playing(is_p):
    global is_playing
    is_playing = is_p
    set_play_pause_button_state(is_playing, _audioconf.supported_cmds)

def get_muted():
    return is_muted

def set_muted(muted):
    global is_muted
    is_muted = muted
    update_mute_button(is_muted)

def skip_next_vol_f():
    global _skip_next_vol_f
    _skip_next_vol_f = True

def skip_next_playing():
    global _skip_next_playing
    _skip_next_playing = True

def skip_next_mute():
    global _skip_next_mute
    _skip_next_mute = True

# def resume_polling():
#     global _skip_next_vol_f
#     global _skip_next_playing
#     global _skip_next_mute
#
#     _skip_next_vol_f = False
#     _skip_next_playing = False
#     _skip_next_mute = False
