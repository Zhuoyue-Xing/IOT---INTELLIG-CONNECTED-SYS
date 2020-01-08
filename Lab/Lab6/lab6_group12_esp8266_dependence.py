# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/30.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, SPI, ADC, RTC
import socket
import ssd1306
import time
import network
import urequests
import json

''' pre defination about the week display and time-setting carry '''
weekday = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
monthdays = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

# Get Current Time and Set ESP8266 Time to current time
def SetCurtTime(rtc):
	# World Clock API
	url = "http://worldclockapi.com/api/json/est/now"
	# returns a json string, convert it to json, get the currentDataTime string as 2019-10-13T15:05-04:00
	webTime = json.loads(urequests.get(url).text)['currentDateTime'].split('T')
	
	date = list(map(int, webTime[0].split('-'))) 	# extract time numbers
	time = list(map(int, webTime[1].split('-')[0].split(':')))
	
	rtc.datetime((date[0], date[1], date[2], 0, time[0], time[1], 0, 0)) # set a specific date and time
	# (year, month, day, weekday, hours, minutes, seconds, mseconds)
	# weekday is automatically computed and value=0-6
	# 2019.13 => 2020.1 automatically
	# print(rtc.datetime())


# Any place to show time
def ShowTime(oled, timeTuple):
	dateStr = "{:0>4d}-{:0>2d}-{:0>2d}".format(int(timeTuple[0]), int(timeTuple[1]), int(timeTuple[2]))
	timeStr = "{:0>2d}:{:0>2d}:{:0>2d}".format(int(timeTuple[4]), int(timeTuple[5]), int(timeTuple[6]))
	oled.text(dateStr, 0, 0)
	oled.text(timeStr, 0, 11)
	oled.text(weekday[int(timeTuple[3])], 0, 22)


# debouncing
# Return 1: equal, means NOT a bounce and the key is stable now
# Return 0: NOT equal, means it's just a bounce
def Debounce(pin):
	currentValue = pin.value()				# once called, read a value and record as current value
	time.sleep_ms(20)						# after 20ms, which means waiting for the bouncing end
	return pin.value() == currentValue		# check if the pin value equals to that 20ms ago


# Show the function choose menu
def Menu(oled, item):
	if item < 3: # first page
		oled.text('>', 0, int(item)*10+0) 	# show the arrow
		oled.text('1. Change Time', 7, 0)	# show the menu content
		oled.text('2. Set Alarm', 7, 11)
		oled.text('3. Voice Cmd', 7, 22)
	else: # second page
		oled.text('>', 0, int(item-3)*10+0) # show the arrow
		oled.text('4. Gestr Recg', 7, 0)	# show the menu content
		oled.text('5. Curt Time', 7, 11)




# refresh the OLED, remove residue
def Refresh(oled, rate):
	time.sleep_ms(int(1000/rate))	# every 1000/rate ms
	oled.fill(0)				# To fill the entire screen with black, that is, refresh the screen


# change the brightness of OLED
def ChangeBright(oled):
	lightSensor = ADC(0) 						# create ADC object on ADC pin
	# Class 'SSD1306_I2C' inherits from Parent Class 'SSD1306', so we can use contrast function
	oled.contrast(255-int(lightSensor.read()*255/1024))	# read value, 0-1024, turn to 0-255


# In the change time screen, to ensure right carry
def Carry(changeTime):
	if changeTime[6] > 59: # second carry to minute
		changeTime[6] = changeTime[6] - 60
		changeTime[5] += 1
	if changeTime[5] > 59: # minute carry to hour
		changeTime[5] = changeTime[5] - 60
		changeTime[4] += 1
	if changeTime[4] > 23: # hour carry to day
		changeTime[4] = changeTime[4] - 24
		changeTime[2] += 1
	if changeTime[2] > monthdays[changeTime[1]]: # day carry to month
		changeTime[2] =  changeTime[2] - monthdays[changeTime[1]]
		changeTime[1] += 1
	if changeTime[1] > 12: # month carry to year
		changeTime[1] = changeTime[1] - 12
		changeTime[0] += 1
	return changeTime


# get the mac address of ESP8266
def GetMacAdd():
	sta_if = network.WLAN(network.STA_IF)
	mac = [] # store the seperate mac address
	# convert betaarray to hex str list
	for i in range(6):
		mac.append(hex(sta_if.config('mac')[i]).replace('0x',''))
	# returns a string like bc:dd:c2:14:68:77
	return "{:0>2s}:{:0>2s}:{:0>2s}:{:0>2s}:{:0>2s}:{:0>2s}".format(mac[0], mac[1], mac[2], mac[3], mac[4], mac[5])


# HTTP JSON POST request, from Google Geolocation API get current location.
def DisplayWeather(oled):
	headers = {"Content-Type": "application/json; charset=UTF-8"}
	url = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCIGgXSrXj0O3nbjN7sf15kskcOcZWwm9o"
	request_data = {
		"considerIp": "true",
		"wifiAccessPoints": [
		{
			"macAddress": GetMacAdd(),
			"signalStrength": -43,
			"signalToNoiseRatio": 0
		}
		]
	}
	# response a json string
	locationDic = json.loads(urequests.post(url, data=json.dumps(request_data), headers=headers).text)
	lat = locationDic['location']['lat'] # latitude
	lng = locationDic['location']['lng'] # longitude
	# HTTP GET request, from OpenWeather API get current weather
	url = "https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=4d34fa16a400db838cd70c2f138dd831".format(latitude = str(lat), longitude = str(lng))
	# response a json string
	weatherDic = json.loads(urequests.get(url).text)

	# try to show weather on OLED, in case we miss some data
	try:
		weather = ['' for i in range(len(weatherDic['weather']))]
		for i in range(len(weather)):
			weather[i] = weatherDic['weather'][i]['main'] 		# Group of weather parameters (Rain, Snow, Extreme etc.)
	except KeyError:
		print('weather miss')
	else:
		print('Weather Condition: {}'.format(weather))
		string = ' '.join(weather)
		print(string)
		oled.text(string, 0, 0)
	
	try: 
		temperature = weatherDic['main']['temp'] - 273.15		# Temperature. Unit Default: Kelvin
	except KeyError:
		print('temperature miss')
	else:
		print('Temperature: {} C'.format(temperature))
		oled.text('{} C'.format(temperature), 0, 11)
	
	try: 
		city = weatherDic['name']								# City name
	except KeyError:
		print('city name miss')
	else:
		print('City: {}'.format(city))
		oled.text('{}'.format(city), 0, 22)


# Send tweets through thingspeak twitter api
def SendTweets(str):
	url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=7DNNLMJWMEY6XNJP&status={}".format(str.replace(' ', '%20'))
	return urequests.post(url).text


# Judge the Command received
def WhatCommand(oled, cmd):
	# cmd is Command in string, like: "display weather"
	# "display weather"
	# "show current time"
	# "send tweets i like study"
	global interrupt_end # a flag to end interrupt handler instantly

	if cmd == 'display weather':
		oled.fill(0)
		DisplayWeather(oled)
		oled.text('Listening',80,22)
		oled.show()
	elif cmd == 'show current time':
		interrupt_end = 1

	if cmd.find('tweets') > (-1):
		twt = cmd.split('tweets ')[1]
		if SendTweets(twt):
			oled.fill(0)
			oled.text(twt,0,0)
			oled.text('Listening',80,22)
			oled.show()
		else:
			oled.fill(0)
			oled.text('Send Failure',0,0)
			oled.text('Listening',80,22)
			oled.show()

# to send accelerator data to AWS EC2 Server
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
	# returns a json string
	return urequests.post(url, data=json.dumps(request_data), headers=headers).text


# ESP8266 connects to a router
def ConnectWIFI(essid, key):
	import network
	sta_if = network.WLAN(network.STA_IF)   # config a station object
	if not sta_if.isconnected():            # if the connection is not established
		print('connecting to network...')
		sta_if.active(True)                 # activate the station interface
		sta_if.connect(essid, key)  # connect to WiFi network
		while not sta_if.isconnected():
			print('connecting')
			pass
		print('network config:', sta_if.ifconfig()) # check the IP address
		# ap_if.active(False)                   # disable the access-point interface
	else:
		print('network config:', sta_if.ifconfig()) # IP address, subnet mask, gateway and DNS server

# SPI write data, MOSI
def SPI_write(spi, cs, address, data):
	# cs <Pin obj> chip select
	# address <bytearray> address of register to write, should + 0x40 to set first two bits '01'
	# data <bytearray> data to write into register
	cs.value(0) # enable chip
	spi.write(address)
	spi.write(data)
	cs.value(1) # disable chip

# SPI read data, MISO
def SPI_read(spi, cs, address, nbyte):
	# cs <Pin obj> chip select
	# address <bytearray> address of register to read, should + 0xC0 to set first two bits '11'
	# nbyte: read nbyte bytes on MISO
	cs.value(0) # enable chip
	spi.write(address)
	b = spi.read(nbyte)
	cs.value(1) # disable chip
	return b

# initial the ADXL345
def ADXL345_init(spi, cs):
	SPI_write(spi, cs, b'\x6C', b'\x0A')  # Add=0x2C Data=00001010 Data rate and power mode control..
	SPI_write(spi, cs, b'\x6D', b'\x28')  # Add=0x2D Data=00101000 Power-saving features control.
	SPI_write(spi, cs, b'\x6E', b'\xFF')  # Add=0x2E Data=11111111 Interrupt enable control.

	SPI_write(spi, cs, b'\x71', b'\x08')  # Add=0x31 Data=00001000  Data format control. A value of 0 in the INT_INVERT bit sets the interrupts to active high.
	SPI_write(spi, cs, b'\x78', b'\x80')  # Add=0x38 Data=10000000 FIFO control.


