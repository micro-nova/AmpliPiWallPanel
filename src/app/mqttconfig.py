import json
import umqtt.simple as umqtt
import machine
import time
import random



_MQTT_CONFIG_FILENAME = 'mqtt.txt'

_ON_VALUE = 'on'
_OFF_VALUE = 'off'
_RELAY1_SUBTOPIC = 'relay1'
_RELAY2_SUBTOPIC = 'relay2'

c: umqtt.MQTTClient = None
config: dict = None

# can also be called again to restart
def start():
    global c
    global config
    try:
        if c is not None:
            c.disconnect()

        config = _read_file()
        broker_ip = get_broker_ip()
        if broker_ip is not None and len(broker_ip) > 0:
            ip_port = broker_ip.split(':')
            # id = machine.unique_id()
            # readable_id = '{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
            id = get_client_id()
            if id is None or len(id) == 0:
                id = f'{random.randint(0, 2**31-1)}'
                update_config(client_id=id)
            username = None if get_username() == '' else get_username()
            password = None if get_password() == '' else get_password()
            if len(ip_port) == 2 and ip_port[1].isnumeric():
                c = umqtt.MQTTClient(id, ip_port[0], port=int(ip_port[1]), user=username, password=password)
            else:
                c = umqtt.MQTTClient(id, ip_port[0], user=username, password=password)

            c.set_callback(_callback)
            try_connect()
            c.subscribe(_relay1_topic(config, True))
            c.subscribe(_relay2_topic(config, True))
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
    # if c is None:
    #     start()
    # else:
    #     try:
    #         c.connect(clean_session=False)
    #     except Exception as e:
    #         print(f'got {e} from c.connect(clean_session=False')

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
    if c is not None:
        try:
            c.check_msg()
        except Exception as e:
            print(f'mqttconfig check_msg threw an error: {e}')
            try_connect()
            time.sleep_ms(100)

def try_connect():
    if c is not None:
        try:
            c.connect()
        except Exception as e:
            print(f'mqttconfig connect threw an error: {e}')

def send_relay1_state(state):
    """Publishes a message indicating the state of relay1."""
    if c is not None:
        try:
            c.publish(_relay1_topic(config, False), 'on' if state else 'off')
        except Exception as e:
            print(f'mqttconfig publish threw an error: {e}')

def send_relay2_state(state):
    """Publishes a message indicating the state of relay2."""
    if c is not None:
        try:
            c.publish(_relay2_topic(config, False), 'on' if state else 'off')
        except Exception as e:
            print(f'mqttconfig publish threw an error: {e}')

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

