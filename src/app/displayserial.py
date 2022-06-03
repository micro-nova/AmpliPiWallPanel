import time

from machine import UART
from math import floor

TERM = b"\xff\xff\xff"

# ui constants
PLAY_UP_PIC_ID = 19
PLAY_DOWN_PIC_ID = 18
PAUSE_UP_PIC_ID = 4
PAUSE_DOWN_PIC_ID = 3

MUTED_PIC_ID = 15
UNMUTED_PIC_ID = 16

SLIDER_MUTED_CURSOR_PIC_ID = 12
SLIDER_UNMUTED_CURSOR_PIC_ID = 13
SLIDER_MUTED_FOREGROUND_PIC_ID = 10
SLIDER_UNMUTED_FOREGROUND_PIC_ID = 11
WIFI_CONNECTED_PIC_ID = 29
WIFI_DISCONNECTED_PIC_ID = 31

RELAY_OFF_PIC_ID = 7
RELAY_ON_PIC_ID = 8

DLNA_PIC_ID = 36
FMRADIO_PIC_ID = 37
INTERNET_RADIO_PIC_ID = 38
PANDORA_PIC_ID = 39
PLEXAMP_PIC_ID = 40
RCA_PIC_ID = 41
SHAIRPORT_PIC_ID = 42
SPOTIFY_PIC_ID = 43

GEAR_PIC_ID = 14
GEAR_W_NOTE_PIC_ID = 47

RELAY_LEFT_OBJNAME = "prelay1"
RELAY_RIGHT_OBJNAME = "prelay2"


# objnames related to polling
STREAM_NAME_OBJNAME = "bstream"
STREAM_ICON_OBJNAME = "picon"
ZONE_NAME_OBJNAME = "bzone"
SOURCE_NAME_OBJNAME = "bsource"
PLAY_BUTTON_OBJNAME = "bplay"
MUTE_BUTTON_OBJNAME = "bmute"
SONG_NAME_OBJNAME = "tname"
ALBUM_NAME_OBJNAME = "talbum"
ARTIST_NAME_OBJNAME = "tartist"
VOL_OBJNAME = "hvol"
VOL_SLIDER_MAX = 1024.0

# serial constants
BUTTON_MESSAGE = 0x65
SLIDER_MESSAGE = 0x64
TEXT_MESSAGE = 0x63

# event constants
PRESSED_EVENT = 0x01
RELEASED_EVENT = 0x00

# page names
HOME_PAGE_NAME = "mainpage"
CONFIG_PAGE_NAME = "configpage"
SSID_PAGE_NAME = "ssidpage"
STREAM_PAGE_NAME = "streampage"
ZONE_PAGE_NAME = "zonepage"
VERSION_PAGE_NAME = "versionpage"
VERSIONINFO_PAGE_NAME = "vinfopage"
CONNECTION_PAGE_NAME = "cpage"
SOURCE_PAGE_NAME = "sourcepage"
GROUP_INVALID_PAGE_NAME = "ginvalidpage"
BOOT_PAGE_NAME = "bootpage"
ADVANCED_SETTINGS_PAGE_NAME = "advpage"

tftUart = UART(2, baudrate=115200, tx=16, rx=17)


def message_id(message) -> int:
    return message[2]

def message_is_button_event(message) -> bool:
    return message[0] == BUTTON_MESSAGE

def message_is_slider_event(message) -> bool:
    return message[0] == SLIDER_MESSAGE

def message_is_text(message) -> bool:
    return message[0] == TEXT_MESSAGE

def button_is_pressed(button_message) -> bool:
    return button_message[3] == PRESSED_EVENT

def stream_type_to_pic_id(stream_type):
    if stream_type == 'rca':
        return RCA_PIC_ID
    elif stream_type == 'airplay':
        return SHAIRPORT_PIC_ID
    elif stream_type == 'pandora':
        return PANDORA_PIC_ID
    elif stream_type == 'dlna':
        return DLNA_PIC_ID
    elif stream_type == 'internetradio':
        return INTERNET_RADIO_PIC_ID
    elif stream_type == 'plexamp':
        return PLEXAMP_PIC_ID
    elif stream_type == 'spotify':
        return SPOTIFY_PIC_ID
    else:
        return None

def change_page(pagename):
    uart_write(f'page {pagename}')


def send_title(title):
    # check if string is too long and trim if it is
    if len(title) > 30:
        title = title[0:26] + "..."
    set_component_txt(HOME_PAGE_NAME, SONG_NAME_OBJNAME, title)


def send_album(album):
    if len(album) > 35:
        album = album[0:31] + "..."
    set_component_txt(HOME_PAGE_NAME, ALBUM_NAME_OBJNAME, album)


def send_artist(artist):
    # check if string is too long and trim if it is
    if len(artist) > 30:
        artist = artist[0:26] + "..."
    set_component_txt(HOME_PAGE_NAME, ARTIST_NAME_OBJNAME, artist)

def send_stream_name(stream_name):
    if len(stream_name) > 30:
        stream_name = stream_name[0:26] + "..."
    set_component_txt(HOME_PAGE_NAME, STREAM_NAME_OBJNAME, stream_name)

def send_stream_type(stream_type):
    image_id = stream_type_to_pic_id(stream_type)
    if image_id is not None:
        set_image(HOME_PAGE_NAME, STREAM_ICON_OBJNAME, image_id)
        set_visible(STREAM_ICON_OBJNAME, True)
    else:
        set_visible(STREAM_ICON_OBJNAME, False)


def send_source_name(source_name):
    set_component_txt(HOME_PAGE_NAME, SOURCE_NAME_OBJNAME, source_name)

def send_zone_or_group_name(zone_name):
    if len(zone_name) > 30:
        zone_name = zone_name[0:26] + "..."
    set_component_txt(CONFIG_PAGE_NAME, ZONE_NAME_OBJNAME, zone_name)


def set_component_txt(pagename, componentname, txt):
    uart_write(f'{pagename}.{componentname}.txt="{txt}"')

def set_component_property(pagename, componentname, propertyname, value):
    uart_write(f'{pagename}.{componentname}.{propertyname}={value}')

def set_image(pagename, componentname, pic):
    uart_write(f'{pagename}.{componentname}.pic={pic}')

# def set_image_local(componentname, pic):
#     uart_write(f'{componentname}.pic="{pic}')


def set_visible(id_or_name, visible):
    uart_write(f'vis {id_or_name},{1 if visible else 0}')


def update_play_pause_button(playing):
    if playing:
        uart_write(f'{HOME_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic={PAUSE_UP_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic2={PAUSE_DOWN_PIC_ID}')
    else:
        uart_write(f'{HOME_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic={PLAY_UP_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic2={PLAY_DOWN_PIC_ID}')


def update_mute_button(muted):
    if muted:
        uart_write(f'{HOME_PAGE_NAME}.{MUTE_BUTTON_OBJNAME}.pic={MUTED_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{MUTE_BUTTON_OBJNAME}.pic2={MUTED_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{VOL_OBJNAME}.pic1={SLIDER_MUTED_FOREGROUND_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{VOL_OBJNAME}.pic2={SLIDER_MUTED_CURSOR_PIC_ID}')
    else:
        uart_write(f'{HOME_PAGE_NAME}.{MUTE_BUTTON_OBJNAME}.pic={UNMUTED_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{MUTE_BUTTON_OBJNAME}.pic2={UNMUTED_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{VOL_OBJNAME}.pic1={SLIDER_UNMUTED_FOREGROUND_PIC_ID}')
        uart_write(f'{HOME_PAGE_NAME}.{VOL_OBJNAME}.pic2={SLIDER_UNMUTED_CURSOR_PIC_ID}')


# returns vol_f from 0 to 1
def get_vol_slider_vol_f(message):
    vol = message[3] + (message[4] << 8) + (message[5] << 16) + (message[6] << 24)
    return vol / VOL_SLIDER_MAX


# returns the string from a test message
def receive_text_message_str(message):
    # get bytes from 3 to len-3 and convert to string
    text_str = ''
    str_msg = message[3:]
    for i in str_msg:
        text_str += chr(i)

        # text_str = text_str + message[i].to_bytes(1, 'big').decode("utf-8")
    return text_str


# vol_f is from 0 to 1
def set_vol_slider_vol_f(vol_f):
    pos = floor(vol_f * VOL_SLIDER_MAX)
    uart_write(f'{HOME_PAGE_NAME}.{VOL_OBJNAME}.val={pos}')


def uart_any():
    return tftUart.any()


def uart_read():
    return tftUart.read()


def uart_write(string):
    tftUart.write(string)
    # tftUart.write(f'{string}{TERM}')
    tftUart.write(TERM)  # message termination for nextion uart
    time.sleep_ms(2)


