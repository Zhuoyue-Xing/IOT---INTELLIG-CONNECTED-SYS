# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/2.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import Pin, I2C
import ssd1306
import time
import network
# import socket
import urequests
import json


# ESP8266 connects to a router
def ConnectWIFI(essid, key):
	import network
	sta_if = network.WLAN(network.STA_IF) 	# config a station object
	if not sta_if.isconnected():			# if the connection is not established
		print('connecting to network...')
		sta_if.active(True)					# activate the station interface
		sta_if.connect(essid, key)	# connect to WiFi network
		while not sta_if.isconnected():
			print('connecting')
			pass
		print('network config:', sta_if.ifconfig())	# check the IP address
		# ap_if.active(False)					# disable the access-point interface
	else:
		print('network config:', sta_if.ifconfig()) # IP address, subnet mask, gateway and DNS server


# get the mac address of ESP8266
def GetMacAdd():
	sta_if = network.WLAN(network.STA_IF)
	mac = [] # store the seperate mac address
	# convert betaarray to hex str list
	for i in range(6):
		mac.append(hex(sta_if.config('mac')[i]).replace('0x',''))
	# returns a string like bc:dd:c2:14:68:77
	return "{:0>2s}:{:0>2s}:{:0>2s}:{:0>2s}:{:0>2s}:{:0>2s}".format(mac[0], mac[1], mac[2], mac[3], mac[4], mac[5])


# # HTTP GET request
# def HTTP_GET(url):
# 	_, _, host, path = url.split('/', 3)
# 	addr = socket.getaddrinfo(host, 80)[0][-1]
# 	s = socket.socket()
# 	s.connect(addr)
# 	s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
# 	while True:
# 		data = s.recv(100)
# 		if data:
# 			print(str(data, 'utf8'), end='')
# 		else:
# 			break
# 	s.close()


# HTTP JSON POST request, from Google Geolocation API get current location.
def GetLocation():
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
	# returns a json string
	return urequests.post(url, data=json.dumps(request_data), headers=headers).text


# HTTP GET request, from OpenWeather API get current weather
def GetWeather(lat, lng):
	url = "https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=4d34fa16a400db838cd70c2f138dd831".format(latitude = str(lat), longitude = str(lng))
	# returns a json string
	return urequests.get(url).text


# try to show weather on OLED, in case we miss some data
def ShowWeather(weatherDic, oled):
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
		pressure = weatherDic['main']['pressure']				# Atmospheric pressure(on the sea level), hPa
	except KeyError:
		print('pressure miss')
	else:
		print('Pressure: {} hPa'.format(pressure))
		# oled.text('hPa'.format(pressure), 20, 11)
	
	try: 
		humidity = weatherDic['main']['humidity']				# Humidity, %
	except KeyError:
		print('humidity miss')
	else:
		print('Humidity: {} %'.format(humidity))
		# oled.text('{} %'.format(humidity), 40, 11)
	
	try:
		visibility = weatherDic['visibility']					# Visibility, meter
	except KeyError:
		print('visibility miss')
	else:
		print('Visibility: {} m'.format(visibility))
		# oled.text('{} m'.format(visibility), 60, 11)
	
	try: 
		windspeed = weatherDic['wind']['speed']				# Wind speed. Unit Default: meter/sec
	except KeyError:
		print('wind speed miss')
	else:
		print('Wind Speed: {} m/s'.format(windspeed))
		# oled.text('{} m/s'.format(windspeed), 0, 22)
	
	try: 
		winddeg = weatherDic['wind']['deg']					# Wind direction, degrees
	except KeyError:
		print('wind degree miss')
	else:
		print('Wind Degree: {}'.format(winddeg))
		# oled.text('{}'.format(winddeg), 40, 22)
	
	try: 
		city = weatherDic['name']								# City name
	except KeyError:
		print('city name miss')
	else:
		print('City: {}'.format(city))
		oled.text('{}'.format(city), 0, 22)



if __name__ == '__main__':
	i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
	i2c.scan()
	oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
	# runTime = time.time() + 60 # program life time
	
	ConnectWIFI('Columbia University','') # connect esp8266 to a router
	
	locationDic = json.loads(GetLocation()) # get the current location, and transfer the json string to json dictionary

	lat = locationDic['location']['lat'] # latitude
	lng = locationDic['location']['lng'] # longitude

	weatherDic = json.loads(GetWeather(lat, lng)) # get the current weather, and transfer the json string to json dictionary
	
	oled.fill(0)
	ShowWeather(weatherDic, oled)
	oled.show()
	









