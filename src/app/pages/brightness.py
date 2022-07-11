import json
from math import sqrt

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
_params = {'timeout': 60, 'active_b': 100, 'inactive_b': 10}
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
    if _file_stale and p >= 1:
        _save_file()

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
            timeout = _timeout_slider_to_value(get_slider_value(message))
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
            _save_file()

def _timeout_slider_to_value(slider_val):
    return 2 + ((slider_val / 255) ** 2) * 600

def _value_to_timeout_slider(value):
    return sqrt((value-2)*(255**2)/600)

def _update_ui():
    if _params["timeout"] >= 60:
        set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', f'{int(_params["timeout"] / 60)} m')
    else:
        set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', f'{int(_params["timeout"])} s')
    timeout_slider_value = _value_to_timeout_slider(_params["timeout"])
    # set slider values
    set_component_value(BRIGHTNESS_PAGE_NAME, 'htime', int(timeout_slider_value))
    set_component_value(BRIGHTNESS_PAGE_NAME, 'hactive', _params['active_b'])
    set_component_value(BRIGHTNESS_PAGE_NAME, 'hinactive', _params['inactive_b'])

def _save_file():
    global _file_stale
    if _file_stale:
        try:
            with open(CONFIG_FILENAME, 'w') as file:
                json.dump(_params, file)
                _file_stale = False
        except OSError:
            pass
