import json

from app.displayserial import message_id, message_is_slider_event, message_is_button_event, button_is_pressed, \
    get_slider_value, uart_write, set_component_txt, BRIGHTNESS_PAGE_NAME, set_component_value

CONFIG_FILENAME = 'brightness.txt'

TIMEOUT_SLIDER_ID = 3
ACTIVE_BRIGHTNESS_SLIDER_ID = 5

BACK_BUTTON_ID = 6

_file_stale = False
_timeout = None
_brightness = None
def init():
    """Load brightness and timeout parameters. Should be called once on boot (not during update)."""
    params = {'timeout': 0, 'active_b': 100}
    try:
        with open(CONFIG_FILENAME) as file:
            params = json.load(file)
    except OSError:
        pass
    print(f'loaded brightness.txt json: {params}')
    _send_params(**params)


def reset():
    """When performing a display firmware update, it is necessary to disable timeout."""
    _send_params(timeout=0, active_b=100)


def handle_msg(message):
    global _file_stale
    global _timeout
    global _brightness
    print("handling brightness page message")
    id = message_id(message)
    if message_is_slider_event(message):
        if id == TIMEOUT_SLIDER_ID:
            _file_stale = True
            _timeout = get_slider_value(message)
            print(f'received {_timeout} for timeout slider')
        elif id == ACTIVE_BRIGHTNESS_SLIDER_ID:
            _file_stale = True
            _brightness = get_slider_value(message)
            print(f'received {_brightness} for active brightness slider')
    elif message_is_button_event(message) and button_is_pressed(message):
        if id == BACK_BUTTON_ID:
            _on_back()
            _file_stale = False

def _on_back():
    global _timeout
    global _brightness

    # save values to file (if changed)
    if _file_stale:
        # get the current parameters
        params = {}
        try:
            with open(CONFIG_FILENAME) as file:
                params = json.load(file)
        except OSError:
            pass
        if _timeout is not None:
            params['timeout'] = _timeout
        if _brightness is not None:
            params['active_b'] = _brightness

        try:
            with open(CONFIG_FILENAME, 'w') as file:
                json.dump(params, file)
        except OSError:
            pass

    _timeout = None
    _brightness = None

def _send_params(timeout=None, active_b=None):
    if timeout is not None:
        if timeout == 0:
            uart_write('thup=0')
            set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', 'Disabled')
            print(f'sent thup=0, {BRIGHTNESS_PAGE_NAME}.ttimeout.txt="Disabled"')
        else:
            uart_write('thup=1')
            set_component_txt(BRIGHTNESS_PAGE_NAME, 'ttimeout', f'{timeout} s')
            print(f'sent thup=1, {BRIGHTNESS_PAGE_NAME}.ttimeout.txt="{timeout} s"')
        uart_write(f'thsp={timeout}')
        set_component_value(BRIGHTNESS_PAGE_NAME, 'htime', timeout)
        print(f'sent {BRIGHTNESS_PAGE_NAME}.htime.val={timeout}')
        print(f'sent thsp={timeout}')
    if active_b is not None:
        uart_write(f'dim={active_b}')
        set_component_value(BRIGHTNESS_PAGE_NAME, 'hactive', active_b)
        print(f'sent dim={active_b}')
        print(f'sent {BRIGHTNESS_PAGE_NAME}.hactive.val={active_b}')

