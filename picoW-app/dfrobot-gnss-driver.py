#Convert from DFRobot_GNSS module for Raspberry Pi provided by DFRobot https://github.com/DFRobot/DFRobot_GNSS/tree/master/python/raspberrypi

from machine import I2C, Pin
import time

# Constants (from original file)
GNSS_DEVICE_ADDR = 0x20
I2C_YEAR_H = 0
I2C_YEAR_L = 1
I2C_MONTH = 2
I2C_DATE = 3
I2C_HOUR = 4
I2C_MINUTE = 5
I2C_SECOND = 6
I2C_LAT_1 = 7
I2C_LON_1 = 13
I2C_USE_STAR = 19
I2C_ALT_H = 20
I2C_SOG_H = 23
I2C_COG_H = 26
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

class DFRobot_GNSS_I2C:
    def __init__(self, i2c, addr=GNSS_DEVICE_ADDR):
        self.i2c = i2c
        self.addr = addr

    def write_reg(self, reg, data):
        try:
            self.i2c.writeto_mem(self.addr, reg, bytes(data))
        except OSError:
            print("I2C Write error")

    def read_reg(self, reg, length):
        try:
            return list(self.i2c.readfrom_mem(self.addr, reg, length))
        except OSError:
            print("I2C Read error")
            return [-1]

    def enable_power(self):
        self.write_reg(I2C_SLEEP_MODE, [ENABLE_POWER])

    def disable_power(self):
        self.write_reg(I2C_SLEEP_MODE, [DISABLE_POWER])

    def rgb_on(self):
        self.write_reg(I2C_RGB_MODE, [RGB_ON])

    def rgb_off(self):
        self.write_reg(I2C_RGB_MODE, [RGB_OFF])

    def get_date(self):
        rslt = self.read_reg(I2C_YEAR_H, 4)
        if rslt[0] != -1:
            year = rslt[0] << 8 | rslt[1]
            month = rslt[2]
            day = rslt[3]
            return year, month, day
        return None

    def get_time(self):
        rslt = self.read_reg(I2C_HOUR, 3)
        if rslt[0] != -1:
            return rslt[0], rslt[1], rslt[2]
        return None

    def get_latitude(self):
        rslt = self.read_reg(I2C_LAT_1, 6)
        if rslt[0] != -1:
            deg = rslt[0]
            minutes = rslt[1]
            fractional = rslt[2]*65536 + rslt[3]*256 + rslt[4]
            direction = chr(rslt[5])
            decimal = deg + (minutes + fractional / 100000) / 60
            if direction == 'S':
                decimal = -decimal
            return decimal
        return None

    def get_longitude(self):
        rslt = self.read_reg(I2C_LON_1, 6)
        if rslt[0] != -1:
            deg = rslt[0]
            minutes = rslt[1]
            fractional = rslt[2]*65536 + rslt[3]*256 + rslt[4]
            direction = chr(rslt[5])
            decimal = deg + (minutes + fractional / 100000) / 60
            if direction == 'W':
                decimal = -decimal
            return decimal
        return None

    def get_altitude(self):
        rslt = self.read_reg(I2C_ALT_H, 3)
        if rslt[0] != -1:
            return rslt[0] << 8 | rslt[1] + rslt[2] / 100.0
        return None

    def get_satellite_count(self):
        rslt = self.read_reg(I2C_USE_STAR, 1)
        if rslt[0] != -1:
            return rslt[0]
        return 0

    def get_speed_over_ground(self):
        rslt = self.read_reg(I2C_SOG_H, 3)
        if rslt[0] != -1:
            sog = (rslt[0] << 8 | rslt[1]) + rslt[2] / 100.0  # km/h
            return sog
        return None

    def get_course_over_ground(self):
        rslt = self.read_reg(I2C_COG_H, 3)
        if rslt[0] != -1:
            cog = (rslt[0] << 8 | rslt[1]) + rslt[2] / 100.0  # degrees
            return cog
        return None

    def get_gnss_mode(self):
        '''!
        @brief Get the used GNSS mode 
        @return mode
        @retval 1 gps
        @retval 2 beidou
        @retval 3 gps + beidou
        @retval 4 glonass
        @retval 5 gps + glonass
        @retval 6 beidou +glonass
        @retval 7 gps + beidou + glonass
        '''
        rslt = self.read_reg(I2C_GNSS_MODE, 1)
        if rslt[0] != -1:
            return rslt[0]  
        return None
    
    def set_gnss_mode(self, mode):
        '''!
        @brief Set GNSS to be used 
        @param mode
        @n   GPS              use gps
        @n   BeiDou           use beidou
        @n   GPS_BeiDou       use gps + beidou
        @n   GLONASS          use glonass
        @n   GPS_GLONASS      use gps + glonass
        @n   BeiDou_GLONASS   use beidou +glonass
        @n   GPS_BeiDou_GLONASS use gps + beidou + glonass
        '''
        if mode < 1 or mode > 7:
            raise ValueError("Invalid mode. Must be between 1 and 7.")
        self.write_reg(I2C_GNSS_MODE, [mode])
        time.sleep(0.1)
