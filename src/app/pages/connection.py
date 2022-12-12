from app import wifi, displayserial, api, polling
from app.displayserial import set_component_txt, CONNECTION_PAGE_NAME, uart_write, receive_text_message_str, \
    WIFI_CONNECTED_PIC_ID, WIFI_DISCONNECTED_PIC_ID, message_is_button_event, \
    button_is_pressed, message_id, message_is_text, set_visible, NETWORK_CONNECTED_PIC_ID, NETWORK_DISCONNECTED_PIC_ID
from app.pages import ssid

_SSID_FIELD_OBJNAME = 'tssidfield'
_PASSWORD_FIELD_OBJNAME = 'tpassfield'
_IP_FIELD_OBJNAME = 'tipfield'
_WIFI_STATUS_OBJNAME = 'pwifi'
_AMPLIPI_STATUS_OBJNAME = 'pnetwork'
_AUTODETECT_BUTTON_OBJNAME = 'bautodetect'

_WHITE = 65535
_GRAY = 35953
_BLACK = 0

# component ids
_CONNECT_BUTTON_ID = 7
_BACK_BUTTON_ID = 8
_SSID_FIELD_ID = 3
_AUTODETECT_BUTTON_ID = 12
_PASSWORD_FIELD_ID = 4 # might not be needed
_IP_FIELD_ID = 9

ssid_list = []
ssid_field_txt = ''
pass_field_txt = ''
ip_field_txt = ''
autodetect = True

def load_connection_page():
    global autodetect
    """Loads connection page contents. Can be called whenever since all relevant components are global in the
    connection page. Although, it shouldn't be called when the user is entering new wifi info since it would override it."""
    # load wifi info
    wifi_info = wifi.load_wifi_info()
    wifi_ssid = wifi_info.get('ssid', '')
    wifi_password = wifi_info.get('password', '')
    amplipi_ip = wifi_info.get('ip', '')
    autodetect = wifi_info.get('autodetect', True)

    # update page components
    print(f'updating ssid and password fields to {wifi_ssid} and {wifi_password}')
    set_component_txt(CONNECTION_PAGE_NAME, _SSID_FIELD_OBJNAME, wifi_ssid)
    set_component_txt(CONNECTION_PAGE_NAME, _PASSWORD_FIELD_OBJNAME, '*' * len(wifi_password))
    set_component_txt(CONNECTION_PAGE_NAME, _IP_FIELD_OBJNAME, amplipi_ip)
    update_autodetect_graphics()
    update_connection_status()

def update_autodetect_graphics():
    if autodetect:
        # make autodetect button toggled in???
        displayserial.set_component_property(displayserial.CONNECTION_PAGE_NAME, _AUTODETECT_BUTTON_OBJNAME, 'pco',
                                             _GRAY)
        displayserial.set_component_property(displayserial.CONNECTION_PAGE_NAME, _AUTODETECT_BUTTON_OBJNAME, 'pco2',
                                             _GRAY)
        # make pi text field gray
        displayserial.set_component_property(displayserial.CONNECTION_PAGE_NAME, _IP_FIELD_OBJNAME, 'pco', _GRAY)
        pass
    else:
        # make autodetect button toggled in???
        displayserial.set_component_property(displayserial.CONNECTION_PAGE_NAME, _AUTODETECT_BUTTON_OBJNAME, 'pco',
                                             _WHITE)
        displayserial.set_component_property(displayserial.CONNECTION_PAGE_NAME, _AUTODETECT_BUTTON_OBJNAME, 'pco2',
                                             _WHITE)
        # make pi text field gray
        displayserial.set_component_property(displayserial.CONNECTION_PAGE_NAME, _IP_FIELD_OBJNAME, 'pco', _BLACK)

def update_connection_status():
    """Updates the config page's WiFi and AmpliPi status symbols."""
    if wifi.is_connected():
        uart_write(f'{CONNECTION_PAGE_NAME}.{_WIFI_STATUS_OBJNAME}.pic={WIFI_CONNECTED_PIC_ID}')
    else:
        uart_write(f'{CONNECTION_PAGE_NAME}.{_WIFI_STATUS_OBJNAME}.pic={WIFI_DISCONNECTED_PIC_ID}')
    if api.get_amplipi_is_connected() and wifi.is_connected():
        uart_write(f'{CONNECTION_PAGE_NAME}.{_AMPLIPI_STATUS_OBJNAME}.pic={NETWORK_CONNECTED_PIC_ID}')
    else:
        uart_write(f'{CONNECTION_PAGE_NAME}.{_AMPLIPI_STATUS_OBJNAME}.pic={NETWORK_DISCONNECTED_PIC_ID}')

def _on_autodetect():
    global autodetect
    autodetect = True
    temp_info = wifi.load_wifi_info()
    wifi.save_wifi_info(temp_info.get('ssid', ''), temp_info.get('password', ''),
                        temp_info.get('ip', ''), autodetect)
    update_autodetect_graphics()

def handle_msg(message):
    global ssid_field_txt
    global pass_field_txt
    global ip_field_txt
    global autodetect
    print("handling connection page message")
    id = message_id(message)
    if message_is_button_event(message) and button_is_pressed(message):
        if id == _CONNECT_BUTTON_ID:
            set_visible('zspinner', True)
            print("Connect button pressed")
            wifi.disconnect()
            print(f'hopefully autodetect is on. autodetect:{autodetect}')
            wifi_info = wifi.load_wifi_info()
            password = pass_field_txt
            # check if the password is unmodified (i.e. not all asterisks)
            if pass_field_txt == '*' * len(wifi_info.get('password', '')):
                print('password is unmodified')
                password = wifi_info.get('password', '')
            else:
                print('password is modified')
            wifi.save_wifi_info(ssid_field_txt, password, ip_field_txt, autodetect)
            wifi.try_connect()
            api.check_amplipi_connection()
            update_connection_status()
            set_visible('zspinner', False)

        elif id == _BACK_BUTTON_ID:
            # back button should reset the fields to their saved state
            # nextion handles the page change on press already
            load_connection_page()
        elif id == _SSID_FIELD_ID:
            # nextion will switch to ssidpage, so we need to init that page
            ssid.load_ssid_page()
        elif id == _AUTODETECT_BUTTON_ID:
            print('autodetect button pressed')
            _on_autodetect()
        elif id == _IP_FIELD_ID:
            # the user entered an IP manually, so disable autodetect
            autodetect = False
            print('setting autodetect to false')
            update_autodetect_graphics()
    elif message_is_text(message):
        text = receive_text_message_str(message)
        if id == _SSID_FIELD_ID:
            ssid_field_txt = text
        elif id == _PASSWORD_FIELD_ID:
            pass_field_txt = text
        elif id == _IP_FIELD_ID:
            print(f'setting ip_field_txt to {text}')
            ip_field_txt = text
            api.set_amplipi_ip(ip_field_txt)

        print(f'Received string: {text}')