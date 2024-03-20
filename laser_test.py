from RPi import GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, 1)
sleep(5)
GPIO.output(16, 0)