# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/12.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.


from machine import Pin
import time

p0 = Pin(0, Pin.OUT, value=1)		# red LED, initial turn off
p2 = Pin(2, Pin.OUT, value=1)		# blue LED, initial turn off

lightValue = 200	# bright LED last time, ms
redGap = 1000		# time between red LED turn on
blueGap = 3000		# time between red LED turn on

redON = time.ticks_add(time.ticks_ms(), redGap)	# add redGap from now, the next time point red LED light
blueOn = time.ticks_add(time.ticks_ms(), blueGap)	# add blueGap from now, the next time point blue LED light
redOff = time.ticks_add(time.ticks_ms(), lightValue)		# add lightValue from now, the next time point red LED turn off
blueOff = time.ticks_add(time.ticks_ms(), lightValue)		# add lightValue from now, the next time point blue LED turn off
runTime = time.time() + 60							# program lifetime = 60s

while (runTime - time.time()) > 0:					# control program life
	if time.ticks_diff(redON, time.ticks_ms()) <= 0:			# if meet the red-LED-light time point
		p0.value(0)												# turn on the red LED
		redON = time.ticks_add(time.ticks_ms(), redGap)		# re-calculate the next red-LED-light time point
		redOff = time.ticks_add(time.ticks_ms(), lightValue)	# reset the red-LED-off time point to lightValue mseconds later

	if time.ticks_diff(redOff, time.ticks_ms()) <= 0:			# if meet the red-LED-off time point
		#redOff = time.ticks_add(time.ticks_ms(), lightValue)
		p0.value(1)												# turn off the red LED

	# situation same as the red LED
	if time.ticks_diff(blueOn, time.ticks_ms()) <= 0:
		p2.value(0)
		blueOn = time.ticks_add(time.ticks_ms(), blueGap)
		blueOff = time.ticks_add(time.ticks_ms(), lightValue)

	if time.ticks_diff(blueOff, time.ticks_ms()) <= 0:
		#blueOff = time.ticks_add(time.ticks_ms(), lightValue)
		p2.value(1)	
