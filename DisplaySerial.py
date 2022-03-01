from machine import UART

PLAY_BUTTON_OBJNAME = "bplay"
SONG_NAME_VAR = "gname"
ARTIST_NAME_VAR = "gartist"

tftUart = UART(2, baudrate=115200, tx=16, rx=17)

# TERM = [0xff, 0xff, 0xff]
TERM = b"\xff\xff\xff"

# image id constants
PLAY_PIC_ID = 2
PAUSE_PIC_ID = 1



def send_title(title):
    # check if string is too long and trim if it is
    if len(title) > 60:
        title = title[0:59]
    uartWrite(f'{SONG_NAME_VAR}.txt="{title}"')


def send_artist(artist):
    # check if string is too long and trim if it is
    if len(artist) > 60:
        artist = artist[0:59]
    uartWrite(f'{ARTIST_NAME_VAR}.txt="{artist}"')


def update_play_pause_button(playing):
    if playing:
        uartWrite(f'{PLAY_BUTTON_OBJNAME}.pic={PAUSE_PIC_ID}')
        # uartWrite(f'{PLAY_BUTTON_OBJNAME}.pic2={PAUSE_PIC_ID}')
    else:
        uartWrite(f'{PLAY_BUTTON_OBJNAME}.pic={PLAY_PIC_ID}')
        # uartWrite(f'{PLAY_BUTTON_OBJNAME}.pic2={PLAY_PIC_ID}')


def any():
    return tftUart.any()


def read():
    return tftUart.read()


def uartWrite(str):
    tftUart.write(str)
    tftUart.write(TERM)
