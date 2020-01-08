# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/30.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, SPI, ADC, RTC
import socket
import ssd1306
import time
import network
import urequests
import json


def SPI_write(spi, cs, address, data):
	cs.value(0)
	spi.write(address)
	spi.write(data)
	cs.value(1)


def SPI_read(spi, cs, address, nbyte):
	cs.value(0)
	spi.write(address)
	b = spi.read(nbyte)
	cs.value(1)
	return b


def ADXL345_init(spi, cs):
	SPI_write(spi, cs, b'\x6C', b'\x0A')
	SPI_write(spi, cs, b'\x6D', b'\x28')
	SPI_write(spi, cs, b'\x6E', b'\xFF')
	SPI_write(spi, cs, b'\x71', b'\x08')
	SPI_write(spi, cs, b'\x78', b'\x80')


def ShowTime(oled, timeTuple):
	dateStr = "{:0>4d}-{:0>2d}-{:0>2d}".format(int(timeTuple[0]), int(timeTuple[1]), int(timeTuple[2]))
	timeStr = "{:0>2d}:{:0>2d}:{:0>2d}".format(int(timeTuple[4]), int(timeTuple[5]), int(timeTuple[6]))
	oled.text(dateStr, 0, 0)
	oled.text(timeStr, 0, 11) 


def Debounce(pin):
	currentValue = pin.value()
	time.sleep_ms(20)
	return pin.value() == currentValue


def Menu(oled, item):
	if item < 3:
		oled.text('>', 0, int(item)*10+0)
		oled.text('1. Change Time', 7, 0)
		oled.text('2. Set Alarm', 7, 11)
		oled.text('3. Voice Cmd', 7, 22)
	else:
		oled.text('>', 0, int(item-3)*10+0)
		oled.text('4. Gestr Recg', 7, 0)
		oled.text('5. Curt Time', 7, 11)

def Refresh(oled, rate):
	time.sleep_ms(int(1000/rate))
	oled.fill(0)

# def ChangeBright(oled):
# 	lightSensor = ADC(0)
# 	oled.contrast(255-int(lightSensor.read()*255/1024))

def DisplayWeather(oled):
	headers = {"Content-Type": "application/json; charset=UTF-8"}
	url = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCIGgXSrXj0O3nbjN7sf15kskcOcZWwm9o"
	request_data = {
		"considerIp": "true",
		"wifiAccessPoints": [
		{
			"macAddress": "bc:dd:c2:14:68:77",
			"signalStrength": -43,
			"signalToNoiseRatio": 0
		}
		]
	}
	locationDic = json.loads(urequests.post(url, data=json.dumps(request_data), headers=headers).text)
	url = "https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=4d34fa16a400db838cd70c2f138dd831".format(latitude = str(locationDic['location']['lat']), longitude = str(locationDic['location']['lng']))
	weatherDic = json.loads(urequests.get(url).text)
	weather = weatherDic['weather'][0]['main']
	oled.text(weather, 0, 0)
	temperature = weatherDic['main']['temp'] - 273.15
	oled.text('{} C'.format(temperature), 0, 11)


def SendTweets(str):
	url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=7DNNLMJWMEY6XNJP&status={}".format(str.replace(' ', '%20'))
	return urequests.post(url).text


def ConnectWIFI(essid, key):
	sta_if = network.WLAN(network.STA_IF)
	if not sta_if.isconnected():
		print('connecting to network...')
		sta_if.active(True)
		sta_if.connect(essid, key)
		while not sta_if.isconnected():
			print('connecting')
			pass
	print('network config:', sta_if.ifconfig())


def SendAWS(label, ID, seq, x1, x2, y1, y2, z1, z2):
	headers = {"Content-Type": "application/json; charset=UTF-8"}
	url = "http://3.87.68.197:8099/predict/post"
	request_data = {
	"label":label,
	"ID":ID,
	"seq":seq, 
	"x1":x1,
	"x2":x2,
	"y1":y1,
	"y2":y2,
	"z1":z1,
	"z2":z2
	}
	return urequests.post(url, data=json.dumps(request_data), headers=headers).text

