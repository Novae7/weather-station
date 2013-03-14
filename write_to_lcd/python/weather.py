#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import time
import math
import logging as log
log.basicConfig(level=log.INFO)

from tinkerforge.ip_connection import IPConnection
from tinkerforge.ip_connection import Error
from tinkerforge.brick_master import Master
from tinkerforge.bricklet_lcd_20x4 import LCD20x4
from tinkerforge.bricklet_ambient_light import AmbientLight
from tinkerforge.bricklet_humidity import Humidity
from tinkerforge.bricklet_barometer import Barometer

class WeatherStation:
    HOST = "localhost"
    PORT = 4223

    ipcon = None
    lcd = None
    al = None
    hum = None
    baro = None

    def __init__(self):
        self.ipcon = IPConnection()
        while True:
            try:
                self.ipcon.connect(WeatherStation.HOST, WeatherStation.PORT)
                break
            except Error as e:
                log.error('Connection Error: ' + str(e.description))
                time.sleep(1)
            except socket.error as e:
                log.error('Socket error: ' + str(e))
                time.sleep(1)

        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, 
                                     self.cb_enumerate)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, 
                                     self.cb_connected)

        while True:
            try:
                self.ipcon.enumerate()
                break
            except Error as e:
                log.error('Enumerate Error: ' + str(e.description))
                time.sleep(1)

    # Format value to fit on LCD with given pre and post digits
    def fmt(self, value, pre, post=2):
        v2, v1 = math.modf(value)
        v1 = str(int(v1))
        v2 = str(int(v2 * 10**post))

        num_space = (pre - len(v1))
        num_zero = (post - len(v2))

        return ' '*num_space + v1 + '.' + v2 + '0'*num_zero

    def cb_illuminance(self, illuminance):
        if self.lcd is not None:
            text = 'Illuminanc %s lx' % self.fmt(illuminance/10.0, 3)
            self.lcd.write_line(0, 0, text)
            log.info('Write to line 0: ' + text)

    def cb_humidity(self, humidity):
        if self.lcd is not None:
            text = 'Humidity %s %%' % self.fmt(humidity/10.0, 5)
            self.lcd.write_line(1, 0, text)
            log.info('Write to line 1: ' + text)
 
    def cb_air_pressure(self, air_pressure):
        if self.lcd is not None:
            text = 'Air Press %s mb' % self.fmt(air_pressure/1000.0, 4)
            self.lcd.write_line(2, 0, text)
            log.info('Write to line 2: ' + text)

            fmt_text = self.fmt(self.baro.get_chip_temperature()/100.0, 2)
            # \xDF == ° on LCD20x4 charset
            text = 'Temperature %s \xDFC' % fmt_text
            self.lcd.write_line(3, 0, text)
            log.info('Write to line 3: ' + text.replace('\xDF', '°'))

    def cb_enumerate(self, 
                     uid, connected_uid, position, hardware_version, 
                     firmware_version, device_identifier, enumeration_type):
        if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
            if device_identifier == LCD20x4.DEVICE_IDENTIFIER:
                try:
                    self.lcd = LCD20x4(uid, self.ipcon)
                    self.lcd.clear_display()
                    self.lcd.backlight_on()
                    log.info('LCD20x4 initialized')
                except Error as e:
                    log.error('LCD20x4 init failed: ' + str(e.description))
                    self.lcd = None
            elif device_identifier == AmbientLight.DEVICE_IDENTIFIER:
                try:
                    self.al = AmbientLight(uid, self.ipcon)
                    self.al.set_illuminance_callback_period(1000)
                    self.al.register_callback(self.al.CALLBACK_ILLUMINANCE, 
                                              self.cb_illuminance)
                    log.info('AmbientLight initialized')
                except Error as e:
                    log.error('AmbientLight init failed: ' + str(e.description))
                    self.al = None
            elif device_identifier == Humidity.DEVICE_IDENTIFIER:
                try:
                    self.hum = Humidity(uid, self.ipcon)
                    self.hum.set_humidity_callback_period(1000)
                    self.hum.register_callback(self.hum.CALLBACK_HUMIDITY, 
                                               self.cb_humidity)
                    log.info('Humidity initialized')
                except Error as e:
                    log.error('Humidity init failed: ' + str(e.description))
                    self.hum = None
            elif device_identifier == Barometer.DEVICE_IDENTIFIER:
                try:
                    self.baro = Barometer(uid, self.ipcon)
                    self.baro.set_air_pressure_callback_period(1000)
                    self.baro.register_callback(self.baro.CALLBACK_AIR_PRESSURE,
                                                self.cb_air_pressure)
                    log.info('Barometer initialized')
                except Error as e:
                    log.error('Barometer init failed: ' + str(e.description))
                    self.baro = None

    def cb_connected(self, connected_reason):
        if connected_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
            while True:
                try:
                    self.ipcon.enumerate()
                    break
                except Error as e:
                    log.error('Enumerate Error: ' + str(e.description))
                    time.sleep(1)

if __name__ == "__main__":
    log.info('Weather Station: Start')

    weather_station = WeatherStation()

    if sys.version_info < (3, 0):
        input = raw_input # Compatibility for Python 2.x
    input('Press key to exit\n')

    if weather_station.ipcon != None:
        weather_station.ipcon.disconnect()

    log.info('Weather Station: End')
