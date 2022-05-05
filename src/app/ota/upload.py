import os, gc
import time

import machine
from machine import UART

from app import displayserial
from app.dt import time_sec

# https://nextion.tech/2017/12/08/nextion-hmi-upload-protocol-v1-1/
class NexUpload:
    def __init__(self, filename):
        self.__filename = filename
        self.__tftUart = UART(2, baudrate=115200, tx=16, rx=17)
        self.__filesize = 0

    def upload(self):
        while self.__tftUart.any():
            print(self.__tftUart.read())

        gc.collect()
        if not self.__check_file():
            print('Error in tft file!')
            return

        if not self.__download_tft_file():
            print('Error uploading tft file to display!')
            return

        print("Tft upload success.")
        # remove file
        os.remove(self.__filename)
        machine.reset()

    def __check_file(self) -> bool:
        # TODO: perform checksum here? or during OTA release download?
        # I think the latter would be better since we can verify all files and re-download them when deemed corrupted
        """
        Determines file size
        :return: True: success. False: failed.
        """

        try:
            # https://forum.micropython.org/viewtopic.php?t=5291
            self.__filesize = os.stat(self.__filename)[6]
        except OSError:
            return False
        return True

    def __download_tft_file(self):
        while self.__tftUart.any():
            print(self.__tftUart.read())
        # self.__tu
        repeating = True
        while repeating:
            self.__tftUart.write(displayserial.TERM)
            time.sleep_ms(39)
            self.__tftUart.write(b"DRAKJHSUYDGBNCJHGJKSHBDN" + displayserial.TERM)
            time.sleep_ms(39)
            self.__tftUart.write(b"connect" + displayserial.TERM)
            time.sleep_ms(39)
            self.__tftUart.write(b"\xff\xffconnect" + displayserial.TERM)
            time.sleep_ms(39)
            if self.__tftUart.any():
                repeating = False

        time.sleep_ms(500)
        while not self.__tftUart.any():
            pass
        while self.__tftUart.any():
            print(self.__tftUart.read())

        connect_str = b"whmi-wri " + bytes(f'{self.__filesize},115200,a', 'UTF-8') + displayserial.TERM
        print(connect_str)
        self.__tftUart.write(connect_str)
        self.__wait_for(b"\x05", 3.0)


        with open(self.__filename, 'rb') as file:
            while (packet := file.read(4096)):
                # we will need to send 4096 bytes and then wait for the 0x05 byte from the display, which takes up to 500 ms
                self.__tftUart.write(packet)
                self.__wait_for(b"\x05", 3.0)
        time.sleep_ms(500)
        return True

    def __wait_for(self, expected_msg, timeout=-1.0):
        if timeout <= 0:
            while True:
                if self.__tftUart.any():
                    msg = self.__tftUart.read()
                    if msg == expected_msg:
                        return True
        else:
            start_time = time_sec()
            current_time = start_time
            while current_time - start_time <= timeout:
                if self.__tftUart.any():
                    msg = self.__tftUart.read()
                    if msg == expected_msg:
                        return True
                current_time = time_sec()
            print(f'Failed to wait for {expected_msg} message. Timeout reached!')
            return False

