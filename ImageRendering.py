from decode import jpeg
import DisplaySerial

# https://github.com/daniel-falk/ujpeg
# image is a jpeg
def draw_image(image, tftUart):
    w, h, data = jpeg.decode(image)

    b5shift = 2**(8-5)
    b6shift = 2**(8-6)

    for y in range(w):
        for x in range(h):
            # fill x, y, 1, 1, rgb
            r, g, b = data[y*w+x]
            # convert RGB888 TO RGB565
            rshifted = round(r / b5shift)
            gshifted = round(g / b6shift)
            bshifted = round(b / b5shift)
            # color = round(rshifted + gshifted * b5shift + bshifted * b5shift * b6shift)
            color = rshifted + (gshifted << 5) + (bshifted << 11)
            DisplaySerial.uartWrite(f'fill {x}, {y}, 1, 1, {color}')


