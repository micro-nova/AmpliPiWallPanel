import ujpeg
from ulab import numpy as np


# https://github.com/daniel-falk/ujpeg
# image is a jpeg
def draw_image(image, tftUart):
    r, g, b = ujpeg.decode(image)
    w, h = r.shape

    b5shift = 2**(8-5)
    b6shift = 2**(8-6)

    for y in range(w):
        for x in range(h):
            # fill x, y, 1, 1, rgb

            # convert RGB888 TO RGB565
            rshifted = round(r[y][x] / b5shift)
            gshifted = round(g[y][x] / b6shift)
            bshifted = round(b[y][x] / b5shift)
            # color = round(rshifted + gshifted * b5shift + bshifted * b5shift * b6shift)
            color = rshifted + (gshifted << 5) + (bshifted << 11)
            tftUart.write(f'fill {x}, {y}, 1, 1, {color}')


