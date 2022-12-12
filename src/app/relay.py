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
    _DEBOUNCE_TIME_NS = 20000000  # nanoseconds

    def __init__(self, relay_pin, init_state, button_objname, mqtt_publish_func):
        self._state = init_state
        self._pstate = init_state
        self._event_time = time.time_ns()
        self._relay_pin = relay_pin
        self._button_objname = button_objname
        self.mqtt_publish_func = mqtt_publish_func
        mqtt_publish_func(init_state)

    def try_toggle(self):
        curr_time = time.time_ns()
        if curr_time - self._event_time >= self._DEBOUNCE_TIME_NS:
            self._state = not self._state
            self._event_time = curr_time
            self._relay_pin.value(self._state)
            _update_indicator(self._state, self._button_objname)
            self.publish_state()
            print(f'current relay state: {get_state()}')
        else:
            self._event_time = curr_time

    def reset_timer(self):
        self._event_time = time.time_ns()

    def file_is_stale(self):
        return self._pstate != self._state

    def update(self):
        self._pstate = self._state

    def get_state(self):
        return self._state

    def publish_state(self):
        self.mqtt_publish_func(self._state)

    def set_state(self, state):
        self._state = state
        self._relay_pin.value(self._state)
        _update_indicator(self._state, self._button_objname)
        self.publish_state()

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
    from app.mqttconfig import send_relay1_state, send_relay2_state
    loaded_state = _read_file()
    state1 = RelayState(_relay1, loaded_state['relay1'], RELAY_LEFT_OBJNAME, send_relay1_state)
    state2 = RelayState(_relay2, loaded_state['relay2'], RELAY_RIGHT_OBJNAME, send_relay2_state)
    _update_indicator(loaded_state['relay1'], RELAY_LEFT_OBJNAME)
    _update_indicator(loaded_state['relay2'], RELAY_RIGHT_OBJNAME)

    _button1.irq(trigger=Pin.IRQ_RISING, handler=button1_rising_edge)
    _button2.irq(trigger=Pin.IRQ_RISING, handler=button2_rising_edge)
    # _button1.irq(trigger=Pin.IRQ_FALLING, handler=button1_falling_edge)
    # _button2.irq(trigger=Pin.IRQ_FALLING, handler=button2_falling_edge)

    # this seems to work fine, but it might make sense to reset the timer on both rising and falling edges

def update():
    file_stale = state1.file_is_stale() or state2.file_is_stale()
    state1.update()
    state2.update()

    if file_stale:
        new_dict = {'relay1': state1.get_state(), 'relay2': state2.get_state()}
        print(new_dict)
        _write_file(new_dict)

def set_relay1_state(state):
    state1.set_state(state)

def set_relay2_state(state):
    state2.set_state(state)

def mqtt_init(state=None):
    """Publishes current relay state"""
    if state is not None:
        state1.set_state(state[0])
        state2.set_state(state[1])
    state1.publish_state()
    state2.publish_state()


def get_state():
    return [state1.get_state(), state2.get_state()]

def _write_file(filedict):
    with open(_RELAY_STATE_FILENAME, 'w') as relay_file:
        json.dump(filedict, relay_file)

def _read_file():
    try:
        with open(_RELAY_STATE_FILENAME) as relay_file:
            return json.load(relay_file)
    except OSError:
        new_dict = {'relay1': False, 'relay2': False}
        _write_file(new_dict)
        return new_dict

def _update_indicator(state, button_objname):
    uart_write('sleep=0')
    if state:
        uart_write(f'{HOME_PAGE_NAME}.{button_objname}.pic={RELAY_ON_PIC_ID}')
    else:
        uart_write(f'{HOME_PAGE_NAME}.{button_objname}.pic={RELAY_OFF_PIC_ID}')
