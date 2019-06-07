#!/usr/bin/python

import serial
import struct
import sys
import time
import json

import aqi
from blinkstick import blinkstick

def  Wheel(wheel_pos):
    # Input a value 0 to 384 to get a color value.
    # The colours are a transition r - g -b - back to r
    r = 0;
    g = 0;
    b = 0;
    case = wheel_pos / 128
    if case == 0:
        r = 127 - wheel_pos % 128;   #Red down
        g = wheel_pos % 128;      # Green up
        b = 0;                  #blue off
    elif case == 1:
        g = 127 - wheel_pos % 128;  #green down
        b = wheel_pos % 128;      #blue up
        r = 0;                  #red off
    elif case == 2:
        b = 127 - wheel_pos % 128;  #blue down 
        r = wheel_pos % 128;      #red up
        g = 0;                  #green off

    return r, g, b


class AqiToBlinkStick(object):
    def __init__(self):
        self.bstick = blinkstick.BlinkStickPro(
            r_led_count=5, g_led_count=5, b_led_count=5, max_rgb_value=255)
        self.bstick.connect()
        self.bstick.bstick.set_max_rgb_value(128)

        self.aqi = aqi.AqiData()

        self.loop_count = 0

    def Loop(self):
        while True:
            self.LoopOne()
            time.sleep(1)
        
    def LoopOne(self):
        data = self.aqi.get_data_point()
        if data is not None:
            pm2_5 = data[0]
            pm10 = data[1]

            self.process_data(pm2_5, pm10)

    def process_data(self, pm2_5, pm10):
        aqipm2_5 = self.calcAQIpm25(pm2_5)
        color2_5 = self.get_color(aqipm2_5)
        intensity2_5 = int(round((aqipm2_5 % 50) / 50.0 * 5.0))
        
        aqipm10 = self.calcAQIpm10(pm10)
        color10 = self.get_color(aqipm10)
        intensity10 = int(round((aqipm10 % 50) / 50.0 * 5.0))

        for i in xrange(intensity2_5):
            self.bstick.set_color(0, i, *color2_5)

        for i in xrange(intensity10):
            self.bstick.set_color(1, i, *color10)

        active = self.loop_count % self.bstick.b_led_count
        for i in xrange(self.bstick.b_led_count):
            if i == active:
                r, g, b = Wheel(self.loop_count % 384)
            else:
                r, g, b = 0, 0, 0
            self.bstick.set_color(2, i, r, g, b)
            
        self.bstick.send_data_all()
        self.loop_count += 1

        print pm2_5, aqipm2_5, intensity2_5, pm10, aqipm10, intensity10

    def get_color(self, aqi):
        if aqi >= 50 and aqi < 100:
            return 255, 255, 0
        elif aqi >= 100 and aqi < 150:
            return 255, 165, 0
        elif aqi >= 150 and aqi < 200:
            return 255, 0, 0
        elif aqi >= 200 and aqi < 300:
            return 128, 0, 128
        elif aqi >= 300:
            return 165, 42, 42
        else:
            return 0, 255, 0

    def calcAQIpm25(self, pm2_5):
        pm = [float(x) for x in 0, 12, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4]
        aqi = [float(x) for x in 0, 50, 100, 150, 200, 300, 400, 500]

        aqipm2_5 = 0

	if (pm2_5 >= pm[0] and pm2_5 <= pm[1]):
		aqipm2_5 = ((aqi[1] - aqi[0]) / (pm[1] - pm[0])) * (pm2_5 - pm[0]) + aqi[0]
	elif (pm2_5 >= pm[1] and pm2_5 <= pm[2]):
		aqipm2_5 = ((aqi[2] - aqi[1]) / (pm[2] - pm[1])) * (pm2_5 - pm[1]) + aqi[1]
	elif (pm2_5 >= pm[2] and pm2_5 <= pm[3]):
		aqipm2_5 = ((aqi[3] - aqi[2]) / (pm[3] - pm[2])) * (pm2_5 - pm[2]) + aqi[2]
        elif  (pm2_5 >= pm[3] and pm2_5 <= pm[4]):
		aqipm2_5 = ((aqi[4] - aqi[3]) / (pm[4] - pm[3])) * (pm2_5 - pm[3]) + aqi[3]
	elif (pm2_5 >= pm[4] and pm2_5 <= pm[5]):
		aqipm2_5 = ((aqi[5] - aqi[4]) / (pm[5] - pm[4])) * (pm2_5 - pm[4]) + aqi[4]
	elif  (pm2_5 >= pm[5] and pm2_5 <= pm[6]):
		aqipm2_5 = ((aqi[6] - aqi[5]) / (pm[6] - pm[5])) * (pm2_5 - pm[5]) + aqi[5]
	elif (pm2_5 >= pm[6] and pm2_5 <= pm[7]):
		aqipm2_5 = ((aqi[7] - aqi[6]) / (pm[7] - pm[6])) * (pm2_5 - pm[6]) + aqi[6]

        return aqipm2_5


    def calcAQIpm10(self, pm10):
        pm = [float(x) for x in 0, 54, 154, 254, 354, 424, 504, 604]
        aqi = [float(x) for x in 0, 50, 100, 150, 200, 300, 400, 500]

	aqipm10 = 0

	if (pm10 >= pm[0] and pm10 <= pm[1]):
		aqipm10 = ((aqi[1] - aqi[0]) / (pm[1] - pm[0])) * (pm10 - pm[0]) + aqi[0]
        elif (pm10 >= pm[1] and pm10 <= pm[2]):
		aqipm10 = ((aqi[2] - aqi[1]) / (pm[2] - pm[1])) * (pm10 - pm[1]) + aqi[1]
        elif (pm10 >= pm[2] and pm10 <= pm[3]):
		aqipm10 = ((aqi[3] - aqi[2]) / (pm[3] - pm[2])) * (pm10 - pm[2]) + aqi[2]
	elif (pm10 >= pm[3] and pm10 <= pm[4]):
		aqipm10 = ((aqi[4] - aqi[3]) / (pm[4] - pm[3])) * (pm10 - pm[3]) + aqi[3]
	elif (pm10 >= pm[4] and pm10 <= pm[5]):
		aqipm10 = ((aqi[5] - aqi[4]) / (pm[5] - pm[4])) * (pm10 - pm[4]) + aqi[4]
	elif (pm10 >= pm[5] and pm10 <= pm[6]):
		aqipm10 = ((aqi[6] - aqi[5]) / (pm[6] - pm[5])) * (pm10 - pm[5]) + aqi[5]
	elif (pm10 >= pm[6] and pm10 <= pm[7]):
		aqipm10 = ((aqi[7] - aqi[6]) / (pm[7] - pm[6])) * (pm10 - pm[6]) + aqi[6]

	return aqipm10


def main():
    server = AqiToBlinkStick()
    server.Loop()


if __name__ == "__main__":
    sys.exit(main())
