import spidev
import RPi.GPIO as GPIO
import time


SPI_BUS = 0             # spidev0
SPI_SS  = 0             # spidev0.0
SPI_CLOCK = 1000000     # 1 Mhz
CP = 18                 # GPIO 18 as CP

# setup SPI
spi = spidev.SpiDev(SPI_BUS, SPI_SS)
spi.max_speed_hz = SPI_CLOCK

# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CP, GPIO.OUT)

# register labels
RCLK = 1 << 7       # bit 7 del segundo byte, es decir bit 15 del word. 
RXOE = 1 << 6       # bit 6 del segundo byte, es decir bit 14 del word. 
RYOE = 1 << 5       # bit 5 del segundo byte, es decir bit 13 del word. 

# TODO: para elegir el WR
RR2 = 1 << 2        # bit 2 del segundo byte, es decir bit 10 del word. 
RR1 = 1 << 1        # bit 1 del segundo byte, es decir bit 9 del word. 
RR0 = 1 << 0        # bit 0 del segundo byte, es decir bit 8 del word. 

def latch():
    """Send a latch pulse (bit 15)"""
    GPIO.output(CP, GPIO.HIGH)
    GPIO.output(CP, GPIO.LOW)

try:
    b = 0x80
    while True:
        spi.writebytes([RYOE, b])
        latch()
        spi.writebytes([RCLK|RYOE, b])
        latch()
        if b > 0:
            b = b >> 1
        else:
            b = 128
        time.sleep(0.5)

finally:
    spi.close()
    GPIO.cleanup()
