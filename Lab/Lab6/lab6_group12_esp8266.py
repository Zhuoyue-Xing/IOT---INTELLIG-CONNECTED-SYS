# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/23.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, SPI, ADC, RTC
import socket
import ssd1306
import time
import network
import urequests
import json
import lab6_group12_esp8266_dependence


# switch A is the function menu switch (short press) and confirm changed time switch (long press)
# switch B is the increasing number switch
# switch C is the moving and confirming function switch

'''
Current Time --A(Short)--> Menu --A(Short)--> Nothing Happen
					     		--A(Long)--> Back to Current Time 
					     		--B--> Move arrow and select function
							    --C--> Enter function 					--Function 1--> --A(Long)--> Save changed time and return to current time [Highly recommend way for press switch A]
							     														--A(Short)--> Back to menu ----> If you do this, please choose the Func 3 many times or long press Switch A, then program will back to normal
							     					 									--B--> Add number, step = 1
							     					 									--C--> Move cursor forward
							     					 					--Function 2--> --A(Long)--> Save alarm time and return to Current Time [Highly recommend way for press switch A]
							     														--A(Short)--> Back to menu ----> If you do this, please choose the Func 3 many times or long press Switch A, then program will back to normal
							     					 									--B--> Add number, step = 1
							     					 									--C--> Move cursor forward
							     					 					--Function 3--> Listening, wait for command --display weather--> show current weather on oled. Still listening and waitting for cmd
							     					 																--send tweets i like study--> if successfully sent, show tweets on oled; else show Failure on oled. Still listening and waitting for cmd
							     					 																--show current time--> return to Current Time
							     					 					--Function 4--> OLED turn off ---->OLED show 'Begin Now' ----> draw letter ----> OLED show 'Waitting', wait for AWS ----> OLED show result and hold for 1 sec ----> return to Menu
							     					 					--Function 5--> Back to Current Time
'''


''' pre setting about OLED screen buttons '''
# When the button A,B,C on OLED is pressed, OLED Pin A,B,C will generate a LOW voltage
switchA = Pin(2, Pin.IN) # GPIO#2 has a pullup resistor connected to it
switchB = Pin(13, Pin.IN) # GPIO#13 is the same as the MOSI 'SPI' pin
switchC = Pin(0, Pin.IN) # GPIO#0 does not have an internal pullup
# We have to give Pin0 Pin13 a outer pullup resistor, but be aware the maximum current drawn per pin is 12mA
# minimum resistor is 250 ohm
switchA.irq(trigger = Pin.IRQ_FALLING, handler = Interrupt) # use falling edge as interupt

''' pre setting about accelerator sensor '''
# The maximum SPI clock speed is 5 MHz with 100 pF maximum loading, and the timing scheme follows clock polarity (CPOL) = 1 and clock phase (CPHA) = 1
spi = SPI(-1, baudrate=100000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12), bits=8)
cs = Pin(16, Pin.OUT, value=1) # chip select
spi.init(baudrate=100000)

''' pre setting about OLED screen '''
i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
i2c.scan()
oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32

''' pre setting about alarm LED '''
redLED = Pin(15, Pin.OUT, value = 0)

''' pre setting about real time clock '''
rtc = RTC()


# ESP8266 as a server to listen and response and react to the commands
def ListenResponse(oled):
	# show listeing on OLED
	oled.fill(0)
	oled.text('Listening',80,22)
	oled.show()

	addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1] # Set web server port number to 80
	s = socket.socket()
	s.bind(addr) # Bind the socket to address
	s.listen(1) # Enable a server to accept connections
	print('listening on', addr)

	while True:	
		global interrupt_end
		if interrupt_end: return # if the voice command is 'show current time', return to the interrupt handler, i.e. menu

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
		except ValueError: # if not, give the response ahout not receiving a JSON POST
			response = "HTTP/1.1 501 Implemented\r\n\r\nBad"
		else: # if can be trasformed to JSON, give good response
			response = "HTTP/1.1 200 OK\r\n\r\nGood"
			lab6_group12_esp8266_dependence.WhatCommand(oled, cl_receive['Command']) # judge what's the command received
		
		# write to the port, i.e., give response
		cl.send(response)
		cl.close()



# interrupt handler
def Interrupt(pin):
	item = 0 # select which item in menu. 0-change time; 1-set alarm; 2-voice command; 3-gesture recognition; 4-current time
	global interrupt_end # a flag to end interrupt handler instantly
	interrupt_end = 0
	while 1:
		lab6_group12_esp8266_dependence.Refresh(oled, 10) # OLED refresh at 10Hz
		lab6_group12_esp8266_dependence.Menu(oled, item)
		oled.show()
		
		# in case user press the switch A in the menu, not cause another interrupt
		# also to cancel the interrupt caused by "back to the main menu and save change" in the change time screen
		if switchA.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchA):
			return

		# Change the arrow pointing, change the choosed item
		if switchB.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchB):
			item += 1
			if item > 4:
				item = 0

		# From the menu, go forward
		if switchC.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchC):
			# choosing the first function, i.e. change time
			if item == 0:	
				# print('1. Change time')
				# Storeage the current date and time to <int> list, year month day hour minute second
				changeTime = list(rtc.datetime())
				indexCT = 0

				while 1:
					lab6_group12_esp8266_dependence.Refresh(oled, 10) 			# clear OLED
					lab6_group12_esp8266_dependence.ShowTime(oled, changeTime) 	# show changed time
					if indexCT > 2:
						oled.text('_', 9+(indexCT-4)*23, 13) # show cursor in second line (time)
					else:
						oled.text('_', 24+indexCT*23, 2) # show cursor in first line (date)
					oled.show()

					# in the change time screen, switch A is LONG pressed, back to the main menu and save change
					# ATTENTION, short press switch A will lead to the interrupt handler, and show the menu.
					# long press switch A will first quit the second interrupt, and then exec the code here
					if switchA.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchA): 
						rtc.datetime(tuple(changeTime))
						break

					# in the change time screen, switch C is pressed, move the cursor
					if switchC.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchC): 
						indexCT += 1
						if indexCT == 3: indexCT +=1 # indexCT == 3 means week
						if indexCT > 6: indexCT = 0 # indexCT > 6 means msec
					
					# in the change time screen, switch B is pressed, add 1 to the value corresponding to the cursor
					if switchB.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchB): 
						changeTime[indexCT] += 1
						changeTime = lab6_group12_esp8266_dependence.Carry(changeTime)


			# choosing the second function, i.e. set alarm
			elif item == 1:			
				# print('2. Set alarm')
				# Storeage the current date and time to <int> list, year month day hour minute second
				changeTime = list(rtc.datetime())
				indexCT = 0

				while 1:
					lab6_group12_esp8266_dependence.Refresh(oled, 10) 			# clear OLED
					lab6_group12_esp8266_dependence.ShowTime(oled, changeTime) 	# show changed time
					if indexCT > 2:
						oled.text('_', 9+(indexCT-4)*23, 13) # show cursor in second line (time)
					else:
						oled.text('_', 24+indexCT*23, 2) # show cursor in first line (date)
					oled.show()

					# in the change time screen, switch A is LONG pressed, back to the main menu and save change
					# ATTENTION, short press switch A will lead to the interrupt handler, and show the menu.
					# long press switch A will first quit the second interrupt, and then exec the code here
					if switchA.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchA): 
						global alarmTime
						alarmTime = time.time() + (changeTime[4]-int(rtc.datetime()[4]))*3600+(changeTime[5]-int(rtc.datetime()[5]))*60+(changeTime[6]-int(rtc.datetime()[6]))
						break

					# in the change time screen, switch C is pressed, move the cursor
					if switchC.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchC): 
						indexCT += 1
						if indexCT == 3: indexCT +=1 # indexCT == 3 means week
						if indexCT > 6: indexCT = 0 # indexCT > 6 means msec
							
					
					# in the change time screen, switch B is pressed, add 1 to the value corresponding to the cursor
					if switchB.value() == 0 and lab6_group12_esp8266_dependence.Debounce(switchB): 
						changeTime[indexCT] += 1
						changeTime = lab6_group12_esp8266_dependence.Carry(changeTime)
			
			# choosing the third function, i.e. Receive and process voice commands 
			elif item == 2:
				ListenResponse(oled)
				if interrupt_end: return # if the voice command is 'show current time', return to the main function

			# choosing the forth function, i.e. Gesture recognition
			elif item == 3:
				# When the OLED display Begin Now, please do the gesture
				oled.fill(0) # clear the OLED
				oled.show()
				time.sleep_ms(1000)
				oled.text('Begin Now',0,0)
				oled.show()
				# Send one letter data in sequence to AWS
				for seq in range(20):
					time.sleep_ms(100)
					accRaw = lab6_group12_esp8266_dependence.SPI_read(spi, cs, b'\xF2', 6)   # Add=0x32, read to accRaw
					print(accRaw[0],'\t',accRaw[1],'\t',accRaw[2],'\t',accRaw[3],'\t',accRaw[4],'\t',accRaw[5])
					lab6_group12_esp8266_dependence.SendAWS("predict",0,seq,accRaw[0],accRaw[1],accRaw[2],accRaw[3],accRaw[4],accRaw[5])
				# Show waitting on OLED, wait for predict result
				oled.fill(0) # clear the OLED
				oled.text('Waitting',0,0)
				oled.show()
				# Using JSON POST to send command about doing predict in AWS and wait for AWS's response (predict result)
				headers = {"Content-Type": "application/json; charset=UTF-8"}
				url = "http://3.87.68.197:8099/predict/order/post"
				request_data = {'order':'predict'}
				# Catch the response and find the predict result in it
				predictResult = json.loads(urequests.post(url=url, data=json.dumps(request_data), headers=headers).text)['result']
				# Show predict result on OLED
				oled.fill(0) # clear the OLED
				oled.text(predictResult,0,0)
				oled.show()
				print('Predict Result is: ', predictResult)

				time.sleep_ms(1000) # maintain the oled display before return to menu


			# choose the fifth function i.e. return to the current time, quit interrupt handler
			else:
				return









if __name__ == '__main__':
	
	''' initial the ESP8266 and peripheral chips '''
	lab6_group12_esp8266_dependence.ADXL345_init(spi, cs) # initial the ADXL345

	lab6_group12_esp8266_dependence.ConnectWIFI('Columbia University','') # connect esp8266 to a router

	lab6_group12_esp8266_dependence.SetCurtTime(rtc) # initiate the real time clock as the current time, (need wifi connection)

	''' pre setting about global variables '''
	global alarmTime
	alarmTime = time.time() -1		# initial alarmtime = -1, to ensure the alarm not burst when program starts

	while True:		# smart watch basic function: show current time
		lab6_group12_esp8266_dependence.ShowTime(oled, rtc.datetime())
		oled.show()
		lab6_group12_esp8266_dependence.Refresh(oled, 10) # OLED refresh at 10Hz
		lab6_group12_esp8266_dependence.ChangeBright(oled)

		if (alarmTime - time.time()) == 0:
			redLED.value(1)
		if (alarmTime - time.time()) == -3:
			redLED.value(0)






