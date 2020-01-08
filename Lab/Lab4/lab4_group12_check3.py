# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/4.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

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

# Send tweet through thingspeak twitter api
def SendTweet():
	url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=7DNNLMJWMEY6XNJP&status=Code%20works%0ADo%20NOT%20touch%20it"
	return urequests.post(url).text


if __name__ == '__main__':
	
	ConnectWIFI('Columbia University','') # connect esp8266 to a router

	print(SendTweet())





