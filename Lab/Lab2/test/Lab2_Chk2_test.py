from machine import Timer
from machine import Pin
import time

switch = Pin(15, Pin.IN) # With the inner pulldown register, we can get a stable 0V when the switch is not pressed. 
redLED = Pin(0, Pin.OUT, value = 1)
# waitTime = time.ticks_add(time.ticks_ms(), 10)



def keyChange(p):
	global switch_state
	global switched
	global last_switch_state
	switch_state = 0
	switched = True
	last_switch_state = 0
	switch_state = switch.value()
	if switch_state != last_switch_state:
		switched = True
	last_switch_state = switch_state

tim = Timer(-1)
tim.init(period=50, mode=Timer.PERIODIC, callback=keyChange)

def Debounce(pin):
	currentValue = pin.value()
	time.sleep_ms(20)
	if pin.value() != currentValue:
		print ("000000000000000")
		return 0
	else:
		print ("1111111111111111")
		return 1
		
def Interrupt(pin):
	global switched
	keyNotBounce = Debounce(pin)
	if keyNotBounce == 0: # The signal is just a bounce
		return
	else:	# The signal is not a bounce and key situation is stable
		if  pin.value() == 1:
			last_switch_state = 1
			while 1:
				print ("Light")
				redLED.value(0)
				if switched:
					switched = False
					return

			# time.sleep_ms(5000)
			# redLED.value(1)
		elif pin.value() == 0:
			last_switch_state = 0
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
# If we have two intrerupts for one Pin, can't def as this. 
# Only run the last sentence
# Should def as "p2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=callback)"
# Only have one interrupt function
# switch.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = Debounce)
switch.irq(trigger = Pin.IRQ_RISING, handler = Interrupt)


runTime = time.time() + 20

while (runTime - time.time()) > 0:
	# waitPinChange(switch)
	print (switch.value())
	redLED.value(1)