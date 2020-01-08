from machine import I2C, Pin, SPI
import ssd1306
import time
#oled = ssd1306.SSD1306_I2C(128, 32, i2c) # the width=128 and height=32
# The maximum SPI clock speed is 5 MHz with 100 pF maximum loading, and the timing scheme follows clock polarity (CPOL) = 1 and clock phase (CPHA) = 1
spi = SPI(-1, baudrate=100000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12), bits=8)
cs = Pin(16, Pin.OUT, value=1)
spi.init(baudrate=100000)

class kalman_filter:
    def __init__(self,Q,R):
        self.Q = Q
        self.R = R
        
        self.P_k_k1 = 1
        self.Kg = 0
        self.P_k1_k1 = 1
        self.x_k_k1 = 0
        self.ADC_OLD_Value = 0
        self.Z_k = 0
        self.kalman_adc_old=0
        
    def kalman(self,ADC_Value):
       
        self.Z_k = ADC_Value
        
        if (abs(self.kalman_adc_old-ADC_Value)>=60):
            self.x_k1_k1= ADC_Value*0.382 + self.kalman_adc_old*0.618
        else:
            self.x_k1_k1 = self.kalman_adc_old;
    
        self.x_k_k1 = self.x_k1_k1
        self.P_k_k1 = self.P_k1_k1 + self.Q
    
        self.Kg = self.P_k_k1/(self.P_k_k1 + self.R)
    
        kalman_adc = self.x_k_k1 + self.Kg * (self.Z_k - self.kalman_adc_old)
        self.P_k1_k1 = (1 - self.Kg)*self.P_k_k1
        self.P_k_k1 = self.P_k1_k1
    
        self.kalman_adc_old = kalman_adc
        
        return kalman_adc


def SPI_write(cs, address, data):
    # cs <Pin obj> chip select
    # address <bytearray> address of register to write, should + 0x40 to set first two bits '01'
    # data <bytearray> data to write into register
    cs.value(0) # enable chip
    spi.write(address)
    spi.write(data)
    cs.value(1) # disable chip


def SPI_read(cs, address, nbyte):
    # cs <Pin obj> chip select
    # address <bytearray> address of register to read, should + 0xC0 to set first two bits '11'
    # nbyte: read nbyte bytes on MISO
    cs.value(0) # enable chip
    spi.write(address)
    b = spi.read(nbyte)
    cs.value(1) # disable chip
    return b


def ADXL345_init(cs):
    SPI_write(cs, b'\x6C', b'\x0A')  # Add=0x2C Data=00001010 Data rate and power mode control..
    SPI_write(cs, b'\x6D', b'\x28')  # Add=0x2D Data=00101000 Power-saving features control.
    SPI_write(cs, b'\x6E', b'\xFF')  # Add=0x2E Data=11111111 Interrupt enable control.

    SPI_write(cs, b'\x71', b'\x0B')  # Add=0x31 Data=00001011  Data format control. A value of 0 in the INT_INVERT bit sets the interrupts to active high.
    SPI_write(cs, b'\x78', b'\x80')  # Add=0x38 Data=10000000 FIFO control.



ADXL345_init(cs)

kalman_filter =  kalman_filter(0.001,0.1)

runTime = time.time() + 60				# program life time is 20s

while (runTime - time.time()) > 0:		# do nothing in main function
    
    accRaw = SPI_read(cs, b'\xF2', 6)            # Add=0x32 
    accData = []
    for i in range(6):
        accData.append(kalman_filter.kalman(accRaw[i]))
    print(accData)
    time.sleep_ms(500)

