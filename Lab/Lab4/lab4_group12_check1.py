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



if __name__ == '__main__':
	i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
	i2c.scan()
	oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
	# runTime = time.time() + 60 # program life time
	
	ConnectWIFI('Columbia University','') # connect esp8266 to a router
	
	locationDic = json.loads(GetLocation()) # get the current location, and transfer the json string to json dictionary

	lat = locationDic['location']['lat'] # latitude
	lng = locationDic['location']['lng'] # longitude

	oled.fill(0)
	oled.text('lat: {}'.format(lat), 0, 0)
	oled.text('lon: {}'.format(lng), 0, 11)
	oled.show()

	









