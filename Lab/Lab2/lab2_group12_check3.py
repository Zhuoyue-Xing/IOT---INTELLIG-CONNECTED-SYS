# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/22.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.


from machine import Pin, PWM, ADC
import time


switch = Pin(15, Pin.IN) # With the inner pulldown register, we can get a stable 0V when the switch is not pressed. 
led = PWM(Pin(13), freq=500, duty=0) # initial a PWM with duty cycle 0 to turn off the led. because the output is random if not defined.


# debouncing
def Debounce(pin):
	currentValue = pin.value()				# once called, read a value and record as current value
	time.sleep_ms(20)						# after 20ms, which means waiting for the bouncing end
	if pin.value() != currentValue:			# check if the pin value equals to that 20ms ago
		return 0							# NOT equal, means it is just a bounce
	else:
		return 1							# equal, means NOT a bounce and the key is stable now 
		

# interrupt handler
def Interrupt(pin):		
	keyNotBounce = Debounce(pin)			# rising edge leads to interrupt, do debounce first
	if keyNotBounce == 0: 				# The signal is just a bounce
		return								# do nothing and return to main function
	else:								# The signal is not a bounce and key situation is stable
		if  pin.value() == 1:				# if caused by rising edge, now the pin value should be HIGH
			bright = 512					# initial duty cycle of PWM is 50% 
			while 1:
				led = PWM(Pin(13), freq=500, duty=bright)		# creat a PWM on Pin 13 as output
				lightSensor = ADC(0) 							# create ADC object on ADC pin
				time.sleep_ms(100)								# ADC run at 10Hz
				bright = lightSensor.read() 					# read value, 0-1024
				if pin.value() == 0:							# if detect the pin value change to LOW
					if Debounce(pin):							# judge if it's bounce caused
						led = PWM(Pin(13), freq=500, duty=0)	# not by bouncing, switch is not being pressed, duty cycle set to 0 and turn off the led
						return									# return to main func

		elif pin.value() == 0:				# if caused by falling edge, now the pin value should be LOW
			return

# def vRising(pin):
# 	print ("V Rising")
# 	Debounce(1,pin)

# def vFalling(pin):
# 	print ("V Falling")
# 	Debounce(0,pin)
	
# switch.irq(trigger = Pin.IRQ_FALLING, handler = vFalling)
# switch.irq(trigger = Pin.IRQ_RISING, handler = vRising)
# If we have two intrerupts for one Pin, can't define as former. 
# Only run the last sentence!!
# Should define as "p2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=callback)"
# Two types of interrupts only can use one interrupt handler

# switch.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = Debounce)
# Also can't write as former, because may cause chaos in program

# use rising edge as interupt and judge in interrupt handler whether pin is LOW to exit handler
switch.irq(trigger = Pin.IRQ_RISING, handler = Interrupt)


runTime = time.time() + 20				# program life time is 20s

while (runTime - time.time()) > 0:		# do nothing in main function
    1+1
