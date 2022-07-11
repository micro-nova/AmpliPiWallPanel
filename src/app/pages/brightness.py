import json

from app import dt
from app.displayserial import message_id, message_is_slider_event, message_is_button_event, button_is_pressed, \
    get_slider_value, uart_write, set_component_txt, BRIGHTNESS_PAGE_NAME, set_component_value, change_page, \
    IDLE_PAGE_NAME

CONFIG_FILENAME = 'brightness.txt'

TIMEOUT_SLIDER_ID = 3
ACTIVE_BRIGHTNESS_SLIDER_ID = 5
INACTIVE_BRIGHTNESS_SLIDER_ID = 9

BACK_BUTTON_ID = 6

_BRIGHTNESS_FADE_TIME = 8

_file_stale = False
_last_touch_time = dt.time_sec()
_params = {'timeout': 10, 'active_b': 100, 'inactive_b': 10}
_last_brightness = -1

def init():
    global _params
    try:
        with open(CONFIG_FILENAME) as file:
            _params = json.load(file)
    except OSError:
        pass
    # ensure _params has all necessary entries
    if 'timeout' not in _params:
        _params['timeout'] = 10
    if 'active_b' not in _params:
        _params['active_b'] = 100
    if 'inactive_b' not in _params:
        _params['inactive_b'] = 10
    _update_ui()

def reset_touch_timer():
    global _last_touch_time
    _last_touch_time = dt.time_sec()

def update():
    global _last_brightness
    t = dt.time_sec()
    # perform linear interpolation between active and inactive brightness based on time
    p = min(max((t - _last_touch_time - _params['timeout']) / _BRIGHTNESS_FADE_TIME, 0), 1)
    brightness = int(_params['inactive_b'] * p + _params['active_b'] * (1-p))
    # print(f'brightness: {brightness}')
    # print(_last_touch_time)
    # print(_params['timeout'])
    # print(p)
    if brightness != _last_brightness:
        _last_brightness = brightness
        # change display brightness
        uart_write(f'dim={brightness}')
        if brightness == 0:
            # change page to blankpage
            change_page(IDLE_PAGE_NAME)

def handle_msg(message):
    global _file_stale
    global _params
    print("handling brightness page message")
    id = message_id(message)
    if message_is_slider_event(message):
        if id == TIMEOUT_SLIDER_ID:
            _file_stale = True
            timeout = 2 + ((get_slider_value(message) / 255) ** 2) * 60 * 10
            _params['timeout'] = timeout
            print(f'received {timeout} for timeout slider')
            if timeout >= 60:
                set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', f'{int(timeout/60)} m')
            else:
                set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', f'{int(timeout)} s')

        elif id == ACTIVE_BRIGHTNESS_SLIDER_ID:
            _file_stale = True
            _params['active_b'] = get_slider_value(message)
            print(f'received {_params["active_b"]} for active brightness slider')

            # ensure inactive is less than or equal to this
            if _params['inactive_b'] > _params['active_b']:
                _params['inactive_b'] = _params['active_b']
                set_component_value(BRIGHTNESS_PAGE_NAME, 'hinactive', _params['inactive_b'])

        elif id == INACTIVE_BRIGHTNESS_SLIDER_ID:
            _file_stale = True
            _params['inactive_b'] = get_slider_value(message)
            print(f'received {_params["inactive_b"]} for active brightness slider')

            # ensure active is greater than or equal to this
            if _params['active_b'] < _params['inactive_b']:
                _params['active_b'] = _params['inactive_b']
                set_component_value(BRIGHTNESS_PAGE_NAME, 'hactive', _params['active_b'])

    elif message_is_button_event(message) and button_is_pressed(message):
        if id == BACK_BUTTON_ID:
            _on_back()


def _update_ui():
    # set timeout value field
    if _params['timeout'] == 0:
        set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', 'Disabled')
    else:
        set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', f'{_params["timeout"]} s')
    # set slider values
    set_component_value(BRIGHTNESS_PAGE_NAME, 'hactive', _params['active_b'])
    set_component_value(BRIGHTNESS_PAGE_NAME, 'hinactive', _params['inactive_b'])



# _file_stale = False
# _timeout = None
# _brightness = None
# def init():
#     """Load brightness and timeout parameters. Should be called once on boot (not during update)."""
#     params = {'timeout': 0, 'active_b': 100, 'inactive_b': 10}
#     try:
#         with open(CONFIG_FILENAME) as file:
#             params = json.load(file)
#     except OSError:
#         pass
#     print(f'loaded brightness.txt json: {params}')
#     _send_params(**params)
#
#
# def reset():
#     """When performing a display firmware update, it is necessary to disable timeout."""
#     _send_params(timeout=0, active_b=100)
#
#
# def handle_msg(message):
#     global _file_stale
#     global _timeout
#     global _brightness
#     print("handling brightness page message")
#     id = message_id(message)
#     if message_is_slider_event(message):
#         if id == TIMEOUT_SLIDER_ID:
#             _file_stale = True
#             _timeout = get_slider_value(message)
#             print(f'received {_timeout} for timeout slider')
#         elif id == ACTIVE_BRIGHTNESS_SLIDER_ID:
#             _file_stale = True
#             _brightness = get_slider_value(message)
#             print(f'received {_brightness} for active brightness slider')
#     elif message_is_button_event(message) and button_is_pressed(message):
#         if id == BACK_BUTTON_ID:
#             _on_back()
#             _file_stale = False
#
def _on_back():
    global _file_stale
    if _file_stale:
        try:
            with open(CONFIG_FILENAME, 'w') as file:
                json.dump(_params, file)
                _file_stale = False
        except OSError:
            pass
