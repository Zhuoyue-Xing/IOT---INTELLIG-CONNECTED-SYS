# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/30.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, SPI, ADC, RTC
import socket
import ssd1306
import time
import network
import urequests
import json
import ntptime
import lab6_group12_esp8266_simple_dependence

switchA = Pin(2, Pin.IN)
switchB = ADC(0)
switchC = Pin(0, Pin.IN)

spi = SPI(-1, baudrate=100000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12), bits=8)
cs = Pin(16, Pin.OUT, value=1)
spi.init(baudrate=100000)

i2c = I2C(-1, scl=Pin(5), sda=Pin(4))
i2c.scan()
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

redLED = Pin(15, Pin.OUT, value = 0)

rtc = RTC()

interrupt_end = 0


def WhatCommand(cmd):
	global interrupt_end

	if cmd == 'show current time':
		interrupt_end = 1

	if cmd.find('tweets') > (-1):
		twt = cmd.split('tweets ')[1]
		oled.fill(0)
		oled.text(twt,0,0)
		oled.text('Listening',80,22)
		oled.show()

	if cmd.find('weather') > (-1):
		wth = cmd.split('weather ')[1]
		oled.fill(0)
		oled.text(wth,0,0)
		oled.text('Listening',80,22)
		oled.show()



def ListenResponse():
	oled.fill(0)
	oled.text('Listening',80,22)
	oled.show()
	addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
	s = socket.socket()
	s.bind(addr)
	s.listen(1)
	print('listening on', addr)
	while True:	
		global interrupt_end
		if interrupt_end: return
		cl, addr = s.accept()
		print('client connected from', addr)
		cl_receive = cl.recv(200).decode("utf-8")
		print(cl_receive)
		cl_receive = json.loads(cl_receive.split("\r\n")[-1])['Command']
		response = "HTTP/1.1 200 OK\r\nGood"
		WhatCommand(cl_receive)
		cl.send(response)
		cl.close()


# interrupt handler
def Interrupt(pin):
	item = 0
	global interrupt_end
	interrupt_end = 0
	while 1:
		lab6_group12_esp8266_simple_dependence.Refresh(oled, 10)
		lab6_group12_esp8266_simple_dependence.Menu(oled, item)
		oled.show()
		
		if switchA.value() == 0 and lab6_group12_esp8266_simple_dependence.Debounce(switchA):
			return

		if switchB.read() < 128:
			item += 1
			time.sleep(1)
			if item > 4:
				item = 0

		if switchC.value() == 0 and lab6_group12_esp8266_simple_dependence.Debounce(switchC):
			if item == 0:
				changeTime = list(rtc.datetime())
				indexCT = 0

				while 1:
					lab6_group12_esp8266_simple_dependence.Refresh(oled, 10)
					lab6_group12_esp8266_simple_dependence.ShowTime(oled, changeTime)
					if indexCT > 2:
						oled.text('_', 9+(indexCT-4)*23, 13)
					else:
						oled.text('_', 24+indexCT*23, 2)
					oled.show()

					if switchA.value() == 0 and lab6_group12_esp8266_simple_dependence.Debounce(switchA):
						rtc.datetime(tuple(changeTime))
						break

					if switchC.value() == 0 and lab6_group12_esp8266_simple_dependence.Debounce(switchC): 
						indexCT += 1
						if indexCT == 3: indexCT +=1
						if indexCT > 6: indexCT = 0
					
					if switchB.read() < 128:
						changeTime[indexCT] += 1
						time.sleep(1)

			elif item == 1:
				changeTime = list(rtc.datetime())
				indexCT = 0

				while 1:
					lab6_group12_esp8266_simple_dependence.Refresh(oled, 10)
					lab6_group12_esp8266_simple_dependence.ShowTime(oled, changeTime)
					if indexCT > 2:
						oled.text('_', 9+(indexCT-4)*23, 13)
					else:
						oled.text('_', 24+indexCT*23, 2)
					oled.show()

					if switchA.value() == 0 and lab6_group12_esp8266_simple_dependence.Debounce(switchA):
						global alarmTime
						alarmTime = time.time()+(changeTime[5]-int(rtc.datetime()[5]))*60+(changeTime[6]-int(rtc.datetime()[6]))
						break

					if switchC.value() == 0 and lab6_group12_esp8266_simple_dependence.Debounce(switchC): 
						indexCT += 1
						if indexCT == 3: indexCT +=1
						if indexCT > 6: indexCT = 0
					
					if switchB.read() < 128:
						changeTime[indexCT] += 1
						time.sleep(1)
			
			elif item == 2:
				ListenResponse()
				if interrupt_end: return
			
			elif item == 3:
				oled.fill(0)
				oled.show()
				time.sleep_ms(1000)
				oled.text('Begin Now',0,0)
				oled.show()
				for seq in range(20):
					time.sleep_ms(100)
					accRaw = lab6_group12_esp8266_simple_dependence.SPI_read(spi, cs, b'\xF2', 6)
					# print(accRaw[0],'\t',accRaw[1],'\t',accRaw[2],'\t',accRaw[3],'\t',accRaw[4],'\t',accRaw[5])
					lab6_group12_esp8266_simple_dependence.SendAWS("predict",0,seq,accRaw[0],accRaw[1],accRaw[2],accRaw[3],accRaw[4],accRaw[5])
				oled.fill(0)
				oled.text('Waitting',0,0)
				oled.show()
				headers = {"Content-Type": "application/json; charset=UTF-8"}
				url = "http://3.87.68.197:8099/predict/order/post"
				request_data = {'order':'predict'}
				predictResult = json.loads(urequests.post(url=url, data=json.dumps(request_data), headers=headers).text)['result']
				oled.fill(0)
				oled.text(predictResult,0,0)
				oled.show()
				print('Predict Result is: ', predictResult)

				time.sleep_ms(1000)

			else:
				return

switchA.irq(trigger = Pin.IRQ_FALLING, handler = Interrupt)



if __name__ == '__main__':
	lab6_group12_esp8266_simple_dependence.ADXL345_init(spi, cs)
	lab6_group12_esp8266_simple_dependence.ConnectWIFI('Rock_NYC','Columbia_SEAS_17')
	ntptime.settime()
	global alarmTime
	alarmTime = -1
	while True:
		lab6_group12_esp8266_simple_dependence.ShowTime(oled, rtc.datetime())
		oled.show()
		lab6_group12_esp8266_simple_dependence.Refresh(oled, 10)
		# lab6_group12_esp8266_simple_dependence.ChangeBright(oled)
		if (alarmTime - time.time()) == 0:
			redLED.value(1)
		if (alarmTime - time.time()) == -3:
			redLED.value(0)






