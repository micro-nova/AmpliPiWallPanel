from machine import UART
from math import floor

TERM = b"\xff\xff\xff"

# ui constants
PLAY_PIC_ID = 2
PAUSE_PIC_ID = 1
PLAY_BUTTON_OBJNAME = "bplay"
SONG_NAME_OBJNAME = "tname"
ARTIST_NAME_OBJNAME = "tartist"
VOL_OBJNAME = "hvol"
VOL_SLIDER_MAX = 1024.0

# serial constants
BUTTON_MESSAGE = 0x65
SLIDER_MESSAGE = 0x64

# page names
MAIN_PAGE_NAME = "mainpage"
CONFIG_PAGE_NAME = "configpage"
SSID_PAGE_NAME = "ssidpage"

tftUart = UART(2, baudrate=115200, tx=16, rx=17)


def change_page(pagename):
    uart_write(f'page {pagename}')


def send_title(title):
    # check if string is too long and trim if it is
    if len(title) > 30:
        title = title[0:26] + "..."
    set_component_txt(MAIN_PAGE_NAME, SONG_NAME_OBJNAME, title)


def send_artist(artist):
    # check if string is too long and trim if it is
    if len(artist) > 30:
        artist = artist[0:26] + "..."
    set_component_txt(MAIN_PAGE_NAME, ARTIST_NAME_OBJNAME, artist)
    # uart_write(f'{MAIN_PAGE_NAME}.{ARTIST_NAME_OBJNAME}.txt="{artist}"')


def set_component_txt(pagename, componentname, txt):
    uart_write(f'{pagename}.{componentname}.txt="{txt}"')


def set_visible(id, visible):
    uart_write(f'vis {id},{1 if visible else 0}')


def update_play_pause_button(playing):
    if playing:
        uart_write(f'{MAIN_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic={PAUSE_PIC_ID}')
        uart_write(f'{MAIN_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic2={PAUSE_PIC_ID}')
    else:
        uart_write(f'{MAIN_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic={PLAY_PIC_ID}')
        uart_write(f'{MAIN_PAGE_NAME}.{PLAY_BUTTON_OBJNAME}.pic2={PLAY_PIC_ID}')


# returns vol_f from 0 to 1
def get_vol_slider_vol_f(message):
    vol = message[3] + (message[4] << 8) + (message[5] << 16) + (message[6] << 24)
    return vol / VOL_SLIDER_MAX


# vol_f is from 0 to 1
def set_vol_slider_vol_f(vol_f):
    pos = floor(vol_f * VOL_SLIDER_MAX)
    uart_write(f'{MAIN_PAGE_NAME}.{VOL_OBJNAME}.val={pos}')


def uart_any():
    return tftUart.any()


def uart_read():
    return tftUart.read()


def uart_write(string):
    tftUart.write(string)
    tftUart.write(TERM)  # message termination for

