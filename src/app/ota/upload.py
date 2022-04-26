import os
from machine import UART

class NexUpload:
    def __init__(self, filename):
        self.__filename = filename
        self.__tftUart = UART(2, baudrate=115200, tx=16, rx=17)
        self.__filesize = 0

    def upload(self):
        # tftUart = UART(2, baudrate=115200, tx=16, rx=17)
        if not self.__check_file():
            print('Error in tft file!')
            return

        if not self.__download_tft_file():
            print('Error uploading tft file to display!')
            return

        print("Tft upload success.")

    def __check_file(self) -> bool:
        try:
            # try opening file
            with open(self.__filename, 'rb'):
                pass
            # get filesize
            self.__filesize = os.size(self.__filename)
        except OSError:
            return False
        return True

    def __download_tft_file(self):
        pass

