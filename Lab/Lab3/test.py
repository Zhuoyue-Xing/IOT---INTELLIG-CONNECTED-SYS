# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/29.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, ADC
import ssd1306
import time


i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
i2c.scan()
oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
redLED = Pin(15, Pin.OUT, value = 0)

# weekday = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
# monthdays = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

# When the button A,B,C on OLED is pressed, OLED Pin A,B,C will generate a LOW voltage
switchA = Pin(2, Pin.IN) # GPIO#2 has a pullup resistor connected to it
switchB = Pin(13, Pin.IN) # GPIO#13 is the same as the MOSI 'SPI' pin
switchC = Pin(0, Pin.IN) # GPIO#0 does not have an internal pullup
# We have to give Pin0 Pin13 a outer pullup resistor, but be aware the maximum current drawn per pin is 12mA
# minimum resistor is 250 ohm

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
							     					 					--Function 2--> --A(Long)--> Save alarm time and return to current time [Highly recommend way for press switch A]
							     														--A(Short)--> Back to menu ----> If you do this, please choose the Func 3 many times or long press Switch A, then program will back to normal
							     					 									--B--> Add number, step = 1
							     					 									--C--> Move cursor forward
							     					 					--Function 3--> Back to current time

'''


rtc = machine.RTC() # real time clock
rtc.datetime((2019, 9, 8, 1, 4, 7, 2, 0)) # initialize, set a specific date and time
# (year, month, day, weekday, hours, minutes, seconds, mseconds)
# weekday is automatically computed and value=0-6
# 2019.13 => 2020.1 automatically

# The first function - show current time
def FuncSCT():
	# Storeage the current date and time to <int> list
	# dateList = [int(rtc.datetime()[0]), int(rtc.datetime()[1]), int(rtc.datetime()[2]), int(rtc.datetime()[3])]
	timeList = [int(rtc.datetime()[4]), int(rtc.datetime()[5]), int(rtc.datetime()[6])]
	# Covert <int> list to <str>
	# dateStr = "{:0>4d}".format(dateList[0])+'-'+"{:0>2d}".format(dateList[1])+'-'+"{:0>2d}".format(dateList[2])
	# weekStr = weekday[dateList[3]]
	timeStr = "{:0>2d}".format(timeList[0])+':'+"{:0>2d}".format(timeList[1])+':'+"{:0>2d}".format(timeList[2])
	# Put string to OLED
	# oled.text(dateStr, 0, 0)	# (message, x, y, color)
	# oled.text(weekStr, 0, 11)
	oled.text(timeStr, 0, 22) 
	# alarm count down
	global alarmTime
	oled.text(str(alarmTime - time.time()), 64, 11)

# debouncing
# Return 1: equal, means NOT a bounce and the key is stable now
# Return 0: NOT equal, means it's just a bounce
def Debounce(pin):
	currentValue = pin.value()				# once called, read a value and record as current value
	time.sleep_ms(20)						# after 20ms, which means waiting for the bouncing end
	return pin.value() == currentValue		# check if the pin value equals to that 20ms ago

# In the function choose menu, show the arrow
def Arrow(item):
	oled.text('>', 0, int(item)*10+0)

# Show the function choose menu
def Menu():
	oled.text('1. Change time', 7, 0)	# (message, x, y, color)
	oled.text('2. Set alarm', 7, 11)
	oled.text('3. Curt time', 7, 22)

# In the set time function, show the cursor under text
def Cursor(x,y):
	oled.text('_', x, y)

# In the set time function, show the changed time
def FuncChgT(changeTime):
	# Covert <int> list to <str>
	# dateStr = "{:0>4d}".format(changeTime[0])+'-'+"{:0>2d}".format(changeTime[1])+'-'+"{:0>2d}".format(changeTime[2])
	timeStr = "{:0>2d}".format(changeTime[0])+':'+"{:0>2d}".format(changeTime[1])+':'+"{:0>2d}".format(changeTime[2])
	# Put string to OLED
	# oled.text(dateStr, 0, 0)	# (message, x, y, color)
	oled.text(timeStr, 0, 11) 

# refresh the OLED, remove residue
def Refresh(rate):
	time.sleep_ms(int(1000/rate))	# every 1000/rate ms
	oled.fill(0)				# To fill the entire screen with black, that is, refresh the screen

# In the change time screen, to ensure right carry
def Carry(changeTime):
	if changeTime[2] > 59: # second carry to minute
		changeTime[2] = changeTime[2] - 60
		changeTime[1] += 1
	if changeTime[1] > 59: # minute carry to hour
		changeTime[1] = changeTime[1] - 60
		changeTime[0] += 1
	if changeTime[0] > 23: # hour carry to day
		changeTime[0] = changeTime[0] - 24
		# changeTime[2] += 1
	# if changeTime[2] > monthdays[changeTime[1]]: # day carry to month
	# 	changeTime[2] =  changeTime[2] - monthdays[changeTime[1]]
	# 	changeTime[1] += 1
	# if changeTime[1] > 12: # month carry to year
	# 	changeTime[1] = changeTime[1] - 12
	# 	changeTime[0] += 1
	return changeTime


# interrupt handler
def Interrupt(pin):
	oled.fill(0) # clear
	item = 0 # select which item in menu. 0-first item; 1-second item; 2-current time
	while 1:
		Refresh(10) # OLED refresh at 10Hz
		Arrow(item)
		Menu()
		oled.show()
		
		# in case user press the switch A in the menu, not cause another interrupt
		# also to cancel the interrupt caused by "back to the main menu and save change" in the change time screen
		if switchA.value() == 0:
			if Debounce(switchA):
				return

		# Change the arrow pointing, change the choosed item
		if switchB.value() == 0:
			if Debounce(switchB):
				item += 1
				if item > 2:
					item = 0

		# From the menu, go forward
		if switchC.value() == 0:
			if Debounce(switchC):
				# choosing the first function
				if item == 0:	
					# print('1. Change time')
					# Storeage the current date and time to <int> list, year month day hour minute second
					changeTime = [int(rtc.datetime()[4]), int(rtc.datetime()[5]), int(rtc.datetime()[6])]
					indexCT = 0

					while 1:
						Refresh(10) 			# clear OLED
						FuncChgT(changeTime) 	# show changed time
						
						Cursor(9+indexCT*23, 13)	# show cursor in second line (time)
						
						oled.show()

						# in the change time screen, switch A is LONG pressed, back to the main menu and save change
						# ATTENTION, short press switch A will lead to the interrupt handler, and show the menu.
						# long press switch A will first quit the second interrupt, and then exec the code here
						if switchA.value() == 0:
							if Debounce(switchA): 
								rtc.datetime((2019, 9, 8, 1, changeTime[0], changeTime[1], changeTime[2], 0))
								break

						# in the change time screen, switch C is pressed, move the cursor
						if switchC.value() == 0: 
							if Debounce(switchC): 
								indexCT += 1
								if indexCT > 2: indexCT = 0 # only have 6 parameters to change
						
						# in the change time screen, switch B is pressed, add 1 to the value corresponding to the cursor
						if switchB.value() == 0:
							if Debounce(switchB): 
								changeTime[indexCT] += 1
								changeTime = Carry(changeTime)


				# choosing the second function
				if item == 1:			
					# print('2. Set alarm')
					# Storeage the current date and time to <int> list, year month day hour minute second
					changeTime = [int(rtc.datetime()[4]), int(rtc.datetime()[5]), int(rtc.datetime()[6])]
					indexCT = 0

					while 1:
						Refresh(10) 			# clear OLED
						FuncChgT(changeTime) 	# show changed time
						
						Cursor(9+indexCT*23, 13)	# show cursor in second line (time)
						oled.show()

						# in the change time screen, switch A is LONG pressed, back to the main menu and save change
						# ATTENTION, short press switch A will lead to the interrupt handler, and show the menu.
						# long press switch A will first quit the second interrupt, and then exec the code here
						if switchA.value() == 0:
							if Debounce(switchA): 
								global alarmTime

								# # year can't carry
								# yearChangeSecs = (changeTime[0]-int(rtc.datetime()[0]))*31536000

								# if month carry to year, first translate it to changed days
								# monthChangeSecs = 0
								# if changeTime[1]-int(rtc.datetime()[1]) > 0: # Not carry to another year
								# 	for i in range(changeTime[1]-int(rtc.datetime()[1])):
								# 		monthChangeSecs += monthdays[int(rtc.datetime()[1])+i]
								# else: # carry to another
								# 	for i in range(int(rtc.datetime()[1])-changeTime[1]):
								# 		monthChangeSecs = monthChangeSecs - monthdays[changeTime[1]+i]
								# # then translate it to changed secs
								# monthChangeSecs = monthChangeSecs*86400
								
								# # if days carry to month or not carry to month
								# dayChangeSecs = (changeTime[2]-int(rtc.datetime()[2]))*86400
								
								# # if hours carry to day or not carry to day
								# hourChangeSecs = (changeTime[3]-int(rtc.datetime()[4]))*3600

								# # if mins carry to hour or not carry to hour
								# minChangeSecs = (changeTime[4]-int(rtc.datetime()[5]))*60

								# # if secs carry to min or not carry to min
								# secChangeSecs = (changeTime[5]-int(rtc.datetime()[6]))
									
								# alarmTime = time.time() + (yearChangeSecs+monthChangeSecs+dayChangeSecs+hourChangeSecs+minChangeSecs+secChangeSecs)
								alarmTime = time.time() + ((changeTime[0]-int(rtc.datetime()[4]))*3600+(changeTime[1]-int(rtc.datetime()[5]))*60+(changeTime[2]-int(rtc.datetime()[6])))
								break

						# in the change time screen, switch C is pressed, move the cursor
						if switchC.value() == 0: 
							if Debounce(switchC): 
								indexCT += 1
								if indexCT > 2: indexCT = 0 # only have 6 parameters to change
						
						# in the change time screen, switch B is pressed, add 1 to the value corresponding to the cursor
						if switchB.value() == 0:
							if Debounce(switchB): 
								changeTime[indexCT] += 1
								changeTime = Carry(changeTime)


				# choose the third function i.e. return to the current time, quit interrupt handler
				else:
					return


# use falling edge as interupt
switchA.irq(trigger = Pin.IRQ_FALLING, handler = Interrupt)


global alarmTime
alarmTime = time.time() -1		# initial alarmtime = -1, to ensure the alarm not burst when program starts


runTime = time.time() + 360				# program life time is 20s

while (runTime - time.time()) > 0:		# do nothing in main function
	FuncSCT()
	oled.show()
	Refresh(10) # OLED refresh at 10Hz
	lightSensor = ADC(0) 						# create ADC object on ADC pin
	
	# Class 'SSD1306_I2C' inherits from Parent Class 'SSD1306', so we can use contrast function
	oled.contrast(255-int(lightSensor.read()*255/1024))	# read value, 0-1024, turn to 0-255

	if (alarmTime - time.time()) == 0:
		# print('ALARM ALARM ALARM ALARM')
		redLED.value(1)

	if (alarmTime - time.time()) == -5:
		redLED.value(0)



