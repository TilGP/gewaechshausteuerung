import RPI.GPIO as GPIO
import time

# definiere Relay Pin
relay_pin = 40

GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay_pin, GPIO.OUT)

GPIO.output(relay_pin, GPIO.LOW)
time.sleep(0.5)
GPIO.output(relay_pin, GPIO.HIGH)
GPIO.cleanup()
