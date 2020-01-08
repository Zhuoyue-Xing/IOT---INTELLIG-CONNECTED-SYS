# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/12.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.


from machine import Pin
import time

P0 = Pin(0, Pin.OUT)	# the red LED
# P2 = Pin(2, Pin.OUT)	# the blue LED

def Dots():
	P0.value(0)			# low to enable the LED
	time.sleep_ms(200)
	P0.value(1)			# high to disable the LED

def Dashes():
	P0.value(0)
	time.sleep_ms(500)
	P0.value(1)

def Blank():			# Blank between the three symbol of a char
	time.sleep_ms(200)

def S():
	Dots()
	Blank()
	Dots()
	Blank()
	Dots()
	Blank()

def O():
	Dashes()
	Blank()
	Dashes()
	Blank()
	Dashes()
	Blank()

for i in range(5):
	# P2.value(0)
	# time.sleep_ms(250)
	# P2.value(1)
	# time.sleep_ms(1000)
	S()
	Blank()
	O()
	Blank()
	S()
	Blank()
	time.sleep_ms(1000)