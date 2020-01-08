# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/18.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.


from machine import Pin
import time

switch = Pin(15, Pin.IN) # With the inner pulldown register in Pin 15, we can get a stable 0V when the switch is not pressed. 
redLED = Pin(0, Pin.OUT, value = 1)

# debouncing
def Debounce(pin):
	currentValue = pin.value()		# once called, read a value and record as current value
	time.sleep_ms(20)				# after 20ms, which means waiting for the bouncing end
	if pin.value() != currentValue:	# check if the pin value equals to that 20ms ago
		print ("000000000000000")
		return 0					# NOT equal, means it is just a bounce
	else:
		print ("1111111111111111")
		return 1					# equal, means NOT a bounce and the key is stable now 

# interrupt handler
def Interrupt(pin):
	keyNotBounce = Debounce(pin)	# rising edge leads to interrupt, do debounce first
	if keyNotBounce == 0: 			# The signal is just a bounce
		return						# do nothing and return to main function
	else:							# The signal is not a bounce and key situation is stable
		if  pin.value() == 1:		# if caused by rising edge, now the pin value should be HIGH
			while 1:
				print ("Light")		# do sth
				redLED.value(0)
				if pin.value() == 0:	# if detect the pin value change to LOW
					if Debounce(pin):	# judge if it's bounce caused
						return			# not by bouncing, switch is not being pressed, return to main func

		elif pin.value() == 0:		# if caused by falling edge, now the pin value should be LOW
			print ("No light")
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


runTime = time.time() + 20		# program life time is 20s

while (runTime - time.time()) > 0:
	print (switch.value())
	redLED.value(1)



