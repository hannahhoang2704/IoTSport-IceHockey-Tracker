# -*- coding: utf-8 -*-
'''!
  @file DFRobot_GNSS.py
  @brief DFRobot_GNSS Class infrastructure, implementation of underlying methods
  @copyright Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license The MIT License (MIT)
  @author [ZhixinLiu](zhixin.liu@dfrobot.com)
  @version V1.0
  @date 2020-10-26
  @url https://github.com/DFRobot/DFRobot_GNSS
  @adapted For Raspberry Pi Pico W with MicroPython
'''
import time
from machine import I2C, Pin, UART

I2C_MODE = 0x01
UART_MODE = 0x02

GNSS_DEVICE_ADDR = 0x20
I2C_YEAR_H = 0
I2C_YEAR_L = 1
I2C_MONTH = 2
I2C_DATE = 3
I2C_HOUR = 4
I2C_MINUTE = 5
I2C_SECOND = 6
I2C_LAT_1 = 7
I2C_LAT_2 = 8
I2C_LAT_X_24 = 9
I2C_LAT_X_16 = 10
I2C_LAT_X_8 = 11
I2C_LAT_DIS = 12
I2C_LON_1 = 13
I2C_LON_2 = 14
I2C_LON_X_24 = 15
I2C_LON_X_16 = 16
I2C_LON_X_8 = 17
I2C_LON_DIS = 18
I2C_USE_STAR = 19
I2C_ALT_H = 20
I2C_ALT_L = 21
I2C_ALT_X = 22
I2C_SOG_H = 23
I2C_SOG_L = 24
I2C_SOG_X = 25
I2C_COG_H = 26
I2C_COG_L = 27
I2C_COG_X = 28
I2C_START_GET = 29
I2C_ID = 30
I2C_DATA_LEN_H = 31
I2C_DATA_LEN_L = 32
I2C_ALL_DATA = 33
I2C_GNSS_MODE = 34
I2C_SLEEP_MODE = 35
I2C_RGB_MODE = 36

ENABLE_POWER = 0
DISABLE_POWER = 1

RGB_ON = 0x05
RGB_OFF = 0x02
GPS = 1
BeiDou = 2
GPS_BeiDou = 3
GLONASS = 4
GPS_GLONASS = 5
BeiDou_GLONASS = 6
GPS_BeiDou_GLONASS = 7


class struct_utc_tim:
    def __init__(self):
        self.year = 2000
        self.month = 1
        self.date = 1
        self.hour = 0
        self.minute = 0
        self.second = 0


class struct_lat_lon:
    def __init__(self):
        self.lat_dd = 0
        self.lat_mm = 0
        self.lat_mmmmm = 0
        self.lat_direction = "S"
        self.latitude_degree = 0.00
        self.latitude = 0.00
        self.lon_ddd = 0
        self.lon_mm = 0
        self.lon_mmmmm = 0
        self.lon_direction = "W"
        self.lonitude = 0.00
        self.lonitude_degree = 0.00


utc = struct_utc_tim()
lat_lon = struct_lat_lon()


class DFRobot_GNSS:
    __m_flag = 0
    __count = 0
    __txbuf = [0]
    __gnss_all_data = [0] * 1300
    __uart_i2c = 0

    def __init__(self, i2c_id=0, baud=9600):
        if i2c_id is not None:
            self.i2cbus = I2C(i2c_id, scl=Pin(1), sda=Pin(0), freq=100000)
            self.__uart_i2c = I2C_MODE
        else:
            self.uart = UART(0, baudrate=baud, tx=Pin(0), rx=Pin(1), timeout=500)
            self.__uart_i2c = UART_MODE

    def begin(self):
        rslt = self.read_reg(I2C_ID, 1)
        time.sleep(0.1)
        if rslt == -1:
            return False
        if rslt[0] != GNSS_DEVICE_ADDR:
            return False
        return True

    def get_date(self):
        rslt = self.read_reg(I2C_YEAR_H, 4)
        if rslt != -1:
            utc.year = rslt[0] * 256 + rslt[1]
            utc.month = rslt[2]
            utc.date = rslt[3]
        return utc

    def get_utc(self):
        rslt = self.read_reg(I2C_HOUR, 3)
        if rslt != -1:
            utc.hour = rslt[0]
            utc.minute = rslt[1]
            utc.second = rslt[2]
        return utc

    def get_lat(self):
        rslt = self.read_reg(I2C_LAT_1, 6)
        if rslt != -1:
            lat_lon.lat_dd = rslt[0]
            lat_lon.lat_mm = rslt[1]
            lat_lon.lat_mmmmm = rslt[2] * 65536 + rslt[3] * 256 + rslt[4]
            lat_lon.lat_direction = chr(rslt[5])
            lat_lon.latitude = lat_lon.lat_dd * 100.0 + lat_lon.lat_mm + lat_lon.lat_mmmmm / 100000.0
            lat_lon.latitude_degree = lat_lon.lat_dd + lat_lon.lat_mm / 60.0 + lat_lon.lat_mmmmm / 100000.0 / 60.0
        return lat_lon

    def get_lon(self):
        rslt = self.read_reg(I2C_LON_1, 6)
        if rslt != -1:
            lat_lon.lon_ddd = rslt[0]
            lat_lon.lon_mm = rslt[1]
            lat_lon.lon_mmmmm = rslt[2] * 65536 + rslt[3] * 256 + rslt[4]
            lat_lon.lon_direction = chr(rslt[5])
            lat_lon.lonitude = lat_lon.lon_ddd * 100.0 + lat_lon.lon_mm + lat_lon.lon_mmmmm / 100000.0
            lat_lon.lonitude_degree = lat_lon.lon_ddd + lat_lon.lon_mm / 60.0 + lat_lon.lon_mmmmm / 100000.0 / 60.0
        return lat_lon

    def get_num_sta_used(self):
        rslt = self.read_reg(I2C_USE_STAR, 1)
        if rslt != -1:
            return rslt[0]
        return 0

    def get_alt(self):
        rslt = self.read_reg(I2C_ALT_H, 3)
        if rslt != -1:
            high = rslt[0] * 256 + rslt[1] + rslt[2] / 100.0
        else:
            high = 0.0
        return high

    def get_cog(self):
        rslt = self.read_reg(I2C_COG_H, 3)
        if rslt != -1:
            cog = rslt[0] * 256 + rslt[1] + rslt[2] / 100.0
        else:
            cog = 0.0
        return cog

    def get_sog(self):
        rslt = self.read_reg(I2C_SOG_H, 3)
        if rslt != -1:
            sog = rslt[0] * 256 + rslt[1] + rslt[2] / 100.0
        else:
            sog = 0.0
        return sog

    def get_gnss_mode(self):
        rslt = self.read_reg(I2C_GNSS_MODE, 1)
        return rslt[0] if rslt != -1 else 0

    def set_gnss(self, mode):
        self.__txbuf[0] = mode
        self.write_reg(I2C_GNSS_MODE, self.__txbuf)
        time.sleep(0.1)

    def enable_power(self):
        self.__txbuf[0] = ENABLE_POWER
        self.write_reg(I2C_SLEEP_MODE, self.__txbuf)
        time.sleep(0.1)

    def disable_power(self):
        self.__txbuf[0] = DISABLE_POWER
        self.write_reg(I2C_SLEEP_MODE, self.__txbuf)
        time.sleep(0.1)

    def rgb_on(self):
        self.__txbuf[0] = RGB_ON
        self.write_reg(I2C_RGB_MODE, self.__txbuf)
        time.sleep(0.1)

    def rgb_off(self):
        self.__txbuf[0] = RGB_OFF
        self.write_reg(I2C_RGB_MODE, self.__txbuf)
        time.sleep(0.1)

    def get_gnss_len(self):
        self.__txbuf[0] = 0x55
        self.write_reg(I2C_START_GET, self.__txbuf)
        time.sleep(0.1)
        rslt = self.read_reg(I2C_DATA_LEN_H, 2)
        if rslt != -1:
            return rslt[0] * 256 + rslt[1]
        return 0

    def get_all_gnss(self):
        len = self.get_gnss_len()
        time.sleep(0.1)
        all_data = [0] * (len + 1)
        len1 = len // 32
        len2 = len % 32
        for num in range(len1 + 1):
            if num == len1:
                rslt = self.read_reg(I2C_ALL_DATA, len2)
                for i in range(len2):
                    if rslt[i] == 0:
                        rslt[i] = 0x0A
                all_data[num * 32:num * 32 + len2] = rslt
            else:
                rslt = self.read_reg(I2C_ALL_DATA, 32)
                for i in range(32):
                    if rslt[i] == 0:
                        rslt[i] = 0x0A
                all_data[num * 32:num * 32 + 32] = rslt
        return all_data


class DFRobot_GNSS_I2C(DFRobot_GNSS):
    def __init__(self, i2c_id, addr):
        self.__addr = addr
        super().__init__(i2c_id=i2c_id)

    def write_reg(self, reg, data):
        try:
            self.i2cbus.writeto_mem(self.__addr, reg, bytes(data))
        except:
            print("I2C write failed! Check connection.")
            time.sleep(1)

    def read_reg(self, reg, len):
        try:
            self.i2cbus.writeto(self.__addr, bytes([reg]))
            rslt = self.i2cbus.readfrom(self.__addr, len)
            return list(rslt)
        except:
            return -1


class DFRobot_GNSS_UART(DFRobot_GNSS):
    def __init__(self, baud):
        self.__baud = baud
        super().__init__(i2c_id=None, baud=baud)

    def write_reg(self, reg, data):
        send = [reg | 0x80, data[0]]
        self.uart.write(bytes(send))

    def read_reg(self, reg, len):
        send = [reg & 0x7F, len]
        self.uart.write(bytes(send))
        time.sleep(0.05)
        start_time = time.time()
        recv = []
        while (time.time() - start_time) <= 1:
            if self.uart.any():
                recv = self.uart.read(len)
                if recv:
                    return list(recv)
        return -1
