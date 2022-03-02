from decode import jpeg
import DisplaySerial


# https://github.com/daniel-falk/ujpeg
# image is a jpeg
def draw_image(image):
    w, h, data = jpeg().decode(image)

    b5shift = 2 ** (8 - 5)
    b6shift = 2 ** (8 - 6)

    x = 0
    y = 0
    for idx, color in enumerate(data):
        if color == 0:
            x += 1
            y = 0
        else:
            r, g, b = color
            y += 1
            # convert RGB888 TO RGB565
            rshifted = round(r / b5shift)
            gshifted = round(g / b6shift)
            bshifted = round(b / b5shift)
            # color = round(rshifted + gshifted * b5shift + bshifted * b5shift * b6shift)
            color = rshifted + (gshifted << 5) + (bshifted << 11)
            # color = 65535
            DisplaySerial.uartWrite(f'fill {x*3},{y*3},3,3,{color}')



    # for y in range(w):
    #     for x in range(h):
    #         # fill x, y, 1, 1, rgb
    #         print(data[y * w + x])
    #         # r, g, b = data[y * w + x]
    #         r = data[y * w + x][0]
    #         g = data[y * w + x][1]
    #         b = data[y * w + x][2]
    #         # convert RGB888 TO RGB565
    #         rshifted = round(r / b5shift)
    #         gshifted = round(g / b6shift)
    #         bshifted = round(b / b5shift)
    #         # color = round(rshifted + gshifted * b5shift + bshifted * b5shift * b6shift)
    #         color = rshifted + (gshifted << 5) + (bshifted << 11)
    #         DisplaySerial.uartWrite(f'fill {x}, {y}, 1, 1, {color}')
