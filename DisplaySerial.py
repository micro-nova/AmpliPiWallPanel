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

tftUart = UART(2, baudrate=115200, tx=16, rx=17)


def send_title(title):
    # check if string is too long and trim if it is
    if len(title) > 30:
        title = title[0:26] + "..."
    uart_write(f'{SONG_NAME_OBJNAME}.txt="{title}"')


def send_artist(artist):
    # check if string is too long and trim if it is
    if len(artist) > 30:
        artist = artist[0:26] + "..."
    uart_write(f'{ARTIST_NAME_OBJNAME}.txt="{artist}"')


def update_play_pause_button(playing):
    if playing:
        uart_write(f'{PLAY_BUTTON_OBJNAME}.pic={PAUSE_PIC_ID}')
        uart_write(f'{PLAY_BUTTON_OBJNAME}.pic2={PAUSE_PIC_ID}')
    else:
        uart_write(f'{PLAY_BUTTON_OBJNAME}.pic={PLAY_PIC_ID}')
        uart_write(f'{PLAY_BUTTON_OBJNAME}.pic2={PLAY_PIC_ID}')


# returns vol_f from 0 to 1
def get_vol_slider_vol_f(message):
    vol = message[5] + (message[6] << 8) + (message[7] << 16) + (message[8] << 24)
    return vol / VOL_SLIDER_MAX


# vol_f is from 0 to 1
def set_vol_slider_vol_f(vol_f):
    pos = floor(vol_f * VOL_SLIDER_MAX)
    uart_write(f'{VOL_OBJNAME}.val={pos}')


def uart_any():
    return tftUart.any()


def uart_read():
    return tftUart.read()


def uart_write(string):
    tftUart.write(string)
    tftUart.write(TERM)  # message termination for
