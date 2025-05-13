from DFRobot_GNSS import *

# Select I2C or UART mode
I2C_MODE = 0x01
UART_MODE = 0x02
ctype = I2C_MODE

# Initialize GNSS module
if ctype == I2C_MODE:
    I2C_ID = 0  # I2C0 on Pico W (SDA=GP0, SCL=GP1)
    gnss = DFRobot_GNSS_I2C(I2C_ID, GNSS_DEVICE_ADDR)
elif ctype == UART_MODE:
    gnss = DFRobot_GNSS_UART(9600)


def setup():
    while not gnss.begin():
        print("Sensor initialize failed!!")
        time.sleep(1)
    gnss.enable_power()
    # Set GNSS mode to GPS + BeiDou + GLONASS
    gnss.set_gnss(GPS_BeiDou_GLONASS)
    gnss.set_gnss(GPS_BeiDou_GLONASS)
    gnss.rgb_on()
    # gnss.rgb_off()
    # gnss.disable_power()        # Disable gnss power, the GNSS data will not be refreshed this time


def loop():
    rslt = gnss.get_all_gnss()
    data = ""
    for num in range(len(rslt)):
        rslt[num] = chr(rslt[num])
        data += rslt[num]
    print(data)
    print("")
    time.sleep(3)


"""

def loop():
    utc = gnss.get_date()
    utc = gnss.get_utc()
    lat_lon = gnss.get_lat()
    lat_lon = gnss.get_lon()
    alt = gnss.get_alt()
    cog = gnss.get_cog()
    sog = gnss.get_sog()
    num = gnss.get_num_sta_used()
    star = gnss.get_gnss_mode()
    print(str(utc.year) + "/" + str(utc.month) + "/" + str(utc.date) + "/" + str(utc.hour) + ":" + str(utc.minute) + ":" + str(utc.second))
    print("star used number = " + str(num))
    print("used star mode = " + str(star))
      #print("latutide DDMM.MMMMM  = " + str(lat_lon.latitude) + "   direction = " + lat_lon.lat_direction)
      #print("lonutide DDDMM.MMMMM = " + str(lat_lon.lonitude) + "   direction = " + lat_lon.lon_direction)
    print("latutide degree = " + str(lat_lon.latitude_degree) + "   direction = " + lat_lon.lat_direction)
    print("lonutide degree = " + str(lat_lon.lonitude_degree) + "   direction = " + lat_lon.lon_direction)
    print("alt = " + str(alt))
    print("sog = " + str(sog) + " N")
    print("cog = " + str(cog) + " T")
    print("")
    time.sleep(1)
"""
if __name__ == "__main__":
    setup()
    while True:
        loop()
