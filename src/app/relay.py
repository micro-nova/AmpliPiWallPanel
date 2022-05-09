import json

from machine import Pin
import time

from app.displayserial import uart_write, HOME_PAGE_NAME, RELAY_LEFT_OBJNAME, RELAY_ON_PIC_ID, RELAY_OFF_PIC_ID, \
    RELAY_RIGHT_OBJNAME

_RELAY_STATE_FILENAME = 'relay.txt'

_BUTTON_1_PIN = 14
_BUTTON_2_PIN = 27

_RELAY_1_PIN = 22
_RELAY_2_PIN = 19

_button1 = Pin(_BUTTON_1_PIN, Pin.IN)
_button2 = Pin(_BUTTON_2_PIN, Pin.IN)
_relay1 = Pin(_RELAY_1_PIN, Pin.OUT)
_relay2 = Pin(_RELAY_2_PIN, Pin.OUT)

class RelayState:
    _DEBOUNCE_TIME_NS = 20000000 # nanoseconds

    def __init__(self, relay_pin, init_state, button_objname):
        self._state = init_state
        self._pstate = init_state
        self._event_time = time.time_ns()
        self._relay_pin = relay_pin
        self._button_objname = button_objname

    def try_toggle(self):
        curr_time = time.time_ns()
        if curr_time - self._event_time >= self._DEBOUNCE_TIME_NS:
            self._state = not self._state
            self._event_time = curr_time
            self._relay_pin.value(self._state)
            _update_indicator(self._state, self._button_objname)
        else:
            print(f'debouncing: {curr_time - self._event_time}')
            self._event_time = curr_time

    def reset_timer(self):
        self._event_time = time.time_ns()

    def file_is_stale(self):
        return self._pstate != self._state

    def update(self):
        self._pstate = self._state

    def get_state(self):
        return self._pstate


state1: RelayState = None
state2: RelayState = None

def button1_rising_edge(pin):
    state1.try_toggle()

def button2_rising_edge(pin):
    state2.try_toggle()

def button1_falling_edge(pin):
    state1.reset_timer()

def button2_falling_edge(pin):
    state2.reset_timer()

def setup():
    global state1
    global state2
    loaded_state = _read_file()
    state1 = RelayState(_relay1, loaded_state['relay1'], RELAY_LEFT_OBJNAME)
    state2 = RelayState(_relay2, loaded_state['relay2'], RELAY_RIGHT_OBJNAME)
    _update_indicators(loaded_state['relay1'], loaded_state['relay2'])

    _button1.irq(trigger=Pin.IRQ_RISING, handler=button1_rising_edge)
    _button2.irq(trigger=Pin.IRQ_RISING, handler=button2_rising_edge)
    # _button1.irq(trigger=Pin.IRQ_FALLING, handler=button1_falling_edge)
    # _button2.irq(trigger=Pin.IRQ_FALLING, handler=button2_falling_edge)
    # TODO: reset timer on both rising and falling edge

def update():
    file_stale = state1.file_is_stale() or state2.file_is_stale()
    state1.update()
    state2.update()

    if file_stale:
        new_dict = {'relay1': state1.get_state(), 'relay2': state2.get_state()}
        print(new_dict)
        _write_file(new_dict)


def _write_file(filedict):
    with open(_RELAY_STATE_FILENAME, 'w') as relay_file:
        # TODO: combine into one line with json.dump?
        relay_file_str = json.dumps(filedict)
        relay_file.write(relay_file_str)

def _read_file():
    try:
        with open(_RELAY_STATE_FILENAME) as relay_file:
            # TODO: combine into one line with json.load?
            relay_file_str = relay_file.read()
            return json.loads(relay_file_str)
    except OSError:
        new_dict = {'relay1': False, 'relay2': False}
        _write_file(new_dict)
        return new_dict

def _update_indicators(left, right):
    _update_indicator(left, RELAY_LEFT_OBJNAME)
    _update_indicator(right, RELAY_RIGHT_OBJNAME)

def _update_indicator(state, button_objname):
    if state:
        uart_write(f'{HOME_PAGE_NAME}.{button_objname}.pic={RELAY_ON_PIC_ID}')
    else:
        uart_write(f'{HOME_PAGE_NAME}.{button_objname}.pic={RELAY_OFF_PIC_ID}')

