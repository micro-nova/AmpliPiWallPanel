import gc
import json
import umqtt.simple as umqtt
import machine
import time
import random

from app import relay
from app.dt import time_sec

_MQTT_CONFIG_FILENAME = 'mqtt.txt'

_ON_VALUE = 'on'
_OFF_VALUE = 'off'
_RELAY1_SUBTOPIC = 'relay1'
_RELAY2_SUBTOPIC = 'relay2'

_RECONNECT_INTERVAL = 60*10  # seconds

c: umqtt.MQTTClient = None
config: dict = None
is_connected = False
last_reconnect_time = time_sec()

# can also be called again to restart
def start():
    global c
    global config
    try:
        if c is not None:
            try:
                c.disconnect()
            except Exception as e:
                print(f'mqttconfig start disconnect threw an error: {e}')
            del c
            c = None
            gc.collect()

        config = _read_file()
        broker_ip = get_broker_ip()
        if broker_ip is not None and len(broker_ip) > 0:
            ip_port = broker_ip.split(':')
            id = get_client_id()
            if id is None or len(id) == 0:
                id = f'{random.randint(0, 2**31-1)},{machine.unique_id()}'
                update_config(client_id=id)
            username = None if get_username() == '' else get_username()
            password = None if get_password() == '' else get_password()
            if len(ip_port) == 2 and ip_port[1].isnumeric():
                c = umqtt.MQTTClient(id, ip_port[0], port=int(ip_port[1]), user=username, password=password)
            else:
                c = umqtt.MQTTClient(id, ip_port[0], user=username, password=password)

            # home assistant tries to change the state for some reason,
            # so store it here and publish it after init
            state = relay.get_state()
            c.set_callback(_callback)
            try_connect()  # this also sets is_connected
            c.subscribe(_relay1_topic(config, True))
            c.subscribe(_relay2_topic(config, True))
            for i in range(10):
                relay.mqtt_init(state)
                time.sleep_ms(20)
                c.check_msg()
                time.sleep_ms(20)
            return True
    except Exception as e:
        print(f'mqttconfig start threw an error: {e}')

    return False

def set_topic_base(base):
    update_config(topic=f'home/{base}/wp')

def update_config(broker_ip=None, topic=None, username=None, password=None, client_id=None):
    global config
    config = _read_file()
    if broker_ip is not None:
        config['broker_ip'] = broker_ip
    if topic is not None:
        config['topic'] = topic
    if username is not None:
        config['username'] = username
    if password is not None:
        config['password'] = password
    if client_id is not None:
        config['client_id'] = client_id
    _write_file(config)

    # start/restart mqtt client
    start()


def get_broker_ip():
    if config is not None:
        return config.get('broker_ip', None)
    return None

def get_topic():
    if config is not None:
        return config.get('topic', None)
    return None

def get_username():
    if config is not None:
        return config.get('username', None)
    return None

def get_password():
    if config is not None:
        return config.get('password', None)
    return None

def get_client_id():
    if config is not None:
        return config.get('client_id', None)
    return None

def update():
    global last_reconnect_time
    global is_connected
    if c is not None and is_connected:
        try:
            c.check_msg()
        except Exception as e:
            print(f'mqttconfig check_msg threw an error: {e}')
            is_connected = False
            time.sleep_ms(20)
    elif c is not None:  # is_connected is false
        curr_time = time_sec()
        if curr_time - last_reconnect_time >= _RECONNECT_INTERVAL:
            last_reconnect_time = curr_time
            print("trying periodic mqtt reconnect...")
            start()

def try_connect():
    global is_connected
    if c is not None:
        try:
            c.connect()
            is_connected = True
        except Exception as e:
            print(f'mqttconfig connect threw an error: {e}')
            is_connected = False
    else:
        is_connected = False

def get_is_connected():
    return is_connected

def send_relay1_state(state):
    """Publishes a message indicating the state of relay1."""
    if c is not None and is_connected:
        try:
            c.publish(_relay1_topic(config, False), 'on' if state else 'off')
        except Exception as e:
            print(f'mqttconfig publish threw an error: {e}')
    else:
        print("tried sending relay state but mqtt is disconnected.")

def send_relay2_state(state):
    """Publishes a message indicating the state of relay2."""
    if c is not None and is_connected:
        try:
            c.publish(_relay2_topic(config, False), 'on' if state else 'off')
        except Exception as e:
            print(f'mqttconfig publish threw an error: {e}')
    else:
        print("tried sending relay state but mqtt is disconnected.")

def _callback(topic, msg):
    # handle switch stuff
    msg_str = msg.decode("utf-8")
    topic_str = topic.decode("utf-8")
    print(f'topic: {topic_str}. msg: {msg_str}')
    from app.relay import set_relay1_state, set_relay2_state
    if topic_str == _relay1_topic(config, True):
        if msg_str == _ON_VALUE:
            set_relay1_state(True)
        elif msg_str == _OFF_VALUE:
            set_relay1_state(False)
    elif topic_str == _relay2_topic(config, True):
        if msg_str == _ON_VALUE:
            set_relay2_state(True)
        elif msg_str == _OFF_VALUE:
            set_relay2_state(False)

def _read_file() -> dict:
    loaded_config = {'broker_ip': '', 'topic': '', 'username': '', 'password': '', 'client_id': ''}
    try:
        with open(_MQTT_CONFIG_FILENAME) as mqtt_file:
            loaded_config = json.load(mqtt_file)
    except OSError:
        _write_file(loaded_config)
    return loaded_config

def _write_file(file: dict):
    with open(_MQTT_CONFIG_FILENAME, 'w') as mqtt_file:
        json.dump(file, mqtt_file)

def _relay1_topic(config, cmd) -> str:
    return f'{config["topic"]}/{_RELAY1_SUBTOPIC}/{"cmd" if cmd else "status"}'

def _relay2_topic(config, cmd) -> str:
    return f'{config["topic"]}/{_RELAY2_SUBTOPIC}/{"cmd" if cmd else "status"}'

