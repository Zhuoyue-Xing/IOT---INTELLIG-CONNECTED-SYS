# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/28.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import Pin, I2C, ADC
import time
import ssd1306

i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
# print(i2c.scan())
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

oled.text('Chenye Yang', 0, 0)	# (message, x, y, color)
oled.text('Haokai Zhao', 0, 11)
oled.text('Zhuoyue Xing', 0, 22) 
oled.show()

runTime = time.time() + 20				# program life time is 20s

while (runTime - time.time()) > 0: 		# main function
	lightSensor = ADC(0) 				# create ADC object on ADC pin
	# print(lightSensor.read())
	time.sleep_ms(100)							# ADC run at 10Hz	
	# Class 'SSD1306_I2C' inherits from Parent Class 'SSD1306', so we can use contrast function
	oled.contrast(255-int(lightSensor.read()*255/1024))	# read value, 0-1024, turn to 0-255
	