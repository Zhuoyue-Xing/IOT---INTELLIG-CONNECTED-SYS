# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/9/29.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.

from machine import I2C, Pin, SPI
import ssd1306
import time
#oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
# The maximum SPI clock speed is 5 MHz with 100 pF maximum loading, and the timing scheme follows clock polarity (CPOL) = 1 and clock phase (CPHA) = 1
spi = SPI(-1, baudrate=100000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12), bits=8)
cs = Pin(16, Pin.OUT, value=1) # chip select
spi.init(baudrate=100000)

i2c = I2C(-1, scl=Pin(5), sda=Pin(4)) # initialize access to the I2C bus
i2c.scan()
oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32

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

# to calculate the scroll direction and speed
def Scroll(x1, x2, y1, y2):
    # get the difference of two sensor output of X and Y
    # do the data normalization
    # reflect data to 0-3, to control the speed
    x = int(3*(x2 - x1)/255)
    y = int(3*(y2 - y1)/255)

    strXL = 70  # the x-axis length of string
    strYL = 8   # the y-axis length of string

    # the initial position of text, defined outside main function loop
    global x0
    global y0
    # change text position, considering the hardware composition
    x0 += x 
    y0 -= y

    if x0 > 128:
        x0 = -strXL     # text scrolls to the right until it goes off screen before it reappears on the left
    elif x0 < -strXL:
        x0 = 128        # text scrolls to the left until it goes off screen before it reappears on the right

    if y0 > 32:
        y0 = -strYL     # text scrolls to the down until it goes off screen before it reappears on the top
    elif y0 < -strYL:
        y0 = 32         # text scrolls to the top until it goes off screen before it reappears on the down

# the text on screen
def Text(x, y):
    oled.text('Code works', x, y)

# refresh the OLED, remove residue
def Refresh(rate):
    time.sleep_ms(int(1000/rate))   # every 1000/rate ms
    oled.fill(0)                # To fill the entire screen with black, that is, refresh the screen


ADXL345_init(cs) # initial the ADXL345

runTime = time.time() + 60				# program life time is 60s

# the initial position of text, in the middle of screen
global x0
global y0
x0 = 25
y0 = 12

while (runTime - time.time()) > 0:		# main function
    accRaw = SPI_read(cs, b'\xF2', 6)	# Add=0x32, read to accRaw
    Scroll(accRaw[0], accRaw[1], accRaw[2], accRaw[3])  # caluculate the scrolled position
    Text(x0, y0)                                        # show text at the scrolled position
    oled.show()
    Refresh(10)


