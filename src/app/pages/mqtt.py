from app import mqttconfig, displayserial
from app.displayserial import message_id, message_is_button_event, button_is_pressed, message_is_text, \
    receive_text_message_str, MQTT_PAGE_NAME, NETWORK_CONNECTED_PIC_ID, NETWORK_DISCONNECTED_PIC_ID

_BROKER_IP_FIELD_OBJNAME = 'tbrokerip'
_TOPIC_FIELD_OBJNAME = 'ttopic'
_USERNAME_FIELD_OBJNAME = 'tusername'
_PASSWORD_FIELD_OBJNAME = 'tpassword'
_CONNECTIVITY_OBJNAME = "pnetwork"

_BROKER_IP_FIELD_ID = 7
_TOPIC_FIELD_ID = 2
_USERNAME_FIELD_ID = 11
_PASSWORD_FIELD_ID = 9
_APPLY_BUTTON_ID = 4


broker_ip = None
topic = None
username = None
password = None
def load_mqtt_page():
    displayserial.set_component_txt(displayserial.MQTT_PAGE_NAME, _BROKER_IP_FIELD_OBJNAME,
                                    _none_to_empty_str(mqttconfig.get_broker_ip()))
    displayserial.set_component_txt(displayserial.MQTT_PAGE_NAME, _TOPIC_FIELD_OBJNAME,
                                    _none_to_empty_str(mqttconfig.get_topic()))
    displayserial.set_component_txt(displayserial.MQTT_PAGE_NAME, _USERNAME_FIELD_OBJNAME,
                                    _none_to_empty_str(mqttconfig.get_username()))
    displayserial.set_component_txt(displayserial.MQTT_PAGE_NAME, _PASSWORD_FIELD_OBJNAME,
                                    _none_to_empty_str(mqttconfig.get_password()))
    _update_is_connected_icon()

def handle_msg(message):
    global broker_ip
    global topic
    global username
    global password
    id = message_id(message)
    if message_is_button_event(message) and button_is_pressed(message):
        if id == _APPLY_BUTTON_ID:
            _on_apply()
    elif message_is_text(message):
        text = receive_text_message_str(message)
        if id == _BROKER_IP_FIELD_ID:
            broker_ip = text
        elif id == _TOPIC_FIELD_ID:
            topic = text
        elif id == _USERNAME_FIELD_ID:
            username = text
        elif id == _PASSWORD_FIELD_ID:
            password = text

def _on_apply():
    displayserial.set_visible('zspinner', True)
    mqttconfig.update_config(broker_ip=broker_ip, topic=topic, username=username, password=password)
    displayserial.set_visible('zspinner', False)
    _update_is_connected_icon()

def _none_to_empty_str(string) -> str:
    return '' if string is None else string

def _update_is_connected_icon():
    if mqttconfig.get_is_connected():
        displayserial.uart_write(f'{MQTT_PAGE_NAME}.{_CONNECTIVITY_OBJNAME}.pic={NETWORK_CONNECTED_PIC_ID}')
    else:
        displayserial.uart_write(f'{MQTT_PAGE_NAME}.{_CONNECTIVITY_OBJNAME}.pic={NETWORK_DISCONNECTED_PIC_ID}')
