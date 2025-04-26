import spidev
import RPi.GPIO as GPIO
import time


SPI_BUS = 0             # spidev0
SPI_SS  = 0             # spidev0.0
SPI_CLOCK = 3000000     # 3 Mhz
CP = 18

# setup SPI
spi = spidev.SpiDev(SPI_BUS, SPI_SS)
spi.max_speed_hz = SPI_CLOCK

# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CP, GPIO.OUT)

# register labels
RCLK = 1 << 7
RXOE = 1 << 6
RYOE = 1 << 5

def latch():
    GPIO.output(CP, GPIO.HIGH)
    GPIO.output(CP, GPIO.LOW)

try:
    b = 128
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
