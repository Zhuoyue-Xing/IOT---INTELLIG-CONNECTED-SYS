# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/18.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.


from machine import Pin, PWM
from machine import ADC
import time


# led = Pin(15, Pin.OUT)
runTime = time.time() + 20	# program lifetime = 60s
bright = 512				# initial duty cycle of PWM is 50% 


while (runTime - time.time()) > 0:
	led = PWM(Pin(13), freq=500, duty=bright) 	# creat a PWM on Pin 13 as output
	lightSensor = ADC(0) 						# create ADC object on ADC pin
	time.sleep_ms(100)							# ADC run at 10Hz
	bright = lightSensor.read() 				# read value, 0-1024, as the duty cycle of PWM
