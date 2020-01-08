# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/26.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, SPI
import socket
import ssd1306
import time
import network
import urequests
import json

#oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
# The maximum SPI clock speed is 5 MHz with 100 pF maximum loading, and the timing scheme follows clock polarity (CPOL) = 1 and clock phase (CPHA) = 1
spi = SPI(-1, baudrate=100000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12), bits=8)
cs = Pin(16, Pin.OUT, value=1) # chip select
spi.init(baudrate=100000)

i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
i2c.scan()
oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
switchA = Pin(2, Pin.IN) # GPIO#2 has a pullup resistor connected to it


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


# debouncing
# Return 1: equal, means NOT a bounce and the key is stable now
# Return 0: NOT equal, means it's just a bounce
def Debounce(pin):
	currentValue = pin.value()				# once called, read a value and record as current value
	time.sleep_ms(20)						# after 20ms, which means waiting for the bouncing end
	return pin.value() == currentValue		# check if the pin value equals to that 20ms ago


# SPI write data, MOSI
def SPI_write(cs, address, data):
	# cs <Pin obj> chip select
	# address <bytearray> address of register to write, should + 0x40 to set first two bits '01'
	# data <bytearray> data to write into register
	cs.value(0) # enable chip
	spi.write(address)
	spi.write(data)
	cs.value(1) # disable chip

# SPI read data, MISO
def SPI_read(cs, address, nbyte):
	# cs <Pin obj> chip select
	# address <bytearray> address of register to read, should + 0xC0 to set first two bits '11'
	# nbyte: read nbyte bytes on MISO
	cs.value(0) # enable chip
	spi.write(address)
	b = spi.read(nbyte)
	cs.value(1) # disable chip
	return b

# initial the ADXL345
def ADXL345_init(cs):
	SPI_write(cs, b'\x6C', b'\x0A')  # Add=0x2C Data=00001010 Data rate and power mode control..
	SPI_write(cs, b'\x6D', b'\x28')  # Add=0x2D Data=00101000 Power-saving features control.
	SPI_write(cs, b'\x6E', b'\xFF')  # Add=0x2E Data=11111111 Interrupt enable control.

	SPI_write(cs, b'\x71', b'\x08')  # Add=0x31 Data=00001000  Data format control. A value of 0 in the INT_INVERT bit sets the interrupts to active high.
	SPI_write(cs, b'\x78', b'\x80')  # Add=0x38 Data=10000000 FIFO control.

# to send accelerator data to AWS EC2 Server
def SendAWS(label, ID, seq, x1, x2, y1, y2, z1, z2):
	headers = {"Content-Type": "application/json; charset=UTF-8"}
	url = "http://3.87.68.197:8099/predict/post"
	request_data = {
	"label":label,
	"ID":ID,
	"seq":seq, 
	"x1":x1,
	"x2":x2,
	"y1":y1,
	"y2":y2,
	"z1":z1,
	"z2":z2
	}
	# returns a json string
	return urequests.post(url, data=json.dumps(request_data), headers=headers).text


# interrupt handler
def Interrupt(pin):
	if Debounce(switchA):
		# When the OLED display Begin Now, please do the gesture
		oled.fill(0) # clear the OLED
		oled.show()
		time.sleep_ms(1000)
		oled.text('Begin Now',0,0)
		oled.show()
		# Send one letter data in sequence to AWS
		for seq in range(20):
			time.sleep_ms(100)
			accRaw = SPI_read(cs, b'\xF2', 6)   # Add=0x32, read to accRaw
			print(accRaw[0],'\t',accRaw[1],'\t',accRaw[2],'\t',accRaw[3],'\t',accRaw[4],'\t',accRaw[5])
			SendAWS("predict",0,seq,accRaw[0],accRaw[1],accRaw[2],accRaw[3],accRaw[4],accRaw[5])
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

		

switchA.irq(trigger = Pin.IRQ_FALLING, handler = Interrupt) # use falling edge as interupt


if __name__ == '__main__':

	ADXL345_init(cs) # initial the ADXL345

	ConnectWIFI('Columbia University','') # connect esp8266 to a router

	while True:
		1+1





