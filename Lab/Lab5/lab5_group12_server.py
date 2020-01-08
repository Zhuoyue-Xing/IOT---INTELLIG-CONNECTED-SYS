# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/13.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.
from machine import Pin, I2C, RTC, Timer
import socket
import ssd1306
import time
import network
import urequests
import json

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


# Get Current Time and Set ESP8266 Time to current time
def SetCurtTime():
	# World Clock API
	url = "http://worldclockapi.com/api/json/est/now"
	webTime = json.loads(urequests.get(url).text) 	# returns a json string, convert it to json
	
	webTime = webTime['currentDateTime'].split('T') # currentDataTime string as 2019-10-13T15:05-04:00
	date = list(map(int, webTime[0].split('-'))) 	# extract time numbers
	time = list(map(int, webTime[1].split('-')[0].split(':')))
	
	timeTuple = (date[0], date[1], date[2], 0, time[0], time[1], 0, 0) # (year, month, day, weekday, hours, minutes, seconds, mseconds)
	rtc.datetime(timeTuple) # set a specific date and time
	# print(rtc.datetime())


# Show current time on OLED
def OLEDShowTime():
	weekday = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
	# Storeage the current date and time to <int> list
	timeList = list(map(int, rtc.datetime()))
	# Covert <int> list to <str>
	dateStr = "{:0>4d}".format(timeList[0])+'-'+"{:0>2d}".format(timeList[1])+'-'+"{:0>2d}".format(timeList[2])
	# weekStr = weekday[timeList[3]]
	timeStr = "{:0>2d}".format(timeList[4])+':'+"{:0>2d}".format(timeList[5])+':'+"{:0>2d}".format(timeList[6])
	# Put string to OLED
	oled.text(dateStr, 0, 0)	# (message, x, y, color)
	# oled.text(weekStr, 0, 11)
	oled.text(timeStr, 0, 22) 


# OLED show whether ESP8266 received commands
def OLEDRecvComd(received):
	if received:
		oled.text('RCVD', 80, 22) # Received the correct command
	else:
		oled.text('MISS', 80, 22) # Received a command ,but NOT a correct one


# Judge the Command received
def WhatCommand(cmd):
	# cmd is Command in string, like: "turn on display"
	global FLAG_True_Comd 	# Flag about whether it is a right command
	global FLAG_Display_On	# Flag about whetehr OLED can display things
	global FLAG_Show_Time	# Flag about whether the current time is shown on OLED

	if cmd == 'turn on display':
		FLAG_True_Comd = 1
		FLAG_Display_On = 1
	elif cmd == 'turn off display':
		FLAG_True_Comd = 1
		FLAG_Display_On = 0
	elif cmd == 'show current time':
		FLAG_True_Comd = 1
		FLAG_Show_Time = 1
	elif cmd == 'close current time':
		FLAG_True_Comd = 1
		FLAG_Show_Time = 0
	else:
		FLAG_True_Comd = 0				# not a right command


# Judge what to display on OLED, and display OLED with Timer
def WhatShowOLED(p):
	global FLAG_True_Comd 	# Flag about whether it is a right command
	global FLAG_Display_On	# Flag about whetehr OLED can display things
	global FLAG_Show_Time	# Flag about whether the current time is shown on OLED
	global showComd
	if FLAG_Display_On: 	# able to display OLED
		oled.text(showComd,0,11)
		OLEDRecvComd(FLAG_True_Comd)	# whether it's a right command, show on OLED
		if FLAG_Show_Time:				# show time on OLED if be able to
			OLEDShowTime()
		oled.show()			# display text
	else:
		oled.fill(0)		# fill OLED with black
		oled.show()			# display all black

	oled.fill(0)			# refresh, remove residue


# ESP8266 as a server to listen and response
def ListenResponse():
	# a response ahout receiving a right JSON POST request
	goodHTML = """<!DOCTYPE html>
	<html>
		<head> <title>Good Command</title> </head>
		<body> <h1>The command from you is received by ESP8266</h1></body>
	</html>
	"""
	# a response ahout NOT receiving a JSON POST request
	badHTML = """<!DOCTYPE html>
	<html>
		<head> <title>Bad Command</title> </head>
		<body> <h1>The command from you is NOT a JSON format</h1></body>
	</html>
	"""

	addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1] # Set web server port number to 80
	s = socket.socket()
	s.bind(addr) # Bind the socket to address
	s.listen(1) # Enable a server to accept connections
	print('listening on', addr)

	global FLAG_True_Comd 	# Flag about whether it is a right command
	global FLAG_Display_On	# Flag about whetehr OLED can display things
	global FLAG_Show_Time	# Flag about whether the current time is shown on OLED
	FLAG_True_Comd = 0
	FLAG_Display_On = 0
	FLAG_Show_Time = 0

	while True:
		print("FLAG_True_Comd", FLAG_True_Comd)
		print("FLAG_Display_On", FLAG_Display_On)
		print("FLAG_Show_Time", FLAG_Show_Time)

		# accept the connect to 80 port
		cl, addr = s.accept()
		print('client connected from', addr)

		# ESP8266 listen from the port
		# The client terminal instruction should be like:
		# curl -H "Content-Type:application/json" -X POST -d '{"Command":"turn on display"}' http://192.168.50.100:80
		cl_receive = cl.recv(500).decode("utf-8").split("\r\n")[-1] # get the whole request and try to split it
		
		try: # if the request is in a JSON POST format
			cl_receive = json.loads(cl_receive) # convert the json string to json
			print(cl_receive['Command'])
			global	showComd
			showComd = cl_receive['Command']
		except ValueError: # if not, give the response ahout not receiving a JSON POST
			response = "HTTP/1.1 501 Implemented\r\n\r\nBad"
		else: # if can be trasformed to JSON, give good response
			response = "HTTP/1.1 200 OK\r\n\r\nGood"
			WhatCommand(cl_receive['Command']) # judge what's the command received
		
		# write to the port, i.e., give response
		cl.send(response)
		cl.close()
		


if __name__ == '__main__':
	i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
	i2c.scan()
	oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
	rtc = RTC()
	tim = Timer(-1)
	tim.init(period=100, mode=Timer.PERIODIC, callback=WhatShowOLED)
	ConnectWIFI('Columbia University','') # connect esp8266 to a router
	SetCurtTime()
	ListenResponse() # Show ESP8266 Pins to test server
	

	

	